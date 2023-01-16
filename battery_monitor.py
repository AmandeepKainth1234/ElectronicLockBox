#! /usr/bin/python3.9
import RPi.GPIO as GPIO
from time import sleep
from SMS import send_sms
GPIO.setmode(GPIO.BCM) 
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW) #Power LED transistor base PIN, to trigger Power SOC to output battery status
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Setup for the three inputs into the RPi, from the LED pins of the Power SOC
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
a=0
b=
c=0
d=0

while True:
 
    GPIO.output(12, GPIO.HIGH) #Emulating the press of the LED pin of the Power SOC
    sleep(0.1)
    GPIO.output(12, GPIO.LOW)
    
    #GPIO 18 (LED 1) ...and 8 (LED 3) ....24 (LED 2). 
    
    if GPIO.input(18)==1 and GPIO.input(8)==0:
    send_sms('07459288940',"Battery at 25%" ) 
        
        
    elif GPIO.input(18)==0 and GPIO.input(8)==1:
        print("50%")
        
   
    elif GPIO.input(24)==1 and GPIO.input(8)==0:
        print("75%")
       
    
    elif GPIO.input(24)==0 and GPIO.input(8)==1:
        print("100%%")
       
    
    send_sms('07459288940',"Battery at 25%" )
    sleep(600)