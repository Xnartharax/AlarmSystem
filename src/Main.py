from math import floor
from kivy.uix.screenmanager import ScreenManager, Screen


import sqlite3 as sql

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config

from Connection import MyConnection
#import RPi.GPIO as GPIO
import time
myconn = MyConnection('../data/coredata.db')
# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.

voltagePin = 29
BuzzerPin = 32
# Declare both screens
    # setup
# GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
# GPIO.setup(BuzzerPin, GPIO.OUT)
# GPIO.output(BuzzerPin, GPIO.HIGH)
# GPIO.setup(voltagePin, GPIO.OUT)
# GPIO.output(voltagePin, GPIO.LOW)


def make_sound():
    # GPIO.output(voltagePin, GPIO.HIGH)
    # Clock.schedule_once(lambda x: GPIO.output(BuzzerPin, GPIO.LOW), 0.5)
    pass


class Alarm:
    def __init__(self):
        self.escalate_times = myconn.get_escalation_times()
        self.levels = [None, None, None]

    def escalate1(self):
        print("level 1")
        self.levels[0] = (Clock.schedule_interval(lambda x: make_sound(), 1), Clock.schedule_once(lambda x: self.escalate2(), self.escalate_times[0][0]))

    def escalate2(self):
        print("level 2")
        self.levels[1] = (Clock.schedule_once(lambda x: myconn.send_emergency(2), 1), Clock.schedule_once(lambda x: self.escalate3(), self.escalate_times[1][0]))

    def escalate3(self):
        print("level 3")
        self.levels[2] = (Clock.schedule_once(lambda x: myconn.send_emergency(3), 1), Clock.schedule_once(lambda x: myconn.send_emergency(3), 1))

    def deescalate(self):
        for escalation in self.levels:
            if escalation is not None:
                escalation[0].cancel()
                escalation[1].cancel()


class MainButton(Button):

    def __init__(self):

        super().__init__()
        self.refresher = Clock.schedule_interval(self.refresh, 1 / 4)
        self.alarmState = False
        self.font_size = 160
        self.AlarmObject = None

    def refresh(self, dt):

        try:
            nextalarm = myconn.get_unapproved_alarms()[0]
            nowseconds = time.time()
            time_diff = nextalarm-nowseconds
            hours = floor(time_diff / 3600) #flooring otherwise to many hours til alarm half the time
            minutes = round((time_diff % 3600) / 60)
            self.text = '{} : {}'.format(hours, minutes)
            if time_diff > 0:


                timebefore = myconn.get_standard_settings()[0]
                if time_diff / 60 < timebefore:
                    self.background_color = (0, 1, 0, 1)
                    if not self.alarmState:
                        self.alarmState = True
                else:
                    self.background_color = (0, 0, 0, 1)
                    self.alarmState = False

            else:
                self.text = "ALARM!!!!"
                self.alarmState = True
                self.background_color = (1, 0, 0, 1)
                if self.AlarmObject is None:
                    self.AlarmObject = Alarm()
                    self.AlarmObject.escalate1()
        except IndexError:
            self.text = "no new alarms"

    def on_press(self):
        if self.AlarmObject is not None:
            self.AlarmObject.deescalate()
            self.AlarmObject = None 
        if self.alarmState:
            alarm_timer = myconn.get_unapproved_alarms()[0]
            myconn.approve_alarm(alarm_timer)
            self.alarmState = False
        else:
            sm.current = 'menu'

            def switchback(x): sm.current = 'main'
            Clock.schedule_once(switchback, 10)


class MainButtonScreen(Screen):
    def __init__(self, name='main'):
        super().__init__(name=name)
        self.add_widget(MainButton())


class MenuScreen(Screen):
    def __init__(self, name='menu'):
        super().__init__(name=name)
        self.add_widget(MenuGUI())


class MenuGUI(BoxLayout):

    def __init__(self):
        super().__init__()

        self.add_widget(NewAlarmLabel())
        self.add_widget(MenuButtons())


class MenuButtons(BoxLayout):
    def __init__(self):
        super().__init__()
        self.orientation = 'vertical'
        self.add_widget(AlarmNowButton())
        self.add_widget(MenuButton(1))
        self.add_widget(MenuButton(24))


class NewAlarmLabel(Label):

    def __init__(self):

        super().__init__()
        self.font_size = 70
        self.refresher = Clock.schedule_interval(self.refresh, 1/4)

    def refresh(self, dt):


        try:
            time_struct = time.localtime(myconn.get_unapproved_alarms()[0])
            newtext = f"{time_struct.tm_mday}.{time_struct.tm_mon}\n{time_struct.tm_hour}:{time_struct.tm_min}"
        except IndexError:
            newtext = "no new alarm"
        #print(newtimer)
        self.text = newtext


class MenuButton(Button):

    def __init__(self, hours):

        super().__init__()
        self.hours = hours
        self.text = "+{}h".format(str(hours))
        self.font_size = 40

    def on_press(self):

        alarm = myconn.get_unapproved_alarms()[0]


        newtimer = alarm+self.hours*3600
        myconn.delay_alarm(alarm, newtimer)
        myconn.update_alarms(alarm, newtimer)


class AlarmNowButton(Button):

    def __init__(self):
        super().__init__()
        self.text = '!'
        self.background_color = (1, 0, 0, 1)
        self.font_size = 50

    def on_press(self):

        myconn.send_emergency(4)
        # make_sound()


class Engine:

    def __init__(self):
        self.conn = myconn
        main_engine = lambda x: self.mainloop()
        sleep_duration = self.conn.get_standard_settings()[2]
        Clock.schedule_interval(main_engine, sleep_duration)

    def mainloop(self):
        print('mainloop step')
        self.conn.send_alive(time.mktime(time.localtime()))
        if len(self.conn.get_unapproved_alarms()) == 0:
                self.new_alarms()

        unsent_approved = self.conn.get_unsent_approved_alarms()

        for unsent in unsent_approved:
                self.conn.send_approved_alarms(approved=unsent[1], timer=unsent[0])
        unsent_new = self.conn.get_unsent_new_alarms()
        for unsent in unsent_new:
            self.conn.send_new_alarms(unsent)

    def new_alarms(self):
        print('making new alarm')
        standard_alarms = self.conn.get_standard_alarms()
        for standard_alarm in standard_alarms:
            self.conn.insert_new_alarm(self.make_new_alarm(standard_alarm[0], standard_alarm[1]))

    def make_new_alarm(self, hour, minute):

        timer = list(time.localtime())
        timer[3] = hour
        timer[4] = minute
        seconds = time.mktime(tuple(timer))
        last_alarm = self.conn.get_last_approved_alarm()
        while seconds <= last_alarm+1000 or seconds < time.time():
            seconds += 24*3600
        return seconds

# Create the screen manager
sm = ScreenManager()
sm.add_widget(MainButtonScreen(name='main'))
sm.add_widget(MenuScreen(name='menu'))


class TestApp(App):

    def build(self):
        return sm


if __name__ == '__main__':
    engine = Engine()
    TestApp().run()

