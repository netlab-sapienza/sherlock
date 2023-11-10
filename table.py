from tabulate import tabulate
import json
import os


    
def print_table(data):
	table_in = []
	table_out = []
	for k, v in data.items():
		print(k)
		for key, value in v.items():
			if isinstance(value, dict):
				print("\t"+key)
				for keyy, valuee in value.items():
					if isinstance(valuee, dict):
						for keyyy, valueee in valuee.items():
							if keyyy == "Hop-By-Hop":
								continue
							if isinstance(valueee, dict):
								print(f"\t\t{keyy}\t{keyyy}")
								for keyyyy, valueeee in valueee.items():
									if keyyyy == "Experiments":
										continue
									print(f"\t\t\t{keyyyy}\t{valueeee}\n")
							else:
								print(f"\t\t{keyy}\t\t{keyyy}\t{valueee}")
							
						continue
						
					print("\t\t"+keyy+"\t\t"+str(valuee))
					table_in.append([keyy, str(valuee)])
					
			else:
				print("\t"+key+"\t\t"+str(value))
				table_out.append([key, str(value)])
		print("\n")



names = {}
ID = 0
files = os.listdir("./output")
print("\nShowing \'./output\' directory:\n")
for f in files:
	if f[0]==".":
		continue
	ID += 1
	names[ID] = f
	print(f"\t{ID} - {f}")
	
print("")

if ID == 0:
	print("Output folder is empty, please run \"python3 start.py\"")
else:	
	fileid = int(input("Please insert the desired output ID: "))

	if fileid not in names.keys():
		print("ID not valid\nReturn None")
		
	else:
		with open("./output/"+names[fileid]) as file:
			data = json.load(file)
		
		print_table(data)
	
	
	
	
