# NeoPixel LED BAR
#
# Python3 version
# 
# TO SET UP AND TEST NEOPIXEL, MUST SEE
# https://learn.adafruit.com/neopixels-on-raspberry-pi/software


import time, math
import board
import neopixel



# LED strip configuration:
LED_COUNT      = 8       # Number of LED pixels.
LED_BRIGHTNESS = 64      # Set to 0 for darkest and 255 for brightest
LED_ORDER      = neopixel.RGB
LED_PIN        = board.D12

# List of colors to assign to each LED
LED_LIST = [
[LED_BRIGHTNESS,0,0],
[LED_BRIGHTNESS,0,0],
[LED_BRIGHTNESS,0,0],
[LED_BRIGHTNESS,LED_BRIGHTNESS,0],
[LED_BRIGHTNESS,LED_BRIGHTNESS,0],
[0,LED_BRIGHTNESS,0],
[0,LED_BRIGHTNESS,0],
[0,LED_BRIGHTNESS,0]
]

def init():
    # Create NeoPixel object with appropriate configuration.
    strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, 
                              auto_write=False, pixel_order=LED_ORDER)

    # Intialize the library (must be called once before other functions).
    return(strip)


# Blink colors
def colorWipe(strip, color, wait_ms=250):
  """Wipe color across display a pixel at a time."""
  strip.fill(color)
  strip.show()
  time.sleep(wait_ms/1000.0)

# Display Bargraph
def bargraph(strip,mag):
  num_leds = int(round(((mag-1.0)/(10.0-1.0))*8))
  for x in range(num_leds):
      g = LED_LIST[x][0]
      r = LED_LIST[x][1]
      b = LED_LIST[x][2]
      strip[x]=(g,r,b)
  strip.show()
  

def leds(strip, g, r, b):
  for i in range(0,5,1):
      colorWipe(strip, (g, r, b))  # Color wipe
      colorWipe(strip, (0, 0, 0))  # Black wipe


