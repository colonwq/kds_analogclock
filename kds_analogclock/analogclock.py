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
        self.static_first_tic_circle = None
        self.static_minute_hand = None
        self.static_hour_hand = None
        self.g1 = None
        self.tg1 = None
        self._static_count = 0  # number of static elements in g1 (only hands are replaced each tick)

        # Static lookup tables for 0 to 42 degrees (step 6)
        # Precision: 4 digits beyond decimal
        self.SIN_0_42 = [0.0000, 0.1045, 0.2079, 0.3090, 0.4067, 0.5000, 0.5878, 0.6691]
        self.COS_0_42 = [1.0000, 0.9945, 0.9781, 0.9511, 0.9135, 0.8660, 0.8090, 0.7431]

    def lookup_sin(self, angle):
        """
        Look up, with low precision, the sine of the angle.
        
        :param angle: Angle in degrees
        :return: sine of the angle
        """
        angle = angle % 360
        if 0 <= angle <= 90:
            if angle <= 42:
                # Direct lookup (0, 6, ..., 42)
                return self.SIN_0_42[int(angle / 6)]
            else:
                # > 42 (e.g. 48, 54 ... 90)
                # sin(x) = cos(90-x)
                return self.COS_0_42[int((90 - angle) / 6)]
        elif 90 < angle <= 180:
            return self.lookup_sin(180 - angle)
        elif 180 < angle <= 270:
            return -self.lookup_sin(angle - 180)
        else: # 270 < angle < 360
            return -self.lookup_sin(360 - angle)

    def lookup_cos(self, angle):
        """
        Look up, with low precision, the cosine of the angle.

        :param angle: Angle in degrees
        :return: cosine of the angle
        """
        angle = angle % 360
        if 0 <= angle <= 90:
            if angle <= 42:
                return self.COS_0_42[int(angle / 6)]
            else:
                # cos(x) = sin(90-x)
                return self.SIN_0_42[int((90 - angle) / 6)]
        elif 90 < angle <= 180:
            return -self.lookup_cos(180 - angle)
        elif 180 < angle <= 270:
            return -self.lookup_cos(angle - 180)
        else: # 270 < angle < 360
            return self.lookup_cos(360 - angle)

    def update(self, wait=None):
        if self.display is None:
            print(f"update: Display is not set. The inheriting class is responsible.")
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
      small_circle_r = int(self.radius * .05) + 1
      if len(self.lines) == 0:
        step = 0
        while step < 60:
          sin_angle = self.lookup_sin(step * 6)
          cos_angle = self.lookup_cos(step * 6)

          x2 = int( self.centerX + (sin_angle * self.radius) )
          y2 = int( self.centerY - (cos_angle * self.radius) )

          if step%15 == 0:
            x3 = int( self.centerX + (sin_angle * self.radius_80 ) )
            y3 = int( self.centerY - (cos_angle * self.radius_80 ) )
          else:
            x3 = int( self.centerX + (sin_angle * self.radius_90 ) )
            y3 = int( self.centerY - (cos_angle * self.radius_90 ) )

          line = Line( x2, y2, x3, y3, self.tickColor )
          self.lines.append(line)
          if step == 0 and self.static_first_tic_circle is None:
            self.static_first_tic_circle = Circle(x3, y3, small_circle_r, fill=self.centerColor, outline=self.centerColor)
          step += 5

      for line in self.lines:
        output.append(line)
      if self.static_first_tic_circle is not None:
        output.append(self.static_first_tic_circle)

    '''
    Draw the clock hand
    The second hand goes all the way to to the edge.
    Hands start from the edge of the center dot.
    '''
    def drawClockSecHand(self, output ):
        angle = self.SEC * 6
        r_dot = int(self.radius * .05) + 1
        x1 = int( self.centerX + (self.lookup_sin(angle) * r_dot) )
        y1 = int( self.centerY - (self.lookup_cos(angle) * r_dot) )
        x2 = int( self.centerX + (self.lookup_sin(angle) * (self.radius) ) )
        y2 = int( self.centerY - (self.lookup_cos(angle) * (self.radius) ) )
        line = Line( x1, y1, x2, y2, self.secColor )
        output.append( line )

    '''
    Draw the minute hand
    The minute hand is 75% of the way from the center to the edge.
    Hands start from the edge of the center dot.
    '''
    def drawClockMinHand(self, output, force=False ):
        if self.static_minute_hand is None or force==True:
            angle = self.MIN * 6
            r_dot = int(self.radius * .05) + 1
            x1 = int( self.centerX + (self.lookup_sin(angle) * r_dot) )
            y1 = int( self.centerY - (self.lookup_cos(angle) * r_dot) )
            x2 = int( self.centerX + (self.lookup_sin(angle) * self.radius_75 ) )
            y2 = int( self.centerY - (self.lookup_cos(angle) * self.radius_75 ) )
            self.static_minute_hand = Line( x1, y1, x2, y2, self.minColor )
        output.append(self.static_minute_hand)

    '''
    Draw the hour hand
    The hour hand is 50% of the way from the center to the edge.
    Hands start from the edge of the center dot.
    '''
    def drawClockHourHand(self, output, force=False ):
        if self.static_hour_hand is None or force==True:
          MIN_TIC = int(self.MIN/12)
          position = (self.HOUR)*5 + MIN_TIC
          if position > 60:
              position -= 60
          angle = position * 6
          r_dot = int(self.radius * .05) + 1
          x1 = int( self.centerX + (self.lookup_sin(angle) * r_dot) )
          y1 = int( self.centerY - (self.lookup_cos(angle) * r_dot) )
          x2 = int( self.centerX + (self.lookup_sin(angle) * (self.radius_50) ) )
          y2 = int( self.centerY - (self.lookup_cos(angle) * (self.radius_50) ) )
          self.static_hour_hand = Line( x1, y1, x2, y2, self.hourColor )
        output.append( self.static_hour_hand )

    '''
    Draw static parts of the dial
    '''
    def drawStatic(self, display):
        if self.display is None:
            print(f"drawStatic: Display is not set. The inheriting class is responsible.")
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
        self._static_count = len(self.g1)

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

        # Ensure static content exists (e.g. if drawStatic was skipped)
        if self.g1 is None:
            palette = displayio.Palette(1)
            palette[0] = self.backColor
            background = displayio.Bitmap(self.WIDTH, self.HEIGHT, 1)
            self.tg1 = displayio.TileGrid(background, pixel_shader=palette)
            self.g1 = displayio.Group()
            self.g1.append(self.tg1)
            self.drawClockCircle(self.g1)
            self.drawClockHourTics(self.g1)
            self.drawClockCenter(self.g1)
            self._static_count = len(self.g1)

        # Remove only the hands (last 3 elements); leave static content in place to minimize flicker
        while len(self.g1) > self._static_count:
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

        # Re-add only the hands (static content already in g1)
        self.drawClockSecHand(self.g1)
        self.drawClockMinHand(self.g1, force=update_min)
        self.drawClockHourHand(self.g1, force=update_hour)

        #self.display.show(self.g1)
        self.display.root_group = self.g1
        #the magtag is an eink display and cannot refresh too quickly
        #if board.board_id == "adafruit_magtag_2.9_grayscale" and self.display.time_to_refresh > 0:
        #    time.sleep(self.display.time_to_refresh)

        #lets run collect at the end of the update
        gc.collect()
        self.display.refresh()

    def connectNetwork(self):
        print(f"connectNetwork: To be implemented by the inheriting class")