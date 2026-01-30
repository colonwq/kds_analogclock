from kds_analogclock.analogclock import AnalogClock
from adafruit_pcf8523.pcf8523 import PCF8523
import board
import rtc
#import busio
#import time

class Clue_AnalogClock(AnalogClock):
    def __init__(self):
        super().__init__()
        my_rtc = None

        self.circleColor = self.WHITE
        self.centerColor = self.WHITE
        self.tickColor = self.RED
        self.secColor = self.RED
        self.minColor = self.ORANGE
        self.hourColor = self.BLUE
        self.backColor = self.GREY77
        self.circleFillColor = self.BLACK

        self.display = board.DISPLAY
        self.display.auto_refresh = False

        self.pre_calc()

        self.drawStatic(self.display)
        self.drawClock(self.display)
        self.connectNetwork()
    
    def connectNetwork(self):
        if self.my_rtc == None:
            self.my_rtc = PCF8523(board.STEMMA_I2C())
        t = self.my_rtc.datetime
        #print("Time from connectNetwork(with rtc): ", t)
        rtc.set_time_source(self.my_rtc)
        #curr_time = time.localtime()
        #print("Curr time: ", curr_time)
