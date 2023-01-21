#! /usr/bin/python3.9

#Main script for the Electronic Lock Box system. Developed by Amandeep Kainth of the James Watt School of Engineering, University of Glasgow.
#Developed for a Final Year MEng Degree Project. 

#  Use Policy: The code provided here, apart from the segments indicated within the respective files /
#  is wholly the author's work. It may not be used or shared for any purpose other than viewing /
#  unless explicit permission has been given to you

# GPS drivers (https://gpsd.gitlab.io/gpsd/client-howto.html)
from gps import *
import time

import RPi.GPIO as GPIO  
import pickle
from csv import writer
from datetime import datetime
from datetime import date     
import time
from time import sleep
import serial

# Fingerprint drivers (See line 150 for source)
import adafruit_fingerprint

# OTP module (https://github.com/pyauth/pyotp)
import pyotp

import digitalio
import board

#Keypad drivers (https://github.com/adafruit/Adafruit_CircuitPython_MatrixKeypad)
import adafruit_matrixkeypad

import multiprocessing
from multiprocessing import Pool
import sys
from datetime import date
import signal
#Following import lines are for SMS
import requests, sys 
from lxml import etree, objectify


#Setup for matrix keypad, using adafruit_matrixkeypad
cols = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]
rows = [digitalio.DigitalInOut(x) for x in (board.D17, board.D27, board.D22, board.D0)]
keys = ((1, 2, 3, "A"), (4, 5, 6, "B"), (7, 8, 9, "C"), ("*", 0, "#", "D"))
matrix_keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)


#GPIO initialisation and setup
GPIO.setmode(GPIO.BCM)  # using BCM(GPIO) pin numbering opposed to Board
GPIO.setup(14, GPIO.OUT, initial=GPIO.LOW)  
GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(20, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(21, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(22, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(11, GPIO.IN,pull_up_down=GPIO.PUD_UP) 
GPIO.setup(10, GPIO.OUT, initial=GPIO.LOW)  
GPIO.setup(1, GPIO.OUT, initial=GPIO.LOW)

#Open data file holding the users/codes database, assign to variable
with open('data.p', 'rb') as fp: 
        user_codes = pickle.load(fp)
        
#Open data file holding the users/fingerprints database, assign to variable
with open('data1.p', 'rb') as fp: 
         user_fingerprints = pickle.load(fp) 

#Exception error handling if GPS module not connected or has an error. Allows system to still operate           
try: 
    gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)  #Begin data stream from GPS
except:
    pass 
    
  
#Defining secret key for pyotp, which handles the OTP generation 
totp = pyotp.TOTP('BFRQ4P7YBV563YJE') 

#Exception error handling if Fingerprint module not connected or has an issue
#Allows system to still operate (using codes for both authentication stages)
try: 
    #UART communication parameters for the fingerprint scanner 
    uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1) 
    #Using adafruit fingerprint scannerner driver code 
    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart) 
except:
    pass
    
#Loading the alarm arming variable 
arming = pickle.load(open("armingStoringFile.dat", "rb")) 

global count
count=0  #Setting authentication stage counter to 0
pickle.dump(count, open("count.dat", "wb"))  #Save this to file 

    

#*****************************************************************************
#*    Source code citation for adapted SMS functionality 
#*    Title: python_huawei_e303 
#*    Author: Goto, Yuske
#*    Date: 15/01/2018
#*    Code version: 1.0
#*    Availability: GitHub: https://github.com/yuskegoto/python_huawei_e303
#*    Usage: Lines 115-144
#*****************************************************************************

#SMS functionality below

E303_ip = 'http://192.168.1.1/'
HTTPPOST_SEND = 'api/sms/send-sms'

def timestamp():
    time_stamp = time.strftime("%Y")
    time_stamp += '-'
    time_stamp += time.strftime("%m")
    time_stamp += '-'
    time_stamp += time.strftime("%d")
    time_stamp += ' '
    time_stamp += time.strftime("%H")
    time_stamp += ':'
    time_stamp += time.strftime("%M")
    time_stamp += ':'
    time_stamp += time.strftime("%S")
    return time_stamp

def send_sms(phone_no, sms_text):
    if isinstance(sms_text, str):
        request = objectify.Element("request")
        request.Index = -1
        request.Phones = ''
        request.Phones.Phone = phone_no
        request.Sca = ''
        request.Content = sms_text
        request.Length = str(len(sms_text))
        request.Reserved = 1
        request.Date = timestamp()
        payload = etree.tostring(request)
        a = requests.post(E303_ip + HTTPPOST_SEND, data = payload)
 
#SMS functionality ends


