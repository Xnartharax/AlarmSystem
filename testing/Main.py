
from kivy.uix.screenmanager import ScreenManager, Screen


import sqlite3 as sql

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config

from Connection import MyConnection
import RPi.GPIO as GPIO
import time
myconn = MyConnection('coredata.db')
# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
conn = sql.connect("./coredata.db")
c = conn.cursor()

voltagePin = 29
BuzzerPin = 32
# Declare both screens
    # setup
GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
GPIO.setup(BuzzerPin, GPIO.OUT)
GPIO.output(BuzzerPin, GPIO.HIGH)
GPIO.setup(voltagePin, GPIO.OUT)
GPIO.output(voltagePin, GPIO.LOW)


def make_sound():
    GPIO.output(voltagePin, GPIO.HIGH)
    Clock.schedule_once(lambda x: GPIO.output(BuzzerPin, GPIO.LOW), 0.5)


class Alarm:
    def __init__(self):
        self.escalate_times = myconn.get_escalating_levels()
        self.levels = [None, None, None]

    def escalate1(self):
        self.levels[0] = (Clock.schedule_interval(lambda x: make_sound(), 1), Clock.schedule_once(lambda x: self.escalate2(), self.escalate_times[0][0]))

    def escalate2(self):
        self.levels[1] = (Clock.schedule_once(lambda x: myconn.send_emergency(2), 1), Clock.schedule_once(lambda x: self.escalate3(), self.escalate_times[1][0]))

    def escalate3(self):
        self.levels[1] = (Clock.schedule_once(lambda x: myconn.send_emergency(3), 1), Clock.schedule_once(lambda x: myconn.send_emergency(3), 1))

    def deescalate(self):
        for escalation in self.levels:
            if not escalation is None:
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
            timenow = time.localtime()
            nowseconds = time.mktime(timenow)
            time_diff = nextalarm-nowseconds

            if time_diff > 0:
                hours = round(time_diff/3600)
                minutes = round((time_diff % 3600) / 60)
                self.text = '{} : {}'.format(hours, minutes)
                c.execute('''select timetoconfirm from standard_settings''')
                timebefore = c.fetchone()[0]

                if time_diff / 60 < timebefore:
                    self.color = (0, 1, 0, 1)
                    if not self.alarmState:
                        self.alarmState = True
                        self.alarm = Clock.schedule_once(self.on_alarm, time_diff * 60)
            else:
                self.text = "ALARM!!!!"
        except IndexError:
            pass
            #print("no valid alarm")

    def on_press(self):
        if not self.AlarmObject is None:
            self.AlarmObject.deescalate
            self.AlarmObject = None
        if self.alarmState:
            c.execute('select timer from alarms where approved is null order by timer asc')
            alarm_timer = c.fetchall()[0][0]
            data = [time.mktime(time.localtime()), alarm_timer]
            c.execute('update alarms set approved=? where timer=?', data)
            conn.commit()
            self.alarm.cancel()

            self.alarmState = False
        else:
            sm.current = 'menu'
            def switchback(x): sm.current = 'main'
            Clock.schedule_once(switchback, 10)

    def on_alarm(self, dt):
        print('alarm')
        self.AlarmObject = Alarm()


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
        self.refresher = Clock.schedule_interval(self.refresh, 1/4)

    def refresh(self, dt):

        c.execute('select timer from alarms where approved is null order by timer asc')
        try:
            newtimer = time.ctime(c.fetchall()[0][0])
        except IndexError:
            newtimer = "no new alarm"
        #print(newtimer)
        self.text = newtimer


class MenuButton(Button):

    def __init__(self, hours):

        super().__init__()
        self.hours = hours
        self.text = "+{}h".format(str(hours))
        self.font_size = 40

    def on_press(self):

        alarms = myconn.get_unapproved_alarms()
        print(alarms)
        for alarm in alarms:
            newtimer = alarm+self.hours*3600
            timers = [newtimer, alarm]
            print(newtimer)
            c.execute('''update alarms set timer=?, sendtoserver=4 where timer=?''', timers)
            conn.commit()
            myconn.update_alarms(alarm, newtimer)


class AlarmNowButton(Button):

    def __init__(self):
        super().__init__()
        self.text = '!'
        self.background_color = (1, 0, 0, 1)
        self.font_size = 50

    def on_press(self):
        def send(dt):
            server_address = myconn.get_standard_settings()[1]
            myconn.send_emergency(4)
        # make_sound()

# Create the screen manager
sm = ScreenManager()
sm.add_widget(MainButtonScreen(name='main'))
sm.add_widget(MenuScreen(name='menu'))

class TestApp(App):

    def build(self):
        return sm


if __name__ == '__main__':
    TestApp().run()
