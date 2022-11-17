from m4matrix_analogclock.m4_analogclock import M4M_AnalogClock

def main():

  clock = M4M_AnalogClock()
  clock.hello()

  while True:
    clock.update(wait=1)

if __name__ == "__main__":
    main()