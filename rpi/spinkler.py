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
    'weather_check_interval': 60,
    'pause_time': 2,
    'tick_interval': 1,
    'weather': {
        'url': 'https://www.aviationweather.gov/adds/dataserver_current/httpparam',
        'args': {
            'dataSource': 'metars',
            'requestType': 'retrieve',
            'format': 'xml',
            'hoursBeforeNow':1,
            'mostRecent':'true',
            'stationString':'KOAK',
        }
    }
#    'weather': {
#        'url': 'http://forecast.weather.gov/MapClick.php',
#        'args': {
#            'lat': 37.8717
#            'lon': -122.272,
#            'unit': 0,
#            'lg': 'english',
#            'FcstType': 'dwml'
#        }
#    }
}

if __name__ == '__main__':

    shifter = bb595.bb595()
    disp = lcd.LCD(shifter,'20x4')
    disp.begin()
    disp.clear()
    disp.backlight(0)

    valves = triacs.Triacs(shifter)
    valves.enable(True)
    valves.set(0);
    cal = GoogleCalendarReader.GoogleCalendarReader(config)
    cal.get_credentials()
    cal.get_service()

    if True:
        spr = SpinklerTimer.SpinklerTimer(config,cal,valves,disp)
        spr.run()

