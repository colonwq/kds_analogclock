from kds_analogclock.analogclock import AnalogClock
from adafruit_funhouse import FunHouse


class Funhouse_AnalogClock(AnalogClock):
    def __init__(self):
        super().__init__()

        self.circleColor = self.WHITE
        self.centerColor = self.WHITE
        self.tickColor = self.RED
        self.secColor = self.RED
        self.minColor = self.ORANGE
        self.hourColor = self.BLUE
        self.backColor = self.GREY77
        self.circleFillColor = self.BLACK

        self.portal = FunHouse()
        self.display = self.portal.display
        self.display.auto_refresh = False

        self.pre_calc()
        self.drawStatic(self.display)
        self.drawClock(self.display)
        self.connectNetwork()

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