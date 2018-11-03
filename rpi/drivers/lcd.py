#!/usr/bin/env python3

import time
import random
import json
from drivers import bb595

class LCD:
    def __init__(self, shifter, ltype = '16x2'):
        self.shifter = shifter
        self.ltype = ltype
        self.LED_MASK       = 0x01
        self.BACKLIGHT_MASK = 0x02
        self.RS_MASK        = 0x04
        self.E_MASK         = 0x08
        self.NIB_MASK       = 0xf0

        self.LCD_CLEARDISPLAY  = 0x01
        self.LCD_RETURNHOME  = 0x02
        self.LCD_ENTRYMODESET  = 0x04
        self.LCD_DISPLAYCONTROL  = 0x08
        self.LCD_CURSORSHIFT  = 0x10
        self.LCD_FUNCTIONSET  = 0x20
        self.LCD_SETCGRAMADDR  = 0x40
        self.LCD_SETDDRAMADDR  = 0x80

        self.LCD_ENTRYRIGHT  = 0x00
        self.LCD_ENTRYLEFT  = 0x02
        self.LCD_ENTRYSHIFTINCREMENT  = 0x01
        self.LCD_ENTRYSHIFTDECREMENT  = 0x00

        self.LCD_DISPLAYON  = 0x04
        self.LCD_DISPLAYOFF  = 0x00
        self.LCD_CURSORON  = 0x02
        self.LCD_CURSOROFF  = 0x00
        self.LCD_BLINKON  = 0x01
        self.LCD_BLINKOFF  = 0x00

        self.LCD_DISPLAYMOVE  = 0x08
        self.LCD_CURSORMOVE  = 0x00
        self.LCD_MOVERIGHT  = 0x04
        self.LCD_MOVELEFT  = 0x00

        self.LCD_8BITMODE  = 0x10
        self.LCD_4BITMODE  = 0x00
        self.LCD_2LINE  = 0x08
        self.LCD_1LINE  = 0x00
        self.LCD_5X10DOTS  = 0x04
        self.LCD_5X8DOTS  = 0x00

        self.dfn           = (self.LCD_4BITMODE | self.LCD_2LINE | self.LCD_5X8DOTS)
        self.dctrl         = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.curr595       = 0

    def size(self):
        return self.ltype

    def shift8(self):
        flipped = bb595.flip8(self.curr595)
        self.shifter.send8(flipped)

    def setclrmask(self,msk,setclr):
        if setclr:
            self.curr595 |= msk
        else:
            self.curr595 &= ~msk

    def backlight(self,on):
        self.setclrmask(self.BACKLIGHT_MASK,not on)
        self.shift8()

    def indicator(self,on):
        self.setclrmask(self.LED_MASK, on)
        self.shift8()

    def write4(self,v4):
        #print('    write4 {:x}'.format(v4))

        self.curr595 &= ~self.NIB_MASK 
        self.curr595 |= (bb595.flip4(v4) << 4)

        self.setclrmask(self.E_MASK,0)
        self.shift8()
        self.setclrmask(self.E_MASK,1)
        self.shift8()
        self.setclrmask(self.E_MASK,0)
        self.shift8()
  
    def send(self, value, mode):
        self.setclrmask(self.RS_MASK,mode)
        self.shift8()

        self.write4((value >> 4) & 0x0f)
        self.write4(value & 0xf)

    def command(self,v):
        #print('command: {:x}'.format(v))
        self.send(v,0)

    def write(self,v):
        #print('write  : {:x}'.format(v))
        self.send(v,1)

    def clear(self):
        #print('clear')
        self.command(self.LCD_CLEARDISPLAY)
        time.sleep(0.003)

    def home(self):
        #print('home')
        self.command(self.LCD_RETURNHOME)
        time.sleep(0.002)

    def _setdctrl(self,what,on):
        if on:
            self.dctrl |= what
        else:
            self.dctrl &= ~what
        self.command(self.LCD_DISPLAYCONTROL | self.dctrl)
       
    def display(self,on):
        self._setdctrl(self.LCD_DISPLAYON,on)
    def cursor(self,on):
        self._setdctrl(self.LCD_CURSORON,on)
    def blink(self,on):
        self._setdctrl(self.LCD_BLINKON,on)

    def gotoxy(self,x=0,y=0):
        rowoffsets = []
        if self.ltype == '20x4':
            y = y % 4
            x = x % 20
            rowoffsets = [0,0x40,0 + 20, 0x40 + 20]
        else:
            y = y % 2
            x = x % 16
            rowoffsets = [0,0x40]

        self.command(self.LCD_SETDDRAMADDR | (x + rowoffsets[y]))
 
    def begin(self):
        #print('begin')

        # set RS and E pins low
        self.setclrmask(self.RS_MASK,0)
        self.setclrmask(self.E_MASK,0)
        self.shift8()

        # try to get into 4b mode
        for x in range(3):
            self.write4(0x03)
            time.sleep(0.005)

        self.write4(0x02)

        self.command(self.LCD_FUNCTIONSET | self.dfn)
        self.display(1)
        self.clear()
        self.dmode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.command(self.LCD_ENTRYMODESET | self.dmode)

    def pr(self,s):
        for i in range(len(s)):
            ch = s[i]
            chv = ord(ch)
            self.write(chv)
    


if __name__ == '__main__':
    import datetime
    import bb595

    s8 = bb595.bb595()
    lcd = LCD(s8)
    lcd.backlight(0)
    lcd.begin()
    lcd.pr('Hello, world!')
    i = 0
    lcd.clear()
    while True:
        lcd.gotoxy(0,1)
        lcd.pr('{}'.format(datetime.datetime.now().isoformat()))
        i+= 1
        time.sleep(0.3)
