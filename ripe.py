import requests
import json
from functions import is_public

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



def find_neighbours(asn, REQ_TIMEOUT):
	url = "https://stat.ripe.net/data/asn-neighbours/data.json"
	params = {"data_overload_limit": "ignore", "resource": str(asn)}
	try:
		response = requests.get(url, params=params, timeout=REQ_TIMEOUT)
		
		if response.status_code == 200:
			r = json.loads(response.content.decode("utf-8"))
			neighbours = []
			if len(r["data"]["neighbours"]) > 1:
				for el in r["data"]["neighbours"]:
					neighbours.append(el["asn"])
			elif len(r["data"]["neighbours"]) < 1:
				print("WARNING: found no asn, returning None")
				return None
			if r["data"]["neighbours"][0]:
				neighbours.append(r["data"]["neighbours"][0]["asn"])
				return neighbours
		else:
			print("Failed GET request. Status code: ", response.status_code)
			return None
	except requests.exceptions.Timeout:
		print("Request timeout.")
		return None



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
					return None, " --- "
				if r["data"]["asns"][0]:
					asn = r["data"]["asns"][0]["asn"]
					holder = r["data"]["asns"][0]["holder"]
					return asn, holder
			else:
				print("Failed GET request. Status code: ", response.status_code)
				return None, " --- "
				
		except requests.exceptions.Timeout:
			print("Request timeout.")
			return None, " --- "
	else:
		return None, " --- "



def check_neighbour(path, REQ_TIMEOUT):
	as_path = {}
	
	for idx, el in enumerate(path):
		if isinstance(el, int):
			as_path[idx] = el
	
	keys = list(as_path.keys())
	for i in range(len(keys) - 1):
		asn = as_path[keys[i]]
		next_asn = as_path[keys[i+1]]
		print(f"\n*** AS {asn} -> {next_asn}:")
		
		neighbours = find_neighbours(asn, REQ_TIMEOUT)
		
		if neighbours is not None:
			num_unknown_hops = keys[i+1]-keys[i]-1
			if next_asn == asn:
				print(f"\tSAME: {num_unknown_hops} unknown hops between them")
			elif next_asn in neighbours:
				print(f"\tCONNECTED: {num_unknown_hops} unknown hops between them")
			else:
				print(f"\tNOT CONNECTED: {num_unknown_hops} unknown hops between them")
		else:
			print("\tERROR: could not complete the request.")



if __name__ == "__main__":
	#ip = "151.99.51.173"
	#asn, holder = find_as(ip)
	#loc = find_location(ip)
	as_path = [3269, 6762, '*', '*', 15169, '*', 15169, 12345]
	check_neighbour(as_path)
	#neighbours = find_neighbours(asn)
	#print(neighbours)
