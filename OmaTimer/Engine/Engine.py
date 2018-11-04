#usr/bin/python3
'''
Created on 06.08.2018

@author: Xnartharax
'''
import sqlite3 as sql
import time

from requests import *
conn=sql.connect("../coredata.db")

c=conn.cursor()
def sendtoserver(timer):
    c.execute('select server_address from standard_settings ')
    server_address=c.fetchone()
    c.execute('select approved from alarms where timer=?',timer)
    approved=c.fetchone()
    r=post("{}/cgi-bin/server.cgi".format(server_address,), data={'approved':approved,'alrmdate':timer})
    try:
        if r.json()== [approved, timer]:
            c.execute('update alarms set sendtoserver=1 where timer=?',timer)
            conn.commit()
        else:
            c.execute('update alarms set sendtoserver=2 where timer=?',timer)
            conn.commit()
    except:
        print("no such alarm")
def newalarms():
    print("newalarms")
    #fetching alarm information
    c.execute('select * from standard_alarms order by hour desc')
    standard_alarms=c.fetchall()
    #fetching unapproved alarms
    c.execute('select timer from alarms where approved is null order by timer desc')
    unapproved=c.fetchall()[0][0]
    #fetching alarmoftheday of last approved alarm    
    c.execute('select alarmoftheday from alarms where approved is not null and sendtoserver=0 order by timer desc')
    if len(c.fetchall())>0:
        lastalarm=c.fetchall()[0][0]
    
        if lastalarm==len(standard_alarms):
            alarmoftheday=0
        else:
            alarmoftheday=lastalarm+1
    else:
        alarmoftheday=1
    i=standard_alarms[alarmoftheday-1] 
    
    localtime=list(time.localtime())
    localtime[3]=i[1]
    localtime[4]=i[2]        
    new_timer=time.mktime(tuple(localtime))
    
    while unapproved>new_timer:
        
        #pushing next timer after next unapproved alarm
        new_timer=new_timer+24*3600
            
    #writing the alarm in db     
    q=[alarmoftheday,new_timer]  
    c.execute('insert into alarms values(?,?,NULL,0)',q)
    conn.commit()
    print("end new alarms")
def check_for_approved_alarms(): 
    c.execute('select approved from alarms where approved is not null and sendtoserver=0')
    if len(c.fetchall())==1:
        newalarms()
        sendtoserver(c.fetchall[0][0])

def mainloop():
    print("mainloop")
    while True:
        print("new loop")
        check_for_approved_alarms()

        c.execute('select loop_duration from standard_settings')

        time.sleep(c.fetchone()[0])
        print("end loop")
newalarms()
mainloop()
