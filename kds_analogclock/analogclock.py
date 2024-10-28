###
'''
My attempt to write an python class for an analog clock

Targeted platforms:
Adafruit pyPortal https://www.adafruit.com/product/4116
'''
###
import time
import math
import displayio
import gc
#https://docs.circuitpython.org/projects/display-shapes/en/latest/index.html
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line


class AnalogClock:
    def __init__(
        self
        ):

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
        self.display = None
        self.UPDATE_HOUR_MINS = [ 12, 24, 36, 48 ]
        self.my_rtc = None

        self.lines = []
        self.static_tics = [None] * 12
        self.static_big_circle = None
        self.static_small_circle = None
        self.static_minute_hand = None
        self.static_hour_hand = None
        self.g1 = None
        self.tg2 = None

        # Pre-defined table of sine values for angles from 0 to 90 degrees, stepping every 6 degrees
        self.sine_table = {
            0: 0,
            6: 0.1045,
            12: 0.2079,
            18: 0.3147,
            24: 0.4067,
            30: 0.5,
            36: 0.5878,
            42: 0.6691,
            48: 0.7431,
            54: 0.8090,
            60: 0.8660,
            66: 0.9135,
            72: 0.9511,
            78: 0.9781,
            84: 0.9945,
            90: 1
        }
        self.cosine_table = {
          0: 1.0000,
          6: 0.9945,
          12: 0.9781,
          18: 0.9511,
          24: 0.9205,
          30: 0.8660,
          36: 0.8090,
          42: 0.7431,
          48: 0.6691,
          54: 0.5878,
          60: 0.5000,
          66: 0.4067,
          72: 0.3090,
          78: 0.2079,
          84: 0.1045,
          90: 0.0000
      }
    
    def lookup_sine(self, angle):
      '''
      Given an angle, return the value in the table
      The input range will be between 0 and 360 
      with multiples of 6
      '''
      #angle %= 360  # Normalize to 0-360 degrees
      if angle > 180:
        angle = 360 - angle  # Use the symmetry of the sine function
      if angle > 90:
         angle = 90 - ( angle - 90 )

      # Find the nearest angle in the table
      #angle = round(angle / 6) * 6

      return self.sine_table[angle]

    def lookup_cosine(self, angle):
      '''
      Given an angle, return the value in the table
      The input range will be between 0 and 360 
      with multiples of 6
      '''
      angle %= 360  # Normalize to 0-360 degrees
      if angle > 180:
        angle = 360 - angle  # Use the symmetry of the sine function
      if angle > 90:
        angle = 90 - ( angle - 90 )
    
      # Find the nearest angle in the table
      angle = round(angle / 6) * 6

      return self.cosine_table[angle]

    def update(self, wait=None):
        if self.display is None:
            print("update: Display is not set. The inheriting class is responcible.")
            return
        if wait is not None:
            time.sleep(wait)
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
        #print("Height: %d Width: %d Radius: %d" % (self.HEIGHT, self.WIDTH, self.radius))
        self.radius_50 = int(self.radius * .5)
        self.radius_75 = int(self.radius * .75)
        self.radius_80 = int(self.radius * .80)
        self.radius_90 = int(self.radius * .90)

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
        for step in range(0,60,5):
          angle = step*6
          sin_angle = self.lookup_sine(angle)
          cos_angle = self.lookup_cosine(angle)

          x2 = int( self.centerX + (sin_angle * self.radius) )
          y2 = int( self.centerY - (cos_angle * self.radius) )

          #What is faster, one mod or 12 comparisons
          if step%15 == 0:
            x3 = int( self.centerX + (sin_angle * self.radius_80 ) )
            y3 = int( self.centerY - (cos_angle * self.radius_80 ) )
          else:
            x3 = int( self.centerX + (sin_angle * self.radius_90 ) )
            y3 = int( self.centerY - (cos_angle * self.radius_90 ) )

          line = Line( x2, y2, x3, y3, self.tickColor )
          self.lines.append(line)

      for line in self.lines:
        output.append(line)

    '''
    Draw the clock hand
    The second hand goes all the way to to the edge
    '''
    def drawClockSecHand(self, output ):
        x2 = int( self.centerX + (self.lookup_sine(self.SEC*6) * (self.radius) ) )
        y2 = int( self.centerY - (self.lookup_cosine(self.SEC*6) * (self.radius) ) )
        line = Line( self.centerX, self.centerY, x2, y2, self.secColor )
        output.append( line )

    '''
    Draw the minute hand
    The minute hand is 75% of the way from the center to the edge
    '''
    def drawClockMinHand(self, output, force=False ):
        if self.static_minute_hand is None or force==True:
            x2 = int( self.centerX + (self.lookup_sine(self.MIN*6) * self.radius_75 ) )
            y2 = int( self.centerY - (self.lookup_cosine(self.MIN*6) * self.radius_75 ) )
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
          x2 = int( self.centerX + (self.lookup_sine(position*6) * (self.radius_50) ) )
          y2 = int( self.centerY - (self.lookup_cosine(position*6) * (self.radius_50) ) )
          static_hour_hand = Line( self.centerX, self.centerY, x2, y2, self.hourColor )
        output.append( static_hour_hand )

    '''
    Draw static parts of the dial
    '''
    def drawStatic(self, display):
        if self.display is None:
            print("drawStatic: Display is not set. The inheriting class is responcible.")
            return
        palette = displayio.Palette(1)
        palette[0] = self.backColor
        background = displayio.Bitmap(self.WIDTH, self.HEIGHT, 1)
        self.tg1 = displayio.TileGrid(background, pixel_shader=palette)
        self.g1 = displayio.Group()
        self.g1.append(self.tg1)
        self.drawClockCircle(self.g1)
        self.drawClockHourTics(self.g1)
        self.drawClockCenter(self.g1)

        #display.show(self.g1)
        display.root_group = self.g1

        display.refresh()

        time.sleep(5)

    '''
    Master clock draw function.
    It also updates the time ever 12 hours
    '''
    def drawClock(self, display):
        update_min = False
        update_hour = False

        curr_time = time.localtime()
        if self.SEC == curr_time.tm_sec:
            time.sleep(.1)
            return

        #delete current tilegroups in the display group
        while len(self.g1)>0:
            self.g1.pop()

        if curr_time.tm_hour != self.HOUR:
            #print("Hour changed")
            self.HOURS_PASSED += 1
        if self.HOURS_PASSED > 12:
            #Update the network time
            #print("More than 12 hours. Time to update time")
            self.connectNetwork()
            self.HOURS_PASSED = 0

        if self.MIN != curr_time.tm_min:
            update_min = True
            #when curr_time.tm_min == 12, 24, 36, 48
            #this will move the hour hand to the next minute tick.
            if curr_time.tm_min in self.UPDATE_HOUR_MINS:
                update_hour = True
        self.HOUR = curr_time.tm_hour
        self.MIN  = curr_time.tm_min
        self.SEC  = curr_time.tm_sec
        if update_min == True:
          print("Current time: %02d:%02d:%02d" % (curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec) )

        self.g1.append(self.tg1)
        self.drawClockCircle(self.g1)
        self.drawClockHourTics(self.g1)
        self.drawClockSecHand(self.g1)
        self.drawClockMinHand(self.g1, force=update_min)
        self.drawClockHourHand(self.g1, force=update_hour)
        self.drawClockCenter(self.g1)

        #self.display.show(self.g1)
        self.display.root_group = self.g1
        #the magtag is an eink display and cannot refresh too quickly
        #if board.board_id == "adafruit_magtag_2.9_grayscale" and self.display.time_to_refresh > 0:
        #    time.sleep(self.display.time_to_refresh)

        #lets run collect at the end of the update
        gc.collect()
        self.display.refresh()

    def connectNetwork(self):
        print( "connectNetwork: To be implemented by the inheriting class")