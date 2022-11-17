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

from macropad_analogclock.macropad_analogclock import Macropad_AnalogClock

def main():

  clock = Macropad_AnalogClock()
  clock.hello()

  while True:
    clock.update()

if __name__ == "__main__":
    main()