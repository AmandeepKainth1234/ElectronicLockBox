"""
Main script for the Electronic Lock Box system. Developed by Amandeep Kainth of the James Watt School of Engineering, University of Glasgow.
Developed for a Final Year MEng Degree Project. 
Licensed under a MIT License, MIT_LICENSE_MAIN, which can be found in the main repository.
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
import requests, sys #for SMS
# for sms Using Lxml to speed up faster parsing, Lxml is used also for writing xml
from lxml import etree, objectify #for SMS


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


try: #exception error handling if GPS module not connected or has an error. Allows system to still operate
    gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) #begin data stream from GPS
except:
    pass 
    
  
    
totp = pyotp.TOTP('BFRQ4P7YBV563YJE') #defining secret key for pyotp, which handles the otp generation 

try: #exception error handling if Finger Print module not connected or has an issue . Allows system to still operate (using codes for both authentication stages)
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
*
***************************************************************************************
"""

#SMS functionality follows below

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
        
#End of SMS functionality 

"""
***************************************************************************************
*    Source code citation for adapted Adafruit code snippets for Fingerprint Scanner
*    Used in lines: 145-153,375-382
*    Title: Adafruit_CircuitPython_Fingerprint
*    Author: Adafruit 
*    Date: 04/10/2022
*    Code version: 2.2.10
*    Availability: GitHub: https://github.com/adafruit/Adafruit_CircuitPython_Fingerprint
*    License: MIT License. See file MIT_LICENSE_ADAFRUIT within the main repository.
*
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
      keys = matrix_keypad.pressed_keys #using adafruit_matrixkeypad driver 
      if keys:                   #beep buzzer upon button press
        GPIO.output(9, GPIO.HIGH) 
        time.sleep(0.1)
        GPIO.output(9, GPIO.LOW)
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

  
  y=0
  z=0
  try:
      while y!=1 and z!=10:#repeat until the first non zero result until a maximum of 11 times
        report = gpsd.next() #get report of gps data from gpsd daemon
        lat = str(getattr(report,'lat',0.0))#get latitude from the lat attribute of the GPS report object
        z=z+1
        
        if lat !="0.0": #proceed only upon a non zero latitude. Zero latitude inidcates no GPS location. Can occur periodically in stream as well as when no signal.
            y=1 #Indicates that a location has been found; preventing the while loop from executing again
            
            lat = str(getattr(report,'lat',0.0))  #get latitude from the lat attribute of the GPS report object
            lon = str(getattr(report,'lon',0.0))  #get longnitude from the lat attribute of the GPS report object
            location= f"https://www.google.co.uk/maps/place/{lat},{lon}" #compile a Google Maps link 
            print(location)
            log(unlock_type, location, user_s1,user_s2) #call the log function
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
      log(unlock_type, location, user_s1, user_s2, capture_date, capture_time) #call the log function

  
def log(unlock_type, location, user_s1, user_s2, capture_date=None, capture_time=None):

    current_date = date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    data = [current_date,current_time, unlock_type, location, user_s1, user_s2, capture_date, capture_time]

    with open('log.csv', 'a') as f_object:
     
        
        writer_object = writer(f_object)
     
      
        writer_object.writerow(data)
     
        f_object.close()  
    message = "Timestamp:" + " " + str(current_date)+ " " + str(current_time) + " " + "Unlock Mode:" + str(unlock_type) + " "+ "Location:" +str(location) + " "+"Location Capture Date:" + str(capture_date)  +" "+"Location Capture Time:" +" "+str(capture_time) +" "+"User_s1:" + str(user_s1) +" "+"User_s2:" + str(user_s2) 
 
    print(message)
    
    send_sms('07459288940',message )
    
def unlock(unlock_type, user_s1,user_s2):

    arming=0
    pickle.dump(arming, open("armingStoringFile.dat", "wb"))
    
    GPIO.output(20, GPIO.LOW)  # Turn off Blue LED
    GPIO.output(21, GPIO.LOW)  # Turn off Red LED
    GPIO.output(16, GPIO.HIGH)  # Turn on Green LED
    GPIO.output(14, GPIO.LOW)  # Turn on
    sleep(5)  # Sleep for 5 seconds
    GPIO.output(14, GPIO.HIGH)  # Turn off
    GPIO.output(16, GPIO.LOW)  # Turn Off Green LED
  
    sleep(0.1)
    arming=1
    pickle.dump(arming, open("armingStoringFile.dat", "wb"))
    tracking(unlock_type, user_s1, user_s2) 
    global terminate
    terminate=1


    
def otpinput():
    with open('data.p', 'rb') as fp:
        my_dict = pickle.load(fp)
    print("otpinput test running")
    count = pickle.load(open("count.dat", "rb"))
    correct=0
    
    attempts=0
    while correct==0:
        if count==0:
            
            
            
            
            print("Input personal code")
            #code=input()
            #code=int(1366)
            code=keypad()
          
            attempts_personal = 0
            print("t2")  
            while attempts_personal <3:
                print("t3")
                if code in my_dict.keys():
                    print("t4")
                    count=1
                    pickle.dump(count, open("count.dat", "wb"))

                    print("First code correct")
                    #print(my_dict.get(code))#will get used for logging function
                    b=(my_dict.get(code)) #get the name of user for a given inputted code
                    correct=1
                    return True
        else:   
            print("t5")
            code=keypad()#run the keypad1 function, and take the returned value and assign to the variable called code. Important to avoid global variables.
            print("oats")
            sleep(1)
            #code=input("A")
            #code=750920
            if totp.verify(code) == 1:
              print("t6")  
              print("Second Stage: 2FA PIN Accepted - Unlocking")
              code_input="" 
              correct=1
              #event.set()
              GPIO.output(21, GPIO.LOW)
              unlock_type="Unlocking by OTP"
              user_s2="N/A"
              
              with open('data1.p', 'rb') as fp:
                my_dict = pickle.load(fp)
                
              finger_ID = pickle.load(open("finger_ID_stage_one.dat", "rb")) #stage one finger ID
              user_s1=(my_dict.get(finger_ID))
              unlock(unlock_type,user_s1,user_s2)
              return True
              return terminate  
            else:
              print("t7")
              if attempts < 2:
                  print("t8")
                  GPIO.output(20, GPIO.LOW)  # Turn off Blue LED
                  print("Code is incorrect. Access Denied - Try Again.")
                  GPIO.output(21, GPIO.HIGH)  # Turn on Red LED
                  sleep(0.5)
                  GPIO.output(21, GPIO.LOW)  # Turn off Red LED
                  input = ""
                  GPIO.output(20, GPIO.HIGH)  # Turn on Blue LED
                  attempts = attempts + 1
              else:
                  print("t9")
                  print("System Locked Out for 5 minutes after Three Failed PIN Attempts! Control alerted!")
                  GPIO.output(20, GPIO.LOW)  # Turn off Blue LED
                  while True:
                    GPIO.output(21, GPIO.HIGH)  # Turn on Red LED
                    sleep(0.5)
                    GPIO.output(21, GPIO.LOW)  # Turn on Red LED
            print("t89")    

                

def printinput():
    global count 
    print("print input running")
    auth=0
    count = pickle.load(open("count.dat", "rb"))
    while True:
        print("t12")
        if finger.read_templates() != adafruit_fingerprint.OK:
            raise RuntimeError("Failed to read templates")
        if finger.count_templates() != adafruit_fingerprint.OK:
            raise RuntimeError("Failed to read templates")
        if finger.read_sysparam() != adafruit_fingerprint.OK:
            raise RuntimeError("Failed to get system parameters")
        if get_fingerprint():
            print("Detected #", finger.finger_id, "with confidence", finger.confidence) ###
            
            
            if count==0:
                print("First Stage: Fingerprint Authorised")
                status= "First Stage: Fingerprint Authorised"
                finger_ID_stage_one = finger.finger_id #Getting the scanned print's ID from the scanner and storing this
                pickle.dump(finger_ID_stage_one, open("finger_ID_stage_one.dat", "wb"))
                count=1
                pickle.dump(count, open("count.dat", "wb"))

                GPIO.output(20, GPIO.HIGH) #Blue on
                GPIO.output(21, GPIO.LOW) #Red off    
                print(count)
                
                return True
            
            else:
                finger_ID = pickle.load(open("finger_ID_stage_one.dat", "rb")) #stage one finger ID
                if finger.finger_id != finger_ID:
                    global disarm
                    disarm =1
                    print("Second Stage: Fingerprint Authorised")
                    status="Second Stage: Fingerprint Authorised"
                    unlock_type="Unlocking by Finger"
                    
                    with open('data1.p', 'rb') as fp:
                        finger_database = pickle.load(fp)
                        
                    print(finger_ID)
                    print(finger_database)
                    user_s1=(finger_database.get(finger_ID))
                    print(user_s1)
                    
                    finger_ID =finger.finger_id #current (s2) finger ID
                    user_s2=(finger_database.get(finger_ID))
                    print(user_s2)
                    
                    unlock(unlock_type, user_s1, user_s2)
                    return True     
                else:
                     print("Access denied - a different authorised user's finger must be scanned!")
                     GPIO.output(21, GPIO.HIGH)            # Turn on Red LED
                     GPIO.output(20, GPIO.LOW) #blue
                     sleep(1)
                     GPIO.output(20, GPIO.HIGH) #blue
                     GPIO.output(21, GPIO.LOW)  # Turn off Red LED

        else:
            print("Finger not found")
            print("Access Denied - Try Again")
            GPIO.output(21, GPIO.LOW)            # Turn off Red LED
            GPIO.output(20, GPIO.LOW) #blue
            if count!=1:
                sleep(1)
            GPIO.output(21, GPIO.HIGH)  # Turn on Red LED
            sleep(1)
            if count==1:
                GPIO.output(21, GPIO.LOW)  # Turn off Red LED
                GPIO.output(20, GPIO.HIGH) #blue
            
           
def test():
    x=1
    for x in range (2):
        print("oats123")
        sleep(10)
    return True
def main():
    pool = Pool(100)

    pool = Pool(100)
    def check(x):
      print(x)
      if x==1:
       
        pool.terminate()
            
      
        print("pool terminate command ran")
        
    pool.apply_async(printinput, callback=check)
    #pool.apply_async(otpinput, callback=check)
    pool.close()
    pool.join()

        
    print("Awaiting Second Authorised Fingerprint, or OTP Code")
    print("Input Code, or Scan Second Authorised Fingerprint..")
    pool = Pool(100)
    sleep(1)
    
    
    pool.apply_async(printinput, callback=check)
    pool.apply_async(otpinput, callback=check)
    pool.close()
    pool.join()
    print("oats2")


def alarm():

    def signal_handler(sig, frame):
        GPIO.cleanup()
        sys.exit(0)
    def contact_callback(channel):
        global disarm
        if disarm==0:
            
            print(" Alarm!")
    if __name__ == '__main__':
        GPIO.setmode(GPIO.BCM)
        global disarm
        if disarm ==0:
            GPIO.add_event_detect(11, GPIO.RISING,
                    callback=contact_callback, bouncetime=100)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.pause()   

   
print("System Ready - Demo V1.6")
print("Scan Authorised Print")
GPIO.output(21, GPIO.HIGH)

main()      


       
         
