#!/usr/bin/env python3

import threading
import atexit
from flask import Flask, request, send_from_directory, jsonify
import time
import logging
import json
import GoogleStuff
import SpinklerTimer
import ConfigMarshaller

from drivers import lcd, triacs, bb595

shdata = {
    'count': 0,
}

bgThread = None


def create_spinkler_app():

    cm = ConfigMarshaller.ConfigMarshaller('./base_config.json')
    ga = GoogleStuff.Authinator(cm.getConfig()['google'], 'web')

    cal = GoogleStuff.CalendarReader(cm.getConfig(),ga)
    mailer = GoogleStuff.Mailer(cm.getConfig(), ga)
    app = Flask(__name__)

    shifter = bb595.bb595()
    valves = triacs.Triacs(shifter)

    @app.route('/static/<fname>', methods=['GET'])
    def sendStatic(fname):
        print('sendStatic fname',fname)
        return send_from_directory('./static',fname)

    @app.route('/', methods=['GET'])
    @app.route('/configure', methods=['GET'])
    def send_config_page():
        return sendStatic('config.html')

    @app.route('/valves', methods=['GET'])
    def send_valves_page():
        return sendStatic('valves.html')

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


    @app.route('/vctrl', methods=['GET','POST'])
    def doValves():
        if request.method == 'POST':
            reqdata = request.get_json(force=True)
            pattern = reqdata.get('pattern',0)
            action  = reqdata.get('action','none')
            if action == 'set':
                valves.set(pattern)
            elif action == 'setbits':
                valves.setBits(pattern)
            elif action == 'clrbits':
                valves.clrBits(pattern)
            else:
                pass
        return jsonify({"current":valves.get()})



    # try to load Google credentials
    c = ga.load_credentials_from_disk()

    disp    = lcd.LCD(shifter,'20x4')
    disp.begin()
    disp.clear()
    disp.backlight(0)

    valves.enable(True)
    valves.set(0);

    spr = SpinklerTimer.SpinklerTimer(cm.getConfig(),cal,mailer,valves,disp)

    def interrupt():
        spr.stop()

    bgThread = threading.Thread(target=spr.run)
    bgThread.start()

    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
    return app


spinkler_app = create_spinkler_app()
