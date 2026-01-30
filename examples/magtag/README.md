# MagTag Analog Clock

This example runs the kds_analogclock on the [Adafruit MagTag](https://www.adafruit.com/product/4800), an e-paper (e-ink) board. It uses the MagTag display and **WiFi + portal time API** for time sync, and customizes the **update** loop for e-ink refresh behavior.

## Customizations from kds_analogclock

### Display and update behavior

- Uses **MagTag** (adafruit_magtag) for display and network.
- **update()** is overridden to match e-ink characteristics:
  - Uses the display’s **time_to_refresh** and **enter_light_sleep** so the MagTag sleeps between updates for the recommended refresh interval, then calls the base class `update()`.
  - Reduces unnecessary refreshes and avoids damaging the e-ink panel.

### Network (connectNetwork)

- **connectNetwork** uses the portal’s network:
  1. Connects to WiFi (retries until `portal.network._wifi.is_connected`).
  2. Syncs time via `portal.network.get_local_time()` with retries.

### Screen drawing (colors)

- E-ink is **black and white**; all clock elements use black on a white background:
  - **circleColor**, **centerColor**, **tickColor**, **secColor**, **minColor**, **hourColor**: black  
  - **backColor**: white  
  - **circleFillColor**: white  

No custom drawing logic beyond color choices; kds_analogclock handles the rest.

## Setup

Configure WiFi (and any Adafruit IO keys used by the portal for time) in **settings.toml** on the CIRCUITPY drive. The MagTag will connect, sync time, then run the clock with e-ink–friendly update timing.
