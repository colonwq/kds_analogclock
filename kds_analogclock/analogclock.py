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

    def update(self, wait=None):
        if self.display is None:
            print("update: Display is not set. The inheriting class is responsible.")
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
        print("Height: %d Width: %d Radius: %d" % (self.HEIGHT, self.WIDTH, self.radius))
        self.radius_50 = int(self.radius * .5)
        self.radius_75 = int(self.radius * .75)
        self.radius_75 = int(self.radius * .75)
        self.radius_80 = int(self.radius * .80)
        self.radius_90 = int(self.radius * .90)

        step = 0
        while step < 61:
            angle = math.radians(step * 6)
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

          if step%15 == 0:
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

        display.show(self.g1)

        display.refresh()

        time.sleep(5)

    '''
    Master clock draw function.
    It also updates the time ever 12 hours
    '''
    def drawClock(self, display):
        update_min = False
        update_hour = False

        #delete current tile groups in the display group
        while len(self.g1)>0:
            self.g1.pop()

        curr_time = time.localtime()
        if self.SEC == curr_time.tm_sec:
            time.sleep(.1)
            return

        if curr_time.tm_hour != self.HOUR:
            #print("Hour changed")
            self.HOURS_PASSED += 1
        if self.HOURS_PASSED > 12:
            #Update the network time
            print("More than 12 hours. Time to update time")
            self.connectNetwork()
            self.HOURS_PASSED = 0

        #Change: Update the update the hour
        if self.MIN != curr_time.tm_min:
            #print("Current time: %d:%d:%d" % (curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec) )
            update_min = True
            if curr_time.tm_min in self.UPDATE_HOUR_MINS:
                update_hour = True
        self.HOUR = curr_time.tm_hour
        self.MIN  = curr_time.tm_min
        self.SEC  = curr_time.tm_sec
        print("Current time: %02d:%02d:%02d" % (curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec) )

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

        self.display.refresh()

    def connectNetwork(self):
        print( "connectNetwork: To be implemented by the inheriting class")