import requests
import json
from functions import is_public, update_caida
from scapy.all import IP, ICMP, sr1



def ping_as(as_number, REQ_TIMEOUT):
	# Step 1: Connect to the BGPView API
	api_url = f'https://api.bgpview.io/asn/{as_number}/prefixes'
	headers = {"User-Agent": "testing uniroma1.com - email@example.com"}
	try:
		response = requests.get(api_url, headers=headers, timeout=REQ_TIMEOUT)

		# Step 2: Extract all IPv4 prefixes
		data = response.json()

		# Step 3: Ping .1 of one prefix using Scapy
		prefix = data['data']['ipv4_prefixes'][0]['ip']
		ip_address = prefix[:-1]+"1"
		try:
			packet = IP(dst=ip_address) / ICMP()
			response = sr1(packet, timeout=1, verbose=False)
			if response:
				return True
		except Exception as e:
			print(f"Error pinging {ip_address} using Scapy: {e}")
			return False
				
	except requests.exceptions.Timeout:
		return False



def get_as_home(REQ_TIMEOUT):
	try:
		response = requests.get("https://api.ipify.org?format=json")
		data = response.json()
		AS, _ = find_as(data["ip"], REQ_TIMEOUT)
		return AS
		
	except Exception as e:
		print("Public IP address of host not found")
		return "*"



def find_location(ip_addr, REQ_TIMEOUT):
	if is_public(ip_addr):
		url = f"https://ipmap-api.ripe.net/v1//locate/all/"
		params = {"resources": ip_addr}
		try:
			response = requests.get(url, params=params, timeout=REQ_TIMEOUT)

			if response.status_code == 200:
				r = json.loads(response.content.decode("utf-8"))
				location_str = []
				if ip_addr in list(r["data"].keys()):
					city = r["data"][ip_addr]["cityName"]
					country = r["data"][ip_addr]["countryName"]
					code = r["data"][ip_addr]["countryCodeAlpha2"]
					return code+", "+country+", "+city
				else:
					return "No available address"
			else:
				print("\tFailed GET request in \"find_location\". Status code: ", response.status_code)
				return " * "
		except requests.exceptions.Timeout:
			print("\t\"find_location\" request timeout.")
			return " * "
	else:
		return "Private address"



def find_as(ip_addr, REQ_TIMEOUT):
	if is_public(ip_addr):
		url = "https://stat.ripe.net/data/prefix-overview/data.json"
		params = {"data_overload_limit": "ignore", "resource": ip_addr, "min_peers_seeing": "1"}
		try:
			response = requests.get(url, params=params, timeout=REQ_TIMEOUT)

			if response.status_code == 200:
				r = json.loads(response.content.decode("utf-8"))
				if len(r["data"]["asns"]) > 1:
					print("WARNING: found more than one asn, returning the first")
				elif len(r["data"]["asns"]) < 1:
					print("WARNING: found no asn, returning None")
					return None, ""
				if r["data"]["asns"][0]:
					asn = r["data"]["asns"][0]["asn"]
					holder = r["data"]["asns"][0]["holder"]
					return asn, holder
			else:
				print("Failed GET request. Status code: ", response.status_code)
				return None, ""
				
		except requests.exceptions.Timeout:
			print("AS Request timeout.")
			return None, ""
	else:
		return None, ""

def check_neighbour(as_path, REQ_TIMEOUT):
	
	ASP = []
	caida_db = update_caida(REQ_TIMEOUT)
	
	for index, asn in enumerate(as_path):
		if isinstance(asn, int):
			ASP.append(asn)
			
	known_asns = [ASP[i] for i in range(len(ASP)) if i == 0 or ASP[i] != ASP[i - 1]]
	
	as_list = []
	for i in range(len(known_asns) - 1):
		print(f"\t\tAS path step {i+1}/{len(known_asns)-1}")
		asn1 = known_asns[i]
		asn2 = known_asns[i + 1]
		
		flag, neighbours = intersect_neighbours(asn1, asn2, caida_db, REQ_TIMEOUT)
		if flag:
			as_list.append(asn1)
		else:
			as_list.append(asn1)
			as_list.append(neighbours)
	
	as_list.append(known_asns[-1])
	
	return as_list
	
def intersect_neighbours(as1, as2, caida_db, REQ_TIMEOUT):
	transit_neighbours_1 = set()
	peering_neighbours_1 = set()
	transit_neighbours_2 = set()
	peering_neighbours_2 = set()
	
	if caida_db is None:
		caida_db = "./20231101.as-rel.txt"

	with open("./"+caida_db, "r") as f:
		for line in f:
			if not line.startswith('#'):
				parts = line.strip().split('|')
				a1 = int(parts[0])
				a2 = int(parts[1])
				rel = int(parts[2])
				
				if (a1 == as1):
					if rel == 0:
						peering_neighbours_1.add(a2)
					elif rel == -1:
						transit_neighbours_1.add(a2)
				elif (a2 == as1):
					if rel == 0:
						peering_neighbours_1.add(a1)
					elif rel == -1:
						transit_neighbours_1.add(a1)
				if (a2 == as2):
					if rel == 0:
						peering_neighbours_2.add(a1)
					elif rel == -1:
						transit_neighbours_2.add(a1)
				elif (a1 == as2):
					if rel == 0:
						peering_neighbours_2.add(a2)
					elif rel == -1:
						transit_neighbours_2.add(a2)
				
	output = {}
	neighbours = False
	output["Transit"] = []
	
	if as2 in transit_neighbours_1 or as2 in peering_neighbours_1 or as1 in transit_neighbours_2 or as1 in peering_neighbours_2:
		neighbours = True
	else:
		inter = list(transit_neighbours_1.intersection(transit_neighbours_2))
		if len(inter)>0:
			idx = 0
			for AS in inter:
				idx += 1
				if idx < 11 and ping_as(AS, REQ_TIMEOUT):
					output["Transit"].append([AS, 'available'])
				elif idx < 11:
					output["Transit"].append([AS, 'unreachable'])
				else:
					output["Transit"].append([AS, 'unknown'])
		else:
			peer_inter = list(peering_neighbours_1.intersection(peering_neighbours_2))
			if len(peer_inter)>0:
				output["Peering"] = peer_inter
			else:
				output = "?"
			
		if len(transit_neighbours_1) == 1:
			if ping_as(list(transit_neighbours_1)[0], REQ_TIMEOUT):
				output["Transit"] = [list(transit_neighbours_1)[0], 'available']
			else:
				output["Transit"] = [list(transit_neighbours_1)[0], 'unreachable']
			f, n = intersect_neighbours(list(transit_neighbours_1)[0], as2, caida_db, REQ_TIMEOUT)
			if not f:
				output["Transit"].append(n)

	return neighbours, output


if __name__ == "__main__":
	#ip = "151.99.51.173"
	#asn, holder = find_as(ip)
	#loc = find_location(ip)
	as_path = [3269, '*', '*', '*', '*', 6762, '*', '*', 16625, '*', 15169, 12345]
	#as_path = [16232, 3269, 20940]
	as_list = check_neighbour(as_path, 5)
	print("INPUT : "+str(as_path))
	print("OUTPUT: "+str(as_list))
	#neighbours = find_neighbours(asn)
	#print(neighbours)
