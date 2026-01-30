# Qualia S3 Analog Clock

This example runs the kds_analogclock on the [Adafruit Qualia S3](https://www.adafruit.com/product/5800) using the Qualia display and **WiFi + portal network** for time sync. The Qualia supports multiple display types; the active one is chosen via configuration.

## Customizations from kds_analogclock

### Display selection

- Uses **Qualia** (adafruit_qualia) for display and WiFi.
- **Display type** is read from the environment: `Qualia(display_type=os.getenv("DISPLAY_TYPE"))`, typically set in **settings.toml** on the CIRCUITPY drive.
- Developed with the 2.1" capacitive touch display; other Qualia display sizes can be used by setting `DISPLAY_TYPE` accordingly.

### Network (connectNetwork)

- **connectNetwork** extends the base behavior using the portal’s network:
  1. Connects to WiFi (retries until `portal.network._wifi.is_connected`).
  2. Syncs time via `portal.network.get_local_time()` with retries on failure.

No display-specific drawing overrides; all clock graphics come from kds_analogclock.

### Screen drawing (colors)

- **circleColor** / **centerColor**: white  
- **tickColor** / **secColor**: red  
- **minColor**: orange  
- **hourColor**: blue  
- **backColor**: grey77  
- **circleFillColor**: black  

**display.auto_refresh = False** is set for explicit refresh control.

## Setup

In **settings.toml** on the CIRCUITPY drive, set at least:

- `DISPLAY_TYPE` – e.g. `"round21"` for the 2.1" round display.
- WiFi credentials (e.g. `CIRCUITPY_WIFI_SSID`, `CIRCUITPY_WIFI_PASSWORD`) and any Adafruit IO keys required by the portal for the time service.

Example:

```toml
DISPLAY_TYPE = "round21"
CIRCUITPY_WIFI_SSID = "your_network_name"
CIRCUITPY_WIFI_PASSWORD = "your_password"
```
