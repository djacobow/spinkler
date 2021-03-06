#!/usr/bin/env python3

import platform 
import datetime
import time
import json
from drivers.disp import update_display
from drivers.disp import RotatingString
import metar

def toJS(x):
    return json.dumps(x,indent=2, sort_keys=True, default=repr)

class SpinklerTimer(object):
    def __init__(self, config, calendar, mailer, valves=None, lcd=None):
        self.config = config
        self.cal = calendar
        self.mailer = mailer
        self.valves = valves
        self.lcd = lcd
        self.next_ev = None
        self.running_ev = None
        self.keep_running = False
        self.watering = False
        self.steps = None
        self.results = {}
        self.zone_bitmap = 0
        self.psr_running = None
        self.weather = metar.Metar()

    def zone_start(self,zones):
        for zone in zones:
            self.zone_bitmap |= 0x1 << (zone-1)
        if self.valves:
            self.valves.set(self.zone_bitmap)
        print('zone_start() : {:x}'.format(self.zone_bitmap))
    def zone_stop(self,zones):
        for zone in zones:
            self.zone_bitmap &= ~(0x1 << (zone-1))
        if self.valves:
            self.valves.set(self.zone_bitmap)
        print('zone_stop() : {:x}'.format(self.zone_bitmap))
    def zone_clear(self):
        self.zone_bitmap = 0
        if self.valves:
            self.valves.set(self.zone_bitmap)
        print('zone_clear()')

    def check_for_new(self,now):
        print('check_for_new()')
        ev = self.cal.get_next_event()
        old_no_exist = self.next_ev is None
        ids_different  = ev is not None and self.next_ev is not None and ev['id'] != self.next_ev['id']
        upds_different = ev is not None and self.next_ev is not None and ev['updated'] != self.next_ev['updated']

        replace = old_no_exist or ids_different or upds_different

        self.last_cal_check = now
        if replace:
            print('new_next_event: {}'.format(toJS(ev)))
            self.next_ev = ev
            return ev
        else:
            return None

    def cancel_watering(self,now):
        print('cancel_watering()')
        if self.steps is not None:
            self.steps['in_progress']['status'] = 'aborted'
            self.steps['in_progress']['abort_time'] = now
            for step in self.steps['to_do']:
                step['status'] = 'aborted'
                step['abort_time'] = now
        self.complete_watering(now)

    def complete_watering(self,now):
        print('complete_watering()')
        self.zone_clear()
        self.psr_running = None
        self.steps['done'].append({'all_stop': now})
        self.results['ev'] = self.running_ev
        self.results['steps'] = self.steps
        self.results['uname'] = platform.uname()
        if self.steps.get('skip_reason',None):
            self.results['event_disposition'] = 'skipped'

        if self.weather:
            rweather = self.results.get('weather',None)
            if rweather:
                rweather['at_end'] = self.weather.getAll()

        self.mailer.send(' '.join(['watering results',now.isoformat()]), toJS(self.results))
        print('watering_results: {}'.format(toJS(self.results)))
        self.running_ev = None
        self.steps = None
        self.watering = False

    def pre_init_watering(self,now):
        print('pre_init_watering')
        self.results = {}
        self.running_ev = self.next_ev
        self.next_ev = None

        if self.weather:
            self.results['weather'] = {
                'at_start': self.weather.getAll()
            }

        skip_reason = self.should_skip()
        if skip_reason:
            self.skip_watering(now, skip_reason)
        else:
            self.init_watering(now)

        self.watering = True

    def skip_watering(self,now,skip_reason):
        print('skip_watering()')

        self.steps = {
            'to_do': [],
            'in_progress': None,
            'done': [],
            'skipped': self.cal.parse_event(self.running_ev),
            'skip_reason': skip_reason,
        }

    def init_watering(self,now):
        print('init_watering()')

        self.steps = {
            'to_do': self.cal.parse_event(self.running_ev),
            'in_progress': None,
            'done': [],
            'skipped': [],
        }

        psr_cfg = self.config.get('psr',None)
        if psr_cfg and psr_cfg.get('enabled',False):
            psr_zone = psr_cfg.get('zone',None)
            if psr_zone:
                self.zone_start([psr_zone])
                self.psr_running = psr_zone
                self.steps['done'].append({'psr_started': now, 'zone':psr_zone})

    def watering_tick(self,now):
        current_step = self.steps.get('in_progress',None)
        if current_step:
            running = current_step.get('status','queued')
            if running == 'queued':
                if now > current_step['start']:
                    current_step['status'] = 'started'
                    current_step['actual_start'] = now
                    self.zone_start(current_step['zones'])
            elif running == 'started':
                if now > (current_step['start'] + current_step['duration']):
                    current_step['status'] = 'complete'
                    current_step['actual_end'] = now
                    self.zone_stop(current_step['zones'])
                else:
                    remaining = current_step['start'] + current_step['duration'] - now
                    current_step['seconds_remaining'] = int(remaining.total_seconds())
            elif running == 'complete':
                self.steps['done'].append(self.steps['in_progress'])
                self.steps['in_progress'] = None
        else:
            remaining = self.steps.get('to_do',[])
            if len(remaining):
                self.steps['in_progress'] = self.steps.get('to_do').pop(0)
            else:
                self.complete_watering(now)

    def check_ev_exists(self,now):
        ev_still_exists = self.cal.check_exists(self.running_ev['id'])
        self.last_cal_check = now
        print('check_ev_exists() {}'.format(ev_still_exists))
        return ev_still_exists

    def should_skip(self):

        w = self.weather

        if w:
            if w.freezing():
                return { 'reason': "freezing"}
            if w.raining():
                return { 'reason': 'rain', 'inches': w.precip_inches() }
            if w.snowing():
                return { 'reason': 'snow', 'inches': w.precip_inches() }
            if self.config.get('min_watering_temp',None):
                if w.temp() < self.config['min_watering_temp']:
                    return { 'reason': 'too_cold',
                             'temp': w.temp(),
                             'min_temp': self.config['min_watering_temp'] }
        return None


    def stop(self):
        self.keep_running = False
    def run(self):
        print('run()')
        self.keep_running = True
        self.last_cal_check = datetime.datetime.fromtimestamp(0)
        self.last_weather_str = RotatingString('', 20 if self.lcd.size() == '20x4' else 16);
        self.last_weather_check = datetime.datetime.fromtimestamp(0)
        self.last_lcd_restart = datetime.datetime.fromtimestamp(0)
        cal_check_interval = datetime.timedelta(seconds=self.config.get('cal_check_interval',60))
        lcd_restart_interval = datetime.timedelta(seconds=self.config.get('lcd_restart_interval',60))
        weather_check_interval = datetime.timedelta(seconds=self.config.get('weather_check_interval',60))

        while self.keep_running:
            try:
                now = datetime.datetime.utcnow()
                self.lcd.indicator(self.watering);
                if self.watering:
                    if now > (self.last_cal_check + cal_check_interval):
                        ev_still_exists = self.cal.check_exists(self.running_ev['id'])
                        self.last_cal_check = now
                        if not ev_still_exists:
                            self.cancel_watering(now)
                    else:
                        self.watering_tick(now)
                elif self.next_ev:
                    # print('now',now,'next_ev',self.next_ev['start_dt'])
                    if now > self.next_ev['start_dt']:
                        self.pre_init_watering(now)

                if now > (self.last_cal_check + cal_check_interval):
                    self.check_for_new(now)
                # print('last_cal_check',self.last_cal_check)

                if now > (self.last_weather_check + weather_check_interval):
                    fetch_ok = self.weather.fetch(self.config['weather'])
                    if fetch_ok:
                        self.last_weather_check = now
                        self.last_weather_str.set(self.weather.text())

                if self.lcd is not None:
                    zinfo = None
                    cstep = None
                    if self.steps is not None:
                        cstep = self.steps.get('in_progress',None)
                    if cstep:
                        zones = cstep['zones']
                        if zones and len(zones):
                            trem  = cstep.get('seconds_remaining','???')
                            zstr  = ','.join([str(z) for z in zones])
                            zinfo = {'zones':zstr,'remaining':trem,'psr_running':self.psr_running}

                    # this is to occasionally reset the LCD on the occasion
                    # that a voltage spike from the valves causes it to go wiggy
                    if now > (self.last_lcd_restart + lcd_restart_interval):
                        self.lcd.begin()
                        self.lcd.clear()
                        self.last_lcd_restart = now

                    update_display(self.lcd, zinfo, self.next_ev, self.last_weather_str.tick())
            except Exception as e:
                print('Exception!')
                print(repr(e))
                import traceback
                print('\n'.join(traceback.format_tb(e.__traceback__)))

            time.sleep(self.config.get('tick_interval',1))


    
