#! /usr/bin/python3.9

import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
GPIO.setmode(GPIO.BCM) 
GPIO.setup(26, GPIO.IN,pull_up_down=GPIO.PUD_UP)
while True:
  GPIO.setup(26, GPIO.IN,pull_up_down=GPIO.PUD_UP)

  if GPIO.input(26) == 0:
    print("System Online")

    exec(open('Main.py').read())
      