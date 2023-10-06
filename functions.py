from tabulate import tabulate
from datetime import datetime as d
import sys



def check_input(link = "https://www.youtube.com/watch?v=XqZsoesa55w"):			#Babyshark link
	
	output = {}
	if len(sys.argv) < 2:
		output["url"] = link
	else:
		output["url"] = sys.argv[1]
		
	if "youtube" in output["url"]:
		output["cname"] = "googlevideo"
	elif "netflix" in output["url"]:
		output["cname"] = "nflxvideo"
	elif "twitch" in output["url"]:
		output["cname"] = "ttvnw.net"
	else:
		print("URL not valid or supported")
		return None
	
	print("Running the script with these inputs:")
	print(tabulate([list(output.keys()), list(output.values())]))
	print(" ")
	return output



def is_public(ip):
	# This function returns True if the input ip address is public
	# INPUT: ip address, type "str"
	# OUTPUT: boolean 
	
	if ip[0:3]=="10.":
		return False
		
	elif ip[0:4]=="172." and ip[6]==".":
		if int(ip[4:6])>=16 and int(ip[4:6])<=31:
			return False
			
	elif ip[0:8]=="192.168.":
		return False
		
	else:
		return True



def find_addr_max_data(ip_count):
	# This function shows and returns the address that sent the most data
	# INPUT: type "dict", 
	#	"key" is an IP address and "value" the number of bytes it sent
	# OUTPUT: type "str", the address that sent the most data
	
	max_k = None
	max_n = 0
	for key, n in ip_count.items():
		if is_public(key):
			if n > max_n:
				max_n = n
				max_k = key
	print(f"\n\nPublic address that sent the most data: {max_k}")
	return max_k



def show_table(table_data, headers, style, table_name, save=False):
	# This function prints on terminal a formatted table
	# INPUTS: [table data, type: list], [headers, type: list], [style, type: "str"], [table_name, type: "str"], [save, type: str]
	# 	some interesting table styles: "pretty", "grid", "latex"
	
	print(f"\nShowing {table_name}...")
	table = tabulate(table_data, headers=headers, tablefmt=style)
	print(table)
	if save:
		moment = str(d.now().year)+str(d.now().month)+str(d.now().day)+"_"+str(d.now().hour)+str(d.now().minute)+str(d.now().second)
		with open('./output/table_'+table_name+'_'+moment+'.txt', 'w') as f:
			f.write(table)

		

def check_server(ip, check_str, dns_values):
	for v in dns_values:
		for entry in (v.values()):				# Inspect DNS record
			if isinstance(entry, list) and ip in entry:
				for el in entry:			# For each element of the DNS record
					if isinstance(el, bytes) and check_str in el.decode("utf-8"):
						return True
			
	return False



def count_data_table_format(count):
	
	table_data = []
	for ip, n in count.items():
		table_data.append([ip, n])

	headers = ["IP", "Amount of Data received"]
	return([table_data, headers, "pretty", "data sent"])
	
	
	
def dns_data_table_format(dns_data):
	
	table_data = []
	for ID, a_r in dns_data.items():
		if len(a_r) > 0:
			id_value = ID
			
			q1 = a_r["Question"][0]
			q2 = a_r["Question"][1]
			question = (f"Type: {str(q1)}, QName: {q2}")
				
			response = []
			answer_data = a_r.get("Answer", [])
			for i in range(0, len(answer_data), 3):
				rr = str(answer_data[i])
				rr_type = str(answer_data[i + 1])
				rr_data = str(answer_data[i + 2])
				response.append(f"RR: {rr}, Type: {rr_type}, Answer: {rr_data}")
				
			response_str = "\n".join(response)
			table_data.append([id_value, question, response_str])

	headers = ["ID", "Question", "Response"]
	return([table_data, headers, "grid", "DNS table"])


		
if __name__ == "__main__":	#For testing...
	# Destination IP address
	destination_ip = "8.8.8.8"

	# Execute traceroute
	where = location_str(destination_ip, 'ipapi')
	print(where)
