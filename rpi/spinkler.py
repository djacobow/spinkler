#!/usr/bin/env python3

import os
import json
import GoogleStuff
import SpinklerTimer

from drivers import lcd
from drivers import triacs
from drivers import bb595

if __name__ == '__main__':

    with open('./spconfig.json') as f:
        config = json.load(f)

        shifter = bb595.bb595()
        disp = lcd.LCD(shifter,'20x4')
        disp.begin()
        disp.clear()
        disp.backlight(0)

        valves = triacs.Triacs(shifter)
        valves.enable(True)
        valves.set(0);
        ga = GoogleStuff.Authinator(config['google'])
        ga.get_credentials()
        cal = GoogleStuff.CalendarReader(config, ga)
        mailer = GoogleStuff.Mailer(config, ga)

        if True:
            spr = SpinklerTimer.SpinklerTimer(config,cal,mailer,valves,disp)
            spr.run()

