import urllib
import sqlite3 as sql
from kivy.network.urlrequest import UrlRequest


def post(url, data={}):
    urlstring = url
    query = urllib.parse.urlencode(data)
    r = UrlRequest(urlstring, req_body=query)
    r.wait()
    return r


class MyConnection:

    def __init__(self, db_path):
        self.conn = sql.connect(db_path, timeout=10)
        self.server_url = self.get_standard_settings()[1]

    def send_approved_alarms(self, timer, approved):

        r = post('http://'+self.server_url+'/cgi-bin/approved.py', data={'timer': timer, 'approved': approved, 'device_id': 1})
        if r.resp_status == 200:
            self.conn.execute('''update alarms set sendtoserver=3 where timer=?''', [timer]).fetchall()
            x = True
        else:
            print('connection not working')
            self.conn.execute('''update alarms set sendtoserver=2 where timer=?''', [timer]).fetchall()
            x = False
        self.conn.commit()
        return x

    def send_new_alarms(self, timer):

        r = post('http://'+self.server_url + '/cgi-bin/new_alarm.py', data={'timer': timer, 'device_id':1})
        if r.resp_status == 200:
            self.conn.execute('''update alarms set sendtoserver=1 where timer=?''', [timer]).fetchall()
            x = True
        else:
            print('connection not working')
            self.conn.execute('''update alarms set sendtoserver=0 where timer=?''', [timer]).fetchall()
            x = False
        self.conn.commit()
        return x

    def update_alarms(self, old_timer, new_timer):

        r = post('http://' + self.server_url + '/cgi-bin/change_alarm_time.py',
                 data={'new_timer': new_timer, 'old_timer': old_timer, 'device_id': 1})
        if r.resp_status == 200:
            self.conn.execute('''update alarms set sendtoserver=1 where timer=?''', [new_timer]).fetchall()
            x = True
        else:
            print('connection not working')
            x = False
            self.conn.execute('''update alarms set sendtoserver=5 where timer=?''', [new_timer]).fetchall()
        self.conn.commit()
        return x

    def send_emergeny(self, emergency_level):

        r = post('http://'+self.server_url + '/cgi-bin/emergency.py', data={'device_id': 1, 'emergency_level': emergency_level})

    def send_alive(self, timer):

        r = post('http://'+self.server_url + '/cgi-bin/alive.py', data={'timer': timer})
        if r.resp_status != 200:
            print('server not working')

    def get_unsent_approved_alarms(self):

        unsent = self.conn.execute('''select timer, approved from alarms where sendtoserver != 3 and approved is not NULL''').fetchall()
        return unsent

    def get_unsent_changed_alarms(self):

        unsent = self.conn.execute('''select timer from alarms where sendtoserver = 5''').fetchall()
        return [alarm[0] for alarm in unsent]

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
        settings = self.conn.execute('''select * from standard_settings''').fetchall()
        return settings[0]

    def get_standard_alarms(self):

        alarms = self.conn.execute('''select * from standard_alarms''').fetchall()
        return alarms

    def get_last_alarm(self):

        alarms = self.conn.execute('''select timer from alarms order by timer asc''').fetchall()
        return alarms[0][0]



