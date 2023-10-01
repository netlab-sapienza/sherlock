from functions import check_input
import multiprocessing
import os



def process1(cname):
	os.system(f"sudo python3 sniffer.py {cname}")
	
def process2(url):
	os.system(f"python3 browser_c.py {url}")

if __name__ == "__main__":
	
	inputs = check_input()
	
	sniff_process = multiprocessing.Process(target=process1, args=(inputs["cname"],))
	browser_process = multiprocessing.Process(target=process2, args=(inputs["url"],))
	
	sniff_process.start()
	browser_process.start()
	
	sniff_process.join()
	browser_process.join()
