
real_gpio = False
try:
    import RPi.GPIO as GPIO
    real_gpio = True
except Exception as e:
    print("Using DUMMY GPIO - is RPi.GPIO installed?")
    from drivers import dummy_gpio as GPIO

def flip8(b):
    b = ((b >> 4) & 0x0f) | ((b << 4) & 0xf0)
    b = ((b >> 2) & 0x33) | ((b << 2) & 0xcc)
    b = ((b >> 1) & 0x55) | ((b << 1) & 0xaa)
    return b
  
def flip4(n):
    n = ((n >> 2) & 0x33) | ((n << 2) & 0xcc)
    n = ((n >> 1) & 0x55) | ((n << 1) & 0xaa)
    return n


class bb595:

    def __init__(self):
        self.SCLK      = 11
        self.DOUT      = 13
        self.LCLK_LCD  = 15
        self.LCLK_TRC  = 16 
        self.TRC_ENB   = 18
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.SCLK,     GPIO.OUT)
        GPIO.setup(self.DOUT,     GPIO.OUT)
        GPIO.setup(self.LCLK_LCD, GPIO.OUT)
        GPIO.setup(self.LCLK_TRC, GPIO.OUT)
        GPIO.setup(self.TRC_ENB,  GPIO.OUT)
        GPIO.output(self.TRC_ENB, GPIO.HIGH)

    def halfclock(self):
        # it seems that the 595 can keep up with python going
        # as fast as it can
        pass

    def triac_en(self,en):
        if en:
            GPIO.output(self.TRC_ENB,GPIO.LOW)
        else:
            GPIO.output(self.TRC_ENB,GPIO.HIGH)

    def shift8(self,inb):
        GPIO.output(self.SCLK,GPIO.HIGH)
        for i in range(8):
            bit = inb & 0x1
            # print(i,bit)
            GPIO.output(self.DOUT,GPIO.HIGH if bit else GPIO.LOW)
            GPIO.output(self.SCLK,GPIO.LOW)
            self.halfclock()
            inb >>= 1
            GPIO.output(self.SCLK,GPIO.HIGH)
            self.halfclock()

    def send8(self,inb,who='lcd'):
        self.shift8(inb)
        use_triac = who is not None and who == 'triacs'
        lpin = self.LCLK_TRC if use_triac else self.LCLK_LCD
        GPIO.output(lpin,GPIO.LOW)
        self.halfclock()
        GPIO.output(lpin,GPIO.HIGH)         
        self.halfclock()
        GPIO.output(lpin,GPIO.LOW)
        self.halfclock()
            
    def __del__(self):
        print('closing and setting as inputs');
        GPIO.setup(self.SCLK,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.DOUT,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.LCLK_TRC,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.LCLK_LCD,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.TRC_ENB,GPIO.IN, pull_up_down=GPIO.PUD_UP)

