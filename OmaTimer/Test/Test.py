'''
Created on 06.08.2018

@author: Xnartharax
'''
import sqlite3 as sql

import time

import tkinter
conn=sql.connect("../coredata.db")
c=conn.cursor()
root=tkinter.Tk()
window=tkinter.Frame(root, width=320, height=240)
class Main_Button(tkinter.Button):
    def counter_Button(self):
        #displays the next ALarm and the time remaining
        c.execute('select timer from alarms where approved is null order by timer asc' )

        x=c.fetchall()[0][0]

        q=list(time.localtime(x))

        gg=str(q[3])+":"+str(q[4])

        def refresh():
            #refreshes the button every second
            
            y=time.mktime(time.localtime())

            z=time.gmtime(x-y)

            self.config(text=gg+"\n"+str(z[3])+":"+str(z[4])+":"+str(z[5]))

            self.after(1000, refresh)

            

        refresh()
        window.mainloop() 
window.grid()
CounterButton=Main_Button(window)   
CounterButton.grid()
CounterButton.counter_Button()