import urllib
import time
from hashlib import sha256
import sqlite3 as sql
from kivy.network.urlrequest import UrlRequest
from hausnotruf.common import *
from sqlalchemy import desc, asc
from kivy.clock import Clock
import kivy
import json
from typing import List
from hausnotruf.db_models import *
    
class Backend:

    def __init__(self, db_path):
        self.conn = sql.connect(db_path, timeout=10)
        self.server_url = self.get_settings()["server_url"]
        self.error_flags = {
            "Auth Error": False,
            "Kein Internet": False,
            "Server kaputt": False
        }
        self.has_to_synchronize = True

    def not_reachable(self, req : UrlRequest, res):
        if req.resp_status == 403:
            self.error_flags["Auth Error"] = True
        elif req.resp_status == 500:
            self.error_flags["Server kaputt"] = True
        else:
            self.error_flags["Keine Verbindung zum Server"] = True

    def post(self, url, data, on_succ=None):
        # encodes the data as json and sends it in the request body hope cgi module can handle this
        urlstring = url
        auth = sha256()
        auth.update(json.dumps(data).encode())
        auth.update(self.get_auth_key().encode())
        query = json.dumps({"data": data, "auth": auth.hexdigest(), "uid": self.get_settings()["uid"]})
        req_headers = {"Content-type": "application/json"}

        UrlRequest(urlstring, req_body=query, req_headers=req_headers, on_failure=self.not_reachable,
                       on_success=on_succ, timeout=10)

    def commit(self):
        self.conn.commit()

    def query(self, query_string, variables):
        # simple wrapper to retry when database is locked TODO: make this asynchronous
        # try:
            return self.conn.execute(query_string, variables)
        # except sql.OperationalError:    # probably locked just trying again 0.01 sec after
        #     time.sleep(0.01)
        #     return self.query(query_string, variables)

    def dictionarize(self, cursor):
        # returns the result of the query with a dict as each row
        result = cursor.fetchall()
        columnnames = [col[0] for col in cursor.description]
        returned = []
        for row in result:
            returned.append({name: value for name, value in zip(columnnames, row)})
        return returned

    def alter_alarm(self, id, update_dict):
        # simple wrapper to handle the update timestamp
        update_sql = ""
        for column, value in update_dict.items():
            update_sql += f"{column}={value}, "
        self.query(f"update alarms set {update_sql} updated=? where id=?", (time.mktime(time.localtime()), id))
        self.commit()
        self.has_to_synchronize = True


    def synchronize_alarms(self):
        # synchronization protocol:
        # send all alarms to the server server decides on wich was the newest update and sends correct set back as json
        # this method takes the json and updates the client table
        # also we dont want to use alter_alarm in this method because this is not an alteration just a synchronization
        def handle(req, resp):
            log("synchronizing alarms from server")
            for alarm in resp:
                if session.query(Alarm).get(alarm["id"]) is None:
                    new_alarm = Alarm.from_dict(alarm)
                    session.add(new_alarm)
                else:
                    session.query(Alarm).get(alarm["id"]).update(alarm)
            self.has_to_synchronize = False
        log("initiating synchronization")
        all_alarms = [alarm.to_dict() for alarm in session.query(Alarm).all()]
        data = {'alarms': all_alarms, 'device_id': self.get_device_id()}
        self.post('http://'+self.server_url+'/api/synchronize', data, on_succ=handle)
        
    def send_alive(self):
        def handle(req, resp):
            log("succesfully send alive")
            if resp[0] == 1:
                self.has_to_synchronize = True
        self.post("http://"+self.server_url+"/api/alive",
                      {'device_id': self.get_device_id(), 'timer': time.mktime(time.localtime())}, on_succ=handle)

    def send_emergency(self, emergency_level):
        log("send alarm")
        self.post('http://' + self.server_url + '/api/emergency',
                            {'device_id': self.get_device_id(), 'emergency_level': emergency_level})

    def get_unconfirmed_alarms(self) -> List[Alarm]:
        """
        in descending order of escalation time
        """
        return session.query(Alarm).order_by(desc(Alarm.timer_escalation)).filter(not Alarm.confirmed).all()

    def clear_old_alarms(self):
        old_alarms = session.query(Alarm).order_by(desc(Alarm.timer_escalation)).filter(not Alarm.confirmed).all()
        for alarm in old_alarms[1:]:
            session.delete(alarm)
        session.commit()

    def get_closest_alarm(self) -> Alarm:
        return session.query(Alarm).order_by(desc(Alarm.timer_escalation)).filter(not Alarm.confirmed).first()

    def send_deescalate(self, emergency_level):
        log("send deescalate")
        self.post('http://'+self.server_url + '/api/deescalate',
                      data={'device_id': self.get_device_id(), 'emergency_level': emergency_level})

    def get_settings(self):
        settings = json.load(open("../data/settings.json"))
        return settings

    def get_device_id(self):
        return self.get_settings()["device_id"]

    def get_auth_key(self):
        auth_key = self.get_settings().get("auth_key")
        if auth_key is None:
            auth_key = self.fetch_auth_key()
        return auth_key
    
    def fetch_auth_key(self):
        r = self.post('http://'+self.server_url + '/api/get_apikey',
                      data={'username': "TestUser", 'emergency_level': "1234"})

