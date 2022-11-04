###
'''
My attempt to write an python class for an analog clock

Targeted platforms:
Adafruit pyPortal https://www.adafruit.com/product/4116
'''
###
import time
import math
import busio
import board
import displayio
#import framebufferio
#import gc
#https://docs.circuitpython.org/projects/display-shapes/en/latest/index.html
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
from digitalio import DigitalInOut

import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi

if board.board_id == "adafruit_macropad_rp2040":
    from adafruit_macropad import MacroPad
    import adafruit_pcf8523
    import rtc

if board.board_id == "adafruit_feather_huzzah32":
    import adafruit_displayio_ssd1306
    import os
    import wifi
    import ipaddress
    import ssl
    import socketpool
    import adafruit_requests
    from dotenv import load_dotenv
    try:
        import rtc
    except ImportError:
        rtc = None
    #stolen from portal base
    TIME_SERVICE = (
      "https://io.adafruit.com/api/v2/%s/integrations/time/strftime?x-aio-key=%s"
    )
    # our strftime is %Y-%m-%d %H:%M:%S.%L %j %u %z %Z see http://strftime.net/ for decoding details
    # See https://apidock.com/ruby/DateTime/strftime for full options
    TIME_SERVICE_FORMAT = "%Y-%m-%d %H:%M:%S.%L %j %u %z %Z"
    LOCALFILE = "local.txt"

if board.board_id == "adafruit_funhouse":
    from adafruit_funhouse import FunHouse
if board.board_id == "pyportal":
    #https://docs.circuitpython.org/projects/matrixportal/en/latest/
    from adafruit_pyportal import PyPortal
    #from adafruit_pyportal.network import Network
if board.board_id == "adafruit_magtag_2.9_grayscale":
    #print("Importing magtag library")
    #https://docs.circuitpython.org/projects/magtag/en/latest/index.html
    from adafruit_magtag.magtag import MagTag
    from adafruit_magtag.network import Network
if board.board_id == "matrixportal_m4":
    #https://docs.circuitpython.org/projects/matrixportal/en/latest/
    from adafruit_matrixportal.matrix import Matrix
    from adafruit_matrixportal.network import Network

