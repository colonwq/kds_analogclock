# M4 Matrix Portal Analog Clock

This example runs the kds_analogclock on the [Adafruit Matrix Portal M4](https://www.adafruit.com/product/4745) (or compatible M4 + [64×32 RGB LED Matrix](https://www.adafruit.com/product/2278)). It uses the MatrixPortal for display and **WiFi + portal time API** for time sync.

## Customizations from kds_analogclock

### Display and portal

- Uses **MatrixPortal** (adafruit_matrixportal) for display and network.
- **connectNetwork** uses the portal’s network:
  1. Connects to WiFi (retries until `portal.network.is_connected`).
  2. Syncs time via `portal.network.get_local_time()` with retries.
- Includes a fallback to create a `Network()` instance if `portal.network` is None (not expected after normal MatrixPortal init).

### Screen drawing (colors)

- Colored theme suited to an RGB matrix:
  - **circleColor** / **centerColor**: white  
  - **tickColor** / **secColor**: red  
  - **minColor**: orange  
  - **hourColor**: blue  
  - **backColor**: black (set twice in init)  
  - **circleFillColor**: black  

All drawing is handled by kds_analogclock; only colors and portal/network setup are customized.

## Setup

Configure WiFi and any Adafruit IO credentials required by the portal for the time service in **settings.toml** on the CIRCUITPY drive. Tested with a 32×64 matrix; other matrix sizes should work with the base class’s dynamic sizing.
