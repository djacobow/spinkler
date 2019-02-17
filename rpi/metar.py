#!/usr/bin/env python3

import urllib.request
import urllib.parse
import xmltodict
import json
import re

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

    def __init__(self):
        pass
    def fetch(self, cfg):
        data = _fetch(cfg)
        if data and data.get('response',None) and data['response'].get('data',None) and data['response']['data'].get('METAR',None):

            metar = data['response']['data']['METAR']
            if isinstance(metar,list):
                # get data as newest first
                self.data = sorted(metar, key=lambda x: x['observation_time'], reverse=True)
                # print(jss(self.data))
            else:
                self.data = [ metar ]

            self.latest = self.data[0]
            return self.data
        else:
            return None

    def text(self):
        return self.latest['raw_text']

    def _get_var(self,vn,mode='last_number'):
        metars_to_sum = [ self.latest ]

        if (mode == 'sum' or mode =='average'):
            metars_to_sum = self.data
        
        rv = None 

        for metar in metars_to_sum:
            t = metar.get(vn,None)
            if t:
                if mode == 'last_text':
                    rv = t
                elif mode == 'min':
                    t = float(t)
                    if rv is None or t < rv:
                        rv = t
                elif mode == 'max':
                    t = float(t)
                    if rv is None or t > rv:
                        rv = t
                else:
                    if rv is None:
                        rv = 0
                    rv += float(t)
            else:
                pass

        if mode == 'average':
            rv /= len(metars_to_sum)

        return rv

    def temp(self):
        return self._get_var('temp_c')
    def precip_inches(self,sum24=False):
        rv = self._get_var('precip_in', 'sum' if sum24 else 'last_number')
        if rv is None:
            return 0
        return rv
    def wx(self):
        return self._get_var('wx_string','last_text')
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
    def snowing(self):
        wx = self.wx()
        if wx is not None:
            m = re.search(r'SN',wx)
            if m:
                return True
        return False
    def getAll(self):
        return self.data if self.data else None

#def get(cfg):
#    data = _fetch(cfg)
#    if data and data.get('response',None) and data['response'].get('data',None) and data['response']['data'].get('METAR',None):
#
#        metar = data['response']['data']['METAR']
#        return Metar(metar)


if __name__ == '__main__':
    wcfg = {
        'url': 'https://www.aviationweather.gov/adds/dataserver_current/httpparam',
        'args': {
            'dataSource': 'metars',
            'requestType': 'retrieve',
            'format': 'xml',
            'hoursBeforeNow':24,
            'mostRecent':'true',
            'stationString':'KOAK',
        }
    }

    m = Metar()
    m.fetch(wcfg)
    print('wx str: {}'.format(m.text()))
    print('temp  : {}'.format(m.temp()))
    print('wx    : {}'.format(m.wx()))
    print('freez : {}'.format(m.freezing()))
    print('precip: {}'.format(m.precip_inches()))
    print('precip24: {}'.format(m.precip_inches(True)))

