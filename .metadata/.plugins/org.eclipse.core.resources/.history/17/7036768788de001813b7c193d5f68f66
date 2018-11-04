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
    post("{}/cgi-bin/server.cgi".format(server_address,), data={'approved':approved,'alrmdate':timer})
    c.execute('update alarms set sendtoserver=1 where timer=?',timer)
    conn.commit()
def newalarms():
    c.execute('select * from standard_alarms order by hour desc')
    standard_alarms=c.fetchall()
    c.execute('select * from alarms where approved is null order by timer desc')
    unapproved=c.fetchall()[0][1]
    localtime=list(time.localtime())
    c.execute('select alarmoftheday from alarms where unapproved is not null and senttoserver=0 order by timer desc')
    lastalarm=c.fetchall()[0][0]
    if lastalarm==len(standard_alarms):
        alarmoftheday=0
    else:
        alarmoftheday=lastalarm
    i=standard_alarms[alarmoftheday] 
    localtime[3]=i[1]
    localtime[4]=i[2]        
    new_timer=time.mktime(tuple(localtime))

    while unapproved>new_timer:
            new_timer+24*3600
    q=[]
    q.append(alarmoftheday)
    q.append(new_timer)
    c.execute('insert into alarms values(?,?,NULL,0)',q)
    conn.commit()
def check_for_alarms(): 
    c.execute('select approved from alarms where approved is not null and sendtoserver=0')
    if len(c.fetchall())==1:
        newalarms()
        sendtoserver(c.fetchall[0][0])
def mainloop():
    while True:
        check_for_alarms()

        c.execute('select loop_duration from standard_settings')

        time.sleep(c.fetchone()[0])
mainloop()
