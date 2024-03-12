from kds_analogclock.analogclock import AnalogClock
import board
import busio
#import adafruit_pcf8523
from adafruit_pcf8523.pcf8523 import PCF8523
import rtc
import time

class Macropad_AnalogClock(AnalogClock):
    def __init__(self):
        super().__init__()

        self.circleColor = self.WHITE
        self.centerColor = self.WHITE
        self.tickColor = self.WHITE
        self.secColor = self.WHITE
        self.minColor = self.WHITE
        self.hourColor = self.WHITE
        self.backColor = self.BLACK
        self.circleFillColor = self.BLACK
        self.display = board.DISPLAY
        self.display.auto_refresh = False

        self.pre_calc()

        self.drawStatic(self.display)
        self.drawClock(self.display)
        self.connectNetwork()

    def connectNetwork(self):
        if self.my_rtc == None:
            myI2C = busio.I2C(board.SCL, board.SDA)
            self.my_rtc = PCF8523(myI2C)
        t = self.my_rtc.datetime
        print("Time from connect network: ", t)
        rtc.set_time_source(self.my_rtc)
        curr_time = time.localtime()
        print("Curr time: ", curr_time)
