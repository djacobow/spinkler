#!/usr/bin/env python3

real_gpio = False
try:
    import RPi.GPIO as GPIO
except Exception as e:
    print("Using dummy_gpio. Is RPi.GPIO installeD?")
    from drivers import dummy_gpio as GPIO

class Buttons(object):
    def __init__(self):
        self.bpins = [ 7, 12 ]
        GPIO.setmode(GPIO.BOARD)
        for bpin in self.bpins:
            GPIO.setup(bpin, GPIO.IN)
    def pressed(self):
        return [ False if GPIO.input(pin) else True for pin in self.bpins ]
    

if __name__ == '__main__':
    import time
    buttons = Buttons()

    while True:
        v = buttons.pressed()
        if any(v):
            print(v)
        time.sleep(1)
