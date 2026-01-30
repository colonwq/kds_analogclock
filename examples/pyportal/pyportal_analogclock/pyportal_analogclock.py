import os
import time
from kds_analogclock.analogclock import AnalogClock
from adafruit_pyportal import PyPortal

# Message shown when WiFi credentials are missing (settings.toml or secrets.py)
_WIFI_CREDENTIALS_MSG = (
    "WiFi credentials not found. On your CIRCUITPY drive, add a settings.toml file with:\n"
    "  CIRCUITPY_WIFI_SSID = \"your_network_name\"\n"
    "  CIRCUITPY_WIFI_PASSWORD = \"your_password\"\n"
    "Or use a secrets.py with 'ssid' and 'password' keys."
)


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
        # Fail early with a clear message if WiFi credentials are missing
        net = self.portal.network
        ssid = getattr(net, "_get_setting", lambda n: os.getenv(n))("CIRCUITPY_WIFI_SSID")
        if not ssid:
            try:
                from secrets import secrets
                ssid = secrets.get("ssid") or secrets.get("CIRCUITPY_WIFI_SSID")
            except ImportError as e:
                print(f"Import error loading secrets for SSID: {e}")
        pwd = getattr(net, "_get_setting", lambda n: os.getenv(n))("CIRCUITPY_WIFI_PASSWORD")
        if not pwd:
            try:
                from secrets import secrets
                pwd = secrets.get("password") or secrets.get("CIRCUITPY_WIFI_PASSWORD")
            except ImportError as e:
                print(f"Import error loading secrets for password: {e}")
        if not ssid or not pwd:
            raise OSError(_WIFI_CREDENTIALS_MSG)

        attempt = 0
        # The Adafruit_Portalbase included with CP 7.3.3 does not have
        # the is_connected property
        while not self.portal.network._wifi.is_connected:
            try:
                self.portal.network.connect()
            except ConnectionError as e:
                print(f"could not connect to AP, retrying: {e}")
                continue
            except TypeError as e:
                if "NoneType" in str(e) and "len" in str(e):
                    raise OSError(_WIFI_CREDENTIALS_MSG) from e
                print(f"TypeError during connect: {e}")
                raise

        while attempt < 3:
            try:
                self.portal.network.get_local_time()
                attempt = 3
            except Exception as e:
                attempt += 1
                print(f"Error updating datetime from network: {e}")
                time.sleep(1)
                continue
