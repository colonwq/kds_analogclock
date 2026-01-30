from kds_analogclock.analogclock import AnalogClock
import board
import displayio
import adafruit_displayio_ssd1306
import os
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
import neopixel
import gc
import time

try:
    import rtc
except ImportError as e:
    print(f"ImportError loading rtc: {e}")
    rtc = None

# pylint: disable=line-too-long, too-many-lines, too-many-public-methods
# you'll need to pass in an io username and key
TIME_SERVICE = (
    "https://io.adafruit.com/api/v2/%s/integrations/time/strftime?x-aio-key=%s"
)
# our strftime is %Y-%m-%d %H:%M:%S.%L %j %u %z %Z see http://strftime.net/ for decoding details
# See https://apidock.com/ruby/DateTime/strftime for full options
TIME_SERVICE_FORMAT = "%Y-%m-%d %H:%M:%S.%L %j %u %z %Z"
#OLD_SETTINGS = {
#    "CIRCUITPY_WIFI_SSID": "ssid",
#    "CIRCUITPY_WIFI_PASSWORD": "password",
#    "AIO_USERNAME": "aio_username",
#    "AIO_KEY": "aio_key",
#}
STATUS_NO_CONNECTION = (100, 0, 0)  # Red
STATUS_CONNECTING = (0, 0, 100)  # Blue
STATUS_FETCHING = (150, 100, 0)  # Orange
STATUS_DOWNLOADING = (0, 100, 100)  # Cyan
STATUS_CONNECTED = (0, 0, 100)  # Blue
STATUS_DATA_RECEIVED = (0, 100, 0)  # Green
STATUS_HTTP_ERROR = (100, 0, 0)  # Red
STATUS_OFF = (0, 0, 0)  # Off

class Huzzah32_AnalogClock(AnalogClock):
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
        self._settings = {}
        self._wifi = wifi
        self._requests = None
        self._debug = True
        


        self.WIDTH = 128
        self.HEIGHT = 32
        self.pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

        self._createDisplay()

        self.pre_calc()
        self.drawStatic(self.display)
        self.drawClock(self.display)
        self.connectNetwork()

    def _createDisplay(self):

     i2c = board.I2C()
     display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
     self.display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

    def _get_setting(self, setting_name, show_error=True):
        if setting_name in self._settings:
            return self._settings[setting_name]

#        old_setting_name = setting_name
##        if setting_name in OLD_SETTINGS:
#            old_setting_name = OLD_SETTINGS.get(setting_name)
        if os.getenv(setting_name) is not None:
            return os.getenv(setting_name)
#        try:
#            from secrets import secrets  # pylint: disable=import-outside-toplevel
#        except ImportError:
#            secrets = {}
#        if old_setting_name in secrets.keys():
#            self._settings[setting_name] = secrets[old_setting_name]
#            return self._settings[setting_name]
        if show_error:
            if setting_name in ("CIRCUITPY_WIFI_SSID", "CIRCUITPY_WIFI_PASSWORD"):
                print(
                    f"WiFi settings are kept in settings.toml, please add them there! "
                    f"The secrets dictionary must contain 'CIRCUITPY_WIFI_SSID' and 'CIRCUITPY_WIFI_PASSWORD' "
                    f"at a minimum in order to use network related features"
                )
            else:
                print(
                    f"{setting_name} not found. Please add this setting to settings.toml."
                )
        return None

    def neo_status(self, value):
        """The status NeoPixel.

        :param value: The color to change the NeoPixel.

        """
        self.pixels.fill(value)

    @staticmethod
    def url_encode(url):
        """
        A function to perform minimal URL encoding
        """
        return url.replace(" ", "+").replace("%", "%25").replace(":", "%3A")

    def get_strftime(self, time_format, location=None):
        """
        Fetch a custom strftime relative to your location.

        :param str location: Your city and country, e.g. ``"America/New_York"``.

        """
        # pylint: disable=line-too-long
        #self.connect()
        api_url = None
        reply = None
        try:
            aio_username = self._get_setting("AIO_USERNAME")
            aio_key = self._get_setting("AIO_KEY")
        except KeyError:
            raise KeyError(
                "\n\nOur time service requires a login/password to rate-limit. Please register for a free adafruit.io account and place the user/key in your secrets file under 'AIO_USERNAME' and 'AIO_KEY'"  # pylint: disable=line-too-long
            ) from KeyError

        if location is None:
            location = self._get_setting("timezone", False)
        if location:
            print(f"Getting time for timezone {location}")
            api_url = (TIME_SERVICE + "&tz=%s") % (aio_username, aio_key, location)
        else:  # we'll try to figure it out from the IP address
            print(f"Getting time from IP address")
            api_url = TIME_SERVICE % (aio_username, aio_key)
        api_url += "&fmt=" + self.url_encode(time_format)

        try:
            self.neo_status(STATUS_FETCHING)
            response = self._requests.get(api_url, timeout=10)
            self.neo_status(STATUS_DATA_RECEIVED)
            if response.status_code != 200:
                print(f"Response: {response}")
                error_message = (
                    "Error connecting to Adafruit IO. The response was: "
                    + response.text
                )
                self.neo_status(STATUS_HTTP_ERROR)
                raise RuntimeError(error_message)
            if self._debug:
                print(f"Time request: {api_url}")
                print(f"Time reply: {response.text}")
            reply = response.text
        except KeyError as e:
            print(f"KeyError in get_strftime: {e}")
            raise KeyError(
                "Was unable to lookup the time, try setting secrets['timezone'] according to http://worldtimeapi.org/timezones"  # pylint: disable=line-too-long
            ) from KeyError
        # now clean up
        response.close()
        response = None
        gc.collect()

        return reply

    def get_local_time(self, location=None):
        # pylint: disable=line-too-long
        """
        Fetch and "set" the local time of this microcontroller to the local time at the location, using an internet time API.

        :param str location: Your city and country, e.g. ``"America/New_York"``.

        """
        reply = self.get_strftime(TIME_SERVICE_FORMAT, location=location)
        if reply:
            times = reply.split(" ")
            the_date = times[0]
            the_time = times[1]
            year_day = int(times[2])
            week_day = int(times[3])
            is_dst = None  # no way to know yet
            year, month, mday = [int(x) for x in the_date.split("-")]
            the_time = the_time.split(".")[0]
            hours, minutes, seconds = [int(x) for x in the_time.split(":")]
            now = time.struct_time(
                (year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst)
            )

            if rtc is not None:
                rtc.RTC().datetime = now

        return reply

    def connectNetwork(self):
      #Alright this seems to be a bit of a cheat
      #The runtime of this board joins the wifi for the web serial to work. 
      #See: https://learn.adafruit.com/circuitpython-with-esp32-quick-start/setting-up-web-workflow
      print(f"I have developed a new connectNetwork")
      if not wifi.Radio.connected:
        print(f"Not connected to wifi")
      else:
        print(f"Connected to wifi")
        print(f"My IP address: {wifi.radio.ipv4_address}")
        if self._requests == None:
           #self._pool = socketpool.SocketPool(self._wifi.radio)
           self._requests = adafruit_requests.Session(socketpool.SocketPool(self._wifi.radio), ssl.create_default_context())

        self.get_local_time()
