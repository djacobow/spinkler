#!/usr/bin/env python3

from drivers import bb595

class Triacs(object):
    def __init__(self,shifter):
        self.sh8 = shifter

    def set(self,v):
        chunks = [ (v >> 8) & 0xff, v & 0xff ]

        for chunk in chunks:
            # zones are reverse order of byte
            ch = bb595.flip8(chunk)
            self.sh8.send8(ch & 0xff, 'triacs')

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


