from kds_analogclock.analogclock import AnalogClock
import board
import adafruit_pcf8523
import rtc

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

    def connectNetwork(self):
        if self.rtc == None:
            myI2C = busio.I2C(board.SCL, board.SDA)
            self.rtc = adafruit_pcf8523.PCF8523(myI2C)
        t = self.rtc.datetime
        rtc.RTC().datetime = t