class AnalogClock:

    def __init__(
        self
        ):
        #print("Called the init function for my AnalogClock class")

        #Some 'reasonable' defaults
        self.WHITE  = 0xffffff
        self.YELLOW = 0xffff00
        self.BLUE   = 0x0000ff
        self.RED    = 0xff0000
        self.ORANGE = 0xffa500
        self.GREEN  = 0x00FF00
        self.BLACK  = 0x000000
        self.GREY77 = 0x777777
        self.WIDTH  = 32
        self.HEIGHT = 32
        self.centerX = self.centerY = self.radius = self.radius_50 = self.radius_75 = self.radius_80 = self.radius_90 = 0
        self.pre_sin = [None] * 61
        self.pre_cos = [None] * 61
        self.HOUR = 0
        self.MIN  = 0
        self.SEC  = 0
        self.HOURS_PASSED = 0
        self.network = None
        self.portal  = None
        self.UPDATE_HOUR_MINS = [ 12, 24,36,48 ]
        self.rtc = None

        self.lines = []
        self.static_tics = [None] * 12
        self.static_big_circle = None
        self.static_small_circle = None
        self.static_minute_hand = None
        self.static_hour_hand = None
        self.g1 = None
        self.tg1 = None

        if board.board_id == "pyportal" or board.board_id == "matrixportal_m4" or board.board_id == "adafruit_funhouse":
            self.circleColor = self.WHITE
            self.centerColor = self.WHITE
            self.tickColor = self.RED
            self.secColor = self.RED
            self.minColor = self.ORANGE
            self.hourColor = self.BLUE
            self.backColor = self.GREY77
            self.circleFillColor = self.BLACK
        if board.board_id == "pyportal":
            self.portal = PyPortal()
            self.display = self.portal.display
        if board.board_id == "matrixportal_m4":
            self.backColor = self.BLACK
            self.portal = Matrix()
            self.display = self.portal.display
        if board.board_id == "adafruit_funhouse":
            self.portal = FunHouse()
            self.display = self.portal.display
        if board.board_id == "adafruit_magtag_2.9_grayscale":
            self.circleColor = self.BLACK
            self.centerColor = self.BLACK
            self.tickColor = self.BLACK
            self.secColor = self.BLACK
            self.minColor = self.BLACK
            self.hourColor = self.BLACK
            self.backColor = self.WHITE
            self.circleFillColor = self.WHITE
        if board.board_id == "adafruit_magtag_2.9_grayscale":
            self.portal = MagTag()
            self.display = self.portal.display
        if board.board_id == "adafruit_feather_huzzah32" or board.board_id == "adafruit_macropad_rp2040":
            self.circleColor = self.WHITE
            self.centerColor = self.WHITE
            self.tickColor = self.WHITE
            self.secColor = self.WHITE
            self.minColor = self.WHITE
            self.hourColor = self.WHITE
            self.backColor = self.BLACK
            self.circleFillColor = self.BLACK
        if board.board_id == "adafruit_macropad_rp2040":
            #displayio.release_displays()
            self.display = board.DISPLAY
            #myI2C = busio.I2C(board.SCL, board.SDA)
            #self.rtc = adafruit_pcf8523.PCF8523(myI2C)
            #t = self.rtc.datetime
            #print(type(t))
            #print(t)
            #rtc.RTC.set_time_source(self.rtc)


        if board.board_id == "adafruit_feather_huzzah32":
            displayio.release_displays()
            i2c = board.I2C()
            display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
            self.display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

        self.pre_calc()

        self.drawStatic(self.display)
        self.drawClock(self.display)

        if board.board_id != "adafruit_magtag_2.9_grayscale":
            #auto_refresh causes the screen to flicker and
            #makes the display update slow
            self.display.auto_refresh = False
        self.connectNetwork()


    def update(self):
        if board.board_id == "adafruit_magtag_2.9_grayscale":
            #print("The magtag is sleeping")
            self.portal.enter_light_sleep(60)
