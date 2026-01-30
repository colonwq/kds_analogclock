# PyPortal Analog Clock

This example runs the kds_analogclock on the [Adafruit PyPortal](https://www.adafruit.com/product/4116) using the PyPortal display and **WiFi + Adafruit IO time API** for time sync.

## Customizations from kds_analogclock

### Network (connectNetwork)

- Uses the **PyPortal** (adafruit_pyportal) for display and network.
- **connectNetwork** extends the base behavior by:
  1. **Credential check**: Before connecting, it verifies WiFi credentials (from `settings.toml` or legacy `secrets.py`). If `CIRCUITPY_WIFI_SSID` or `CIRCUITPY_WIFI_PASSWORD` is missing, it raises a clear `OSError` instead of failing later in the ESP32 SPI stack.
  2. **WiFi connect**: Retries until the portal’s network is connected (`portal.network._wifi.is_connected`).
  3. **Time sync**: Calls `portal.network.get_local_time()` (Adafruit IO time service) with retries.
- Handles library version mismatch: if PyPortal passes `secrets_data` to Network and the installed Network doesn’t accept it, the example can work around it (see code).

### Display

- **portal.display** with **auto_refresh = False**.

### Screen drawing (colors)

- **circleColor** / **centerColor**: white  
- **tickColor** / **secColor**: red  
- **minColor**: orange  
- **hourColor**: blue  
- **backColor**: grey77  
- **circleFillColor**: black  

Standard colored analog clock; all drawing logic comes from kds_analogclock.

## Setup

On the CIRCUITPY drive, add a **settings.toml** with WiFi credentials:

```toml
CIRCUITPY_WIFI_SSID = "your_network_name"
CIRCUITPY_WIFI_PASSWORD = "your_password"
```

Adafruit IO credentials (for the time API) are also read from settings (e.g. `ADAFRUIT_AIO_USERNAME`, `ADAFRUIT_AIO_KEY`) by the portal network layer.
