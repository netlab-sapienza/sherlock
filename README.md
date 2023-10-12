# Sherlock
This project revolves around the implementations of a scraping and sniffing mechanism: locating the position of any CDN's surrogate server(s).

## Installation
Please note that several libraries are required to make the code working:

* geopy
* PyVirtualDisplay
* Requests
* scapy
* selenium
* tabulate

To install them, use the command:
```
pip install -r requirements.txt
```

It is also required to have an internet browser installed on the system (either Chrome or Firefox).
For example, to get Chrome:
```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

Finally, it is required also X video frame buffer:
```
sudo apt install xvfb
```

### Installation on RaspberryPi
Given the previous steps, in this scenario is required to manually install the webdriver for the browser (Chromium).
```
sudo apt-get install chromium-browser
sudo apt-get install chromium-chromedriver
```

It can be used `which` command to check if anything is already installed, for example:
```
which chromedriver
```


## Usage
To execute the program, run this instruction inside the directory of the project:
```
python3 start.py
```

It is also possible adding an url pointing to a content, by runnig:
```
python3 start.py https://www.---.com/---
```

The parameters that can be tuned are located in the `init.txt` file;
* `SNIFFER_TIMEOUT`, set in seconds as the time to wait before interrupting the execution if packets are no longer received
* `TH_BYTES`, set as the threshold of received bytes from a cache server to stop the execution 
* `TRACEROUTE_MAXHOPS`, set as the maximum number of hops for tracerouting
* `REQ_TIMEOUT`, set as the timeout for web API requests (geolocation, AS info, ...)
* `SAVE`, set as `True` to store the tables in the output folder

If none are set, default values will be used.


## License

This project is under the terms of MIT license - see [LICENSE](LICENSE) for details.

## Contacts
Consoli Flavio @ La Sapienza Università di Roma: consoli.1855575@studenti.uniroma1.it

Ranieri Paolo  @ La Sapienza Università di Roma: ranieri.1867163@studenti.uniroma1.it
