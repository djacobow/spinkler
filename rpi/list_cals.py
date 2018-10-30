#!/usr/bin/env python3

import os
import GoogleCalendarReader
config = {
    'google': {
        'refresh_period': 3600,                                                 
        'credentials_file': 'creds.json',                          
        'credentials_dir': os.path.expanduser('~') + '/.spinkler',
        'client_secrets': 'spinkler_client_secrets.json',                                
        'scopes': ['https://www.googleapis.com/auth/calendar.readonly'],                    
    },
}

if __name__ == '__main__':

    cal = GoogleCalendarReader.GoogleCalendarReader(config)
    cal.get_credentials()
    cal.get_service()
    cal.show_calendars()
