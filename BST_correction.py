import os
import datetime
e = datetime.datetime.now()
import subprocess
from datetime import datetime
import pickle

import sys
import calendar
currentyear=int(e.strftime("%Y"))
year = currentyear
if len(sys.argv) > 1:
    try:
        year = int(sys.argv[-1])
    except ValueError:
        pass

##for march  #################################################################################################
    
last_sunday = max(week[-1] for week in calendar.monthcalendar(year, 3)) #get last sunday in march 
x=('{}-{}-{:2}'.format(year, 3, last_sunday))
y= " 01:00:00"
z=x+y

current=e.strftime("%Y-%m-%d %H:%M:%S")

adjusted_hour= int(e.strftime("%H"))+1 #add one hour to the current time
adjusted_stamp1 = e.strftime("%d/%m/%Y ")

adjusted_stamp2= str(adjusted_hour)

adjusted_stamp3 = e.strftime(":%M:%S")

master_stamp= adjusted_stamp1+adjusted_stamp2+adjusted_stamp3
print("March...")
print(master_stamp)

octyear = pickle.load(open("octyearStoringFile.dat", "rb"))
marchdone = pickle.load(open("marchdoneStoringFile.dat", "rb"))
octdone = pickle.load(open("octdoneStoringFile.dat", "rb"))
print(z)
z= datetime.strptime(z, '%Y-%m-%d %H:%M:%S') #need to put into time object format
print(current)
current_year= int(e.strftime("%Y"))
current = datetime.strptime(current, '%Y-%m-%d %H:%M:%S') #need to put into time object format
print(current_year)
print(octyear)
print(marchdone)
#current=int(current)
#z=int(z)
if current>z:

    print("year compare works")
if current>z and marchdone!=1 and current_year>octyear:
    print("it is passed the last sun in march @1am")
    os.system(f"sudo hwclock --set --date \"{master_stamp}\"")   
    os.system("sudo hwclock --hctosys")   
    octdone=0
    pickle.dump(octdone, open("octdoneStoringFile.dat", "wb"))
    marchdone=1
    pickle.dump(marchdone, open("marchdoneStoringFile.dat", "wb"))

    
    
###for oct    ############################################################################################

last_sunday = max(week[-1] for week in calendar.monthcalendar(year, 10)) #get last sunday in october 
x=('{}-{}-{:2}'.format(year, 10, last_sunday))
y= " 02:00:00"
z=x+y

current=e.strftime("%Y-%m-%d %H:%M:%S")
adjusted_hour= int(e.strftime("%H"))-1 #subtract one hour from the current time
adjusted_stamp1 = e.strftime("%d/%m/%Y ")

adjusted_stamp2= str(adjusted_hour)

adjusted_stamp3 = e.strftime(":%M:%S")

master_stamp= adjusted_stamp1+adjusted_stamp2+adjusted_stamp3
print("Oct..")
print(master_stamp)




 
marchdone = pickle.load(open("marchdoneStoringFile.dat", "rb"))
octdone = pickle.load(open("octdoneStoringFile.dat", "rb"))
octyear = pickle.load(open("octyearStoringFile.dat", "rb"))
z= datetime.strptime(z, '%Y-%m-%d %H:%M:%S') #need to put into time object format
current = datetime.strptime(current, '%Y-%m-%d %H:%M:%S') #need to put into time object format

print(z)
print (current)
current_year= int(e.strftime("%Y"))

if current>z and octdone!=1:
    print("it is passed the last sun in oct @2am")
    os.system(f"sudo hwclock --set --date \"{master_stamp}\"")  
    os.system("sudo hwclock --hctosys")       
    octdone=1
    pickle.dump(octdone, open("octdoneStoringFile.dat", "wb"))
    marchdone=0
    pickle.dump(marchdone, open("marchdoneStoringFile.dat", "wb"))
    octyear=int(e.strftime("%Y"))
    pickle.dump(octyear, open("octyearStoringFile.dat", "wb"))