#***************************************************************************************
#*    Source code citation for adapted fingerprint scanner functionality 
#*    Title: Adafruit_CircuitPython_Fingerprint
#*    Author: Limor Fried for Adafruit Industries 
#*    Date: 04/10/2022
#*    Code version: 2.2.10
#*    Availability: GitHub: https://github.com/adafruit/Adafruit_CircuitPython_Fingerprint
#*    Usage: Lines 166-174, 403-413
#*    License: MIT License. See file MIT_LICENSE_ADAFRUIT within the main repository.
#***************************************************************************************

 
def get_fingerprint():

    #Note in the following, adafruit.OK corresponds to the OK message from the scanner
    #This is sent from the scanner upon a succesful operation
    
    while finger.get_image() != adafruit_fingerprint.OK: #take fingerprint image
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK: #convert to template
        return False 
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK: #search for print in database 
        return False
    return True  #Returns true upon fingerprint, that exists in database, being recognised 
   
def keypad(): #Gets user code input from matrix keypad

    code_input = "" #Holder for user code input 
    while True:
      keys = matrix_keypad.pressed_keys  #Using adafruit_matrixkeypad driver library 
      if keys:  #If keypad pressed                  
        GPIO.output(1, GPIO.HIGH)  #Beep buzzer upon button press
        time.sleep(0.1)
        GPIO.output(1, GPIO.LOW)
        print("Pressed: ", keys)
        
        if(keys[0] == 1):
            #Delay before saving pressed button, to prevent unintentional multiple enteries
            time.sleep(0.3) 
            
            code_input += "1"  #Add the corresponding pressed key to the code_input variable 
            
        if(keys[0] == 2):
            time.sleep(0.3)
            code_input += "2"
        if(keys[0] == 3):
            time.sleep(0.3)
            code_input += "3"
        if(keys[0] == 4):
            time.sleep(0.3)
            code_input += "4"
        if(keys[0] == 5):
            time.sleep(0.3)
            code_input += "5"
        if(keys[0] == 6):
            time.sleep(0.3)
            code_input += "6"
        if(keys[0] == 7):
            time.sleep(0.3)
            code_input += "7"
        if(keys[0] == 8):
            time.sleep(0.3)
            code_input += "8"
        if(keys[0] == 9):
            time.sleep(0.3)
            code_input += "9"
        if(keys[0] == 0):
            time.sleep(0.3)
            code_input += "0"
        if(keys[0] == '*'):
            time.sleep(0.3)
            
        if(keys[0] == '#'):  #Upon pressing "#", return the inputted user code 
            time.sleep(0.3)
            print(code_input)
            return code_input 
          
def tracking(unlock_type, user_s1, user_s2): 
  #Handles GPS location extraction and calls the logging functio
  
  y=0  #Set location found variable to 0
  z=0  #Set attempt counter to 0
  try:
      #Repeat until the first non zero result until a maximum of 11 times
      while y!=1 and z!=10: 
        report = gpsd.next()  #Get report of gps data from gpsd daemon
        
        #Get latitude from the lat attribute of the GPS report object
        lat = str(getattr(report,'lat',0.0))
        z=z+1  #Increment the attempt counter 
        
        if lat !="0.0": 
            #Proceed only upon a non zero latitude. Zero latitude indicates no GPS location 
            #Can occur periodically in stream as well as when no signal.
            
            #y indicates that location has been found; preventing the while loop from repeating 
            y=1  
            
            #Get latitude & longnitude from the lat attribute of the GPS report object
            lon = str(getattr(report,'lon',0.0))  
            lat = str(getattr(report,'lat',0.0)) 
            #Compile a Google Maps link 
            location= f"https://www.google.co.uk/maps/place/{lat},{lon}" 
            print(location)  #For debugging 
            #Call the log function, passing information regarding the unlock to it
            log(unlock_type, location, user_s1,user_s2)
            
  except:  #Exception handling if no signal obtained 
  
      print("no GPS lock - last known GPS data follows")
      
      #Open the GPS log and extract the last known location 
      with open('GPSlogger.csv','r') as file: 
          data = file.readlines() 
          
      last_row = data[-1] 
      list1 = last_row.split(',')
      location= str(list1[2]+"," + list1[3]) #Get link from gpslog.py output csv gpslogger.py
      location = location.replace('"', '') #Removing quotes from around location link
      
      #Extract date and time of last known location       
      capture_date = list1[0] 
      capture_time = list1[1] 
      #Call the log function, passing information regarding the unlock to it
      log(unlock_type, location, user_s1, user_s2, capture_date, capture_time) 

  
