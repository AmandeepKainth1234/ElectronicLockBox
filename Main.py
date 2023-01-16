
"""
Main script for the Electronic Lock Box system. Developed by Amandeep Kainth of the James Watt School of Engineering, University of Glasgow.
Developed for a Final Year MEng Degree Project. 
""" 

#! /usr/bin/python3.9
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
import adafruit_fingerprint
import pyotp
import digitalio
import board
import adafruit_matrixkeypad
import multiprocessing
from multiprocessing import Pool
import sys
from datetime import date
import signal
import requests, sys #for sms
# for sms Using Lxml to speed up faster parsing, Lxml is used also for writing xml
from lxml import etree, objectify



#Setup for matrix keypad, using adafruit_matrixkeypad

cols = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]
rows = [digitalio.DigitalInOut(x) for x in (board.D17, board.D27, board.D22, board.D0)]
keys = ((1, 2, 3, "A"), (4, 5, 6, "B"), (7, 8, 9, "C"), ("*", 0, "#", "D"))
matrix_keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)


#GPIO initialisation and setup

GPIO.setmode(GPIO.BCM)  #Using BCM(GPIO) pin numbering opposed to Board
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
GPIO.setup(1, GPIO.OUT, initial=GPIO.LOW

with open('user_codes.p', 'rb') as fp: #open data file holding the users/codes database 
        user_codes = pickle.load(fp) #assign this to user_codes dictionary
        
with open('user_fingerprints.p', 'rb') as fp: #open data file holding the users/fingerprints database 
         user_fingerprints = pickle.load(fp) #assign this to user_fingerprints dictionary
                
try: #exception error handling if GPS module not connected or has an error. Allows system to still operate
    gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) #begin data stream from GPS
except:
    pass 
    
  
    
totp = pyotp.TOTP('BFRQ4P7YBV563YJE') #defining secret key for pyotp, which handles the otp generation 

try: #exception error handling if Fingerprint module not connected or has an issue . Allows system to still operate (using codes for both authentication stages)
    uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1) #UART communication parameters for the fingerprint scanner 

    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart) #using adafruit fingerprint scanner driver code 
except:
    pass

arming = pickle.load(open("armingStoringFile.dat", "rb")) #loading the alarm arming variable 

global count

count=0 #setting authentication stage counter to 0
pickle.dump(count, open("count.dat", "wb")) #save this to file 

    
"""
***************************************************************************************
*    Source code citation for adapted SMS functionality 
*    Title: python_huawei_e303 
*    Author: Goto, Yuske
*    Date: 15/01/2018
*    Code version: 1.0
*    Availability: GitHub: https://github.com/yuskegoto/python_huawei_e303
*    Usage: Lines 98-129
***************************************************************************************
"""
#SMS functionality below

E303_ip = 'http://192.168.1.1/'
HTTPPOST_SEND = 'api/sms/send-sms'

def timestamp():
    # Formatting time stamp
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
        # Formatting request
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

"""
***************************************************************************************
*    Source code citation for adapted fingerprint scanner functionality 
*    Title: Adafruit_CircuitPython_Fingerprint
*    Author: Limor Fried for Adafruit Industries 
*    Date: 04/10/2022
*    Code version: 2.2.10
*    Availability: GitHub: https://github.com/adafruit/Adafruit_CircuitPython_Fingerprint
*    Usage: Lines 145-158, 373-378
*    License: MIT License. See file MIT_LICENSE_ADAFRUIT within the main repository.
***************************************************************************************
"""
 
def get_fingerprint():

    #note in the following, adafruit.OK corresponds to the OK message from the scanner
    #this is sent from the scanner upon a succesful operation
    
    while finger.get_image() != adafruit_fingerprint.OK: #take fingerprint image
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK: #convert to template
        return False 
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK: #search for print in database 
        return False
    return True #returns true upon fingerprint, that exists in database, being recognised 
   
