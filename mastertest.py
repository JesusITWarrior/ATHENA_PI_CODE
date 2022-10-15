from time import sleep
from w1thermsensor import W1ThermSensor
from picamera import PiCamera #Pi camera load lib
from picamera import Color
import database_logger
import datetime as dt
import RPi.GPIO as GPIO #Pi LIB GPIO
import os
import base64
from PIL import Image
from bluetooth_handler import OnboardingProcess


def tempcheck():
    sensor = W1ThermSensor()
    temperature = sensor.get_temperature()
    tempf = ((temperature *1.8)+32)
    print("Current Temp is %s celsius and %s fahrenheit" % (temperature , tempf))
    return temperature, tempf


def doorcheck():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(16, GPIO.IN)
    if GPIO.input(16) == 1:
        doorstatus = False #Door closed
    else:
        doorstatus = True #Door open
    return doorstatus


def imagecapture():
    #Turn on LED while camera is warming up
    GPIO.setmode (GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(17,GPIO.OUT)#sets GPIO17 as an output pin
    GPIO.output(17,GPIO.HIGH)#sets LED ON
    sleep(2)#sleep for LED being on


    camera = PiCamera()
    sleep(2)
    camera.resolution = (1920, 1080)
    camera.brightness = 50
    camera.contrast = 10

    # now = datetime.now()
    # dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    camera.start_preview()
    camera.annotate_text_size = 60
    camera.annotate_foreground = Color('black')
    camera.annotate_background = Color('white')
    camera.annotate_text = dt.datetime.now().strftime('Athena Fridge - %Y-%m-%d %H:%M:%S')

    sleep(2)#sleep for camera preview
    camera.capture ('masterpic.png')#takes still from camera
    camera.stop_preview()#stops view from camera

    sleep(2)

    im=Image.open('masterpic.png')
    width, height = im.size

    left = 350 #width/2
    top = 0 #height/2
    right = 1570 #(3*(width/2))
    bottom = 1080 #(3* (height/2))

    im1=im.crop((left, top, right, bottom))
    
    im1.save('masterpic1.png')

    GPIO.output(17,GPIO.LOW)#turns off LED

    camera.stop_preview()
    
    camera.close()

def convertPicToString():
    if os.path.exists('masterpic1.png'):
        with open('masterpic1.png','rb') as img_file:
            string = base64.b64encode(img_file.read())
        return string
    else:
        return ""

OnboardingProcess()

i=1
database_logger.initConnection()
temp = int(32)
doorIsOpen = True
try:
    picString = convertPicToString().decode('utf-8')
except:
    print("No picture/Picture parse error")
    

while True:
    if i % 5 == 0:
        temp = int(tempcheck()[1])
        doorIsOpen = doorcheck()
        if doorIsOpen:
            print("Door is Open")
        else:
            print("Door is Closed")
        print(i)
        database_logger.logData(temp, doorIsOpen, picString)
        
    if i % 15 == 0:
        imagecapture()
        i=0
        pictureString = convertPicToString()
        picString = pictureString.decode('utf-8')
        database_logger.logData(temp, doorIsOpen, picString)
        
    sleep(1)
    i=i+1
    
    