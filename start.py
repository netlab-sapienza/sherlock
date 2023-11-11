from functions import check_input
from pprint import pprint
import multiprocessing
import subprocess
import platform
import sys
import os



def process1(cname, provider):
	os.system(f"sudo ./myenv/bin/python sniffer.py {cname} {provider}")
	
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

	if len(sys.argv) < 2:
		provider = ["youtube", "twitch", "bbc", "twitter", "tiktok", "facebook", "instagram"]
		num_iterations = len(provider)
	else:
		provider = (sys.argv[1]).lower()
		num_iterations = 1
	
	for i in range(num_iterations):
		if num_iterations>1:
			inputs = check_input(provider[i])
		else:
			inputs = check_input(provider)
		print(f"Analyzing provider {i+1}/{num_iterations}:")
		pprint(inputs)
		print(" ")
		
		sniff_process = multiprocessing.Process(target=process1, args=(inputs["cname"], inputs["provider"],))
		browser_process = multiprocessing.Process(target=process2, args=(inputs["provider"],))
		
		browser_process.start()
		sniff_process.start()
		
		browser_process.join()
		sniff_process.join()
