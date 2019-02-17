
OUT      = 'out' 
IN       = 'in' 
LOW      = 'low' 
HIGH     = 'high' 
BOARD    = 'board'
PUD_DOWN = 'pud_down'
PUD_UP   = 'pud_up'

def setmode(pin_order):
    return
    print('DummyGPIO setupmode order={}'.format(pin_order))

def setup(pin,mode,pull_up_down = None):
    return
    print('DummyGPIO setup pin={}, direction={}, mode={}'.format(pin,mode,pull_up_down))

def output(pin,value):
    return
    print('DummyGPIO output pin={}, value={}'.format(pin,value))