#        if board.board_id == "matrixportal_m4":
#            time.sleep(5)
        self.drawClock(self.display)

    def hello(self):
        print("Hello from a hello function")

    '''
    Precalculate some needed parameters

    '''
    def pre_calc(self):
        self.WIDTH   = self.display.width
        self.HEIGHT  = self.display.height
        self.centerX = int((self.WIDTH-1)/2)
        self.centerY = int((self.HEIGHT-1)/2)
        self.radius  = min(self.centerX, self.centerY)
        print("Height: %d Width: %d Radius: %d" % (self.HEIGHT, self.WIDTH, self.radius))
        self.radius_50 = int(self.radius * .5)
        self.radius_75 = int(self.radius * .75)
        self.radius_75 = int(self.radius * .75)
        self.radius_80 = int(self.radius * .80)
        self.radius_90 = int(self.radius * .90)

        step = 0
        while step < 61:
            angle = math.radians(step * 6)
            #print("Pre calculating angle %f" % (angle) )
            self.pre_cos[step] = math.cos(angle)
            self.pre_sin[step] = math.sin(angle)
            step += 1

    '''
    Draw the big clock circle
    '''
    def drawClockCircle(self,output):
        if self.static_big_circle is None:
            self.static_big_circle = Circle(self.centerX, self.centerY, self.radius, fill=self.circleFillColor, outline=self.circleColor, )
        output.append(self.static_big_circle)

    '''
    Draw the center circle
    The center of the clock is the 5% of the big circle plus 1
    '''
    def drawClockCenter(self,output):
        if self.static_small_circle is None:
            self.static_small_circle = (Circle(self.centerX, self.centerY, int(self.radius *.05)+1, fill=self.centerColor, outline=self.centerColor))
        output.append(self.static_small_circle)

    '''
    Draw each of the tics around the clock face
    The tics are 20% the distance from the edge to the center on the quaters
    and 90% for the rest
    '''
    def drawClockHourTics(self,output):
      if len(self.lines) == 0:
        step = 0
        while step < 60:
          sin_angle = self.pre_sin[step]
          cos_angle = self.pre_cos[step]

          x2 = int( self.centerX + (sin_angle * self.radius) )
          y2 = int( self.centerY - (cos_angle * self.radius) )
          x2 = int( self.centerX + (sin_angle * self.radius) )
          y2 = int( self.centerY - (cos_angle * self.radius) )

          if step%4 == 0:
            x3 = int( self.centerX + (sin_angle * self.radius_80 ) )
            y3 = int( self.centerY - (cos_angle * self.radius_80 ) )
          else:
            x3 = int( self.centerX + (sin_angle * self.radius_90 ) )
            y3 = int( self.centerY - (cos_angle * self.radius_90 ) )

          line = Line( x2, y2, x3, y3, self.tickColor )
          self.lines.append(line)
          step += 5

      for line in self.lines:
        output.append(line)

    '''
    Draw the clock hand
    The second hand goes all the way to to the edge
    '''
    def drawClockSecHand(self, output ):
        x2 = int( self.centerX + (self.pre_sin[self.SEC] * (self.radius) ) )
        y2 = int( self.centerY - (self.pre_cos[self.SEC] * (self.radius) ) )
        line = Line( self.centerX, self.centerY, x2, y2, self.secColor )
        output.append( line )

    '''
    Draw the minute hand
    The minute hand is 75% of the way from the center to the edge
    '''
    def drawClockMinHand(self, output, force=False ):
        if self.static_minute_hand is None or force==True:
            x2 = int( self.centerX + (self.pre_sin[self.MIN] * self.radius_75 ) )
            y2 = int( self.centerY - (self.pre_cos[self.MIN] * self.radius_75 ) )
            self.static_minute_hand = Line( self.centerX, self.centerY, x2, y2, self.minColor )
        output.append(self.static_minute_hand)

    '''
    Draw the hour hand
    The hour hand is 50% of the way from the center to the edge
    '''
    def drawClockHourHand(self, output, force=False ):
        if self.static_hour_hand is None or force==True:
          MIN_TIC = int(self.MIN/12)
          position = (self.HOUR)*5 + MIN_TIC
          if position > 60:
              position -= 60
          x2 = int( self.centerX + (self.pre_sin[position] * (self.radius_50) ) )
          y2 = int( self.centerY - (self.pre_cos[position] * (self.radius_50) ) )
          static_hour_hand = Line( self.centerX, self.centerY, x2, y2, self.hourColor )
        output.append( static_hour_hand )

    '''
    Draw static parts of the dial
    '''
    def drawStatic(self, display):
        palette = displayio.Palette(1)
        palette[0] = self.backColor
        background = displayio.Bitmap(self.WIDTH, self.HEIGHT, 1)
        self.tg1 = displayio.TileGrid(background, pixel_shader=palette)
        self.g1 = displayio.Group()
        self.g1.append(self.tg1)
        self.drawClockCircle(self.g1)
        self.drawClockHourTics(self.g1)
        self.drawClockCenter(self.g1)

        display.show(self.g1)

        #the magtag is an eink display and cannot refresh too quickly
        if board.board_id == "adafruit_magtag_2.9_grayscale" and self.display.time_to_refresh > 0:
            time.sleep(self.display.time_to_refresh)

        display.refresh()

        time.sleep(5)

    '''
    Master clock draw function.
    It also updates the time ever 12 hours
    '''
    def drawClock(self, display):
      update_min = False
      update_hour = False

      #delete current tilegroups in the display group
      while len(self.g1)>0:
          self.g1.pop()

      curr_time = time.localtime()
      if self.SEC == curr_time.tm_sec:
        return

      if curr_time.tm_hour != self.HOUR:
          self.HOURS_PASSED += 1
      if self.HOURS_PASSED > 12:
          #Update the network time
          self.connectNetwork()
          self.HOURS_PASSED = 0

      #Change: Update the update the hour
      if self.MIN != curr_time.tm_min:
        #print("Current time: %d:%d:%d" % (curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec) )
        update_min = True
        #when curr_time.tm_min == 12, 24, 36, 48
        if curr_time.tm_min in self.UPDATE_HOUR_MINS:
          update_hour = True
      self.HOUR = curr_time.tm_hour
      self.MIN  = curr_time.tm_min
      self.SEC  = curr_time.tm_sec
      print("Current time: %d:%d:%d" % (curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec) )

      #gc.collect()
      self.g1.append(self.tg1)
      #print("Before drawing Free memory: " , gc.mem_free() )
      self.drawClockCircle(self.g1)
      self.drawClockHourTics(self.g1)
      self.drawClockSecHand(self.g1)
      self.drawClockMinHand(self.g1, force=update_min)
      self.drawClockHourHand(self.g1, force=update_hour)
      self.drawClockCenter(self.g1)

      #print("After drawing Free memory: " , gc.mem_free() )
      self.display.show(self.g1)
      #the magtag is an eink display and cannot refresh too quickly
      if board.board_id == "adafruit_magtag_2.9_grayscale" and self.display.time_to_refresh > 0:
        time.sleep(self.display.time_to_refresh)

      while not self.display.refresh():
          print(".")
          pass


    def url_encode(self,url):
        """
        A function to perform minimal URL encoding
        """
        url = url.replace(" ", "+")
        url = url.replace("%", "%25")
        url = url.replace(":", "%3A")
        return url

    def connectNetwork(self):
        if board.board_id == "pyportal" or board.board_id == "adafruit_funhouse":
            #print("I run special pyportal network code")
            self.portal.network.connect()
            self.portal.network.get_local_time()
        elif board.board_id == "adafruit_magtag_2.9_grayscale" or board.board_id == "matrixportal_m4":
            if self.network == None:
                self.network = Network()
            attempt = 0
            while not self.network._wifi.is_connected:
                try:
                    self.network.connect()
                except ConnectionError as e:
                    print("could not connect to AP, retrying: ", e)
                    continue

            while attempt < 3:
                try:
                    self.network.get_local_time()
                    attempt = 3
                except :
                    attempt += 1
                    print("Error updating datetime from network: ")
                    time.sleep(1)
                    continue
        elif board.board_id == "adafruit_feather_huzzah32":
            load_dotenv()
            SSID = os.getenv('CIRCUITPY_WIFI_SSID')
            WIFI_PASSWD = os.getenv('CIRCUITPY_WIFI_PASSWORD')
            wifi.radio.connect(SSID, WIFI_PASSWD)

            print("Trying to get network time")
            pool = socketpool.SocketPool(wifi.radio)
            requests = adafruit_requests.Session(pool, ssl.create_default_context())

            aio_username = os.getenv("AIO_USERNAME")
            aio_key = os.getenv("AIO_KEY")
            timezone = os.getenv("TIMEZONE")
            if timezone is None:
                print("No timezone provided")
                print("Getting time from IP address")
                api_url = TIME_SERVICE % (aio_username, aio_key)
            else:
                print("Getting time for %s" % (timezone))
                api_url = (TIME_SERVICE + "&tz=%s") % (aio_username, aio_key, timezone)

            api_url += "&fmt=" + self.url_encode(TIME_SERVICE_FORMAT)

            response = requests.get(api_url)

            if response:
                #print("Setting time")
                times = response.text.split(" ")
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
        elif board.board_id == "adafruit_macropad_rp2040":
            if self.rtc == None:
                myI2C = busio.I2C(board.SCL, board.SDA)
                self.rtc = adafruit_pcf8523.PCF8523(myI2C)
            t = self.rtc.datetime
            rtc.RTC().datetime = t

        else:
            #here is the next board
            pass