def log(unlock_type, location, user_s1, user_s2, capture_date=None, capture_time=None): 
    #Handles logging
    
    current_date = date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    #Compile packet to be written
    data = [current_date,current_time, unlock_type, location, user_s1, user_s2, capture_date, capture_time] 

    with open('log.csv', 'a') as f_object:  #Opening log CSV
     
        
        writer_object = writer(f_object)
     
      
        writer_object.writerow(data)  #Writing packet 
     
        f_object.close()  
        
    # Compiling SMS message to be sent
    message = ("Timestamp:" + " " + str(current_date)+ " " + str(current_time) + " "
    + "Unlock Mode:" + str(unlock_type) + " "+ "Location:" +str(location) + " "
    +"Location Capture Date:" + str(capture_date)  +" "+"Location Capture Time:" +" "
    +str(capture_time) +" "+"User_s1:" + str(user_s1) +" "+"User_s2:" + str(user_s2)) 
 
    print(message)
    
    send_sms('07459288940',message )  #Send SMS with information 
    
def unlock(unlock_type, user_s1,user_s2): 
    #Handles unlocking process  

    arming=0  #Disarm alarm system
    
    #Write disarm variable to file. Is accessed by alarm monitor script
    pickle.dump(arming, open("armingStoringFile.dat", "wb")) 
    
    GPIO.output(20, GPIO.LOW)  # Turn off Blue LED
    GPIO.output(21, GPIO.LOW)  # Turn off Red LED
    GPIO.output(16, GPIO.HIGH)  # Turn on Green LED
    GPIO.output(10, GPIO.HIGH)  # Turn on solenoid
    sleep(5)  #Sleep for 5 seconds - unlocking window 
    GPIO.output(10, GPIO.LOW)  # Turn off solenoid 
    GPIO.output(16, GPIO.LOW)  # Turn Off Green LED
  
    sleep(0.1)
    arming=1  #Rearm alarm system via the disarm variable 
    #Writing it to file
    pickle.dump(arming, open("armingStoringFile.dat", "wb")) 
    #Call the tracking function, passing information about unlock to it
    tracking(unlock_type, user_s1, user_s2) 
  


    
def code_input(): 
    #Handles OTP and personal code input
    
    #Read the authentication stage counter variable
    count = pickle.load(open("count.dat", "rb")) 
    while True: 
        if count==0:  
            #If handling first stage of authentication (count==0) then take personal code input 
            
            print("Input personal code")
            code=keypad()  #Get code via keypad function, assign to variable 
          
            attempts_personal = 0  #Attempt counter for personal code 
            
            while attempts_personal <3:  #3 attempts allowed 
            
                #Allow authentication if inputted code is in the code database
                if code in user_codes.keys(): 
                    #Set the authentication stage counter to 1, to indicate stage one has been completed
                    count=1  
                    pickle.dump(count, open("count.dat", "wb"))  #Write this to file 
                    print("First code correct")
                    b=(user_codes.get(code))  #Get the name of user for a given inputted code
                    return True  #Exit loop and return to main execution flow to enable next stage
        else:   
            #If count not ==0, i.e., if stage two authentication is occuring 
            code=keypad()  #Get code via keypad function, assign to variable 
          
            sleep(1)
            
            if totp.verify(code) == 1: #Use PyOTP to verify if the code is the correct OTP
           
              print("Second Stage: 2FA PIN Accepted - Unlocking")
              GPIO.output(21, GPIO.LOW)
              unlock_type="Unlocking by OTP" 
              user_s2="N/A"  #No stage two user, as OTP has been used 
              
              #Getting stage one finger ID from storing file 
              finger_ID = pickle.load(open("finger_ID_stage_one.dat", "rb"))
              
              #Getting corresponding user name from the users/fingerprints database 
              user_s1=(user_fingerprints.get(finger_ID)) 
              
              unlock(unlock_type,user_s1,user_s2)  #Call the unlock function 
              return True  #Return to main execution flow
             
            else:  
                #If given code is wrong 
                
                GPIO.output(20, GPIO.LOW)  # Turn off Blue LED
                print("Code is incorrect. Access Denied - Try Again.")
                GPIO.output(21, GPIO.HIGH)  # Turn on Red LED
                sleep(0.5)
                GPIO.output(21, GPIO.LOW)  # Turn off Red LED
                #input = ""  #Reset input variable
                GPIO.output(20, GPIO.HIGH)  # Turn on Blue LED
                attempts = attempts + 1
              

                

