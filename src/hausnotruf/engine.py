from kivy.clock import Clock
from hausnotruf.common import *
from hausnotruf.db_models import *
from hausnotruf.backend import Backend
class Engine:

    def __init__(self, backend : Backend):
        self.backend = backend
        main_engine = lambda x: self.mainloop()
        self.closest_alarm = self.backend.get_closest_alarm()
        sleep_duration = self.backend.get_settings()["sleep"]
        Clock.schedule_interval(main_engine, sleep_duration)
        self.active_alarm = False
        self.sound = None
        self.send_alarm = False


    def mainloop(self):
        log('mainloop step')
        if self.backend.get_auth_key() is None:
            device_auth(self)
        self.backend.send_alive()
        if len(self.backend.get_unconfirmed_alarms()) == 0:
                self.backend.has_to_synchronize = True
        self.backend.clear_old_alarms()
        
        if self.backend.has_to_synchronize:
            self.backend.synchronize_alarms()
        self.check_alarm()
        for error, flag in self.backend.error_flags.items():
            if flag:
                popup_error_msg(error)
        self.closest_alarm = self.backend.get_closest_alarm()
        
        
    def confirm_alarm(self):
        self.closest_alarm.confirmed = True
        self.closest_alarm.altered()
        session.commit()
        self.backend.has_to_synchronize = True
        self.closest_alarm = self.backend.get_closest_alarm()
        if self.sound is not None:
            self.sound.cancel()
            self.sound = None

    def check_alarm(self):
        alarms = self.backend.get_unconfirmed_alarms()
        for alarm in alarms:
            alarm.status_check()
            if alarm.get_escalation_level() > 0:
                if not self.send_alarm:
                    self.send_alarm = True
                    self.send_emergency(alarm.get_escalation_level())
                if self.sound is None: self.sound = Clock.schedule_interval(lambda t: make_sound(), 1)

    def deescalate(self):
        if self.sound is not None:
            self.sound.cancel()
            self.sound = None
        if not self.active_alarm:
            self.closest_alarm.confirmed = True
            self.backend.send_deescalate(self.closest_alarm.get_escalation_level())
            self.closest_alarm.altered()
            self.send_alarm = False
        else:
            self.active_alarm = False
            self.backend.send_deescalate(4)
        self.closest_alarm = None
        self.backend.has_to_synchronize = True

    def postpone_alarm(self, hours):
        if self.closest_alarm is not None:
            self.closest_alarm.postpone(hours)
            for alarm in session.query(Alarm).filter(Alarm.timer_escalation < self.closest_alarm.timer_confirmation).all():
                alarm.confirmed = True
                alarm.altered()
            self.backend.has_to_synchronize = True

    def send_emergency(self, level):
        self.backend.send_emergency(level)

    def fetch_api_key(self, value):
        self.backend.fetch_auth_key(value)