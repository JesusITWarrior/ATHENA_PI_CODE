import os
import subprocess

mine = subprocess.check_output("bluetoothctl devices", shell = True).decode('utf-8')
#print(subprocess.check_output("bluetoothctl devices", shell = True).decode('utf-8'))
if mine == "":
    print("Nothing!")
else:
    print(mine)
    
while mine != "":
    device = mine[7:24:1]
    mine = mine[mine.index("\n")+1:len(mine):1]
    os.system("sudo bluetoothctl disconnect {}".format(device))
    os.system("sudo bluetoothctl remove {}".format(device))
    print(device)
#os.system("bluetoothctl devices")
#os.system("")