def keypad(): #gets user code input from matrix keypad

    code_input = "" #holder for user code input 
    while True:
      keys = matrix_keypad.pressed_keys #using adafruit_matrixkeypad driver library 
      if keys: #if keypad pressed                  
        GPIO.output(1, GPIO.HIGH) #beep buzzer upon button press
        time.sleep(0.1)
        GPIO.output(1, GPIO.LOW)
        print("Pressed: ", keys)
        
        if(keys[0] == 1):
            time.sleep(0.3) #delay before saving pressed button, to prevent unintentional multiple enteries
            
            code_input += "1" #add the corresponding pressed key to the code_input variable 
            
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
            
        if(keys[0] == '#'): #upon pressing "#", return the inputted user code 
            time.sleep(0.3)
            print(code_input)
            return code_input 
          
def tracking(unlock_type, user_s1, user_s2): #handles GPS location extraction and calls the logging function

  
  y=0 #set location found variable to 0
  z=0 #set attempt counter to 0
  try:
      while y!=1 and z!=10:#repeat until the first non zero result until a maximum of 11 times
        report = gpsd.next() #get report of gps data from gpsd daemon
        lat = str(getattr(report,'lat',0.0))#get latitude from the lat attribute of the GPS report object
        z=z+1 #increment the attempt counter 
        
        if lat !="0.0": #proceed only upon a non zero latitude. Zero latitude inidcates no GPS location. Can occur periodically in stream as well as when no signal.
            y=1 #Indicates that a location has been found; preventing the while loop from executing again
            
            lat = str(getattr(report,'lat',0.0))  #get latitude from the lat attribute of the GPS report object
            lon = str(getattr(report,'lon',0.0))  #get longnitude from the lat attribute of the GPS report object
            location= f"https://www.google.co.uk/maps/place/{lat},{lon}" #compile a Google Maps link 
            print(location) #for debugging 
            log(unlock_type, location, user_s1,user_s2) #call the log function, passing information regarding the unlock to it
  except:  #exception handling if no signal obtained 
  
      print("no GPS lock - last known GPS data follows")
      
      with open('GPSlogger.csv','r') as file: #open the GPS log and extract the last known location 
          data = file.readlines() 
          
      last_row = data[-1] 
      list1 = last_row.split(',')
      location= str(list1[2]+"," + list1[3]) #get link from gpslog.py output csv gpslogger.py
      location = location.replace('"', '') #removing quotes from around location link 
      capture_date = list1[0] #extract date of last known location 
      capture_time = list1[1] #extract time of last known location 
      log(unlock_type, location, user_s1, user_s2, capture_date, capture_time) #call the log function, passing information regarding the unlock to it.

  
def log(unlock_type, location, user_s1, user_s2, capture_date=None, capture_time=None): #handles logging

    current_date = date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    data = [current_date,current_time, unlock_type, location, user_s1, user_s2, capture_date, capture_time] #compile packet to be written

    with open('log.csv', 'a') as f_object: #opening log CSV
     
        
        writer_object = writer(f_object)
     
      
        writer_object.writerow(data) #writing packet 
     
        f_object.close()  
    message = "Timestamp:" + " " + str(current_date)+ " " + str(current_time) + " " + "Unlock Mode:" + str(unlock_type) + " "+ "Location:" +str(location) + " "+"Location Capture Date:" + str(capture_date)  +" "+"Location Capture Time:" +" "+str(capture_time) +" "+"User_s1:" + str(user_s1) +" "+"User_s2:" + str(user_s2) 
 
    print(message)
    
    send_sms('07459288940',message ) #send SMS with information 
    