def fingerprint_input(): 

    #Gets fingerprint scanner input    
    print("print input running")
    
    #Read the authentication stage counter variable
    count = pickle.load(open("count.dat", "rb")) 
    while True:
        #Exception error handling 
        if finger.read_templates() != adafruit_fingerprint.OK: 
            raise RuntimeError("Failed to read templates")
        if finger.count_templates() != adafruit_fingerprint.OK:
            raise RuntimeError("Failed to read templates")
        if finger.read_sysparam() != adafruit_fingerprint.OK:
            raise RuntimeError("Failed to get system parameters")
        if get_fingerprint(): 
            #If nominally gotten a fingerprint result from scanner 
            
            #Printing info regarding the print
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)  
            
            
            if count==0:  
                #If handling first stage of authentication(count==0),return to main upon success rather than unlocking 
                print("First Stage: Fingerprint Authorised")
                
                #Getting the scanned print's ID from the scanner and storing as variable
                finger_ID_stage_one = finger.finger_id 
                #Writing this to file
                pickle.dump(finger_ID_stage_one, open("finger_ID_stage_one.dat", "wb")) 
                
                #Set the authentication stage counter to 1, to indicate stage one has been completed 
                count=1 
                pickle.dump(count, open("count.dat", "wb")) #Write this to file 

                GPIO.output(20, GPIO.HIGH) #Blue LED on
                GPIO.output(21, GPIO.LOW)  #Red LED off    
            
                return True  #Exit loop and return to main execution flow to enable next stage
            
            else:
                #If count not ==0, i.e., if stage two authentication is occuring
                
                #Reading stage one finger ID
                finger_ID = pickle.load(open("finger_ID_stage_one.dat", "rb")) 
                
                if finger.finger_id != finger_ID: 
                    #Proceed so long as a different fingerprint is being used 
                    print("Second Stage: Fingerprint Authorised")
                    unlock_type="Unlocking by Finger"
                    
                    print(finger_ID)  #Print current finger ID
                    print(finger_database) #Print users/fingerprints database
                    
                    #Get the name of the stage one fingerprint user, via users/fingerprints database
                    user_s1=(finger_database.get(finger_ID))
                    print(user_s1)
                    
                    #Get the fingerprint ID of the current (stage two) fingerprint user
                    finger_ID =finger.finger_id 
                    
                    #Get the name of the current (stage two) fingerprint user, via users/fingerprints database
                    user_s2=(finger_database.get(finger_ID))
                    print(user_s2)
                    
                    unlock(unlock_type, user_s1, user_s2) #Call the unlock function
                    return True  #Return to main execution flow
                else: 
                    #If scanned fingerprint is the same as the first 
                     print("Access denied - a different authorised user's finger must be scanned!")
                     GPIO.output(21, GPIO.HIGH) # Turn on Red LED
                     GPIO.output(20, GPIO.LOW)  #Turn off Blue LED
                     sleep(1)
                     GPIO.output(20, GPIO.HIGH) #Turn on Blue LED
                     GPIO.output(21, GPIO.LOW)  # Turn off Red LED

        else: 
            #If fingerprint is not registered 
            print("Finger not found")
            print("Access Denied - Try Again")
            GPIO.output(21, GPIO.LOW)  # Turn off Red LED
            GPIO.output(20, GPIO.LOW)  #Turn off Blue LED
            if count!=1:  #If performing stage one authentication
                sleep(1)
            GPIO.output(21, GPIO.HIGH)  #Turn on Red LED
            sleep(1)
            if count==1: #If perofmring stage two authentication
                GPIO.output(21, GPIO.LOW)  #Turn off Red LED
                GPIO.output(20, GPIO.HIGH) #Turn on Blue LED
            
          
def main(): 
    #Main execution function 

    pool = Pool(100) #Setup the multiprocessing pool
     
      
    def check(x):
    #Callback function. "x" is the returned value from whichever 
    #function below is being executed by multiprocessing    
    
      if x==1:  #If True has been returned 
       
        pool.terminate()  #Terminate the multiprocessing pool of function(s)
            
      
        print("pool terminate command ran")
        

    if fingerprint_input(): 
    #Stage one via fingerprint scan. If authorised, continue
    
    #if code_input(): 
    
    #Uncomment above line and comment out "if fingerprint_input()" to change to personal code as first stage 
    
        print("Input OTP Code, or Scan Second Authorised Fingerprint..")
        
        #Comment out above line and uncomment below to change to personal code as first stage
        
        #print("Input Second User's Personal Code")
       
        pool = Pool(100)  #Setup the multiprocessing pool
        sleep(1)
        
        #Execute the fingerprint input function via multiprocessing and
        #run callback function upon function exit
        
        pool.apply_async(fingerprint_input, callback=check) 
        
        #Execute the code input function via multiprocessing and
        #run callback function upon function exit
        pool.apply_async(code_input, callback=check)
        
        pool.close()
        pool.join()

#Script start 

print("System Ready")
#print("Enter Personal Code") #Uncomment for personal code as first stage
print("Scan Authorised Print")  #Comment out for personal code as first stage
GPIO.output(21, GPIO.HIGH) #Turn on Red LED
main()  #Execute main function 


       
         
