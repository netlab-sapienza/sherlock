import time
import requests
import json
from datetime import datetime
from geopy.geocoders import Nominatim
from ripe.atlas.cousteau import (
	Ping,
	AtlasSource,
	AtlasCreateRequest,
)

REQ_TIMEOUT = 10
IDEAL_RTT = 10
penalty_factor = 5

VERBOSE = True




def geolocalization(lats, longs, rtts, verbose = False):
	
	# Calcola i pesi
	pesi_rtt = [(abs(rtt-IDEAL_RTT)/(min(rtts)))**(-penalty_factor) for rtt in rtts]
	totale_pesi = sum(pesi_rtt)
	
	if verbose:
		for rtt, w in zip(rtts, pesi_rtt):
			print(str(round(rtt, 4))+"\t\t->\t"+str(w))
		print("\n")
	# Calcola la posizione ponderata
	la_ponderata = sum([w * la for w, la in zip(pesi_rtt, lats)])
	lo_ponderata = sum([w * lo for w, lo in zip(pesi_rtt, longs)])

	# Calcola la posizione stimata finale
	la_stimata = round(la_ponderata/totale_pesi, 4)
	lo_stimata = round(lo_ponderata/totale_pesi, 4)
	
	return [la_stimata, lo_stimata]
	
	
	

def probe_info(probe_id, REQ_TIMEOUT):
	url = f'https://atlas.ripe.net/api/v2/probes/{probe_id}/'
	params = {"format": "json"}
	try:
		response = requests.get(url, params=params, timeout=REQ_TIMEOUT)

		if response.status_code == 200:
			r = json.loads(response.content.decode("utf-8"))
			return r["geometry"]["coordinates"]
			
		else:
			print("\tFailed GET request in \"probe_info\". Status code: ", response.status_code)
			return " * "
	except requests.exceptions.Timeout:
		print("\t\"probe_info\" request timeout.")
		return " * "




def createMeasurement(ip_target, country_code, num_probes, ATLAS_API_KEY):
	ping = Ping (
		af = 4,
		target = ip_target,
		packets = 3,
		description = "Ping towards specified IPv4"
	)

	source = AtlasSource(
		type = "country",
		value = country_code,
		requested = num_probes,
		tags = {"include":["system-ipv4-works"]}
	)

	atlas_request = AtlasCreateRequest(
		start_time = datetime.utcnow(),
		key = ATLAS_API_KEY,
		measurements = [ping],
		sources = [source],
		is_oneoff = True
	)

	(is_success, response) = atlas_request.create()
	if is_success:
		print(f"Measurement succesfully created with id: {response}")
	else:
		print("Error in creating measurement, please try again")




def analyzeMeasurement(msm_id):
	url = f"https://atlas.ripe.net/api/v2/measurements/{msm_id}/results/"
	params = {"format": "json"}
	try:
		response = requests.get(url, params=params, timeout=REQ_TIMEOUT)
		lats = []
		longs = []
		rtts = []
		if response.status_code == 200:
			r = json.loads(response.content.decode("utf-8"))
			for el in r:
				long, lat = probe_info(el["prb_id"], REQ_TIMEOUT)
				lats.append(lat)
				longs.append(long)
				rtts.append(el["avg"])
				
			LA, LO = geolocalization(lats, longs, rtts, VERBOSE)
			coordinates = str(LA)+", "+str(LO)
			print(coordinates)
			geolocator = Nominatim(user_agent="sherlock")
			location = geolocator.reverse(coordinates)
			geo = location.address.split(", ")
			print(geo[2]+", "+geo[6])
			print(geo)
		else:
			print("\tFailed GET request in \"retrieving measurement info\". Status code: ", response.status_code)
			#return " * "
	except requests.exceptions.Timeout:
		print("\t\"Retrieving measurement info\" request timeout.")
		#return " * "
		
		
		
	
print("What do you want to do:\n1 - Create a new measurement\n2 - Retrieve infos about a done measurement")
interaction = input("[1 / 2]: ")
if interaction == "1":
	ATLAS_API_KEY = input("Please enter your ATLAS_API_KEY: ")
	num_probes = input("Please enter how many probes do you want to use: ")
	country_code = input("Please enter country_code for selecting probes: ")
	ip_target = input("Please enter the IPv4 address of the target: ")
	createMeasurement(ip_target, country_code, num_probes, ATLAS_API_KEY)
elif interaction == "2":
	measurement_id = input("Please enter measurement id: ")
	analyzeMeasurement(measurement_id)
