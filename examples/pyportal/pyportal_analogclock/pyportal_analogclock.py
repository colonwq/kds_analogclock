from kds_analogclock.analogclock import AnalogClock
#https://docs.circuitpython.org/projects/matrixportal/en/latest/
from adafruit_pyportal import PyPortal

class Pyportal_AnalogClock(AnalogClock):
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
        self.portal = PyPortal()
        self.display = self.portal.display
        self.display.auto_refresh = False
        
        self.pre_calc()
        self.drawStatic(self.display)
        self.drawClock(self.display)
        self.connectNetwork()


    def connectNetwork(self):
        attempt = 0
        #The Adafruit_Portalbase included with CP 7.3.3 does not have
        #the is_connected property 
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
