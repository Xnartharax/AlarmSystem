'''
Created on 06.08.2018

@author: Xnartharax
'''
import tkinter
import sqlite3 as sql
import time
from tkinter import *
import threading
conn=sql.connect("../coredata.db")
c=conn.cursor()
c.execute('select alarmoftheday from alarms where approved is not null and sendtoserver=0 order by timer desc')
print(c.fetchall())