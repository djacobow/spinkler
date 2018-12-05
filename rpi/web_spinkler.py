#!/usr/local/bin/python3

import threading
import atexit
from flask import Flask, request, send_from_directory, jsonify
import time
import logging
import json
import GoogleStuff
import SpinklerTimer

from drivers import lcd, triacs, bb595

shdata = {
    'count': 0,
}

bgThread = None

class ConfigMarshaller(object):
    def __init__(self,base_fn,user_fn):

        with open(base_fn, 'r') as f:
            self._config = json.load(f)

        self._paths = {}
        for changeable in self._config['config_ui_changeables']:
            path = changeable.get('path',None)
            if path:
                self._paths[path] = changeable

        with open(self._config['user_config_fn'], 'r') as f:
            overrides = json.load(f);
            for override in overrides:
                self.setV(override['path'],override['value'])
            
    def getConfig(self):
        return self._config

    def getV(self, changeable):
        path = changeable.get('path',None)
        if path:
            chunks = path.split('/')
            v = self._config
            for chunk in chunks:
                v = v.get(chunk,None)
            return v
        return None

    def setV(self, path, value):
        if self._paths.get(path,None) is not None:
            chunks = path.split('/')
            t = self._config
            for i in range(len(chunks)-1):
                t = t[chunks[i]]
            t[chunks[-1]] = value

    def dcopy(self, i):
        return { k:v for (k,v) in i.items() }

    def mergeChanges(self,indata):
        print(indata)
        for datum in indata:
            path = datum.get('path',None)
            if path and path in self._paths:
                self.setV(path,datum.get('value',None))

    def saveConfig(self):
        rv = []
        for changeable in self._config['config_ui_changeables']:
            v = self.getV(changeable);
            path = changeable.get('path',None)
            if path:
                rv.append({'path':path,'value':v});
        with open(self._config['user_config_fn'], 'w') as ofh:
            ofh.write(json.dumps(rv,sort_keys=True,indent=2))


    def getValues(self):
        rv = []
        for changeable in self._config['config_ui_changeables']:
            v = self.getV(changeable)
            o = self.dcopy(changeable)
            o['value'] = v
            rv.append(o)
        return rv





def create_spinkler_app():

    cm = ConfigMarshaller('./base_config.json','./user_config.json')
    ga = GoogleStuff.Authinator(cm.getConfig()['google'])

    cal = GoogleStuff.CalendarReader(cm.getConfig(),ga)
    mailer = GoogleStuff.Mailer(cm.getConfig(), ga)
    app = Flask(__name__)

    def interrupt():
        global bgThread
        bgThread.cancel()

    @app.route('/static/<fname>', methods=['GET'])
    def sendStatic(fname):
        print('sendStatic fname',fname)
        return send_from_directory('./static',fname)

    @app.route('/', methods=['GET'])
    @app.route('/configure', methods=['GET'])
    def send_config_page():
        return sendStatic('config.html')

    @app.route('/config', methods=['GET'])
    def send_config():
        return jsonify(cm.getValues())

    @app.route('/config', methods=['POST'])
    def save_config():
        cfgdata = request.get_json(force=True)
        cm.mergeChanges(cfgdata);
        cm.saveConfig()
        return jsonify({'result':'ok'})

    @app.route('/storeauth', methods=['POST'])
    def storeauth():
        auth_code = request.get_data()
        ga.store_credentials_from_web(auth_code)
        return 'OK'

    @app.route('/oauth2callback', methods=['GET'])
    def loginSuccess():
        return 'Maybe that worked?'

    @app.route('/login', methods=['GET'])
    def splatLogin():
        print('splatLogin')
        return sendStatic('login.html')

    @app.route('/calendars', methods=['GET'])
    def getCalendars():
        res = cal.get_calendars()
        return jsonify(res)
        
    @app.route('/whoami', methods=['GET'])
    def whoami():
        cr = ga.get_credentials()
        if cr:
            return jsonify(cr.id_token)
        return '[]'

    @app.route('/count', methods=['GET'])
    def get_count():
        print(request.args.get('foo','_no_foo'))
        return 'count is {}'.format(shdata['count'])

    # try to load Google credentials
    c = ga.load_credentials_from_disk()

    shifter = bb595.bb595()
    disp    = lcd.LCD(shifter,'20x4')
    disp.begin()
    disp.clear()
    disp.backlight(0)

    valves = triacs.Triacs(shifter)
    valves.enable(True)
    valves.set(0);

    if False:
        spr = SpinklerTimer.SpinklerTimer(cm.get_config(),cal,mailer,valves,disp)
        bgThread = threading.Thread(target=spr.run)
        bgThread.start()

    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
    return app

spinkler_app = create_spinkler_app()
