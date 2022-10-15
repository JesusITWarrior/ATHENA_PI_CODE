import time
from w1thermsensor import W1ThermSensor
sensor = W1ThermSensor()
while True:
    temperature = sensor.get_temperature()
    tempf = ((temperature *1.8)+32)
    print("Current Temp is %s celsius and %s freedom units" % (temperature , tempf))
    time.sleep(1)


