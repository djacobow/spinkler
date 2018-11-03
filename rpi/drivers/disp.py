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

def padN(s, n = 16, left = None):
    if left:
        return ''.join(['{:',str(n),'.',str(n),'}']).format(s)
    else:
        return ''.join(['{:>',str(n),'}']).format(s)

def timestr(dt,w):
    if w == 20:
        fstr = '{0:3} {1:02}/{2:02} {3:02}:{4:02}:{5:02}'
        weekday = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][dt.weekday()]
        fd = [ weekday, dt.month, dt.day, dt.hour, dt.minute, dt.second]
    else:
        fstr = 'now {0:02}/{1:02} {2:02}:{3:02}'
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
        zstr = 'Zone {} ({}s)'.format(zinfo['zones'],zinfo['remaining'])
        lcd.gotoxy(0,2 if lcd_height == 4 else 1)
        lcd.pr(padN(zstr,True,lcd_width))
    else:
        if lcd_height == 4:
            lcd.gotoxy(0,2)
            lcd.pr(padN('',lcd_width))

    if next_ev is not None:
        if lcd_width == 20:
            nstr = 'Next:'
        else:
            nstr = 'Nxt:'
        nstr += ' ' + timestr(next_ev['start_dt'],16)

        if lcd_height == 4 or zinfo is None:
            lcd.gotoxy(0,1)
            lcd.pr(padN(nstr,lcd_width))

    if lcd_height == 4:
        lcd.gotoxy(0,3)
        lcd.pr(padN('{:20}'.format(wstr),lcd_width,True))

        
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
  
