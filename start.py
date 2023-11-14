from functions import check_input, get_default_interface, get_time
from dns import *
from pprint import pprint
import multiprocessing
import subprocess
import platform
import sys
import os



def process1(cname, provider, dns):
	#os.system(f"sudo python3 sniffer.py {cname} {provider} {dns}")			#Use with system-wide installation
	os.system(f"sudo ./myenv/bin/python sniffer.py {cname} {provider} {dns}")	#Use with virtualenv installation
	
def process2(provider):
	operating_system = str(platform.system()).lower()
	default_browser = str(subprocess.getoutput("update-alternatives --display x-www-browser")).lower()
	
	if "linux" in operating_system:
		if "chromium" in default_browser:
			os.system(f"python3 browser_cm.py {provider}")
		elif "chrome" in default_browser:
			os.system(f"python3 browser_c.py {provider}")
		elif "firefox" in default_browser:
			os.system(f"python3 browser_f.py {provider}")
		else:
			print("ERROR: Please set Chromium, Chrome or Firefox as default browser")
			
	else:
		print("ERROR: Please run in Linux environment")

if __name__ == "__main__":
	
	connectivity = check()
	if connectivity:
		print("Internet connection verified")
		if len(sys.argv) < 2:
			provider = ["youtube", "twitch", "bbc", "twitter", "tiktok", "facebook", "instagram"]
			num_iterations = len(provider)
		else:
			provider = (sys.argv[1]).lower()
			num_iterations = 1
		
		#With default DNS
		for i in range(num_iterations):
			if num_iterations>1:
				inputs = check_input(provider[i])
			else:
				inputs = check_input(provider)
			print(f"\nSTEP 1/2 (default DNS) Analyzing provider {i+1}/{num_iterations}:")
			pprint(inputs)
			print(" ")
			
			sniff_process = multiprocessing.Process(target=process1, args=(inputs["cname"], inputs["provider"], get_current_dns(),))
			browser_process = multiprocessing.Process(target=process2, args=(inputs["provider"],))
			
			browser_process.start()
			sniff_process.start()
			
			browser_process.join()
			sniff_process.join()
		
		DNS = change_dns()
		if DNS is not None:
			#With modified DNS
			for i in range(num_iterations):
				if num_iterations>1:
					inputs = check_input(provider[i])
				else:
					inputs = check_input(provider)
				print(f"\nSTEP 2/2 (public DNS) Analyzing provider {i+1}/{num_iterations}:")
				pprint(inputs)
				print(" ")
				
				sniff_process = multiprocessing.Process(target=process1, args=(inputs["cname"], inputs["provider"], DNS))
				browser_process = multiprocessing.Process(target=process2, args=(inputs["provider"],))
				
				browser_process.start()
				sniff_process.start()
				
				browser_process.join()
				sniff_process.join()
		else:
			print("No available public DNS server")
		
	else:
		print("Internet connection error!")
	
	output_name = f'results_{get_time()}'
	tar_name = output_name.replace(" ", "_")
	subprocess.run(f'tar -cvf {tar_name}.tar output', shell=True)
	reset_network_manager()
