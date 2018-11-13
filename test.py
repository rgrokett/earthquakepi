#!/usr/bin/env python
# TEST EARTHQUAKE 

# Uses LCD 20x4 I2C code from 
# https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
# 
# Turn off unused Options, below
# Expects LCD I2C on 0x27 address
# Optional NeoPixel 8 LED strip -- NEOPIXEL
# Optional Audio		-- AUDIO
# Optional Motor		-- MOTOR
#
# Usage:
#   sudo python test.py
#
#
# Version 1.3 2016.06.12 - LCD updates
# Version 1.4 2018.11.13 - Test program
#
# License: GPLv3, see: www.gnu.org/licenses/gpl-3.0.html
#


import subprocess
import os
import urllib2
import json
import datetime
import time
import atexit
import socket
import sys
import re
import traceback
import RPi.GPIO as GPIO

import RPi_I2C_driver

############ USER VARIABLES
DEBUG    = 1       # Debug ON for Testing
LOG      = 1       # Log Earthquake data for past 15 min
MINMAG   = 3.0     # Minimum magnitude to alert on
AUDIO    = 1       # Sound 0 off, 1 on
MOTOR    = 1	   # Vibrate Motor 0 off, 1 on
MOTORPIN = 16      # GPIO Pin for PWM motor control
NEOPIXEL = 1       # 1 use Neopixel, 0 don't use Neopixel
NEO_BRIGHTNESS = 64 # Set to 0 for darkest and 255 for brightest
## OTHER SETTINGS
PAUSE    = 5      # Display each test for X sec
WAV = "/home/pi/earthquakepi/earthquake.wav"  # Path to Sound file
DISPLAY  = 0       # 0 Turn off LCD at exit, 1 Leave LCD on after exit
########### END OF USER VARIABLES

if NEOPIXEL:
   import ledbar

GPIO.setmode(GPIO.BCM)  # Using BCM Pin layout
GPIO.setup(MOTORPIN, GPIO.OUT)
GPIO.output(MOTORPIN, False)

## METHODS BELOW

def blink(lcd): # Blink the LCD
    for i in range(0,3,1):
        lcd.backlight(1)
        time.sleep(0.3)
        lcd.backlight(0)
        time.sleep(0.3)
    lcd.backlight(1)

def volume(val): # Set Volume based on Magnitude
    vol = str((int(val) * 5) + 50)
    cmd = "sudo amixer -q sset PCM,0 "+str(vol)+"%"
    if DEBUG:
        cmd = "sudo amixer sset PCM,0 "+str(vol)+"%"
	print(cmd)
    os.system(cmd)
    return

def sound(val): # Play a sound
    time.sleep(1)
    cmd = "/usr/bin/aplay -q "+str(val)
    if DEBUG:
	print(cmd)
    os.system(cmd)
    return

def motor(mag): # Run Motor
    pulse = 1
    speed = int(mag * 3 + 20)  # Min 20 max 50
    duration = int(10 - mag)    # 2 sec to 20 sec
    sec = 0.1
    
    p = GPIO.PWM(MOTORPIN, 50)  # channel=MOTORPIN frequency=50Hz
    p.start(0)
    p.ChangeDutyCycle(speed)
    time.sleep(0.1)
    for dc in range(speed, 10, -(duration)):
         p.ChangeDutyCycle(dc)
         time.sleep(pulse)
         pulse = pulse + sec
    p.stop()
    return

def motor2(mag):	# If needed, use on/off motor instead of PWM
    GPIO.output(MOTORPIN, True)
    time.sleep(int(mag))
    GPIO.output(MOTORPIN, False)
    return 
    

def exit():
    """
    Exit handler, which clears all custom chars and shuts down the display.
    """
    try:
	if not DISPLAY:
            lcd = RPi_I2C_driver.lcd()
            lcd.backlight(0)
        if DEBUG:
            print "exit()"
        GPIO.cleanup()
    except:
        # avoids ugly KeyboardInterrupt trace on console...
        pass


#####


#####
# MAIN HERE
if __name__ == '__main__':
    atexit.register(exit)

    print "Testing each module..."  
    print "You should see/hear each installed module in turn."

    if NEOPIXEL:
        strip = ledbar.init()

    print "TESTING: LCD SCREEN..."
    lcd = RPi_I2C_driver.lcd()
    if DEBUG:
        lcd.backlight(1)
        lcd.lcd_clear()
        lcd.lcd_display_string('EarthquakePi',1)
        lcd.lcd_display_string('TESTING ON',2)
        lcd.lcd_display_string('DISPLAY TEST',3)
        print "LCD DISPLAY SHOULD BE ON"
        time.sleep(PAUSE)
        lcd.lcd_clear()
        lcd.backlight(0)
        if NEOPIXEL:
            print "TESTING: BARGRAPH..."
            ledbar.bargraph(strip,9)
            print "BARGRAPH SHOULD BE ON"
            time.sleep(PAUSE)
            ledbar.colorWipe(strip, ledbar.Color(0, 0, 0))  # Black wipe
        else :
            print "NEOPIXEL is NOT ACTIVATED" 
	if MOTOR:
            print "TESTING: MOTOR..."
            print "MOTOR SHOULD BE ON"
	    motor(4)
            time.sleep(PAUSE)
        else :
            print "MOTOR is NOT ACTIVATED" 
	if AUDIO:
            print "TESTING: AUDIO..."
	    volume(6)
            print "SOUND SHOULD BE ON"
	    sound(WAV)
            time.sleep(PAUSE)
        else :
            print "AUDIO is NOT ACTIVATED" 
    
    URL = "https://earthquake.usgs.gov/fdsnws/event/1/application.json"

    print "TESTING: URL ACCESS..."
    print URL

    try:
        tmout = 120
        response = urllib2.urlopen(URL, timeout=tmout)
        data = json.load(response)   
        if data['producttypes']:
            print "URL to USGS API TESTS GOOD"
    except:
	print "timeout waiting for USGS"
    
    if DEBUG:
        lcd.lcd_clear()
        lcd.backlight(0)
	
    if DEBUG:
        print "END OF TEST RUN"

