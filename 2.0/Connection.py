import urllib
import sqlite3 as sql
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock


def post(url, on_succ, on_fail, data={}):
    urlstring = url
    query = urllib.parse.urlencode(data)

    r = UrlRequest(urlstring, req_body=query, on_failure=on_fail, on_success=on_succ)

    return r


class MyConnection:

    def __init__(self, db_path):
        self.conn = sql.connect(db_path, timeout=10)
        self.server_url = self.get_standard_settings()[1]

    def send_approved_alarms(self, timer, approved):


        def on_succ(request, stuff):
            print('connection_worked')
            self.conn.execute('''update alarms set sendtoserver=3 where timer=?''', [timer]).fetchall()
            self.conn.commit()

        def on_fail(request, stuff):

            print('connection not working')
            self.conn.execute('''update alarms set sendtoserver=2 where timer=?''', [timer]).fetchall()
            self.conn.commit()
            print('connection failed: trying again')

            Clock.schedule_once(lambda x:post('http://'+self.server_url+'/cgi-bin/approved.py', data={'timer': timer, 'approved': approved, 'device_id': 1}, on_succ=on_succ,
                         on_fail=on_fail), 10)

            self.conn.commit()

        r = post('http://'+self.server_url+'/cgi-bin/approved.py', data={'timer': timer, 'approved': approved, 'device_id': 1}, on_succ=on_succ,
                 on_fail=on_fail)

    def send_new_alarms(self, timer):


        def on_succ(request, stuff):
            print('connection_worked')
            self.conn.execute('''update alarms set sendtoserver=1 where timer=?''', [timer]).fetchall()
            self.conn.commit()

        def on_fail(request, stuff):

            print('connection not working')
            self.conn.execute('''update alarms set sendtoserver=0 where timer=?''', [timer]).fetchall()
            self.conn.commit()
            print('connection failed: trying again')

            Clock.schedule_once(lambda x:post('http://' + self.server_url + '/cgi-bin/new_alarm.py',
                         ddata={'timer': timer, 'device_id': 1}, on_succ=on_succ,
                         on_fail=on_fail), 10)

            self.conn.commit()

        r = post('http://' + self.server_url + '/cgi-bin/new_alarm.py',
                 data={'timer': timer, 'device_id': 1}, on_succ=on_succ,
                 on_fail=on_fail)

    def update_alarms(self, old_timer, new_timer):

        def on_succ(request, stuff):
            print('connection_worked')

            self.conn.execute('''update alarms set sendtoserver=1 where timer=?''', [new_timer]).fetchall()
            self.conn.commit()

        def on_fail(request, stuff):

            print('connection not working')
            self.conn.execute('''update alarms set sendtoserver=5 where timer=?''', [new_timer]).fetchall()
            print('connection failed: trying again')

            Clock.schedule_once(lambda x:post('http://' + self.server_url + '/cgi-bin/change_alarm_time.py',
                     data={'new_timer': new_timer, 'old_timer': old_timer, 'device_id': 1}, on_succ=on_succ,
                     on_fail=on_fail), 10)

            self.conn.commit()
        r = post('http://' + self.server_url + '/cgi-bin/change_alarm_time.py',
                 data={'new_timer': new_timer, 'old_timer': old_timer, 'device_id': 1}, on_succ=on_succ,
                 on_fail=on_fail)

        self.conn.commit()

    def send_emergeny(self, emergency_level):

        def on_fail(req, res):
            Clock.schedule_once(lambda x: post('http://'+self.server_url + '/cgi-bin/emergency.py', data={'device_id': 1, 'emergency_level': emergency_level}))

        def on_succ(req, res):
            print('alarm send')

        r = post('http://'+self.server_url + '/cgi-bin/emergency.py', data={'device_id': 1, 'emergency_level': emergency_level}, on_fail=on_fail, on_succ=on_succ)

    def send_alive(self, timer):
        def on_fail(req, res):
            Clock.schedule_once(lambda x:post('http://'+self.server_url + '/cgi-bin/alive.py', data={'timer': timer, 'device_id': 1}))

        def on_succ(req, res):
            print('alive send')

        r = post('http://'+self.server_url + '/cgi-bin/alive.py', data={'timer': timer, 'device_id': 1,},on_fail=on_fail, on_succ=on_succ)

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



