import sqlite3 as sql
import time
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
conn=sql.connect("../coredata.db")
c=conn.cursor()
class MenuGUI(BoxLayout):
    def __init__(self):
        super().__init__()

        self.add_widget(NewAlarmLabel())

class MainButton(Button):
    def __init__(self, master):
        super().__init__()
        self.refresher = Clock.schedule_interval(self.refresh, 1 / 0.5)
        self.master=master
    def refresh(self, dt):
        conn = sql.connect("../coredata.db")
        c = conn.cursor()
        c.execute('select timer from alarms where approved is null order by timer asc')
        newtimer = time.ctime(c.fetchall()[0][0])
        print(newtimer)
        self.text = newtimer
    def on_touch_down(self, touch):
        pass
class NewAlarmLabel(Label):
    def __init__(self):
        super().__init__()
        self.refresher = Clock.schedule_interval(self.refresh, 1/0.5)

    def refresh(self, dt):
        conn = sql.connect("../coredata.db")
        c = conn.cursor()
        c.execute('select timer from alarms where approved is null order by timer asc')
        newtimer = time.ctime(c.fetchall()[0][0])
        print(newtimer)
        self.text=newtimer

class MenuButtons(BoxLayout):
    def __init__(self):
        super().__init__()
class MenuButton(Button):
    def __init__(self):
        super().__init__()
class AlarmGUI(App):
    def build(self):
        return MenuGUI()
AlarmGUI().run()