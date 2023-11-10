import scapy.all as scapy
from ripe import *
from functions import show_table
import math


# These functions generate and listen to the packet response
# 	send_icmp: works with icmp protocol
# 	send_udp: works with udp protocol
# INPUT: destination IP address (type "str"), time to live, timeout
# OUTPUT: reply captured
#
def send_icmp(dst, ttl, t = 0.1):
	pkt = scapy.IP(dst=dst, ttl=ttl) / scapy.ICMP(type=8, code=0)	#Type 8: echo request, code 0: reply
	reply = scapy.sr1(pkt, verbose = 0, timeout = t)
	return reply
def send_udp(dst, ttl, t = 0.1):
	pkt = scapy.IP(dst=dst, ttl=ttl) / scapy.UDP(dport=53)
	reply = scapy.sr1(pkt, verbose = 0, timeout = t)
	return reply



def traceroute(destination, max_hops=30, REQ_TIMEOUT=10):
	# This function implements the traceroute command, by using ICMP or UDP packets.
	# INPUT: destination IP address (type "str"), api to be used for geolocation, max_hops
	# OUTPUT: hop_dict, as_path
	#
	print("\t\tTracing route to: "+destination)
	hop_dict = {}
	as_path = []
	ttl = 1
	nFail = 0
	while ttl <= max_hops:
		if nFail<3:
			reply = send_icmp(destination, ttl)
			if reply is not None:
				print(f"\t\t\t{ttl}:\tICMP,\treply from {str(reply.src)}")
				where = find_location(str(reply.src), REQ_TIMEOUT)
				AS, holder = find_as(str(reply.src), REQ_TIMEOUT)
				
				hop_dict[ttl] = {"Protocol": "ICMP", "IP Address": reply.src, "Location": where, "Holder": holder, "AS": AS}
				
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
				print(f"\t\t\t{ttl}:\tUDP,\treply from {str(reply.src)}")
				where = find_location(str(reply.src), REQ_TIMEOUT)
				AS, holder = find_as(str(reply.src), REQ_TIMEOUT)
				
				hop_dict[ttl] = {"Protocol": "UDP", "IP Address": reply.src, "Location": where+", "+holder, "AS": AS}
				
				as_path.append(AS) if AS is not None else None
				if reply.src == destination:
					break
				ttl += 1
				nFail = 0
			else:
				nFail += 1
		
		else:
			print(f"\t\t\t{ttl}:\t*,\tno reply")
			hop_dict[ttl] = {"Protocol": "*", "IP Address": " ", "Location": " ", "AS": " "}
			
			as_path.append("*")
			nFail = 0
			ttl += 1
			
	this_as = get_as_home(REQ_TIMEOUT)
	as_path.insert(0, this_as)
	as_list = check_neighbour(as_path, REQ_TIMEOUT)
	
	return hop_dict, as_list
	
def extract_statistics(rtt):
	mean_rtt = sum(rtt)/len(rtt)
	variance_rtt = sum((x-mean_rtt)**2 for x in rtt)/(len(rtt)-1)
	devstd_rtt = math.sqrt(variance_rtt)
	rms_rtt = math.sqrt(sum(x**2 for x in rtt) / len(rtt))
	quadratic_norm_rtt = math.sqrt(sum(x**2 for x in rtt))
	
	sorted_rtt = sorted(rtt)
	if len(rtt)%2==0:
		median_rtt = (sorted_rtt[len(rtt)//2-1] + sorted_rtt[len(rtt)//2])/2
	else:
		median_rtt = sorted_rtt[len(rtt)//2]
	
	metrics_rtt = {
		"Mean": round(mean_rtt, 2),
		"Max": round(max(rtt), 2),
		"Min": round(min(rtt), 2),
		"Median": round(median_rtt, 2),
		"Variance": round(variance_rtt, 2),
		"Std Dev": round(devstd_rtt, 2),
		"RMS": round(rms_rtt, 2),
		"Norm2": format(quadratic_norm_rtt/(quadratic_norm_rtt**2), ".2e")
	}
	return metrics_rtt
	
def rtt_measurement(target_ip, N_REQUESTS, REQ_TIMEOUT, SAVE):
	print(f"\t\tPerforming RTT measurements on {target_ip}...")
	
	icmp_rtt = []
	icmp_pkt_loss = 0
	
	tcp_rtt = []
	tcp_pkt_loss = 0
	
	for _ in range(N_REQUESTS):
		packet = scapy.IP(dst=target_ip) / scapy.ICMP(type=8, code=0)
		ans, _ = scapy.sr(packet, verbose=False, timeout=REQ_TIMEOUT)
		if ans:
			sent = ans[0][0].sent_time
			received = ans[0][1].time
			time_delta = received-sent
			if time_delta>0:
				icmp_rtt.append(round((time_delta)*1e3, 3))
		else:
			icmp_pkt_loss += 1
			
	for _ in range(N_REQUESTS):
		packet = scapy.IP(dst=target_ip) / scapy.TCP(dport=80, flags='S')
		ans, _ = scapy.sr(packet, verbose=False, timeout=REQ_TIMEOUT)
		if ans:
			sent = ans[0][0].sent_time
			received = ans[0][1].time
			time_delta = received-sent
			if time_delta>0:
				tcp_rtt.append(round((time_delta)*1e3, 3))
		else:
			tcp_pkt_loss += 1
			
	icmp_metrics = extract_statistics(icmp_rtt)
	icmp_results = {"Metrics": icmp_metrics, "Experiments": icmp_rtt}
	
	tcp_metrics = extract_statistics(tcp_rtt)
	tcp_results = {"Metrics": tcp_metrics, "Experiments": tcp_rtt}
	
	
	return icmp_results, icmp_pkt_loss, tcp_results, tcp_pkt_loss
	
	
	
if __name__ == "__main__":	#For testing...
	# Destination IP address
	destination_ip = "23.220.255.66"	#Youtube: "173.194.18.136"

	# Execute test
	#table_traceroute, table_aspath = sherlock_traceroute("152.199.21.141", 30, 5, False)
	#table_rtt, rtt = multi_rtt(destination_ip, 2, False)
	
	_, a= traceroute(destination_ip)
	print(a)
	#print(rtt)
	
	
