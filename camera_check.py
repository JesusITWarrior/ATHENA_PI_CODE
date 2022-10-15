from picamera import PiCamera #Pi camera load lib
from time import sleep
import RPi.GPIO as GPIO #Pi LIB GPIO

#Turn on LED while camera is warming up
GPIO.setmode (GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)#sets GPIO17 as an output pin
GPIO.output(17,GPIO.HIGH)#sets LED ON
sleep(5)#sleep for LED being on




camera = PiCamera()

camera.start_preview()
sleep(5)#sleep for camera preview
camera.capture ('image.png')#takes still from camera
camera.stop_preview()#stops view from camera

GPIO.output(17,GPIO.LOW)#turns off LED

         