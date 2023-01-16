#! /usr/bin/python3.9
from SMS import send_sms
import pickle
from time import sleep
from ds18b20 import DS18B20
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
GPIO.setmode(GPIO.BCM) 
GPIO.setup(1, GPIO.OUT, initial=GPIO.LOW)  
GPIO.setup(9, GPIO.OUT, initial=GPIO.LOW)  

#!/usr/bin/env python3
import signal
import sys
import RPi.GPIO as GPIO
sensors = []
for sensor_id in DS18B20.get_available_sensors():
    sensors.append(DS18B20(sensor_id))
Contact_GPIO = 11
def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
def contact_callback(channel):
    arming = pickle.load(open("armingStoringFile.dat", "rb"))
    sleep(0.2)
    if GPIO.input(11):
    
        GPIO.output(9, GPIO.HIGH)  #Turn on the internal light 
        if arming==1:
            print(" Alarm!")
            

            
            #GPIO.output(1, GPIO.HIGH)  # Turn on buzzer alarm
            #send_sms('07459288940',"Alarm Triggered" )
            
    else:
         GPIO.output(9, GPIO.LOW)  #Turn off the internal light
         print("test light off")


    


GPIO.setup(Contact_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(Contact_GPIO, GPIO.BOTH,
        callback=contact_callback, bouncetime=300)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()



while True:
  #for sensor in sensors:
     # print(sensor.get_temperature)
      
    print("Test")
    sleep(60) 