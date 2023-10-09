from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from pyvirtualdisplay import Display
import socket
import time
import sys



def scraping(video_url):
	
	# Automatically install Firefox WebDriver, if not already installed
	service = Service()
	
	# Creating a virtual display
	display = Display(visible=0, size=(1920, 1080), backend="xvfb")
	display.start()
	
	# Add browser extensions
	options = Options()
	options.add_argument("--start-maximized")		# open Browser in maximized mode
	options.add_argument("--disable-dev-shm-usage")	# overcome limited resource problems
	options.add_argument("--mute-audio")
	
	# Browser's driver initialization
	driver = webdriver.Firefox(service=service, options=options)
	driver.implicitly_wait(10)
	
	# Load extensions
	driver.install_addon('./ext/cookie.xpi', temporary=True)
	driver.install_addon('./ext/ad_block.xpi', temporary=True)
	
	# Open the video URL in the browser
	try:
		driver.get(video_url)
		
	except Exception:
		print("\n* WebDriver internal error, please restart *")
		driver.quit()
		return None, None
	
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
					if web_driver is None and display is None:
						sys.exit()
				else:
					print("FATAL INTERNAL ERROR: webdriver got no url.")
					
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind(("localhost", 8080))
		s.listen()
		conn, addr = s.accept()
		with conn:
			data = conn.recv(1024)
			if str(data.decode()) == "STOP" and web_driver is not None and display is not None:
				web_driver.quit()
				display.stop()
