from datetime import datetime as d
from functions import *
from tr import *
import scapy.all as scapy
import sys
import time
import zmq
import os

context = zmq.Context()
requester = context.socket(zmq.REQ)
requester.connect("tcp://localhost:8000")



def process_packet(packet, cname):
	# Once the sniffer is activated, we keep track of DNS communications.
	# We also count how many bytes are received until a traffic source exceeds TH_BYTES.
	# Most-likely, the latter will be the content-cache server.
	# This function is executed for every received packet.
	global max_bytes
	global SNIFFER_TIMEOUT
	global last_update
	
	if scapy.IP in packet:						# Check if the packet contains IP layer
		
		if scapy.DNS in packet:				# Check if the packet contains DNS layer
			dns_info = packet[scapy.DNS]			# and process it
			if dns_info.qr == 0:  				#DNS query
				dns_data[str(dns_info.id)] = {}
				
			elif dns_info.qr == 1:				#DNS response
				#qdcount, ancount, nscount, arcount
				if str(dns_info.id) in dns_data.keys():
					if dns_info.qd is not None:	#Question
						dns_data[str(dns_info.id)]["Question"] = []
						dns_data[str(dns_info.id)]["Question"].append(dns_info.qd.qtype)
						dns_data[str(dns_info.id)]["Question"].append(dns_info.qd.qname.decode("utf-8"))
					if dns_info.an is not None:	#Answer
						dns_data[str(dns_info.id)]["Answer"] = []
						for x in range(dns_info.ancount):
							dns_data[str(dns_info.id)]["Answer"].append(dns_info.an[x].rrname)
							dns_data[str(dns_info.id)]["Answer"].append(dns_info.an[x].type)
							dns_data[str(dns_info.id)]["Answer"].append(dns_info.an[x].rdata)
					if dns_info.ns is not None:	#Authority (Name Server)
						dns_data[str(dns_info.id)]["NameServer"] = []
						for x in range(dns_info.nscount):
							dns_data[str(dns_info.id)]["NameServer"].append(dns_info.ns[x].rrname)
							dns_data[str(dns_info.id)]["NameServer"].append(dns_info.ns[x].type)
							if "mname" in dns_info.ns[x]: 
								dns_data[str(dns_info.id)]["NameServer"].append(dns_info.ns[x].mname)
					#if dns_info.ar is not None:	#Additional Record
					#We don't use it
		
		src_ip = packet[scapy.IP].src				# Keep track of source IP addresses
		if src_ip not in count.keys():
			count[src_ip] = packet[scapy.IP].len
		else:
			count[src_ip] += packet[scapy.IP].len
		
		if check_server(src_ip, cname, dns_data.values()):
			content_servers.add(src_ip)				
				
			if count[src_ip]>max_bytes:
				last_update = time.time()
				
				max_bytes = count[src_ip]
				perc = count[src_ip]/TH_BYTES*100
				byte_monitor = f"\tProgress {round(perc)} %    (for cache server {src_ip})"
				print(byte_monitor) if round(perc) % 10 == 0 else None
		
		if ((count[src_ip] > TH_BYTES) and check_server(src_ip, cname, dns_data.values())) or (time.time()-last_update>SNIFFER_TIMEOUT):
			# Stop when receive more than TH_bytes from a content server or SNIFFER_TIMEOUT exceeded
			#print("Timeout interruption") if time.time()-last_update>SNIFFER_TIMEOUT else None
			#print(f'IP {src_ip} has sent {count[src_ip]} > {TH_BYTES} bytes') if count[src_ip] > TH_BYTES else None
			return True
	return False



def import_variables():
	
	with open("init.txt", "r") as file:
		for line in file:
			line = line.strip()				# Removing white spaces and lines
			if not line or line.startswith("#"):		# Ignore empty or comment lines
				continue
			variable_name, value = line.split(" = ")
			variable_name = variable_name.strip()
			value = value.strip()
			globals()[variable_name] = eval(value)		# Variables initialization



