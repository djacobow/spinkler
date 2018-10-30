#!/usr/bin/env python3

class Triacs(object):
    def __init__(self,shifter):
        self.sh8 = shifter

    def set(self,v):
        self.sh8.send8(v & 0xff, 'triacs')

