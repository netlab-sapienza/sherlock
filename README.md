# Sherlock
This project revolves around the implementations of a scraping and sniffing mechanism: locating the position of any CDN's surrogate server(s).
We will provide a Virtual Machine (all libraries are already included), but you can follow the Installation Section Guide to eventually install the software manually (on a Linux Operating System).

## Installation
It is required to have an internet browser and virtual display installed on the current system (either Chrome, Chromium or Firefox).
If no browser is already in your system, it is suggested to install Chromium for its size. 

### Browser installation
#### Chromium
```
sudo apt-get install chromium-browser 
sudo apt-get install chromium-chromedriver
```
#### Chrome
```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```
#### Firefox
```
sudo snap install firefox
```

### VirtualDisplay installation
It is also required also X-server video frame buffer:
```
sudo apt-get install xvfb
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
Create and activate a virtual environment called **myenv** in this directory, using `virtualenv`.
To use the appropriate python version, check the one installed in the system with `python3 --version`, and replace "X":
```
sudo apt-get install -y python3-virtualenv

python3 --version
virtualenv --python=3.X myenv
source myenv/bin/activate
```
To install all libraries in `myenv`, use the following commands:
```
pip install -r requirements.txt
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

Lastly, to export the output folder in a compressed .tar archive use:
```
tar -cvf {any_name}.tar ./output
```
The virtual environment can be stopped deactivated with the command `deactivate`

## All useful code
```
sudo apt-get install -y chromium-browser 
sudo apt-get install -y chromium-chromedriver
sudo apt-get install -y xvfb
sudo apt-get install -y git
sudo apt-get install -y python3-pip
sudo apt-get install -y python3-virtualenv
```
```
git clone https://github.com/PaoloGit99/sherlock
cd sherlock
```
```
python3 --version
virtualenv --python=3.X
source myenv/bin/activate
pip install requirements.txt
```
```
python3 start.py
python3 start.py {provider_name}
python3 table.py
tar -cvf {any_name}.tar ./output
deactivate
```


In case of "{user} is not in the sudoers file" error:
```
cd
su root
nano /etc/sudoers
```
And, in the "# User privilege specification", add after root line:
```
username	ALL=(ALL:ALL)	ALL
```
In case of "{path} is not in $PATH" warning:
```
cd
su root
nano ./.bashrc
```
Then add at the end of the file:
```
export "/new_path:$PATH"
```
And reboot
## License

This project is under the terms of MIT license - see [LICENSE](LICENSE) for details.

## Contacts

Consoli Flavio @ La Sapienza Università di Roma: consoli.1855575@studenti.uniroma1.it

Ranieri Paolo  @ La Sapienza Università di Roma: ranieri.1867163@studenti.uniroma1.it
