# MacroPad RP2040 Analog Clock

This example runs the kds_analogclock on the [Adafruit MacroPad RP2040](https://www.adafruit.com/product/5128) using its built-in display and an **RTC (real-time clock)** instead of a network time API.

## Customizations from kds_analogclock

### Time source: RTC

- **connectNetwork** is overridden to use a [PCF8523 RTC](https://learn.adafruit.com/adafruit-pcf8523-real-time-clock) on the STEMMA I2C bus instead of WiFi or internet time.
- The RTC is set as the system time source via `rtc.set_time_source(self.my_rtc)`.
- Time must be set on the RTC (e.g. using the `RTC-pcf8523/code.py` utility in this folder); no network is used.

### Display

- Uses **board.DISPLAY** (the MacroPad’s built-in TFT).
- **display.auto_refresh = False** for explicit refresh control.

### Screen drawing (colors)

- Monochrome theme: all hands and markings are **white** on a **black** background.
- **circleColor**, **centerColor**, **tickColor**, **secColor**, **minColor**, **hourColor**: white  
- **backColor**, **circleFillColor**: black  

Suited to the small built-in display with no network dependency.

## RTC setup

Use `RTC-pcf8523/code.py` in this folder to set the PCF8523’s time (e.g. from your computer or a one-time script) before relying on the clock for correct time.
