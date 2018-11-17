#!/usr/bin/env python3

import os
import json
import GoogleStuff 

if __name__ == '__main__':

    with open('./spconfig.json') as fh:
        config = json.load(fh)
        ga  = GoogleStuff.Authinator(config['google'])
        ga.get_credentials()
        cal = GoogleStuff.CalendarReader(config,ga)
        cal.show_calendars()
