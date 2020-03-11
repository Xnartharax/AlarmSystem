import urllib
import time
from hashlib import sha256

from kivy.network.urlrequest import UrlRequest
from hausnotruf.common import *
from sqlalchemy import desc, asc
from kivy.clock import Clock
import kivy
import json
from typing import List
from hausnotruf.db_models import *
    
class Backend:

    def __init__(self):
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
            self.error_flags["Kein Internet"] = True 

    def request_succ_handle(self, func):
        def new_func(*args, **kwargs):
            for error in self.error_flags:
                self.error_flags[error] = False
            func(*args, **kwargs)
        return new_func

    def post(self, url, data, on_succ=None):
        # encodes the data as json and sends it in the request body hope cgi module can handle this
        auth_key = self.get_auth_key()
        if auth_key is not None:
            urlstring = url
            auth = sha256()
            auth.update(json.dumps(data, sort_keys=True).encode())
            auth.update(self.get_auth_key().encode())
            query = json.dumps({"data": data, "auth": auth.hexdigest(),
                    "uid": self.get_settings()["uid"],
                    "device_id": self.get_settings()["device_id"]}, sort_keys=True)
            req_headers = {"Content-type": "application/json"}

            UrlRequest(urlstring, req_body=query, req_headers=req_headers, on_failure=self.not_reachable,
                        on_success=on_succ, timeout=10)


    def dictionarize(self, cursor):
        # returns the result of the query with a dict as each row
        result = cursor.fetchall()
        columnnames = [col[0] for col in cursor.description]
        returned = []
        for row in result:
            returned.append({name: value for name, value in zip(columnnames, row)})
        return returned


    def synchronize_alarms(self):
        # synchronization protocol:
        # send all alarms to the server server decides on wich was the newest update and sends correct set back as json
        # this method takes the json and updates the client table
        # also we dont want to use alter_alarm in this method because this is not an alteration just a synchronization
        @self.request_succ_handle
        def handle(req, resp):
            log("synchronizing alarms from server")
            for alarm in resp:
                if session.query(Alarm).get(alarm["id"]) is None:
                    new_alarm = Alarm.from_dict(alarm)
                    session.add(new_alarm)
                else:
                    session.query(Alarm).get(alarm["id"]).update(alarm)
            self.has_to_synchronize = False
            session.commit()
        log("initiating synchronization")
        all_alarms = [alarm.to_dict() for alarm in session.query(Alarm).all()]
        data = {'alarms': all_alarms, 'device_id': self.get_device_id()}
        self.post('https://'+self.server_url+'/api/synchronize', data, on_succ=handle)

    def send_alive(self):
        @self.request_succ_handle
        def handle(req, resp):
            log("succesfully send alive")
            if resp[0] == 1:
                self.has_to_synchronize = True
        self.post("https://"+self.server_url+"/api/alive",
                      {'device_id': self.get_device_id(), 'timer': time.mktime(time.localtime())}, on_succ=handle)

    def send_emergency(self, emergency_level):
        log("send alarm")
        self.post('https://' + self.server_url + '/api/emergency',
                            {'device_id': self.get_device_id(), 'emergency_level': emergency_level})

    def get_unconfirmed_alarms(self) -> List[Alarm]:
        """
        in descending order of escalation time
        """
        return session.query(Alarm).order_by(desc(Alarm.timer_escalation)).filter(Alarm.confirmed != True).all()

    def clear_old_alarms(self):
        old_alarms = session.query(Alarm).order_by(desc(Alarm.timer_escalation)).filter(Alarm.confirmed == True).all()
        for alarm in old_alarms[1:]:
            session.delete(alarm)
        session.commit()

    def get_closest_alarm(self) -> Alarm:
        return session.query(Alarm).order_by(asc(Alarm.timer_escalation)).filter(Alarm.confirmed != True).first()

    def send_deescalate(self, emergency_level):
        log("send deescalate")
        self.post('https://'+self.server_url + '/api/deescalate',
                      data={'device_id': self.get_device_id(), 'emergency_level': emergency_level})

    def get_settings(self):
        settings = json.load(open("../data/settings.json"))
        return settings

    def get_device_id(self):
        return self.get_settings().get("device_id")

    def get_auth_key(self):
        auth_key = self.get_settings().get("api_key")
        return auth_key

    def write_settings(self, settings):
        fp = open("../data/settings.json", "w")
        json.dump(settings, fp)
        fp.close()

    def fetch_auth_key(self, token):
        @self.request_succ_handle
        def on_succ(req, resp):
            settings = self.get_settings()
            settings["api_key"] = resp["api_key"]
            settings["uid"] = resp["uid"]
            settings["device_id"] = resp["device_id"]
            self.write_settings(settings)

        
        data={'token': token}
        query = json.dumps(data)
        req_headers = {"Content-type": "application/json"}
        UrlRequest('https://'+self.server_url + '/api/get_apikey', req_body=query, 
                        req_headers=req_headers, on_failure=self.not_reachable,
                        on_success=on_succ, timeout=10)

    