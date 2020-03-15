from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemandmulti')
from hausnotruf import engine, TestApp
TestApp().run()