import scapy.all as scapy
from ripe import *
from functions import show_table


# These functions generate and listen to the packet response
# 	send_icmp: works with icmp protocol
# 	send_udp: works with udp protocol
# INPUT: destination IP address (type "str"), time to live, timeout
# OUTPUT: reply captured
#
def send_icmp(dst, ttl, t = 0.5):
	pkt = scapy.IP(dst=dst, ttl=ttl) / scapy.ICMP(type=8, code=0)	#Type 8: echo request, code 0: reply
	reply = scapy.sr1(pkt, verbose = 0, timeout = t)
	return reply
def send_udp(dst, ttl, t = 0.5):
	pkt = scapy.IP(dst=dst, ttl=ttl) / scapy.UDP(dport=53)
	reply = scapy.sr1(pkt, verbose = 0, timeout = t)
	return reply



def traceroute(destination, max_hops=30, REQ_TIMEOUT=10):
	# This function implements the traceroute command, by using ICMP or UDP packets.
	# INPUT: destination IP address (type "str"), api to be used for geolocation, max_hops
	# OUTPUT: hop_list
	#
	print("\n\nTracing route to: "+destination)
	hop_list = []
	as_path = []
	ttl = 1
	nFail = 0
	while ttl <= max_hops:
		if nFail<3:
			reply = send_icmp(destination, ttl)
			if reply is not None:
				print(f"{ttl}:\tICMP,\treply from {str(reply.src)}")
				where = find_location(str(reply.src), REQ_TIMEOUT)
				AS, holder = find_as(str(reply.src), REQ_TIMEOUT)
				hop_list.append([ttl, "ICMP", reply.src, where+", "+holder])
				as_path.append(AS) if AS is not None else None
				if reply.src == destination:
					break
				ttl += 1
				nFail = 0
			else:
				nFail += 1
		elif nFail<6:
			reply = send_udp(destination, ttl)
			if reply is not None:
				print(f"{ttl}:\tUDP,\treply from {str(reply.src)}")
				where = find_location(str(reply.src), REQ_TIMEOUT)
				AS, holder = find_as(str(reply.src), REQ_TIMEOUT)
				hop_list.append([ttl, "UDP", reply.src, where+", "+holder])
				as_path.append(AS) if AS is not None else None
				if reply.src == destination:
					break
				ttl += 1
				nFail = 0
			else:
				nFail += 1
		
		else:
			print(f"{ttl}:\t*,\tno reply")
			hop_list.append([ttl, " . ", "*.*.*.*", " "])
			as_path.append("*")
			nFail = 0
			ttl += 1
	return hop_list, as_path
	
	
	
def multi_traceroute(content_servers, TRACEROUTE_MAXHOPS, REQ_TIMEOUT, SAVE):
	if len(content_servers)>0:
		print(f"Content servers found: {content_servers}")
		headers_tr = ["Hop", "Protocol", "Address", "Location"]
		header_asp = ["Autonomous System"]
		for ip_target in content_servers:
			hop_list, as_path = traceroute(ip_target, TRACEROUTE_MAXHOPS, REQ_TIMEOUT)
			ASP = []
			for el in as_path:
				ASP.append([el])
			headers = ["Hop", "Protocol", "Address", "Location"]
			show_table(hop_list, headers, "pretty", "Traceroute towards "+ip_target, SAVE)	#TODO AFTER CHECK NEIGHBOURS
			show_table(ASP, header_asp, "pretty", "AS path towards "+ip_target, SAVE)
			
			check_neighbour(as_path, REQ_TIMEOUT)
	else:
		print("No content server found")


if __name__ == "__main__":	#For testing...
	# Destination IP address
	destination_ip = "151.99.51.175"	#Youtube: "173.194.18.136"

	# Execute traceroute
	hop_list, as_path = traceroute(destination_ip)
	print(as_path)
