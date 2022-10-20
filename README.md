# Circuitpython Class to display an analog clock on multiple displays

## Introduction

I watched a video from [Dave's Garage](https://www.youtube.com/watch?v=yIpdBVu9xv8) where he wrote an analog clock for his LED display. Afterwards I realized I had a few Adafruit CircuitPython powered microcontrollers with displays. I have since implemented a CircuitPython class to display an analog clock. 

I have adopted my class to the boards around my desk as I find them. Most of these came from Adaboxes or other small projects I started and eventually abandoned.

## Supported Boards
| Board | Supported | Notes|
|----------|--------|--------
| [Funhouse](https://www.adafruit.com/product/4985) | Yes    | (1)(3)) |
| [Magtag](https://www.adafruit.com/product/4800)   | Yes    | (2)(3) |
| [Pyportal](https://www.adafruit.com/product/4116) | Yes    | (1)(3) |
| [M4 Matrix](https://www.adafruit.com/product/4745) | Yes   | (1)(3)(9) |
| [Feather Huzzah32](https://www.adafruit.com/product/3405)| Yes | (2)(5)(6) |
| [Circuit Playground Express](https://www.adafruit.com/product/3333) | No | (7)(8) |

## Notes
1) Lots of colors
2) Black and White
3) Uses Adafuit portal class for board
4) Uses a daily build of CircuitPython 8.0.0-beta.2
5) No portal class but cribbed local time code from the PortalBase class. 
6) Added the [128x32 OLED Feather Wing](https://www.adafruit.com/product/2900)
7) Added the [TFT Gizmo](https://www.adafruit.com/product/4367) for the display
8) Ran out of memory early in the development attempt
9) Added the [64x32 RGB LED Matrix](https://www.adafruit.com/product/2278)


## Design Notes

### Pre-computed the sin() and cos() values
There are 60 possible locations for the clock hands. The code will pre-compute the sin() and cos() values for these angles and store them in a table. The values are looked up as needed instead of being computed. 

### Reuse static image elements
The entire display is not generated with each update. 
The following elements are always static:
- The outer clock circle
- The center clock circle
- The tick marks around the clock
- The background behind the clock (if used)

Only the hands are regenerated when they have moved from a previous location with the hour hand updating only when it aligns with a tick mark.

### Update time
The class library will attempt to obtain the current time from Adafruit IO on startup and twice per day at 1AM and 1PM local time

### Dynamic sizing on startup
The size of the various elements is calculated based on the side of the display. The radius of the clock face is the smaller dimension of the display dimensions. All other elements are based from the radius with the values pre-calculated on startup. 

## Possible future / Todos
- Add more boards and displays
- Auto discover display size for boards with multiple displays. There are multiple OLED display wings
- Memory optimization. I think I can cut the sin()/cos() table by a quarter
- Clean up the connectNetwork(). The portal classes for the various boards are almost the same.
- Bug fixes. I think I have a 12:00 display issue with the hour hand. 
- Write a huzzah portal??
- Pictures
