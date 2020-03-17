from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.window import Window



try:
    import RPi.GPIO as GPIO
    voltagePin = 29
    BuzzerPin = 32
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BuzzerPin, GPIO.OUT)
    GPIO.output(BuzzerPin, GPIO.HIGH)
    GPIO.setup(voltagePin, GPIO.OUT)
    GPIO.output(voltagePin, GPIO.HIGH)
    gpio = True
    def make_sound():
        GPIO.output(BuzzerPin, GPIO.LOW)
        Clock.schedule_once(lambda x: GPIO.output(BuzzerPin, GPIO.HIGH), 0.5)

except ImportError:
    gpio = False
    def make_sound():
        pass


def log(msg):
    print(f"[INFO   ] [Hausnotruf   ] {msg}")


def err(msg):
    print(f"[ERROR  ] [Hausnotruf   ] {msg}")
    
popup_open = False
def popup_closing(func):
    def wrapped(*args, **kwargs):
        global popup_open
        func(*args, **kwargs)
        popup_open = False
    return wrapped

def popup_opening(func):
    def wrapped(*args, **kwargs):
        global popup_open
        if not popup_open:
            func(*args, **kwargs)
            popup_open = True
    return wrapped

@popup_opening
def popup_error_msg(msg):
    
    dismiss_button = Button(text="OK", font_size=140)
    msg_label = Label(text=msg, font_size=140)
    content = BoxLayout(orientation="vertical")
    content.add_widget(msg_label)
    content.add_widget(dismiss_button)
    popup = Popup(content=content, auto_dismiss=False)
    dismiss_button.bind(on_press=popup_closing(popup.dismiss))
    popup.open()
    

@popup_opening
def device_auth(eng):
    from hausnotruf.widgets import sm
    sm.current = "auth"


        

        