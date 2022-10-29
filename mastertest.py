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
import asyncio


def tempcheck():
    sensor = W1ThermSensor()
    temperature = sensor.get_temperature()
    #converts the temperature into Farenheit
    tempf = ((temperature *1.8)+32)
    print("Current Temp is %s celsius and %s fahrenheit" % (temperature , tempf))
    return temperature, tempf


def doorcheck():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(16, GPIO.IN)
    if GPIO.input(16) == 1:
        return False #Door closed
    else:
        return True #Door open


def imagecapture():
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
    
    #Turn on LED
    GPIO.setmode (GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(17,GPIO.OUT)#sets GPIO17 as an output pin
    GPIO.output(17,GPIO.HIGH)#sets LED ON

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
    
async def mainProcess():
    print("Starting logging loop...")
    doorTask = asyncio.create_task(doorProcess())
    asyncio.create_task(tempProcess())
    await doorTask
    
async def doorProcess():
    while True:
        #Only runs if not interrupting. Otherwise, waits until it can interrupt
        if not dontInterrupt:
            dontInterrupt = True
            
            #If the door was open previously, it will run this code
            if doorIsOpen:
                doorIsOpen = doorcheck()
                #if the door is currently closed, it takes a picture and logs to database
                if not doorIsOpen:
                    print("Door was closed. Taking picture...")
                    imagecapture()
                    pictureString = convertPicToString()
                    picString = pictureString.decode('utf-8')
                    database_logger.logData(temp, doorIsOpen, picString)
                    print("Logged Door Status to Database")
            #If the door was closed previously, it will run this code
            else:
                doorIsOpen = doorcheck()
                #If door is currently open, log the data to reflect this
                if doorIsOpen:
                    print("Door was opened. Logging to database...")
                    database_logger.logData(temp, doorIsOpen, picString)
                    print("Logged Door Status to Database")
            #All processes are finished, so other task can run now
            dontInterrupt = False
                
            #Wait 5 seconds until next reading
            await asyncio.sleep(5)
        #Waits 1 second since it was interrupting
        else:
            print("Door Postponed")
            await asyncio.sleep(1)
    
async def tempProcess():
    while True:
        print("Starting temperature log")
        #Waits 5 seconds since it was interrupting
        if dontInterrupt:
            print("Temp Postponed")
            await asyncio.sleep(5)
        #Takes temperature and waits 20 minutes
        else:
            dontInterrupt = True
            temp = int(tempcheck()[1])
            database_logger.logData(temp, doorIsOpen, picString)
            print("Logged Temperature to Database")
            dontInterrupt = False
            await asyncio.sleep(10)
            #await asyncio.sleep(1200)
        
    
OnboardingProcess()

database_logger.initConnection()
temp = int(32)
doorIsOpen = True
try:
    picString = convertPicToString().decode('utf-8')
except:
    print("No picture/Picture parse error")   

dontInterrupt = False
i=1
asyncio.run(mainProcess)

    