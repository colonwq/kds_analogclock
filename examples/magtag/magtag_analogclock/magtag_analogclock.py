'''
This is a AnalogClock derived class which is updated
for the magtag eink portal
https://www.adafruit.com/product/4800

'''

from kds_analogclock.analogclock import AnalogClock
from adafruit_magtag.magtag import MagTag

class Magtag_AnalogClock(AnalogClock):
    def __init__(self):
        super().__init__()

        self.circleColor = self.BLACK
        self.centerColor = self.BLACK
        self.tickColor = self.BLACK
        self.secColor = self.BLACK
        self.minColor = self.BLACK
        self.hourColor = self.BLACK
        self.backColor = self.WHITE
        self.circleFillColor = self.WHITE

        self.portal = MagTag()
        self.display = self.portal.display

        self.pre_calc()
        self.drawStatic(self.display)
        self.drawClock(self.display)
        self.connectNetwork()

    def update(self, wait=None):
        wait_time = self.display.time_to_refresh
        self.portal.enter_light_sleep(max(wait_time,wait))
        super().update()

    def connectNetwork(self):
        attempt = 0
        #The Adafruit_Portabase included with CP 7.3.3 does not have
        #the is_connected property 
        #while not self.portal.network.is_connected:
        while not self.portal.network._wifi.is_connected:
            try:
                self.portal.network.connect()
            except ConnectionError as e:
                print("could not connect to AP, retrying: ", e)
                continue

        while attempt < 3:
            try:
                self.portal.network.get_local_time()
                attempt = 3
            except:
                attempt += 1
                print("Error updating datetime from network: ")
                time.sleep(1)
                continue
