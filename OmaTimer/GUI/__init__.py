import sqlite3 as sql
import time
import tkinter
from tkinter import *
window=tkinter.Tk()
CounterButton=tkinter.Button(width=320,pady=240)
conn=sql.connect("../coredata.db")
c=conn.cursor()

def Alarmconfirmed(MainButton):
    
    x=time.mktime(time.localtime())
    y=[x,x]
    c.execute('update alarms set approved=? where timer<? and approved is null',y)
    conn.commit()
    MainButton.config(command=SwitchGUI(window, MainButton))
    MainButton.config(background="white")
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
def SwitchGUI(window, OldButton):
    NewButton=OldButton
    OldButton.destroy
    AlarmNow=tkinter.Button(window,pady=80, padx=160, text="Alarm ausloesen", background="red")
    AlarmPlusAnHour=tkinter.Button(window,pady=80,padx=160,text="Alarm 1 Stunde verschieben",command=AlarmplusHours(1))
    Alarmplus1day=tkinter.Button(window,pady=80,padx=160,text="Alarm 1 Tag verschieben",command=AlarmplusHours(24))
    NextAlarm=tkinter.Label(window,pady=240, padx=160, justify="left")
    def newalarm(label):
        def count():
              
                c.execute('select timer from alarms where approved is null order by timer asc')
                x=time.ctime(c.fetchall[0][0])
                label.configure(text=x)
                label.after(1000, count)
        count()   
    NextAlarm.grid(row=0,column=0,rowspan=3)
    newalarm(NextAlarm)
    Alarmplus1day.grid(row=0,column=1)
    AlarmPlusAnHour.grid(row=1,column=1)
    AlarmNow.grid(row=2,column=1)
    window.mainloop()
    time.sleep(20)
    NextAlarm.destroy()
    Alarmplus1day.destroy()
    AlarmPlusAnHour.destroy()
    AlarmNow.destroy()
    NewButton.pack()
    window.mainloop
def counter_label(label):
        c.execute('select timer from alarms where approved is null order by timer asc' )
        x=c.fetchall()[0][0]
        print(x)
                  
        q=list(time.localtime(x))

        gg=str(q[3])+":"+str(q[4])
        
        def count():
            
            y=time.mktime(time.localtime())
            z=time.gmtime(x-y)
            label.config(text=gg+"\n"+str(z[3])+":"+str(z[4])+":"+str(z[5]))
            label.after(1000, count)
            
        count()
def alarm(window, MainButton):
    
    
    MainButton.config(background="green", command=Alarmconfirmed(MainButton))
   
    
    
    
    
    
    
def check_for_alarm():
    c.execute('select timer from alarms where approve is null order by timer asc')
    x=c.fetchall()
    c.execute('select timebefore form standard_alarms, alarms where alarmoftheday=standard_alarms.Id')
    y=c.fetchone()
    if x[0][0]-y<time.mktime(time.localtime()):
        alarm()
def mainloop():
    while True:
        check_for_alarm()
        c.execute('select loop_duration from standard_settings')
        time.sleep(c.fetchone()[0])
mainloop()