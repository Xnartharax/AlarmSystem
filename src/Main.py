from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemandmulti')
Config.set('kivy', 'keyboard_layout', 'number')
from hausnotruf import engine, TestApp
TestApp().run()