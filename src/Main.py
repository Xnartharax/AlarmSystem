from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.write()
from hausnotruf import engine, TestApp
TestApp().run()