from functions import *
from tr import *
import scapy.all as scapy
import socket
import sys
import time



def process_packet(packet, cname):
	# Once the sniffer is activated, we keep track of DNS communications.
	# We also count how many bytes are received until a traffic source exceeds TH_BYTES.
	# Most-likely, the latter will be the content-cache server.
	# This function is executed for every received packet.
	global max_bytes
	global SNIFFER_TIMEOUT
	global last_update
	
	if scapy.IP in packet:						# Check if the packet contains IP layer
		
		if scapy.DNS in packet:					# Check if the packet contains DNS layer
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
				byte_monitor = f"Progress {round(perc)} %    (for surrogate server {src_ip})"
				print(byte_monitor) if round(perc) % 10 == 0 else None
		
		if ((count[src_ip] > TH_BYTES) and check_server(src_ip, cname, dns_data.values())) or (time.time()-last_update>SNIFFER_TIMEOUT):
			# Stop when receive more than TH_bytes from a content server or SNIFFER_TIMEOUT exceeded
			print("Timeout interruption") if time.time()-last_update>SNIFFER_TIMEOUT else None
			print(f'IP {src_ip} has sent {count[src_ip]} > {TH_BYTES} bytes')
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.connect(("localhost", 8080))
				s.send(b"STOP")			# Sending STOP condition to webdriver process
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



def activate_scraping():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect(("localhost", 8080))
		s.send(b"START")



if __name__ == "__main__":
	
	import_variables()						# Import global variables from "init.txt" files
	
	if len(sys.argv) > 1:
		cname = sys.argv[1]
	else:
		print("INTERNAL ERROR: CNAME NOT GIVEN")
		sys.exit()
	
	# Sniff DNS packets on the network interface
	network_interface = scapy.conf.iface
	print(f"Sniffing on default interface: {network_interface}\nInterface IP address: {scapy.get_if_addr(network_interface)}\n")
	activate_scraping()
	scapy.sniff(iface=network_interface, store=False, stop_filter=lambda packet: process_packet(packet, cname))
	
	# Process DNS data and show the table
	dns_args = dns_data_table_format(dns_data)
	show_table(dns_args[0], dns_args[1], dns_args[2], dns_args[3], SAVE)
	
	# Process traffic data and show the table
	count_args = count_data_table_format(count)
	show_table(count_args[0], count_args[1], count_args[2], count_args[3], SAVE)
	
	# Obtain the address that sent the most data
	ip_most_traffic = find_addr_max_data(count)
	
	# Perform traceroute analysis to all content servers
	multi_traceroute(content_servers, TRACEROUTE_MAXHOPS, REQ_TIMEOUT, SAVE)
	
	
	
