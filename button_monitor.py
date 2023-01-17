#! /usr/bin/python3.9

import RPi.GPIO as GPIO 
#Use BCM rather than board numbering 
GPIO.setmode(GPIO.BCM) 

#Setup pushbutton GPIO input 
GPIO.setup(26, GPIO.IN,pull_up_down=GPIO.PUD_UP)

while True:
  
  #If button pressed 
  if GPIO.input(26) == 0:
    print("System Online")
    #Execute the main.py script 
    exec(open('main.py').read())
      