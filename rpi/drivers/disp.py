#!/usr/bin/env python3

import datetime
import time
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def pad16(s,left = None):
    if left:
        return '{:16.16}'.format(s)
    else:
        return '{:>16}'.format(s)

def timestr(dt):
    fstr = '{0:02}/{1:02} {2:02}:{3:02}'
    tstr = fstr.format(
        dt.month,    
        dt.day,
        dt.hour,
        dt.minute)
    return tstr

def update_display(lcd, zinfo = None, next_ev = None):
    now = datetime.datetime.now()

    lcd.gotoxy(0,0)
    if (now.second < 10):
        lcd.pr(pad16(get_ip()))
    else:
        lcd.pr(pad16('now: ' + timestr(now)))

    if zinfo is not None:
        zstr = 'Zone {} ({}s)'.format(zinfo['zones'],zinfo['remaining'])
        lcd.gotoxy(0,1)
        lcd.pr(pad16(zstr,True))
    elif next_ev is not None:
        nstr = 'nxt: ' + timestr(next_ev['start_dt'])
        lcd.gotoxy(0,1)
        lcd.pr(pad16(nstr))
    else:
        lcd.pr(pad16('SPinkler!'))

        

if __name__ == '__main__':
    import bb595
    import lcd
    import random
    s8 = bb595.bb595()
    lcd = lcd.LCD(s8)
    lcd.begin()
    lcd.clear()
    lcd.backlight(0)
    last = datetime.datetime.now()

    while True:
        now = datetime.datetime.now()
        if now > (last + datetime.timedelta(seconds=1)):
            update_display(lcd,{'zones':'3', 'remaining':4922},None)
            last = now
        else:
            s8.send8(random.randrange(256),'triacs')
  
