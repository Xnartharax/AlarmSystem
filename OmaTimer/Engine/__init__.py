import sqlite3 as sql
import time
conn=sql.connect("../coredata.db")
c=conn.cursor()
c.execute('select * from standard_alarms')
print("standard alarms "+str(c.fetchall()))
alarmcounter=0
def sendtoserver(approvedtimestamp):
    pass
def new_alarms(alarmcounter):
    
        print(time.asctime(time.localtime()))
        
        c.execute('select * from standard_alarms')
        y=c.fetchall()
        c.execute('select timer from alarms where approved is null order by timer asc')
        
        unapprovedtimers=c.fetchall()
        
        for i in y:
            z=list(time.localtime())
            z[3]=i[1]
            z[4]=i[2]
            if len(unapprovedtimers)>0:
                if unapprovedtimers[0][0]<time.mktime(tuple(z)):
                    q=[]
                    q.append(i[0])
                
                    q.append(time.mktime(tuple(z)))
            
                    q.append(alarmcounter)
                    c.execute('Insert into alarms values(?,?,NULL,?,0)',q)
                    alarmcounter+=1
                    conn.commit()
            
            
            
def mainloop():
    while True:
        c.execute('select loop_duration from standard_settings')
        time.sleep(c.fetchone()[0])
        c.execute('select approved from alarms where sendtoserver=0 and approved is not null') 
        x=c.fetchall()  
        if len(x)>0:
            new_alarms(alarmcounter)
            sendtoserver(x[0][0])
        

