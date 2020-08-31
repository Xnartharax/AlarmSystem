import urllib
import time
from hashlib import sha256
import os
from kivy.network.urlrequest import UrlRequest
from hausnotruf.common import *
from sqlalchemy import desc, asc
from kivy.clock import Clock
import kivy
import json
from typing import List
from hausnotruf.db_models import *
from typing import Dict, Sequence, Callable

settingspath = os.environ.get("HAUSNOTRUFSETTINGS") or "../data/settings.json"
class Backend:

    def __init__(self):
        self.server_url = self.get_settings()["server_url"]
        self.error_flags = {
            "Authentfication Error": False,
            "Kein Internet": False,
            "Server nicht erreicht": False
        }
        self.has_to_synchronize = True
    
    def not_reachable(self, req : UrlRequest, res):
        if req.resp_status == 403:
            self.error_flags["Authentfication Error"] = True
        elif req.resp_status == 500:
            self.error_flags["Server Error"] = True
        else:
            self.error_flags["Server nicht erreicht"] = True 

    def request_succ_handle(self, func):
        """
        handy wrapper for standard procedure on successfull requests
        """
        def new_func(*args, **kwargs):
            for error in self.error_flags:
                self.error_flags[error] = False
            func(*args, **kwargs)
        return new_func

    def post(self, url : str, data : Dict, on_succ=None):
        """
        encodes the data as json and sends it in the request body.
        """
        def on_err(req, err):
            self.error_flags["Server nicht\n errreichbar"] = True
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
                        on_success=on_succ, on_error=on_err, timeout=10)


    def synchronize_alarms(self):
        """
        synchronization protocol:
        send all alarms to the server server decides on wich was the newest update and sends correct set back as json
        this method takes the json and updates the client table
        also we dont want to use alter_alarm in this method because this is not an alteration just a synchronization
        """
        @self.request_succ_handle
        def handle(req, resp: Sequence):
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
        def handle(req, resp: Sequence):
            log("succesfully send alive")
            if resp[0] == 1:
                self.has_to_synchronize = True

        self.post("https://"+self.server_url+"/api/alive",
                      {'device_id': self.get_device_id(), 'timer': time.mktime(time.localtime())}, on_succ=handle)

    def send_emergency(self, emergency_level: int):
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

    def send_deescalate(self, emergency_level: int):
        log("send deescalate")
        self.post('https://'+self.server_url + '/api/deescalate',
                      data={'device_id': self.get_device_id(), 'emergency_level': emergency_level})

    def get_settings(self)-> dict:
        settings = json.load(open(settingspath))
        return settings

    def get_device_id(self)-> int:
        return self.get_settings().get("device_id")

    def get_auth_key(self)->str:
        auth_key = self.get_settings().get("api_key")
        return auth_key

    def write_settings(self, settings: Dict):
        fp = open(settingspath, "w")
        json.dump(settings, fp)
        fp.close()

    def fetch_auth_key(self, token : str):

        @self.request_succ_handle
        def on_succ(req, resp: Dict):
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

    