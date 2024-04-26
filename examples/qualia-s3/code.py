from qualia_s3_analogclock.qualia_s3_analogclock import Qualia_S3_AnalogClock

def main():

  clock = Qualia_S3_AnalogClock()
  #clock.hello()

  while True:
    clock.update()

if __name__ == "__main__":
    main()
