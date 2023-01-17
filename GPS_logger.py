#GPS Logger script for the Electronic Lock Box system. Developed by Amandeep Kainth of the James Watt School of Engineering, University of Glasgow.
#Developed for a Final Year MEng Degree Project. 

#  Use Policy: The code provided here, apart from the segments indicated within the respective files /
#  is wholly the author's work. It may not be used or shared for any purpose other than viewing /
#  unless explicit permission has been given to you

#GPS drivers (https://gpsd.gitlab.io/gpsd/client-howto.html)
from gps import *

import time, inspect
from csv import writer
from datetime import datetime
from datetime import date   

#Begin GPS datasteam from GPSD driver (https://gpsd.gitlab.io/gpsd/client-howto.html)
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)


def logging():

  #Logging function
  
  while True: 
    report = gpsd.next() #get report of gps data from gpsd daemon
    lat = str(getattr(report,'lat',0.0))#get lat
    if lat !="0.0": 
        #Proceed only upon a non zero latitude. Zero latitude indicates no GPS location 
        #Can occur periodically in stream as well as when no signal.
        
        #Get latitude & longnitude from the lat attribute of the GPS report object
        lat = str(getattr(report,'lat',0.0))
        lon = str(getattr(report,'lon',0.0))
        #Compile a Google Maps link 
        locationlink= f"https://www.google.co.uk/maps/place/{lat},{lon}"
        
        
        current_date = date.today()
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        #Compile packet for being written to log
        List = [current_date, current_time, locationlink]
        #Open GPS Log CSV file for appending to
        with open('GPSlogger.csv', 'a') as file:
     
          # Create writer method for opened file   
          writer_object = writer(file)
     
          # Write new row with packet created above
          writer_object.writerow(List)
     
          file.close()  
          
          time.sleep(20)
          

          
  
logging()  
    
 



