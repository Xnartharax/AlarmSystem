import sqlite3 as sql
import time
import tkinter
window=tkinter.Tk()
CounterButton=tkinter.Button(padx=320,pady=240)
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
    NewButton=OldButton.copy()
    OldButton.destroy()
    AlarmNow=tkinter.Button(window,pady=80, padx=160, text="Alarm ausloesen", background="red",justify="left")
    AlarmPlusAnHour=tkinter.Button(window,pady=80,padx=160,text="Alarm 1 Stunde verschieben", justify="left",command=AlarmplusHours(1))
    Alarmplus1day=tkinter.Button(window,pady=80,padx=160,text="Alarm 1 Tag verschieben",justify="left", command=AlarmplusHours(24))
    NextAlarm=tkinter.Label(window,pady=240, padx=160, justify="left")
    def newalarm(label):
        while True :
            try:  
                c.execute('select timer from alarms where approved is null order by timer asc')
                x=time.ctime(c.fetchall[0][0])
                label.configure(text=x)
                time.sleep(0.1)
            except:
                break
    NextAlarm.pack()
    newalarm(NextAlarm)
    Alarmplus1day.pack()
    AlarmPlusAnHour.pack()
    AlarmNow.pack()
    window.mainloop()
    time.sleep(60)
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