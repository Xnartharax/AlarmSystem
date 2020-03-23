from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.write()
import os
pid_fp = open("./hausnortuf_pid.txt", "w+")
pid_fp.write(str(os.getpid())) # to kill and restart the process after update
pid_fp.close()
from hausnotruf import engine, TestApp
TestApp().run()