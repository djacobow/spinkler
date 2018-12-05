#!/usr/bin/env python3

import datetime
import time
import socket
from dateutil import tz

class RotatingString:
    def __init__(self,ins = '', maxw = 0):
        self.iter = 0
        self.maxw = maxw
        self.s = ins
    def set(self,s):
        self.s = s
        self.iter = 0
        return self._rot()

    def _rot(self):
        c = self.iter % len(self.s)
        if not c:
            return self.s

        l = self.s[c:]
        r = self.s[0:c-1]
        rotated = l + r
        if self.maxw:
            return rotated[0:self.maxw-1]
        else:
            return rotated
    def tick(self):
        rv = None
        if self.iter % 2:
            rv = self._rot()
        else:
            rv = self.s

        self.iter += 1
        return rv


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

def padN(s, n = 16, left = None):
    if left:
        return ''.join(['{:',str(n),'.',str(n),'}']).format(s)
    else:
        return ''.join(['{:>',str(n),'}']).format(s)

def zuluToSystem(ind):
    utc = ind.replace(tzinfo=tz.tzutc())
    loc = utc.astimezone(tz.tzlocal())
    return loc
    
def timestr(dt,w):
    if w == 20:
        fstr = '{0:3} {1:02}/{2:02} {3:02}:{4:02}:{5:02}'
        weekday = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][dt.weekday()]
        fd = [ weekday, dt.month, dt.day, dt.hour, dt.minute, dt.second]
    else:
        fstr = '{0:02}/{1:02} {2:02}:{3:02}'
        fd = [ dt.month, dt.day, dt.hour, dt.minute ]

    tstr = fstr.format(*fd)
    return tstr

def update_display(lcd, zinfo = None, next_ev = None, wstr = None):
    now = datetime.datetime.now()

    lcd_size  = lcd.size()
    lcd_width  = 20 if lcd_size == '20x4' else 16
    lcd_height = 4  if lcd_size == '20x4' else 2

    lcd.gotoxy(0,0)
    if (now.second < 10):
        lcd.pr(padN(get_ip(),lcd_width))
    else:
        lcd.pr(padN(timestr(now,lcd_width),lcd_width))

    if zinfo is not None:
        zstr = 'Zone {} ({}s) {}'.format(zinfo['zones'],zinfo['remaining'],'P' if zinfo['psr_running'] else '')
        lcd.gotoxy(0,2 if lcd_height == 4 else 1)
        lcd.pr(padN(zstr,lcd_width,True))
    else:
        if lcd_height == 4:
            lcd.gotoxy(0,2)
            lcd.pr(padN('',lcd_width))

    if next_ev is not None:
        nstr = 'Nxt:'
        if lcd_width == 20:
            nstr = 'Next:'
        nstr += ' ' + timestr(zuluToSystem(next_ev['start_dt']),16)

        if lcd_height == 4 or zinfo is None:
            lcd.gotoxy(0,1)
            lcd.pr(padN(nstr,lcd_width))

    if wstr and lcd_height == 4:
        lcd.gotoxy(0,3)
        lcd.pr(padN('{:20}'.format(wstr),lcd_width,True))

        
if __name__ == '__main__':

    s = 'This is a very long string that must be rotated'
    r = RotatingString(s,16)
    for i in range(50):
        print(r.tick())

    if False:
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
  
