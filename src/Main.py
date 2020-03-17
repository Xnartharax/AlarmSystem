from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddocked')
from hausnotruf import engine, TestApp
TestApp().run()