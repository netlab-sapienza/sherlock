from matplotlib import pyplot as plt
import json
import os
from glob import glob

i_fig = 0

def boxplot(fpath):
	datas = []
	data_json = json.load(open(fpath))
	for content in data_json.values():
		i = 0
		while f"Server {i}" in content:
			data = content[f"Server {i}"]["RTT Measurements"]["TCP"]["Experiments"]
			ip_addr = content[f"Server {i}"]["IP Address"]
			datas.append((ip_addr, data))
			i += 1

	# Plot
	datas.sort(key=lambda x: x[0])
	ips = [x[0] for x in datas]
	vals = [x[1] for x in datas]
	plt.figure(i_fig)
	plt.boxplot(vals)
	plt.ylim(bottom=0, top=200)
	plt.xticks([i for i in range(1, len(ips)+1)], ips)
	plt.title(fpath.split("/")[-1])


output_dir = "output_test/"
for fpath in glob(os.path.join(output_dir, "*.json")):
	boxplot(fpath)
	i_fig += 1

plt.show()