def unlock(unlock_type, user_s1,user_s2): #handles unlocking process

    arming=0 #disarm alarm system
    pickle.dump(arming, open("armingStoringFile.dat", "wb")) #write disarm variable to file. Is accessed by alarm monitor script
    
    GPIO.output(20, GPIO.LOW)  # Turn off Blue LED
    GPIO.output(21, GPIO.LOW)  # Turn off Red LED
    GPIO.output(16, GPIO.HIGH)  # Turn on Green LED
    GPIO.output(10, GPIO.HIGH)  # Turn on solenoid
    sleep(5)  # Sleep for 5 seconds - unlocking window 
    GPIO.output(10, GPIO.LOW)  # Turn off solenoid 
    GPIO.output(16, GPIO.LOW)  # Turn Off Green LED
  
    sleep(0.1)
    arming=1 #rearm alarm system via the disarm variable 
    pickle.dump(arming, open("armingStoringFile.dat", "wb")) #writing it to file
    tracking(unlock_type, user_s1, user_s2) #call the tracking function, passing information about unlock to it
  


    
def otpinput(): #handles OTP and personal code input
    
    count = pickle.load(open("count.dat", "rb")) #read the authentication stage counter variable
    while True: 
        if count==0:  #if handling first stage of authentication (count==0) then take personal code input 
          
            print("Input personal code")
            code=keypad() #get code via keypad function, assign to variable 
          
            attempts_personal = 0 #attempt counter for personal code 
            
            while attempts_personal <3: #3 attempts allowed 
            
                if code in user_codes.keys(): #allow authentication if inputted code is in the code database
            
                    count=1 #set the authentication stage counter to 1, to indicate stage one has been completed 
                    pickle.dump(count, open("count.dat", "wb")) #write this to file 
                    print("First code correct")
                    b=(user_codes.get(code)) #get the name of user for a given inputted code
                    return True #exit loop and return to main execution flow to enable next stage
        else:   #if count not ==0, i.e., if stage two authentication is occuring 
          
            code=keypad()#get code via keypad function, assign to variable 
          
            sleep(1)
            
            if totp.verify(code) == 1: #use PyOTP to verify if the code is the correct OTP
           
              print("Second Stage: 2FA PIN Accepted - Unlocking")
              GPIO.output(21, GPIO.LOW)
              unlock_type="Unlocking by OTP" 
              user_s2="N/A" #no stage two user, as OTP has been used 
              
              finger_ID = pickle.load(open("finger_ID_stage_one.dat", "rb")) #getting stage one finger ID from storing file 
              user_s1=(user_fingerprints.get(finger_ID)) #getting corresponding user name from the users/fingerprints database 
              unlock(unlock_type,user_s1,user_s2) #call the unlock function 
              return True #return to main execution flow
             
            else: #if given code is wrong 
            
                GPIO.output(20, GPIO.LOW)  # Turn off Blue LED
                print("Code is incorrect. Access Denied - Try Again.")
                GPIO.output(21, GPIO.HIGH)  # Turn on Red LED
                sleep(0.5)
                GPIO.output(21, GPIO.LOW)  # Turn off Red LED
                #input = "" #reset input variable
                GPIO.output(20, GPIO.HIGH)  # Turn on Blue LED
                attempts = attempts + 1
              

                

