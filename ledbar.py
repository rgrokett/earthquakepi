# NeoPixel LED BAR
#
# 
# TO SET UP AND TEST NEOPIXEL, MUST SEE
# https://learn.adafruit.com/neopixels-on-raspberry-pi/software


import time, math
from neopixel import *


# LED strip configuration:
LED_COUNT      = 8       # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 64     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

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
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    return(strip)


# Blink colors
def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

# Display Bargraph
def bargraph(strip,mag):
        num_leds = int(round(((mag-1.0)/(10.0-1.0))*8))
	for x in range(0,num_leds):
	    g = LED_LIST[x][0]
	    r = LED_LIST[x][1]
	    b = LED_LIST[x][2]
	    strip.setPixelColor(x, Color(g,r,b))
	strip.show()
	

def leds(strip, g, r, b):
	for i in range(0,5,1):
	    colorWipe(strip, Color(g, r, b))  # Color wipe
	    colorWipe(strip, Color(0, 0, 0))  # Black wipe


