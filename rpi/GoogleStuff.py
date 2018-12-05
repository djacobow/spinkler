#!/usr/bin/env python3

import os
import datetime
import re
import base64
import json
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from dateutil.parser import parse as parsedate
from email.mime.text import MIMEText


class Authinator(object):


    def __init__(self, config, server_type =  'web'):
        self._last_cred_refresh = 0
        self._services = {}
        self._credentials = None
        self._config = config
        self._server_type = server_type

    def cred_path(self):
        credential_dir = self._config['credentials_dir']
        if not re.match(r'^/', credential_dir):
            credential_dir = os.path.join(os.path.expanduser('~'), credential_dir)

        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_file_name = self._config['credentials_file'][self._server_type]
        credential_path = os.path.join(credential_dir, credential_file_name)
        return credential_path

    def store_credentials_from_web(self, auth_code):

        credentials = client.credentials_from_clientsecrets_and_code(
            self._config['client_secret']['web'],
            self._config['scopes'],
            auth_code)

        store = file.Storage(self.cred_path())

        with open(self.cred_path(),'w') as ofh:
            ofh.write(credentials.to_json())
        self._credentials = credentials


    def get_credentials(self):
        if self._credentials and not self._credentials.invalid:
            return self._credentials

        self.load_credentials_from_disk()

        if self._credentials and not self._credentials.invalid:
            return self._credentials

        if self._server_type == 'console':
            return self.get_credentials_by_console()
        return None

    def load_credentials_from_disk(self):
        credentials = None
        try:
            store = file.Storage(self.cred_path())
            credentials = store.get()
        except Exception as e:
            print('exception: {}'.format(repr(e)))

        self._credentials = credentials
        return credentials

    def get_credentials_by_console(self):

        credentials = None

        class MyFlags(object):
            logging_level = 'WARNING'
            noauth_local_webserver = True 
            auth_host_port = [8080,8090]
            auth_host_name = 'localhost'
            def __init__(self):
                pass

        flags = MyFlags()

        store = file.Storage(self.cred_path())
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(
                self._config['client_secret']['console'],
                self._config['scopes'])
            flow.user_agent = 'Sprinkler Calendar Checker'
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run_flow(flow, store)
            print('Storing credentials to: ' + self.cred_path())

        self._last_cred_refresh = datetime.datetime.now()
        self._credentials = credentials
        return credentials

    def refresh_credentials(self):
        """refresh googld credentials"""
        now = helpers.get_now()
        if (now > (self._last_cred_refresh +
                   self._config['refresh_period'])):
            print('refreshing Google credentials')
            self.get_credentials(self._config)
            self._last_cred_refresh = datetime.datetime.now()

    def get_service(self,what = 'calendar'):
        if self._services.get(what,None):
            return self._services[what]

        if self._credentials:
            versions = {
                'calendar': 'v3',
                'gmail': 'v1',
            }
            self._services[what] = build(what,versions.get(what,None),
                http=self._credentials.authorize(http=Http()),
                cache_discovery=False)
            print('created service')
        else:
            print('-error- no google credentials')
            return None
        return self._services[what]




class CalendarReader(object):
    _config = None
    def __init__(self, config, authinator):
        self._config = config
        self._gauth = authinator


    def get_calendars(self):
        page_token = None
        olist = []
        if self._gauth.get_service('calendar'):
            done = False
            while not done:
                page_list = self._gauth.get_service('calendar').calendarList().list(pageToken=page_token).execute()
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
        ev = self._gauth.get_service('calendar').events().get(calendarId=self._config['sprinkler_calendar'], eventId=evid).execute()
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
        nowp24 = now + datetime.timedelta(hours=24)
        nowstr = self.gapi_toisodate(now)
        nowp24str = self.gapi_toisodate(nowp24)

        calservice = self._gauth.get_service('calendar')
        if not calservice:
            return None

        events = calservice.events().list(calendarId=self._config['sprinkler_calendar'],
                timeMin=nowstr,timeMax=nowp24str,timeZone='UTC',maxResults=10,singleEvents=True,).execute()

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





class Mailer(object):
    def __init__(self, config, authinator):
        self._config = config
        self._gauth = authinator

    def send(self, subject, text):
        mcfg = self._config.get('mail')
        if not mcfg or not mcfg.get('send',False):
            print('Not configured to send mail.')
            return
        try:
            gm = self._gauth.get_service('gmail');

            m = MIMEText(text)

            tolist = mcfg.get('to',[])
            if isinstance(tolist, str):
                tolist = [ tolist ]
            m['to']   = ','.join(tolist)
            m['subject'] = subject

            b64_bytes = base64.urlsafe_b64encode(m.as_bytes())
            b64_str   = b64_bytes.decode()
            body = {'raw': b64_str}

            dr = gm.users().drafts().create(userId='me',body={'message': body}).execute()
            print('draft',dr)


            if dr and dr.get('id',None):
                res = gm.users().drafts().send(userId='me', body={'id':dr['id']}).execute()
                print('res',res)
                return res 

        except Exception as e:
            print('An Error occured',e)
            return None
