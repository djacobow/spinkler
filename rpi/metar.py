#!/usr/bin/env python3

import urllib.request
import urllib.parse
import xmltodict
import json

def _fetch(cfg):
    try:
        cfgstr = urllib.parse.urlencode(cfg['args'])
        req = urllib.request.Request(cfg['url'] + '?' + cfgstr)
        with urllib.request.urlopen(req) as response:
            data_xml = response.read()
            data = xmltodict.parse(data_xml)
            return data
    except Exception as e:
        return None

def jss(x):
    return json.dumps(x,indent=2,sort_keys=True)

class Metar:
    def __init__(self,data):
        self.data = data 
    def text(self):
        return self.data['raw_text']
    def _get_var(self,vn,number = True):
        t = self.data.get(vn,None)
        if t and number:
            t = float(t)
        return t
    def temp(self):
        return self._get_var('temp_c')
    def rain_inches(self):
        return self._get_var('rain_in')
    def wx(self):
        return self._get_var('wx_string',False)
    def freezing(self):
        t = self.temp()
        if t is not None:
            return t <= 0
        return False
    def raining(self):
        wx = self.wx()
        if wx is not None:
            m = re.search(r'RA',wx)
            if m:
                return True
        return False

def get(cfg):
    data = _fetch(cfg)
    if data and data.get('response',None) and data['response'].get('data',None) and data['response']['data'].get('METAR',None):

        metar = data['response']['data']['METAR']
        return Metar(metar)


if __name__ == '__main__':
    wcfg = {
        'url': 'https://www.aviationweather.gov/adds/dataserver_current/httpparam',
        'args': {
            'dataSource': 'metars',
            'requestType': 'retrieve',
            'format': 'xml',
            'hoursBeforeNow':1,
            'mostRecent':'true',
            'stationString':'KMBS',
        }
    }

    print(get(wcfg))
