#! /usr/bin/python3.9

#Door monitor script for the Electronic Lock Box system. Developed by Amandeep Kainth of the James Watt School of Engineering, University of Glasgow.
#Developed for a Final Year MEng Degree Project. 

#  Use Policy: The code provided here, apart from the segments indicated within the respective files /
#  is wholly the author's work. It may not be used or shared for any purpose other than viewing /
#  unless explicit permission has been given to you
#Import adapted SMS functionality code 
from SMS import send_sms

import pickle
from time import sleep
import RPi.GPIO as GPIO  

#Use BCM rather than Board numbering 
GPIO.setmode(GPIO.BCM) 

GPIO.setup(1, GPIO.OUT, initial=GPIO.LOW)  #Buzzer
GPIO.setup(9, GPIO.OUT, initial=GPIO.LOW)  #Light
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Reed Switch
 
import signal
import sys
import RPi.GPIO as GPIO


    
def contact_callback(channel):
    #Runs on callback from GPIO event detection 
    
    #Read alarm system arming variable 
    arming = pickle.load(open("armingStoringFile.dat", "rb"))
    
    sleep(0.2)
    if GPIO.input(11):
        #If reed switch input is high, door was opened
        
        GPIO.output(9, GPIO.HIGH)  #Turn on the internal light 
        if arming==1:
            #If system armed (not unlocked)
            print(" Alarm!")
           
            GPIO.output(1, GPIO.HIGH)  # Turn on buzzer alarm
            #Send alarm SMS
            send_sms('07459288940',"Alarm Triggered" )
            
    else:
         #If reed switch input is low, door was closed 
         GPIO.output(9, GPIO.LOW)  #Turn off the internal light
        


#Add new GPIO event detection, for rising or falling on reed switch GPIO 
#Triggers contact_callback function above when event detected

GPIO.add_event_detect(11, GPIO.BOTH,
        callback=contact_callback, bouncetime=300)

signal.pause() #Sleep until a signal is detected 

