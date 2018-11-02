#!/usr/bin/env python3

import os
import GoogleCalendarReader
import SpinklerTimer
from drivers import lcd
from drivers import triacs
from drivers import bb595

config = {
    'google': {
        'refresh_period': 3600,                                                 
        'credentials_file': 'creds.json',                          
        'credentials_dir': os.path.expanduser('~') + '/.spinkler',
        'client_secrets': 'spinkler_client_secrets.json',                                
        'scopes': ['https://www.googleapis.com/auth/calendar.readonly'],                    
    },
    'sprinkler_calendar': 'd5mhbl6ei4jt4a37iirhoa3ajg@group.calendar.google.com',
    'zone_count': 8,
    'cal_check_interval': 15,
    'pause_time': 2,
    'tick_interval': 2,
}

if __name__ == '__main__':

    shifter = bb595.bb595()
    disp = lcd.LCD(shifter)
    disp.begin()
    disp.clear()
    disp.backlight(0)

    valves = triacs.Triacs(shifter)

    cal = GoogleCalendarReader.GoogleCalendarReader(config)
    cal.get_credentials()
    cal.get_service()

    if True:
        spr = SpinklerTimer.SpinklerTimer(config,cal,valves,disp)
        spr.run()

