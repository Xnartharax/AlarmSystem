'''
Created on 14.07.2018


'''
import time
import sqlite3 as sql
conn=sql.connect("../coredata.db")
c=conn.cursor()
def midnight(alarmcounter):
    if time.localtime()[3]==24&time.localtime()[4]==0:
        print(time.asctime(time.localtime()))
        x=list(time.localtime())
        c.execute('select * from standard_alarms')
        y=c.fetchall
        for i in y:
            q=[]
            q.append(i)
            q.append(alarmcounter)
            c.execute('Insert into alarms values(?,?,?)',q)
            alarmcounter+=1
print(time.localtime())
            