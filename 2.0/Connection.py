
import sqlite3 as sql
from kivy.network.urlrequest import UrlRequest


def post(url, data={}):
    urlstring = url
    if len(data) > 0:
        urlstring += '?'
    for i, (key, value) in enumerate(data.items()):
        urlstring += str(key)+'='+str(value)
        if i != len(data)-1:
            urlstring += '&'
    r = UrlRequest(urlstring)
    return r


class MyConnection:

    def __init__(self, db_path):
        self.conn = sql.connect(db_path)
        self.server_url = self.get_standard_settings()[1]

    def send_approved_alarms(self, timer, approved):

        r = post('http://'+self.server_url+'/cgi-bin/approved.py', data={'timer': timer, 'approved': approved})
        if r.resp_status == 200:
            self.conn.execute('''update alarms set sendtoserver=3 where timer=?''', [timer]).fetchall()
        else:
            self.conn.execute('''update alarms set sendtoserver=2 where timer=?''', [timer]).fetchall()
        self.conn.commit()

    def send_new_alarms(self, timer):

        r = post('http://'+self.server_url + '/cgi-bin/new_alarm.py', data={'timer': timer})
        if r.resp_status == 200:
            self.conn.execute('''update alarms set sendtoserver=1 where timer=?''', [timer]).fetchall()

        else:
            self.conn.execute('''update alarms set sendtoserver=0 where timer=?''', [timer]).fetchall()
        self.conn.commit()

    def send_emergeny(self, timer):

        r = post('http://'+self.server_url + '/cgi-bin/new_alarm.py', data={'timer': timer})

        r = post('http://' + self.server_url + '/cgi-bin/new_alarm.py', data={'timer': timer})

    def send_alive(self, timer):

        r = post('http://'+self.server_url + '/cgi-bin/alive.py', data={'timer': timer})
        if r.resp_status != 200:
            print('server not working')

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
        settings = self.conn.execute('''select * from standard_settings''').fetchall()
        return settings[0]

    def get_standard_alarms(self):

        alarms = self.conn.execute('''select * from standard_alarms''').fetchall()
        return alarms

    def get_last_alarm(self):

        alarms = self.conn.execute('''select timer from alarms order by timer asc''').fetchall()
        return alarms[0][0]



