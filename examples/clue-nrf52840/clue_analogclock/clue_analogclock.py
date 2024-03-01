from kds_analogclock.analogclock import AnalogClock
from adafruit_pcf8523.pcf8523 import PCF8523
import board
import rtc
import busio

class Clue_AnalogClock(AnalogClock):
    def __init__(self):
        super().__init__()
        rtc = None
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
    
    def connectNetwork(self):
        if self.rtc == None:
            myI2C = busio.I2C(board.SCL, board.SDA)
            self.rtc = PCF8523(myI2C)
        t = self.rtc.datetime
        self.rtc.RTC().datetime = t
