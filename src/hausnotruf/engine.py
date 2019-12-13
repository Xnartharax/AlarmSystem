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

    def mainloop(self):
        log('mainloop step')
        self.backend.send_alive()
        if len(self.backend.get_unconfirmed_alarms()) == 0:
                self.backend.has_to_synchronize = True
        self.backend.clear_old_alarms()
        self.check_alarm()
        if self.backend.has_to_synchronize:
            self.backend.synchronize_alarms()
        for error, flag in self.backend.error_flags.items():
            if flag:
                popup_error_msg(error)
    def confirm_alarm(self):
        self.closest_alarm.confirmed = True
        session.commit()
        self.backend.has_to_synchronize = True

    def check_alarm(self):
        alarms = self.backend.get_unconfirmed_alarms()
        for alarm in alarms:
            alarm.status_check()
            if alarm.get_escalation_level() > 0:
                self.send_emergency(alarm.get_escalation_level())

    def deescalate(self):
        
        self.backend.send_deescalate(self.closest_alarm.get_escalation_level())

    def postpone_alarm(self, hours):
        alarms = self.backend.get_unconfirmed_alarms()
        for alarm in alarms:
            alarm.postpone(hours)

    def send_emergency(self, level):
        self.backend.send_emergency(level)