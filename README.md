# Sherlock
This project revolves around the implementations of a scraping and sniffing mechanism: locating the position of any CDN's surrogate server(s).
We will provide a Virtual Machine (all libraries are already included), but you can follow the Installation Section Guide to eventually install the software manually (on a Linux Operating System).

## Installation
It is required to have an internet browser and virtual display installed on the current system (either Chrome, Chromium or Firefox).
If no browser is already in your system, it is suggested to install Chromium for its size. 

### How to install Chrome
```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```
### How to install Chromium
```
sudo apt-get install chromium-browser 
sudo apt-get install chromium-chromedriver
```
### How to install Firefox
```
sudo snap install firefox
```

### How to install VirtualDisplay
It is also required also X-server video frame buffer:
```
sudo apt install xvfb
```

### How to install all Libraries
Please note that several libraries are required to make the code working:

* PyVirtualDisplay
* Requests
* selenium
* tabulate
* scapy
* pyzmq

Pip & Git are requirements in order to install the packages:
```
sudo apt-get install python3-pip
sudo apt-get install git
```

Proceed by cloning this repository and open the appropriate directory:
```
git clone https://github.com/PaoloGit99/sherlock
cd sherlock
```

To install all libraries, use the following commands (user & root):
```
pip install -r requirements.txt
sudo pip install -r sudo_requirements.txt
```

## Usage
To execute the program, run this instruction inside the directory of the project:
```
python3 start.py
```

It is also possible adding a specific provider, by running:
```
python3 start.py {provider_name}
```

Where provider_name is one of the following:
* bbc
* facebook
* instagram
* tiktok
* twitch
* twitter
* youtube

The output will be saved inside the "output" directory, and it will be saved as follows:
```
measure_{provider_name}_hh:mm:ss Weekday dd-mm-yyyy.json
```

Some parameters can be tuned and are located in the `init.txt` file;
* `SNIFFER_TIMEOUT`, set in seconds as the time to wait before interrupting the execution if packets are no longer received
* `N_REQUESTS`, set as the number of requests for packet loss estimation towards content 
* `TH_BYTES`, set as the threshold of received bytes from a cache server to stop the execution 
* `TRACEROUTE_MAXHOPS`, set as the maximum number of hops for tracerouting
* `REQ_TIMEOUT`, set as the timeout for web API requests (geolocation, AS info, ...)
* `SHOW_count_and_dns`, set as 'True' to terminal-print DNS and received traffic tables.
* `SAVE`, set as `True` to write tables of DNS and CountBytes in "./output"

If none are set, default values will be used.

To observe the results properly formatted, run the following command:
```
python3 table.py
```

## License

This project is under the terms of MIT license - see [LICENSE](LICENSE) for details.

## Contacts

Consoli Flavio @ La Sapienza Università di Roma: consoli.1855575@studenti.uniroma1.it

Ranieri Paolo  @ La Sapienza Università di Roma: ranieri.1867163@studenti.uniroma1.it
