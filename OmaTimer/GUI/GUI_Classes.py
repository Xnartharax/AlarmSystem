#usr/bin/python3
'''
Created on 15.09.2018

@author: Xnartharax
'''

import tkinter
import sqlite3 as sql
import time
from tkinter import N, W, E, S
import threading
conn=sql.connect("../coredata.db")
c=conn.cursor()

class Main_Button(tkinter.Button):
    def counter_Button(self):
        #displays the next ALarm and the time remaining
        c.execute('select timer from alarms where approved is null and timer>{} order by timer asc '.format(str(time.mktime(time.localtime()))))

        x=c.fetchall()[0][0]
        print(x)
        q=list(time.localtime(x))
        
        gg=str(q[3])+":"+str(q[4])

        def refresh():
            while True:
                #refreshes the button every second
            
                y=int(time.mktime(time.localtime()))
            
                z=time.gmtime(x-y)
                
                if x-y>0:
                    print(x-y)
                    self.config(text=gg+"\n"+str(z[3])+":"+str(z[4])+":"+str(z[5]))
                else:
                    print(x-y)
                    self.config(text="Alarm")
            
                self.master.mainloop() 
                time.sleep(0.5)
        Refresher = threading.Thread(target=refresh)
        Refresher.start()
        Refresher.run()

        
        self.master.mainloop() 
class GUI():
    def __init__(self,root):
        self.root=root
        self.Elements=[]
    def add_Element(self, conf):
        self.Elements.append(conf)
    def grid_all_Elements(self):
        for i in self.Elements:
            if len(i)==5:
                i[0].grid(row=i[1],column=i[2],rowspan=[3],columnspan=[4],sticky=N+E+S+W)
            elif len(i)==3:
                i[0].grid(row=i[1],column=i[2],sticky=N+E+S+W)
        #self.root.mainloop()
    def grid_forget_all(self):
        for i in self.Elements:
            i[0].grid_forget()  
        #self.root.mainloop()
    def get_Element(self,index):
        return self.Elements[index] 
def SwitchGUI(master, oldGUI, newGUI, timetoswitchback,switchback, label):
    
    #switches the GUI to the settings mode
    def switch_back():
        
        
        def switching_back():
        #switches back to the main button
            print("switch back")
            newGUI.grid_forget_all()
            oldGUI.grid_all_Elements()
        
        if switchback:
            print("initialsing switch back")
            label.after(timetoswitchback*1000,switching_back)
            
    print("switch")
    oldGUI.grid_forget_all()
    newGUI.grid_all_Elements()
    thread=threading.Thread(group=None, target=switch_back, name="backswitch")
    thread.start()
    thread.run()
    thread.join(0)
    newalarm(label)
    master.mainloop()
    
        
        

    
    #grid the menu 
    
def newalarm(label):
        print("newalarm")
        def count():
            while True:
                #displays the next alarm in a label next to the buttons
                #fetches timestamp of the nextalarm and converts it into readable text
                c.execute('select timer from alarms where approved is null order by timer asc')
                x=time.ctime(c.fetchall()[0][0])
                label.configure(text=x)
            
                label.after(1000, count)
                label.master.mainloop()

        Refresher=threading.Thread(target=count)
        Refresher.start()
        Refresher.run()      
        