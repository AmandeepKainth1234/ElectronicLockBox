#os is used to run terminal commands 
import os
import datetime

#Assign current timestamp to variable 
e = datetime.datetime.now()

import subprocess
import pickle
import calendar



##For March  ***********************************************************************************

#Get last Sunday in March 
last_sunday = max(week[-1] for week in calendar.monthcalendar(year, 3)) 

#Compile timestamp of March time adjustment (i.e., when it needs to happen) 

#Date
x=('{}-{}-{:2}'.format(year, 3, last_sunday))

#Time
y= " 01:00:00"

#Full Timestamp 
z=x+y
#Need to put into time object format
z= datetime.strptime(z, '%Y-%m-%d %H:%M:%S') 

#Get the current time 
current=e.strftime("%Y-%m-%d %H:%M:%S")
#Need to put into time object format
current = datetime.strptime(current, '%Y-%m-%d %H:%M:%S') 

#Add one hour to the current time
adjusted_hour= int(e.strftime("%H"))+1 
adjusted_hour_str= str(adjusted_hour)  #Format as string 

#Get current date
current_date = e.strftime("%d/%m/%Y ")

#Get current minutes and seconds 
current_m_s = e.strftime(":%M:%S")

#Current timestamp + one hour 
master_stamp= current_date+adjusted_hour_str+current_m_s

#Read variable holding the year in which the previous october change occured
octyear = pickle.load(open("octyearStoringFile.dat", "rb"))

#Read variable which indicates if the March adjustment has happened already (in the current cycle)
marchdone = pickle.load(open("marchdoneStoringFile.dat", "rb"))

#Read variable which indicates if the October adjustment has happened already (in the current cycle)
octdone = pickle.load(open("octdoneStoringFile.dat", "rb"))

#The cycle runs from Oct-Oct

#Get the current year 
current_year= int(e.strftime("%Y"))


    

    
if current>z and marchdone!=1 and current_year>octyear:
    #If current timestamp is beyond the moment of the March adjustment.. 
    #and if March adjustment has not already happened...
    #and if the current year is greater than the year in which the October change occured,
    #(prevents correction repeating after the October change) 
    
    print("It is passed the last Sunday in March @1am")
    #Write the adjusted timstamp to the RTC
    os.system(f"sudo hwclock --set --date \"{master_stamp}\"")  
    
    #Write the newly adjusted timestamp to the system (from the RTC)
    os.system("sudo hwclock --hctosys") 

    #Set the October done variable to 0, i.e., October adjustment has not be done 
    #in this way, when timestamp next passes October, the October adjustment can be made

    octdone=0
    #Write it to file 
    pickle.dump(octdone, open("octdoneStoringFile.dat", "wb"))
    #Set the March done variable to 1, i.e., March adjustment has been done 
    marchdone=1
    #Write it to file
    pickle.dump(marchdone, open("marchdoneStoringFile.dat", "wb"))

    
    
##For October    *********************************************************************************

#Get last Sunday in October  
last_sunday = max(week[-1] for week in calendar.monthcalendar(year, 10)) 

#Compile timestamp of October time adjustment (i.e., when it needs to happen) 

#Date
x=('{}-{}-{:2}'.format(year, 10, last_sunday))

#Time
y= " 02:00:00"
z=x+y

#Need to put into time object format
z= datetime.strptime(z, '%Y-%m-%d %H:%M:%S') 

#Full Timestamp 
current=e.strftime("%Y-%m-%d %H:%M:%S")
#Need to put into time object format
current = datetime.strptime(current, '%Y-%m-%d %H:%M:%S') #need to put into time object format

#Remove one hour to the current time
adjusted_hour= int(e.strftime("%H"))-1 
#Format as string 
adjusted_hour_str= str(adjusted_hour)

#Get current date
current_date = e.strftime("%d/%m/%Y ")

#Get current minutes and seconds 

current_m_s = e.strftime(":%M:%S")

#Current timestamp + one hour 
master_stamp= current_date+adjusted_hour_str+current_m_s


#Read variable holding the year in which the previous october change occured
octyear = pickle.load(open("octyearStoringFile.dat", "rb"))

#Read variable which indicates if the March adjustment has happened
marchdone = pickle.load(open("marchdoneStoringFile.dat", "rb"))

#Read variable which indicates if the October adjustment has happened 
octdone = pickle.load(open("octdoneStoringFile.dat", "rb"))



if current>z and octdone!=1:
    #If current timestamp is beyond the moment of the October adjustment.. 
    #and the October adjustment has not already happened
    print("it is passed the last Sunday in October @2am")
    
    #Write the adjusted timstamp to the RTC
    os.system(f"sudo hwclock --set --date \"{master_stamp}\"") 
    
    #Write the newly adjusted timestamp to the system (from the RTC)
    os.system("sudo hwclock --hctosys")     

    #Set the October done variable to 1, i.e., October adjustment has been done 
    #Write this to file
    pickle.dump(octdone, open("octdoneStoringFile.dat", "wb"))
    #Set the March done variable to 0, i.e., March adjustment has not been done
    #in this way, when timestamp next passes March, and it's the next year, adjustment will occur 
    marchdone=0
    pickle.dump(marchdone, open("marchdoneStoringFile.dat", "wb"))
    octyear=int(e.strftime("%Y"))
    pickle.dump(octyear, open("octyearStoringFile.dat", "wb"))
