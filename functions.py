from tabulate import tabulate
from datetime import datetime as d
import subprocess
import requests
import shutil
import bz2
import os
import re
import sys

def get_default_interface():
	try:
		result = subprocess.run(['ip', '-o', '-4', 'route', 'show', 'to', 'default'], capture_output=True, text=True)
		
		address = result.stdout.split()[2]
		interface = result.stdout.split()[4]

		return interface, address
	except subprocess.CalledProcessError as e:
		print(f"No interface found: {e}")
		return None, None

def update_caida(REQ_TIMEOUT):
	try:
		url = "https://publicdata.caida.org/datasets/as-relationships/serial-1/"
		response = requests.get(url, timeout = REQ_TIMEOUT)
		
		if response.status_code == 200:
			file_links = re.findall(r'<a href="([^"]*as-rel.txt.bz2)"', response.text)
			dates = [re.search(r'(\d{8})\.as-rel.txt.bz2', link).group(1) for link in file_links]
			latest_date = max(dates)
			latest_file = f"{latest_date}.as-rel.txt.bz2"
			
			if os.path.exists(latest_file[:-4]):
				# Latest file is already in the working directory
				return latest_file[:-4]
				
			else:
				latest_file_url = f"{url}/{latest_file}"
				file_response = requests.get(latest_file_url, timeout=REQ_TIMEOUT)
				
				if file_response.status_code == 200:
					with open(latest_file, "wb") as file:
						file.write(file_response.content)
						
					# Succesfully downloaded latest_file, now extracting and saving
					with bz2.BZ2File(latest_file, 'rb') as bz2_file:
						content = bz2_file.read()
					extracted_file = f"{latest_date}.as-rel.txt"
					with open(extracted_file, "wb") as file:
						file.write(content)
						
					# Changing from root-group to user-group
					uid = os.getuid()
					gid = os.getgid()
					new_gid = 1000					# UserGroup
					os.chown('./'+extracted_file, uid, new_gid)
					os.chmod('./'+extracted_file, 0o664)		# Permissions: -rw-rw-r--
					
					# Removing the bz2 file
					os.remove(latest_file)
					
					# Remove old files
					for old_date in dates:
						if old_date != latest_date:
							old_file = f"{old_date}.as-rel.txt.bz2"
							old_extracted_file = f"{old_date}.as-rel.txt"
							
							if os.path.exists(old_file):
								os.remove(old_file)
							
							if os.path.exists(old_extracted_file):
								os.remove(old_extracted_file)
								
					return extracted_file
					
				else:
					print(f"Error in CAIDA file download. Status code: {file_response.status_code}")
					return None
				
		else:
			print(f"Error CAIDA in file download. Status code: {response.status_code}")
			return None
			
	except Exception as e:
		print(f"Error in updating CAIDA database, error: {e}")
		return None

def import_url(provider = "youtube"):
	l = []
	with open(f'./contents/{provider}.txt', 'r') as file:
		for line in file:
			l.append(line.strip())
	file.close()
	return l

def check_input(provider):

	output = {}
	output["provider"] = provider
	
	if output["provider"] == "youtube":
		output["cname"] = "googlevideo"
		
	elif output["provider"] == "twitch":
		output["cname"] = "cloudfront"
		
	elif output["provider"] == "bbc":
		output["cname"] = "fastly+akamai"
		
	elif output["provider"] == "twitter":
		output["cname"] = "edgecastcdn"
		
	elif output["provider"] == "tiktok":
		output["cname"] = "akamai"
		
	elif output["provider"] == "facebook":
		output["cname"] = "fbcdn"
		
	elif output["provider"] == "instagram":
		output["cname"] = "cdninstagram"
		
	else:
		print("Provider not valid or supported")
		return None
	
	output["url"] = import_url(output["provider"])
	
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



def show_table(table_data, headers, style, table_name, save=False):
	# This function prints on terminal a formatted table
	# INPUTS: [table data, type: list], [headers, type: list], [style, type: "str"], [table_name, type: "str"], [save, type: str]
	# 	some interesting table styles: "pretty", "grid", "latex"
	
	#print(f"\nShowing {table_name}...")
	table = tabulate(table_data, headers=headers, tablefmt=style)
	#print(table)
	if save:
		moment = str(d.now().year)+str(d.now().month)+str(d.now().day)+"_"+str(d.now().hour)+str(d.now().minute)+str(d.now().second)
		with open('./output/table_'+table_name+'_'+moment+'.txt', 'w') as f:
			f.write(table)
	return table

		

def check_server(ip, check_list, dns_values):
	for v in dns_values:
		for entry in (v.values()):				# Inspect DNS record
			if isinstance(entry, list) and ip in entry:
				for el in entry:			# For each element of the DNS record
					for check_str in check_list.split("+"):
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


		
def get_time():
	return d.now().strftime("%H:%M:%S_%A_%d-%m-%Y")
	
	
	
if __name__ == "__main__":	#For testing...
	# Destination IP address
	destination_ip = "8.8.8.8"

	# Execute traceroute
	where = location_str(destination_ip, 'ipapi')
	print(where)
