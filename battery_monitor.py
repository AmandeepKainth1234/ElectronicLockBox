#! /usr/bin/python3.9

import RPi.GPIO as GPIO
from time import sleep

#Import adapted SMS functionality code 
from SMS import send_sms

GPIO.setmode(GPIO.BCM)  #Use BCM rather than board numbering
  
#Power LED transistor base PIN, to trigger Power SOC to output battery status
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW) 

#Setup for the three inputs into the RPi, from the LED pins of the Power SOC
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


while True:
    #Emulating the press of the LED pin of the Power SOC
    GPIO.output(12, GPIO.HIGH) 
    sleep(0.1)
    GPIO.output(12, GPIO.LOW)
    

    #Identify if 25% signal active. High/low based on IP5306 SOC schematic 
    #Send SMS alert 
    if GPIO.input(18)==1 and GPIO.input(8)==0:
    send_sms('07459288940',"Battery at 25%" ) 
        
    #Identify if 50% signal active. High/low based on IP5306 SOC schematic     
    elif GPIO.input(18)==0 and GPIO.input(8)==1:
        print("50%")
        
    #Identify if 75% signal active. High/low based on IP5306 SOC schematic 
    elif GPIO.input(24)==1 and GPIO.input(8)==0:
        print("75%")
       
    #Identify if 100% signal active. High/low based on IP5306 SOC schematic 
    elif GPIO.input(24)==0 and GPIO.input(8)==1:
        print("100%%")
       
    
    sleep(600)