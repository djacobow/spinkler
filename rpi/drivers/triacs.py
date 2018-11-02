#!/usr/bin/env python3

class Triacs(object):
    def __init__(self,shifter):
        self.sh8 = shifter

    def set(self,v):
        self.sh8.send8(v & 0xff, 'triacs')
    def enable(self,en):
        self.sh8.triac_en(en)

if __name__ == '__main__':
    import time
    import bb595
    s8 = bb595.bb595()
    t = Triacs(s8)
    t.enable(True)
    o = 0x1
    while True:
        t.set(o)
        if o == 0x80:
            o = 0x1
        else:
            o <<= 1
        time.sleep(0.250)
        print('o',o)