if __name__ == "__main__":

	cname = sys.argv[1]
	provider = sys.argv[2]
	url = import_url(provider)
	json_output = {}
	for i in range(len(url)):
		json_output[f"Content {i}"] = {}
		json_output[f"Content {i}"]["URL"] = url[i]
		json_output[f"Content {i}"]["Content Provider"] = provider
		json_output[f"Content {i}"]["CNAME"] = cname.split("+")
	
	# Import global variables from "init.txt" files
	import_variables()
	
	network_interface = scapy.conf.iface
	print(f"\tSniffing on default interface: {network_interface}\n\tInterface IP address: {scapy.get_if_addr(network_interface)}\n")
	
	# Start the execution & save timestamp
	requester.send_string("START")
	i = int(0)
	for key, value in json_output.items():
		if isinstance(value, dict) and value["URL"] == url[i]:
			json_output[key]["Timestamp"] = get_time()
			break
	
	scapy.sniff(iface=network_interface, store=False, stop_filter=lambda packet: process_packet(packet, cname))
	
	while True:
		msg = requester.recv_string()
		print(f"\tSNIFFER has received: {msg}")
		
		if msg=="DRIVER_READY":
			# The Web driver loaded the page and activated the strem of the content.
			# It is now ready to be stopped and prepared for the next content request
			print(f"\tFound {len(content_servers)} cache servers, starting measurements:")
			for cs in range(len(content_servers)):
				print(f"\n\tServer {cs+1} out of {len(content_servers)}")
				icmp_results, icmp_ploss, tcp_results, tcp_ploss = rtt_measurement(list(content_servers)[cs], N_REQUESTS, REQ_TIMEOUT, SAVE)
				results_traceroute, results_aspath = traceroute(list(content_servers)[cs], TRACEROUTE_MAXHOPS, REQ_TIMEOUT)
				for x in range(max(1, i)):
					for value in json_output.values():
						if isinstance(value, dict):
							server_location = results_traceroute[max(list(results_traceroute.keys()))]['Location']
							server_asn = results_traceroute[max(list(results_traceroute.keys()))]['AS']
							json_output["Content "+str(i)]["Server "+str(cs)] = {}
							json_output["Content "+str(i)]["Server "+str(cs)]["RTT Measurements"] = {}
							json_output["Content "+str(i)]["Server "+str(cs)]["Packet Loss"] = {}
							json_output["Content "+str(i)]["Server "+str(cs)]["Traceroute"] = {}
							json_output["Content "+str(i)]["Server "+str(cs)]["IP Address"] = list(content_servers)[cs]
							json_output["Content "+str(i)]["Server "+str(cs)]["ASN"] = server_asn
							json_output["Content "+str(i)]["Server "+str(cs)]["Location"] = server_location
							json_output["Content "+str(i)]["Server "+str(cs)]["RTT Measurements"]["ICMP"] = icmp_results
							json_output["Content "+str(i)]["Server "+str(cs)]["RTT Measurements"]["TCP"] = tcp_results
							json_output["Content "+str(i)]["Server "+str(cs)]["Packet Loss"]["ICMP"] = icmp_ploss/N_REQUESTS
							json_output["Content "+str(i)]["Server "+str(cs)]["Packet Loss"]["TCP"] = tcp_ploss/N_REQUESTS
							json_output["Content "+str(i)]["Server "+str(cs)]["Traceroute"]["Hop-By-Hop"] = results_traceroute
							json_output["Content "+str(i)]["Server "+str(cs)]["Traceroute"]["As-Path"] = results_aspath
							break
			max_bytes = 0
			
			if SHOW_count_and_dns:
				# Process traffic data and show the table
				count_args = count_data_table_format(count)
				print(show_table(count_args[0], count_args[1], count_args[2], count_args[3], SAVE))
			
			count = {}
			last_update = time.time()
			content_servers = set()
			i += 1
			requester.send_string("STOP")
		
		if msg=="CONTINUE":
			# Instructing the Web driver to start the request for the next content on the list
			requester.send_string("START")
			for key, value in json_output.items():
				if isinstance(value, dict) and value["URL"] == url[i]:
					json_output[key]["Timestamp"] = get_time()
					break
			scapy.sniff(iface=network_interface, store=False, stop_filter=lambda packet: process_packet(packet, cname))
		
		if msg=="DONE":
			# The Web driver has now completed the list of content URLs.
			break
	
	now = get_time()
	filename = 'measure_'+provider+'_'+now+'.json'
	with open('./output/'+filename, 'w') as f:
		f.write(json.dumps(json_output, sort_keys=True, indent=4))
		f.close()
	print(f"\tResults stored in the output folder, file: {filename}")
	
	# This script is executed with sudo, so the file will be read-only.
	# Changing from root-group to user-group
	uid = os.getuid()
	gid = os.getgid()
	new_gid = 1000  				# UserGroup
	os.chown('./output/'+filename, uid, new_gid)
	os.chmod('./output/'+filename, 0o664)  	# Permissions: -rw-rw-r--
	
	if SHOW_count_and_dns:
		# Process DNS data and show the table
		dns_args = dns_data_table_format(dns_data)
		print(show_table(dns_args[0], dns_args[1], dns_args[2], dns_args[3], SAVE))
	
	'''
	print(json.dumps(json_output, sort_keys=False, indent=4))
	'''
	
