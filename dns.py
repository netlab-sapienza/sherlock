from functions import get_default_interface
import time
import re
import subprocess
import requests
        
def change_dns():
	iface, _ = get_default_interface()
	dns_list = ["8.8.8.8", 
		"1.1.1.1", 
		"76.76.2.0", 
		"9.9.9.9", 
		"208.67.222.222", 
		"185.228.168.9", 
		"76.76.19.19", 
		"94.140.14.14",
		"8.26.56.26",
		"205.171.3.65",
		"149.112.121.10",
		"38.103.195.4",
		"216.146.35.35",
		"77.88.8.8",
		"74.82.42.42",
		"94.130.180.225",
		"185.236.104.104",
		"80.80.80.80"]
		
	try:
		for dns in dns_list:
			print(f"Checking {dns} as DNS server...")
			subprocess.run(['sudo', 'systemd-resolve', '--interface', iface, '--set-dns', dns])
			time.sleep(5)
			
			connectivity = check()
			if connectivity:
				print("DNS correctly set up")
				return get_current_dns()
		
		reset_network_manager()
		return None
		
	except subprocess.CalledProcessError as e:
		reset_network_manager()
		print(f"change_dns: {e}")

def check(url = "https://www.example.com/"):
	try:
		response = requests.get(url, timeout = 5)
		if response.status_code == 200:
			return True
		return False
	except:
		return False
		
def reset_network_manager():
	subprocess.run(['sudo', 'systemctl', 'restart', 'NetworkManager'])
	time.sleep(5)
	
def get_current_dns():
	try:
		result = subprocess.run(['resolvectl', 'status'], capture_output=True, text=True)
		return extract_current_dns(result.stdout)
	except subprocess.CalledProcessError as e:
		print(f"get_current_dns: {e}")
		
def extract_current_dns(string):
    match = re.search(r'Current DNS Server:\s+([\d.]+)', string)
    if match:
        return match.group(1)
    else:
        return None





if __name__ == "__main__":
	
	DNS = change_dns()
	print(DNS)
	print("---")
	reset_network_manager()
	print(get_current_dns())
