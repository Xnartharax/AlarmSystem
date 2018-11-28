import sqlite3 as sql
import time
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import requests
conn = sql.connect("../coredata.db")
c = conn.cursor()


class MenuGUI(BoxLayout):

    def __init__(self):
        super().__init__()

        self.add_widget(NewAlarmLabel())
        self.add_widget(MenuButtons())


class MainButton(Button):

    def __init__(self):

        super().__init__()
        self.refresher = Clock.schedule_interval(self.refresh, 1 / 4)
        self.alarmState= False

    def refresh(self, dt):

        c.execute('select timer from alarms where approved is null order by timer asc')
        time_diff = 0
        try:
            nextalarm = c.fetchall()[0][0]
            timenow = time.localtime()
            nowseconds = time.mktime(timenow)
            time_diff = nextalarm-nowseconds

            if time_diff > 0:
                hours = str(time.localtime(time_diff)[3])
                minutes = str(time.localtime(time_diff)[4])
                print(hours+":"+minutes)
                self.text = hours+':'+minutes
                c.execute('''select timetoconfirm from standard_settings''')
                timebefore = c.fetchone()[0]

                if time_diff / 60 < timebefore:
                    self.color = (0, 1, 0, 1)
                    if not self.alarmState:
                        self.alarmState = True
                        self.alarm = Clock.schedule_once(self.on_alarm, timebefore * 60)
        except IndexError:
            pass
            #print("no valid alarm")

    def on_press(self):
        if self.alarmState:
            c.execute('select timer from alarms where approved is null order by timer asc')
            alarm_timer = c.fetchall()[0][0]
            data=[time.mktime(time.localtime()),alarm_timer]
            c.execute('update alarms set approved=? where timer=?', data)
            conn.commit()
            self.alarm.cancel()
            self.alarmState = False

        else:

            self.parent.switch_gui(MenuGUI())


    def on_alarm(self, dt):

        print("ALARM!!!!")


class NewAlarmLabel(Label):

    def __init__(self):

        super().__init__()
        self.refresher = Clock.schedule_interval(self.refresh, 1/4)

    def refresh(self, dt):

        conn = sql.connect("../coredata.db")
        c = conn.cursor()
        c.execute('select timer from alarms where approved is null order by timer asc')
        try:
            newtimer = time.ctime(c.fetchall()[0][0])
        except IndexError:
            newtimer = "no new alarm"
        #print(newtimer)
        self.text=newtimer


class MenuButton(Button):

    def __init__(self, hours,):

        super().__init__()
        self.hours = hours
        self.text = "Alarm um {} Stunden verschieben".format(str(hours))

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
        main_button= MainButton()
        self.old_gui=main_button
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
        self.text = 'Alarm auslösen'
        self.background_color=(1,0,0,1)

    def on_press(self):
        c.execute('''select server_address from standard_settings ''')
        server_address = c.fetchone()[0]
        r = requests.post('http://{}/cgi-bin/emergency.cgi'.format(server_address), data={'timer': time.mktime(time.localtime())})


alarm_gui = AlarmGUI()
alarm_gui.run()

