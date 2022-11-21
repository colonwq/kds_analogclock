'''
This project was inspired by Dave's Garage 'Live' coding of a analog clock
displaying on his LED display.
I do not have his display or hardware.
I do have a Matrix M4 portal and 64x32 display gathering dust.

References:
Dave's Garage: https://www.youtube.com/watch?v=yIpdBVu9xv8
Various Adafruit howto's, API documentation and *gasp* looking at various Adafruit git repos.

All mistakes are my fault.
'''

from magtag_analogclock.magtag_analogclock import Magtag_AnalogClock

def main():

  clock = Magtag_AnalogClock()
  clock.hello()

  while True:
    clock.update(wait=27)

if __name__ == "__main__":
    main()
