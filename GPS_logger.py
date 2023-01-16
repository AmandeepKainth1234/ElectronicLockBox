
from gps import *
import time, inspect
 
from csv import writer

from datetime import datetime
from datetime import date    
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)


def tracking():

 
  while True: #y!=1 and z!=5:#repeat until get first non zero result, otherwise attempt to get non zero result 5 times.
    report = gpsd.next() #get report of gps data from gpsd daemon
    lat = str(getattr(report,'lat',0.0))#get lat
    if lat !="0.0": #ignore results with 0 lat (which means all is 0)
        
        
        lat = str(getattr(report,'lat',0.0))
        lon = str(getattr(report,'lon',0.0))
        locationlink= f"https://www.google.co.uk/maps/place/{lat},{lon}"
        
    
        current_date = date.today()
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        List = [current_date, current_time, locationlink]
        with open('GPSlogger.csv', 'a') as f_object:
     
        
          writer_object = writer(f_object)
     
      
          writer_object.writerow(List)
     
          f_object.close()  
          
          time.sleep(20)
          
   
          
  
tracking()  
    
 



