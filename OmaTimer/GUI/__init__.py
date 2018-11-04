#usr/bin/python3
import sqlite3 as sql
import time
import threading
import tkinter
import GUI_Classes
from tkinter import *
import requests
import asyncio
#setup for window and frame for the fixed size
root=tkinter.Tk()

root.wm_attributes("-fullscreen", True)
window=tkinter.Frame(root, width=320, height=240)
window.grid_propagate(False)
window.grid(sticky=S+W+N+E)
MainGUI=GUI_Classes.GUI(root)
MenuGUI=GUI_Classes.GUI(root)

#main Button
CounterButton=GUI_Classes.Main_Button(window, font=("Helvetica",40),command=lambda:GUI_Classes.SwitchGUI(root, MainGUI, MenuGUI, 10, True,NextAlarm),padx=50,pady=50)

#menu Buttons and labels
AlarmNow=tkinter.Button(window, text="Alarm ausloesen", background="red",command= lambda: AlarmNow(),padx=30,pady=30)   
AlarmPlusAnHour=tkinter.Button(window,text="Alarm 1 Stunde verschieben",command=lambda: AlarmplusHours(1),padx=30,pady=30)    
Alarmplus1day=tkinter.Button(window,text="Alarm 1 Tag verschieben",command=lambda: AlarmplusHours(24),padx=30,pady=30)
NextAlarm=tkinter.Label(window)   
#connects to the main DB
conn=sql.connect("../coredata.db")
c=conn.cursor()


MainGUI.add_Element([CounterButton, 0, 0, 3, 2])
MenuGUI.add_Element([AlarmNow, 0,1])
MenuGUI.add_Element([AlarmPlusAnHour, 1,1])
MenuGUI.add_Element([Alarmplus1day, 2,1])
MenuGUI.add_Element([NextAlarm,0,0])
def AlarmNow():
    c.execute('select server_address from standard_settings ')
    server_address=c.fetchone()
    r=requests.post("{}/cgi-bin/emergency.cgi".format(server_address,), data={'timer':time.mktime(time.localtime())})


def AlarmplusHours(Hours):
     
    c.execute('select timer from alarms where approved is null order by timer asc')

    alarms=c.fetchall()

    for i in alarms:

        seconds=Hours*3600

        x=i[0]

        y=x+seconds

        q=[y,x]

        c.execute('update alarms set timer=? where timer=?',q)

        conn.commit()

#sets up the main Button
MainGUI.grid_all_Elements()

CounterButton.counter_Button()
root.mainloop()
def alarm(window, MainButton):

    MainButton.config(background="green", command=lambda: Alarmconfirmed(MainButton))
    
    window.mainloop()
        

def Alarmconfirmed(MainButton):    

    x=time.mktime(time.localtime())
    y=[x,x]
    c.execute('update alarms set approved=? where timer<? and approved is null',y)
    conn.commit()
    MainButton.config(command=lambda:GUI_Classes.SwitchGUI(root, MainGUI, MenuGUI, 10, True,NextAlarm))
    MainButton.config(background="white")
    
def check_for_alarm():

    c.execute('select timer from alarms where approved is null order by timer asc')

    timer=c.fetchall()

    c.execute('select timebefore from standard_alarms join alarms on (alarmoftheday=standard_alarms.Id)')

    timeBefore=c.fetchone()[0]
    

    if timer[0][0]-timeBefore<time.mktime(time.localtime()):

        alarm(root, CounterButton)
    if timer[0][0]<time.mktime(time.localtime()):
        
        notApprovedAlarmHandler()
def notApprovedAlarmHandler():
    pass
def mainloop():

    while True:

        check_for_alarm()

        c.execute('select loop_duration from standard_settings')

        time.sleep(c.fetchone()[0])

mainloop()
