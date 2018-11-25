#usr/bin/python3
'''
Created on 06.08.2018

@author: Xnartharax
'''
import sqlite3 as sql
import time

from requests import *




class Engine:

    def __init__(self, db_path):
        self.conn= My_connection(db_path)


    def mainloop(self):

        while True:

            if len(self.conn.get_unapproved_alarms()) == 0:
                self.new_alarms()

            unsent_approved = self.conn.get_unsent_approved_alarms()

            for unsent in unsent_approved:
                self.conn.send_approved_alarms(approved=unsent[1], timer=unsent[0])
            unsent_new = self.conn.get_unsent_new_alarms()
            for unsent in unsent_new:
                self.conn.send_new_alarms(unsent)

            sleep_duration = self.conn.get_standard_settings()[2]
            time.sleep(sleep_duration)

    def new_alarms(self):

        standard_alarms = self.conn.get_standard_alarms()
        for standard_alarm in standard_alarms:
            self.conn.insert_new_alarm(self.make_new_alarm(standard_alarm))

    def make_new_alarm(self,hour, minute):

        timer=list(time.localtime())
        timer[3]=hour
        timer[4]=minute
        seconds=time.mktime(tuple(timer))
        last_alarm = self.conn.get_last_alarm()
        while seconds <= last_alarm:
            seconds+=24*3600


class My_connection:

    def __init__(self, db_path):


        self.conn = sql.connect(db_path)
        self.server_url = self.get_standard_settings()[1]

    def send_approved_alarms(self, timer ,approved):

        r=post('http://'+self.server_url+'/cgi-bin/approved.py', data={'timer':timer, 'approved':approved})
        if r.status_code == 200:
            self.conn.execute('''update alarms set sendtoserver=3 where timer=?''', [timer]).fetchall()
        else:
            self.conn.execute('''update alarms set sendtoserver=2 where timer=?''', [timer]).fetchall()
        self.conn.commit()

    def send_new_alarms(self, timer):

        r = post('http://'+self.server_url + '/cgi-bin/new_alarm.py', data={'timer': timer})
        if r.status_code == 200:

            self.conn.execute('''update alarms set sendtoserver=1 where timer=?''', [timer]).fetchall()

        else:
            self.conn.execute('''update alarms set sendtoserver=0 where timer=?''', [timer]).fetchall()
        self.conn.commit()

    def send_emergeny(self, timer):

        r = post('http://'+self.server_url + '/cgi-bin/new_alarm.py', data={'timer': timer})
        while r.status_code !=200:
            r = post('http://' + self.server_url + '/cgi-bin/new_alarm.py', data={'timer': timer})

    def send_alive(self, timer):

        r = post('http://'+self.server_url + '/cgi-bin/alive.py', data={'timer': timer})

    def get_unsent_approved_alarms(self):

        unsent = self.conn.execute('''select timer, approved from alarms where sendtoserver != 3 and approved is not NULL''').fetchall()
        return unsent

    def get_unsent_new_alarms(self):

        unsent = self.conn.execute('''select timer from alarms where sendtoserver = 0''').fetchall()
        return [alarm[0] for alarm in unsent]

    def get_unapproved_alarms(self):

        unapproved = self.conn.execute('''select timer from alarms where approved is NULL order by timer asc''').fetchall()
        return [alarm[0] for alarm in unapproved]

    def insert_new_alarm(self, timer):

        self.conn.execute('''insert into alarms values(?, NULL, 0)''', [timer]).fetchall()
        self.conn.commit()

    def get_standard_settings(self):
        settings=self.conn.execute('''select * from standard_settings''').fetchall()
        return settings[0]

    def get_standard_alarms(self):

        alarms = self.conn.execute('''select * from standard_alarms''').fetchall()
        return alarms

    def get_last_alarm(self):

        alarms = self.conn.execute('''select timer from alarms order by timer asc''').fetchall()
        return alarms[0][0]


Engine('../coredata.db').mainloop()
