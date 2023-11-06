'''
This is a AnalogClock derived class which is updated
for the M4 Matrix portal backpack. 
This was tested with a 32x64 but should work with other
sizes.
'''
from kds_analogclock.analogclock import AnalogClock
#https://docs.circuitpython.org/projects/matrixportal/en/latest/
from adafruit_matrixportal.matrixportal import MatrixPortal

class M4M_AnalogClock(AnalogClock):
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
        self.backColor = self.BLACK

        self.portal = MatrixPortal()
        self.display = self.portal.display

        self.pre_calc()
        self.drawStatic(self.display)
        self.drawClock(self.display)
        self.connectNetwork()

    def connectNetwork(self):
        print("connectNetwork called")
        #this should not happen as athe MatrixPortal init creats it
        if self.portal.network is None:
            self.portal.network = Network()
        attempt = 0
        while not self.portal.network.is_connected:
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