def printinput(): #gets fingerprint scanner input 
       
    print("print input running")
    auth=0
    count = pickle.load(open("count.dat", "rb")) #read the authentication stage counter variable
    while True:
     
        if finger.read_templates() != adafruit_fingerprint.OK: #exception error handling 
            raise RuntimeError("Failed to read templates")
        if finger.count_templates() != adafruit_fingerprint.OK:
            raise RuntimeError("Failed to read templates")
        if finger.read_sysparam() != adafruit_fingerprint.OK:
            raise RuntimeError("Failed to get system parameters")
        if get_fingerprint(): #if nominally gotten a fingerprint result from scanner 
            print("Detected #", finger.finger_id, "with confidence", finger.confidence) #printing info regarding the print 
            
            
            if count==0:  #if handling first stage of authentication (count==0) then return to main upon success rather than unlocking 
                print("First Stage: Fingerprint Authorised")
                finger_ID_stage_one = finger.finger_id #Getting the scanned print's ID from the scanner and storing as variable
                pickle.dump(finger_ID_stage_one, open("finger_ID_stage_one.dat", "wb")) #writing this to file
                count=1 #set the authentication stage counter to 1, to indicate stage one has been completed 
                pickle.dump(count, open("count.dat", "wb")) #write this to file 

                GPIO.output(20, GPIO.HIGH) #Blue LED on
                GPIO.output(21, GPIO.LOW) #Red LED off    
            
                return True #exit loop and return to main execution flow to enable next stage
            
            else: #if count not ==0, i.e., if stage two authentication is occuring
                finger_ID = pickle.load(open("finger_ID_stage_one.dat", "rb")) #reading stage one finger ID
                if finger.finger_id != finger_ID: #proceed so long as a different fingerprint is being used 
                   
                    print("Second Stage: Fingerprint Authorised")
                    unlock_type="Unlocking by Finger"
                    
                    print(finger_ID) #print current finger ID
                    print(finger_database)#print users/fingerprints database
                    user_s1=(finger_database.get(finger_ID))#get the name of the stage one fingerprint user, via users/fingerprints database
                    print(user_s1)
                    
                    finger_ID =finger.finger_id #get the fingerprint ID of the current (stage two) fingerprint user
                    user_s2=(finger_database.get(finger_ID))#get the name of the current (stage two) fingerprint user, via users/fingerprints database
                    print(user_s2)
                    
                    unlock(unlock_type, user_s1, user_s2) #call the unlock function
                    return True     #return to main execution flow
                else: #if scanned fingerprint is the same as the first 
                     print("Access denied - a different authorised user's finger must be scanned!")
                     GPIO.output(21, GPIO.HIGH)            # Turn on Red LED
                     GPIO.output(20, GPIO.LOW) #Turn off Blue LED
                     sleep(1)
                     GPIO.output(20, GPIO.HIGH) #Turn on Blue LED
                     GPIO.output(21, GPIO.LOW)  # Turn off Red LED

        else: #if fingerprint is not registered 
            print("Finger not found")
            print("Access Denied - Try Again")
            GPIO.output(21, GPIO.LOW)            # Turn off Red LED
            GPIO.output(20, GPIO.LOW) #Turn off Blue LED
            if count!=1: #if performing stage one authentication
                sleep(1)
            GPIO.output(21, GPIO.HIGH)  # Turn on Red LED
            sleep(1)
            if count==1: #if perofmring stage two authentication
                GPIO.output(21, GPIO.LOW)  # Turn off Red LED
                GPIO.output(20, GPIO.HIGH) #Turn on Blue LED
            
          
def main(): #main execution function 

    pool = Pool(100) #setup the multiprocessing pool
    def check(x): #callback function. "x" is the returned value from whichever function below is being executed by multiprocessing
      
      if x==1: #if True has been returned 
       
        pool.terminate() #terminate the multiprocessing pool of function(s)
            
      
        print("pool terminate command ran")
        

    if printinput(): #stage one via fingerprint scan. If authorised, continue
    #if otpinput(): #comment above line and uncomment this one to change to personal code as first stage     
        print("Input OTP Code, or Scan Second Authorised Fingerprint..")
        #print("Input Second User's Personal Code")#comment above line and uncomment this one to change to personal code as first stage
        pool = Pool(100) #setup the multiprocessing pool
        sleep(1)
        
        
        pool.apply_async(printinput, callback=check) #execute the fingerprint input function via multiprocessing. Run above callback function upon function exit
        pool.apply_async(otpinput, callback=check) #execute the keypad code input function via multiprocessing. Run above callback function upon function exit
        pool.close()
        pool.join()

#script start 
print("System Ready")
#print("Enter Personal Code") #uncomment for personal code as first stage
print("Scan Authorised Print")
GPIO.output(21, GPIO.HIGH) #Turn on Red LED
main()   #execute main function 


       
         
