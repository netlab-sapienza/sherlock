from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display
import subprocess
import socket
import time
import sys



def scraping(video_url):
	
	# Check Chromium WebDriver
	driver_path = str(subprocess.getoutput("which chromedriver"))
	if len(driver_path < 10):
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
	#time.sleep(5)
	
	# Open the video URL in the browser
	driver.get(video_url)
	
	#time.sleep(10)
	
	return driver, display



if __name__ == "__main__":

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind(("localhost", 8080))
		s.listen()
		conn, addr = s.accept()
		with conn:
			data = conn.recv(1024)
			if str(data.decode()) == "START":
				if len(sys.argv) > 1:
					web_driver, display = scraping(sys.argv[1])		# Initialize content demand
				else:
					print("FATAL INTERNAL ERROR: webdriver got no url.")
					
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind(("localhost", 8080))
		s.listen()
		conn, addr = s.accept()
		with conn:
			data = conn.recv(1024)
			if str(data.decode()) == "STOP":
				web_driver.quit()
				display.stop()
