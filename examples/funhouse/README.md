# FunHouse Analog Clock

This example runs the kds_analogclock on the [Adafruit FunHouse](https://www.adafruit.com/product/4985) using the FunHouse display and **WiFi + portal time API** for time sync.

## Customizations from kds_analogclock

### Network (connectNetwork)

- Uses **FunHouse** (adafruit_funhouse) for display and network.
- **connectNetwork** extends the base behavior using the portal’s network:
  1. Connects to WiFi (retries until `portal.network._wifi.is_connected`).
  2. Syncs time via `portal.network.get_local_time()` with retries on failure.

### Display

- **portal.display** with **auto_refresh = False**.

### Screen drawing (colors)

- **circleColor** / **centerColor**: white  
- **tickColor** / **secColor**: red  
- **minColor**: orange  
- **hourColor**: blue  
- **backColor**: grey77  
- **circleFillColor**: black  

Standard colored analog clock; all drawing is done by kds_analogclock. No custom display or update overrides beyond the portal setup.

## Setup

Configure WiFi (and any Adafruit IO credentials used by the portal for the time service) in **settings.toml** on the CIRCUITPY drive.
