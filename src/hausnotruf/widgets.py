from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from hausnotruf import eng, sm
from kivy.uix.vkeyboard import VKeyboard
from kivy.core.window import Window
from kivy.uix.popup import Popup
from common.import *

class MainButton(Button):
    # the full screen button displayed in the main screnn
    def __init__(self):

        super().__init__()
        self.refresher = Clock.schedule_interval(self.refresh, 1 / 4)
        self.alarmState = False
        self.font_size = 160
        self.AlarmObject = None
        self.background_color = (0, 0, 0, 1)

    def refresh(self, dt):
        # refreshes the timer
        if eng.closest_alarm != None:
            self.text = eng.closest_alarm.timer()
            if eng.closest_alarm.status == 1:
                self.background_color = (0, 1, 0, 1) # green -> confirmable
            elif eng.closest_alarm.status >= 2: 
                sm.current = "alarm" # alarmscreen red -> alarm
            else:
                self.background_color = (0, 0, 0, 1) # black -> normal
        else:
            self.text = "kein\n neuer\n  Alarm"
            self.background_color = (0, 0, 0, 1) # black -> normal

    def on_press(self):
        # switch to menu screen and schedule switching back
        if eng.closest_alarm is None or eng.closest_alarm.status == 0:
            sm.current = 'menu'
            def switchback(delay):
                if sm.current != "alarm":
                    sm.current = 'main'
            Clock.schedule_once(switchback, 10)
        else:
            if eng.closest_alarm.status == 1:
                eng.confirm_alarm()

class AlarmButton(Button):
    # fullscreen button displayed in the alarm screen
    def __init__(self):
        super().__init__()
        self.text = "Alarm!!!"
        self.font_size = 160
        self.background_color = (1, 0, 0, 1)

    def on_press(self):
        eng.deescalate()
        sm.current = 'main'
        


class MainButtonScreen(Screen):
    def __init__(self, name='main'):
        super().__init__(name=name)
        self.add_widget(MainButton())


class MenuScreen(Screen):
    def __init__(self, name='menu'):
        super().__init__(name=name)
        self.add_widget(MenuGUI())


class AlarmScreen(Screen):
    def __init__(self, name='alarm'):
        super().__init__(name=name)
        self.add_widget(AlarmButton())


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


        if eng.closest_alarm is not None:
            newtext = eng.closest_alarm.format()
        else:
            newtext = "kein \nneuer \nAlarm"
        #log(newtimer)
        self.text = newtext


class MenuButton(Button):

    def __init__(self, hours):

        super().__init__()
        self.hours = hours
        self.text = "+{}h".format(str(hours))
        self.font_size = 40

    def on_press(self):

        eng.postpone_alarm(self.hours)


class AlarmNowButton(Button):

    def __init__(self):
        super().__init__()
        self.text = '!'
        self.background_color = (1, 0, 0, 1)
        self.font_size = 50

    def on_press(self):

        eng.send_emergency(4)
        eng.active_alarm = True
        sm.current = 'alarm'
        eng.alarmState = True
        make_sound()

