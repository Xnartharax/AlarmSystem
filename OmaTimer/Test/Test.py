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
    server_address="localhost"
    c.execute('select approved from alarms where timer={}'.format(timer))
    approved=10
    r=post("http://{}/cgi-bin/server.cgi".format(server_address,), data={'approved':approved,'alrmdate':timer})
    print(r)
sendtoserver(10)
    