from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
#import RPi.GPIO as GPIO
# this is only used for the device but is included for completeness
    # setup
# GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
# GPIO.setup(BuzzerPin, GPIO.OUT)
# GPIO.output(BuzzerPin, GPIO.HIGH)
# GPIO.setup(voltagePin, GPIO.OUT)
# GPIO.output(voltagePin, GPIO.LOW)


voltagePin = 29
BuzzerPin = 32

def make_sound():
    # GPIO.output(voltagePin, GPIO.HIGH)
    # Clock.schedule_once(lambda x: GPIO.output(BuzzerPin, GPIO.LOW), 0.5)
    pass

def log(msg):
    print(f"[INFO   ] [Hausnotruf   ] {msg}")


def err(msg):
    print(f"[ERROR  ] [Hausnotruf   ] {msg}")

def popup_error_msg(msg):
        dismiss_button = Button(text="Ok")
        msg_label = Label(text=msg)
        content = BoxLayout(orientation="vertical")
        content.add_widget(msg_label)
        content.add_widget(dismiss_button)
        popup = Popup(content=content, auto_dismiss=False)
        dismiss_button.bind(on_press=popup.dismiss)
        popup.open()

def prompt_for_pass():
    pass