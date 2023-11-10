from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display
from functions import import_url
import subprocess
import zmq
import sys

context = zmq.Context()
responder = context.socket(zmq.REP)
responder.bind("tcp://*:8000")



def scraping(video_url):
	
	# Check Chromium WebDriver
	driver_path = str(subprocess.getoutput("which chromedriver"))
	if len(driver_path) < 12:
		print("ERROR: driver not found, please install with 'sudo apt-get install chromium-chromedriver'")
		return None, None
	service = webdriver.ChromeService(executable_path=driver_path)
	
	# Creating a virtual display
	display = Display(visible=0, size=(1080, 720), backend="xvfb")
	display.start()
	
	# Add browser extensions
	chrome_options = Options()
	chrome_options.add_argument("--start-maximized")  	# open Browser in maximized mode
	chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
	chrome_options.add_argument("--mute-audio")
	
	# Load extensions
	chrome_options.add_extension('./ext/cookie.crx')
	chrome_options.add_extension('./ext/ad_block.crx')
	
	# Browser's driver initialization
	driver = webdriver.Chrome(service=service, options=chrome_options)
	driver.implicitly_wait(10)
	
	# Open the video URL in the browser
	try:
		driver.get(video_url)
		
	except Exception:
		print("\n* WebDriver internal error, please restart *")
		driver.quit()
		return None, None
	
	return driver, display



def scraping_open(driver, url):
	
	# Open the video URL in the browser
	try:
		driver.get(url)
		
	except Exception:
		print("\n* WebDriver internal error, please restart *")
		driver.quit()
		return None, None
	
	return driver



if __name__ == "__main__":
	
	provider = (sys.argv[1]).lower()
	
	url_list = import_url(provider)
	url_n = 0
	while True:
		message = responder.recv_string()
		print(f"\tBROWSER has received: {message}")
		
		if (message)=="START" and url_n == 0:
			print(f"\nStep {url_n+1} of {len(url_list)}")
			url = url_list[url_n]
			web_driver, display = scraping(url)
			responder.send_string("DRIVER_READY")
			
			if web_driver is None or display is None:
				sys.exit()
				
		if (message)=="START" and url_n > 0 and url_n <= len(url_list)-1:
			print(f"\nStep {url_n+1} of {len(url_list)}")
			url = url_list[url_n]
			web_driver = scraping_open(web_driver, url)
			responder.send_string("DRIVER_READY")
			
			if web_driver is None:
				sys.exit()
				
		if (message)=="STOP":
			url_n += 1
			if url_n > len(url_list)-1:
				responder.send_string("DONE")
				web_driver.quit()
				display.stop()
				break
			else:
				responder.send_string("CONTINUE")
