#!/usr/bin/env python3

import os
import datetime
import re
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from dateutil.parser import parse as parsedate

class GoogleCalendarReader(object):
    _config = None
    def __init__(self, config):
        self._last_cred_refresh = 0
        self._calservice = None
        self._credentials = None
        self._config = config

    def get_credentials(self):
        if self._credentials and not self._credentials.invalid:
            return self._credentials

        credentials = None

        class MyFlags(object):
            logging_level = 'WARNING'
            noauth_local_webserver = True
            auth_host_port = [8080,8090]
            auth_host_name = 'localhost'
            def __init__(self):
                pass

        flags = MyFlags()

        credential_dir = self._config['google']['credentials_dir']
        if not re.match(r'^/', credential_dir):
            credential_dir = path.join(os.getcwd(), credential_dir)

        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_file_name = self._config['google']['credentials_file']
        credential_path = os.path.join(credential_dir, credential_file_name)

        store = file.Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(
                self._config['google']['client_secrets'],
                self._config['google']['scopes'])
            flow.user_agent = 'Sprinkler Calendar Checker'
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run_flow(flow, store)
            print('Storing credentials to: ' + credential_path)

        self._last_cred_refresh = datetime.datetime.now()
        self._credentials = credentials
        return credentials

    def refresh_credentials(self):
        """refresh googld credentials"""
        now = helpers.get_now()
        if (now > (self._last_cred_refresh +
                   self._config['google']['refresh_period'])):
            print('refreshing Google credentials')
            self.get_credentials(self._config)
            self._last_cred_refresh = datetime.datetime.now()

    def get_service(self):
        if self._calservice:
            return self._calservice

        if self._credentials:
            self._calservice = build('calendar','v3',
                http=self._credentials.authorize(http=Http()),
                cache_discovery=False)
        else:
            print('-error- no google credentials')
        return self._calservice

    def get_calendars(self):
        page_token = None
        olist = []
        if self._calservice:
            done = False
            while not done:
                page_list = self._calservice.calendarList().list(pageToken=page_token).execute()
                olist += page_list['items']
                page_token = page_list.get('nextPageToken')
                if not page_token:
                    done = True
        else:
            print('-error-','no calendar service')

        return olist

    def show_calendars(self):
        cals = self.get_calendars()
        f = '{:30} {:45}'
        print(f.format('summary','ID'))
        print(f.format('----------','-----------'))
        for cal in cals:
            print(f.format(cal['summary'],cal['id']))

    def gapi_toisodate(self,d):
        return d.isoformat() + 'Z'
    
    def gapi_fromisodate(self,ds):
        return parsedate(ds).replace(tzinfo=None)

    def check_exists(self,evid):
        ev = self._calservice.events().get(calendarId=self._config['sprinkler_calendar'], eventId=evid).execute()
        if not ev:
            return False
        elif ev['status'] != 'confirmed':
            print('ev status',ev['status'])
            return False
        return True


    def debugEVs(self,evs):
        evs.sort(key=lambda x: x['start']['dateTime'])
        for ev in evs:
            print('{} {} {} {}'.format(
                ev['summary'],
                ev['start']['dateTime'],
                ev['end']['dateTime'],
                ev['id']))

    def get_next_event(self):
        now = datetime.datetime.utcnow()
        nowstr = self.gapi_toisodate(now)
        events = self._calservice.events().list(calendarId=self._config['sprinkler_calendar'],
                timeMin=nowstr,timeZone='UTC',maxResults=10,singleEvents=True,).execute()

        # print('QUERY')
        # self.debugEVs(events['items'])

        if events and len(events['items']):
            events = list(filter(lambda ev: self.gapi_fromisodate(ev['start']['dateTime']).replace(tzinfo=None) >= now and re.match(r'watering',ev['summary']), events['items']))
            print('AFTER FILTER')
            self.debugEVs(events)
            if len(events):
                ev = events[0]
                ev['start_dt'] = self.gapi_fromisodate(ev['start']['dateTime'])
                return ev
        return None


    def parse_event(self, ev):
        if ev is None or not len(ev):
            return None

        current_start = ev['start_dt']
        
        if ev.get('description',None) is None:
            print('-warning- no event description')
            return None

        m0 = re.finditer(r'(run((\s*\d+,?)+)\sduration (\d*[\.:]?\d+))+',ev['description'])
        steps = []
        for m in m0:
            zones = [ int(x) for x in m.group(2).strip().split() ]
            tstr = m.group(4)
            cmatch = re.search(r'(\d*):(\d*)',m.group(4))
            duration = None
            if cmatch:
                h = cmatch.group(1)
                m = cmatch.group(2)
                if len(h):
                    h = int(h)
                    m = int(m)
                else:
                    h = 0
                    m = int(m)
                duration = datetime.timedelta(hours=h,minutes=m)
            else:
                duration = datetime.timedelta(hours=float(tstr))

            if duration is not None:
                steps.append({'zones':zones,'duration':duration,'start':current_start})
                current_start += duration + datetime.timedelta(seconds=self._config['pause_time'])

        return steps






