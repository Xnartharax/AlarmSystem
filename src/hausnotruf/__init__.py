from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemandmulti')
from math import floor
from kivy.uix.screenmanager import ScreenManager, Screen




from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from hausnotruf.common import *
from hausnotruf.backend import Backend


import time
from hausnotruf.engine import Engine
backend = Backend()
sm = ScreenManager()
eng = Engine(backend)
from hausnotruf.widgets import AlarmScreen, MainButtonScreen, MenuScreen, AuthScreen


sm.add_widget(AlarmScreen())
sm.add_widget(MainButtonScreen(name='main'))
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(AuthScreen(name='auth'))
sm.current = 'main'


class TestApp(App):

    def build(self):
        return sm


if __name__ == '__main__':
    
    TestApp().run()

