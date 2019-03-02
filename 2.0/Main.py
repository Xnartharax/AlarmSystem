from requests import *
import sqlite3 as sql
import time

import sqlite3 as sql
import time
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import requests
from Connection import MyConnection
# import RPi.GPIO as GPIO


conn = sql.connect("./coredata.db")
c = conn.cursor()
myconn = MyConnection("./coredata.db")


class MenuGUI(BoxLayout):

    def __init__(self):
        super().__init__()

        self.add_widget(NewAlarmLabel())
        self.add_widget(MenuButtons())


class MainButton(Button):

    def __init__(self):

        super().__init__()
        self.refresher = Clock.schedule_interval(self.refresh, 1 / 4)
        self.alarmState = False
        self.font_size = 160

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
        except IndexError:
            pass
            #print("no valid alarm")

    def on_press(self):
        if self.alarmState:
            c.execute('select timer from alarms where approved is null order by timer asc')
            alarm_timer = c.fetchall()[0][0]
            data = [time.mktime(time.localtime()), alarm_timer]
            c.execute('update alarms set approved=? where timer=?', data)
            conn.commit()
            self.alarm.cancel()

            self.alarmState = False

        else:
            self.parent.switch_gui(MenuGUI())

    def on_alarm(self, dt):
         pass
    #
    #     BuzzerPin = 32
    #     voltagePin = 29
    #     # setup
    #     GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    #     GPIO.setup(BuzzerPin, GPIO.OUT)
    #     GPIO.output(BuzzerPin, GPIO.LOW)
    #     GPIO.setup(voltagePin, GPIO.OUT)
    #     GPIO.output(voltagePin, GPIO.HIGH)
    #     GPIO.output(BuzzerPin, GPIO.HIGH)


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
        c.execute('select timer from alarms where approved is null order by timer asc')
        alarms = c.fetchall()
        print(alarms)
        for alarm in alarms:
            newtimer = alarm[0]+self.hours*3600
            timers = [newtimer, alarm[0]]
            c.execute('''update alarms set timer=? where timer=?''',timers)
        conn.commit()


class MainGUI(BoxLayout):

    def __init__(self):

        super().__init__()
        main_button = MainButton()
        self.old_gui = main_button
        self.add_widget(main_button)

    def switch_gui(self, GUI, switchback=True, switchbacktime=10):

        self.remove_widget(self.old_gui)
        self.add_widget(GUI)
        print('switched gui')
        if switchback:
            print('set up switch back')
            old_gui = self.old_gui
            switching_back = lambda x: self.switch_back(old_gui)
            Clock.schedule_once(switching_back, switchbacktime)
        self.old_gui = GUI

    def switch_back(self, old_GUI):
        print('switching back')
        self.remove_widget(self.old_gui)
        self.add_widget(old_GUI)
        self.old_gui = old_GUI


class AlarmGUI(App):

    def build(self):

        return MainGUI()


class MenuButtons(BoxLayout):
    def __init__(self):
        super().__init__()
        self.orientation = 'vertical'
        self.add_widget(AlarmNowButton())
        self.add_widget(MenuButton(1))
        self.add_widget(MenuButton(24))


class AlarmNowButton(Button):

    def __init__(self):
        super().__init__()
        self.text = '!'
        self.background_color = (1, 0, 0, 1)
        self.font_size = 50

    def on_press(self):
        server_address = myconn.get_standard_settings()[1]
        r = requests.post('http://{}/cgi-bin/emergency.py'.format(server_address), data={'timer': time.mktime(time.localtime())})
        if r.status_code != 200:
            send_again = lambda x: self.on_press()
            Clock.schedule_once(send_again, 1)


class Engine:

    def __init__(self, conn):
        self.conn = conn
        main_engine = lambda x: self.mainloop()
        sleep_duration = self.conn.get_standard_settings()[2]
        Clock.schedule_interval(main_engine, sleep_duration)

    def mainloop(self):
        if len(self.conn.get_unapproved_alarms()) == 0:
                self.new_alarms()

        unsent_approved = self.conn.get_unsent_approved_alarms()

        for unsent in unsent_approved:
                self.conn.send_approved_alarms(approved=unsent[1], timer=unsent[0])
        unsent_new = self.conn.get_unsent_new_alarms()
        for unsent in unsent_new:
            self.conn.send_new_alarms(unsent)

    def new_alarms(self):

        standard_alarms = self.conn.get_standard_alarms()
        for standard_alarm in standard_alarms:
            self.conn.insert_new_alarm(self.make_new_alarm(standard_alarm[0], standard_alarm[1]))

    def make_new_alarm(self, hour, minute):

        timer = list(time.localtime())
        timer[3] = hour
        timer[4] = minute
        seconds = time.mktime(tuple(timer))
        last_alarm = self.conn.get_last_alarm()
        while seconds <= last_alarm:
            seconds += 24*3600
        return seconds


engine = Engine(myconn)
Alarmgui = AlarmGUI()
Alarmgui.run()


