# Feather Huzzah32 Analog Clock

This example runs the kds_analogclock on the [Adafruit Feather Huzzah32 (ESP32)](https://www.adafruit.com/product/3405) with a **128×32 I2C OLED** (e.g. [128×32 OLED FeatherWing](https://www.adafruit.com/product/2900)). It does **not** use a portal class; it uses native WiFi and a custom display setup, and implements its own **network/time logic** (Adafruit IO time API).

## Customizations from kds_analogclock

### Display

- **No portal.** Display is created manually:
  - **adafruit_displayio_ssd1306.SSD1306** on **board.I2C()** at address `0x3c`, **128×32** resolution.
  - Fixed **WIDTH** / **HEIGHT** (128, 32) for the OLED; the base clock sizes itself to the smaller dimension.

### Network and time (connectNetwork / get_local_time)

- **No portal network.** WiFi and time are implemented in this example:
  - **connectNetwork**: Assumes WiFi may already be connected (e.g. by the runtime for web workflow). If connected, uses `wifi.radio` and builds an `adafruit_requests.Session` for HTTP. Then calls **get_local_time()**.
  - **get_strftime** / **get_local_time**: Custom implementation using the **Adafruit IO time/strftime API**. Reads **AIO_USERNAME** and **AIO_KEY** from settings (via **_get_setting**); supports optional **timezone** in settings. Sets the RTC from the API response.
- **_get_setting**: Reads from **settings.toml** (and optionally legacy secrets); prints a clear message if WiFi or AIO settings are missing.

### Screen drawing (colors)

- Monochrome for the OLED: all elements **white** on **black**.
  - **circleColor**, **centerColor**, **tickColor**, **secColor**, **minColor**, **hourColor**: white  
  - **backColor**, **circleFillColor**: black  

NeoPixel status LED is used for connection/fetch status (e.g. connecting, fetching, data received).

## Setup

In **settings.toml** on the CIRCUITPY drive, set at least:

- `CIRCUITPY_WIFI_SSID` and `CIRCUITPY_WIFI_PASSWORD` (if not already connected by the runtime).
- `AIO_USERNAME` and `AIO_KEY` (or equivalent) for the Adafruit IO time service.
- Optional: `timezone` for the time API.

This example is the only one that implements the full network/time path itself instead of using a portal or an RTC.
