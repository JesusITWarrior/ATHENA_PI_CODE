import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN)

while True:
    if GPIO.input(16) == 1:
        print("Fridge Closed")
    else:
        print("Fridge Open")
    time.sleep(1)