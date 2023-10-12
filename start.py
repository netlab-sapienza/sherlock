from functions import check_input
import multiprocessing
import subprocess
import platform
import os



def process1(cname):
	os.system(f"sudo python3 sniffer.py {cname}")
	
def process2(url):
	operating_system = str(platform.system()).lower()
	default_browser = str(subprocess.getoutput("update-alternatives --display x-www-browser | grep 'link currently points to' | awk '{print $NF}'")).lower()
	
	if "linux" in operating_system:
		if "chrome" in default_browser:
			os.system(f"python3 browser_c.py {url}")
		elif "firefox" in default_browser:
			os.system(f"python3 browser_f.py {url}")
		elif "chromium" in default_browser:
			os.system(f"python3 browser_cm.py {url}")
		else:
			print("ERROR: Please set Chrome (Chromium on Debian) or Firefox as default browser")
			
	else:
		print("ERROR: Please run in Linux environment")

if __name__ == "__main__":
	
	inputs = check_input()
	
	sniff_process = multiprocessing.Process(target=process1, args=(inputs["cname"],))
	browser_process = multiprocessing.Process(target=process2, args=(inputs["url"],))
	
	sniff_process.start()
	browser_process.start()
	
	sniff_process.join()
	browser_process.join()
