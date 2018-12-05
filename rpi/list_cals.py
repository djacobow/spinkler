#!/usr/bin/env python3

import os
import json
import GoogleStuff 
import ConfigMarshaller

if __name__ == '__main__':

    cm = ConfigMarshaller.ConfigMarshaller('./base_config.json')
    config = cm.getConfig()
    ga  = GoogleStuff.Authinator(config['google'],'console')
    ga.load_credentials_from_disk()
    if not ga.get_credentials():
        ga.get_credentials_by_console()

    cal = GoogleStuff.CalendarReader(config,ga)
    cal.show_calendars()
