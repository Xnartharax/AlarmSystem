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
    r=post("{}/cgi-bin/server.cgi".format(server_address,), data={'approved':approved,'alrmdate':timer})
    try:
        if r.json()== [approved, timer]:
            c.execute('update alarms set sendtoserver=1 where timer=?',timer)
            conn.commit()
        else:
            c.execute('update alarms set sendtoserver=2 where timer=?',timer)
            conn.commit()
    except:
        print("no such alarm")


def check_for_approved_alarms(): 
    c.execute('select approved from alarms where approved is not null and sendtoserver=0')
    if len(c.fetchall())==1:
        newalarms()
        for send_please in [raw[0] for raw in c.fetchall()]
            sendtoserver(send_please)
class Engine:

    def __init__(self, db_path):
        self.conn= Connection(db_path)


    def mainloop():

        while True:

            check_for_approved_alarms()



            time.sleep(c.fetchone()[0])


    def new_alarms(self):

        standard_alarms = self.conn.get_unapproved_alarms()
        for standard_alarm in standard_alarms:
            self.conn.insert_new_alarm(self.make_new_alarm(standard_alarm))

    def make_new_alarm(self,hour, minute):

        timer=list(time.localtime())
        timer[3]=hour
        timer[4]=minute
        seconds=time.mktime(tuple(timer))
        unnapproved = self.conn.get_unapproved_alarms()




class Connection:

    def __init__(self, db_path):


        self.conn = sql.connect(db_path)
        self.server_url = self.get_standard_settings()[1]

    def send_approved_alarms(self, timer ,approved):

        r=post(self.server_url+'/cgi-bin/approved.py', data={'timer':timer, 'approved':approved})
        if r.status_code == 200:
            self.conn.execute('''update alarms set sendtoserver=3 where timer=?''', [timer])
        else:
            self.conn.execute('''update alarms set sendtoserver=2 where timer=?''', [timer])
        self.conn.commit()

    def send_new_alarms(self, timer):

        r = post(self.server_url + '/cgi-bin/new_alarm.py', data={'timer': timer})
        if r.status_code == 200:

            self.conn.execute('''update alarms set sendtoserver=1 where timer=?''', [timer])

        else:
            self.conn.execute('''update alarms set sendtoserver=0 where timer=?''', [timer])
        self.conn.commit()

    def get_unsent_approved_alarms(self):

        unsent = self.conn.execute('''select timer, approved from alarms where sendtoserver != 3 and approved is not NULL''')
        return unsent

    def get_unsent_new_alarms(self):

        unsent = self.conn.execute('''select timer from alarms where sendtoserver = 0''')
        return [alarm[0] for alarm in unsent]

    def get_unapproved_alarms(self):

        unapproved = self.conn.execute('''select timer from alarms where approved is NULL order by timer asc''')
        return [alarm[0] for alarm in unapproved]

    def insert_new_alarm(self, timer):

        self.conn.execute('''insert into alarms values(?, NULL, 0)''', [timer])
        self.conn.commit()

    def get_standard_settings(self):
        settings=self.conn.execute('''select * from stanard_settings''')
        return settings[0]

    def get_standard_settings(self):

        alarms = self.conn.execute('''select * from stanard_alarms''')
        return alarms