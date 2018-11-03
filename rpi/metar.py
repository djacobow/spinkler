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

def get(cfg):
    data = _fetch(cfg)
    if data and data.get('response',None) and data['response'].get('data',None) and data['response']['data'].get('METAR',None):

        m = data['response']['data']['METAR']['raw_text']
        return m


if __name__ == '__main__':
    wcfg = {
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

    print(get(wcfg))
