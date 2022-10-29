Needs the following packages:
	sudo pip install azure-cosmos
	sudo pip install w1thermsensor
	sudo pip install pybluez

Make these changes!!!!
	sudo raspi-config
		Interface Options:
			1 Wire Enabled
			Legacy Camera Enabled

	sudo nano /etc/systemd/system/dbus-org.bluez.service
		Make sure this is what you see in [Service]
		ExecStart=/usr/lib/bluetooth/bluetoothhd -C
		
	sudo nano /etc/rc.local
		Before the exit 0 and outside of any ifs, add the following:
		sudo python3 /home/pi/Desktop/Athena/master.py &
		
