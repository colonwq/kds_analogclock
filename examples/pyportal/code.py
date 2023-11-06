from pyportal_analogclock.pyportal_analogclock import Pyportal_AnalogClock

def main():

  clock = Pyportal_AnalogClock()
  clock.hello()

  while True:
    clock.update()

if __name__ == "__main__":
    main()
