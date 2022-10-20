'''
This project was inspired by Dave's Garage 'Live' coding of a analog clock
displaying on his LED display.
I do not have his display or hardware.
I do have a variety of Adafruit displays gathering dust.

References:
Dave's Garage: https://www.youtube.com/watch?v=yIpdBVu9xv8
Various Adafruit howto's, API documentation and *gasp* looking at Adafruit git repos.

All mistakes are my fault.
'''

from kds_analogclock.analogclock import AnalogClock

def main():

  clock = AnalogClock()
  clock.hello()

  while True:
    clock.update()

if __name__ == "__main__":
    main()