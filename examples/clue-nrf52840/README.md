# CLUE (nRF52840) Analog Clock

This example runs the kds_analogclock on the [Adafruit CLUE](https://www.adafruit.com/product/4500) using the built-in display and an **RTC (real-time clock)** instead of a network time API.

## Customizations from kds_analogclock

### Time source: RTC

- **connectNetwork** is overridden to use a [PCF8523 RTC](https://learn.adafruit.com/adafruit-pcf8523-real-time-clock) on the STEMMA I2C bus instead of WiFi or internet time.
- The RTC is set as the system time source via `rtc.set_time_source(self.my_rtc)`, so the clock runs from the RTC after it has been set (e.g. by the RTC utility or once over I2C).
- No network connection or portal network stack is used.

### Display

- Uses **board.DISPLAY** (the CLUE’s built-in TFT).
- **display.auto_refresh = False** so updates are explicit.

### Screen drawing (colors)

- **circleColor** / **centerColor**: white  
- **tickColor** / **secColor**: red  
- **minColor**: orange  
- **hourColor**: blue  
- **backColor**: grey77  
- **circleFillColor**: black  

Standard colored analog clock on the CLUE’s built-in screen, driven entirely by the PCF8523 RTC.
