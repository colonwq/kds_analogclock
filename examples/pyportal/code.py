from pyportal_analogclock.pyportal_analogclock import Pyportal_AnalogClock

def main():

  clock = Pyportal_AnalogClock()
  clock.hello()

  while True:
    #clock.update(wait=1)
    clock.update()

if __name__ == "__main__":
    main()
