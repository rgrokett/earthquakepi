#!/usr/bin/env python
# EARTHQUAKE 

# Uses LCD 20x4 I2C code from 
# https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
# 
# Expects LCD I2C on 0x27 address
#
# Install:
# $ sudo apt-get update
# $ sudo apt-get install build-essential git
# $ sudo apt-get install python-dev python-smbus python-pip 
# $ sudo pip install RPi.GPIO
# $ sudo apt-get install i2c-tools
#
# Optional NeoPixel 8 LED strip
# Optional Audio
# Optional Motor
#
# Usage via cron: 
# $ crontab -e
# 0,15,30,45 08-22 * * * sudo python /home/pi/earthquakepi/earthquakepi.py >/home/pi/earthquakepi/earth.log 2>&1
#
#
# Version 1.2 2016.06.07 - LCD updates
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
DEBUG    = 1       # Debug 0 off, 1 on
MINMAG   = 1.0     # Minimum magnitude to alert on
AUDIO    = 1       # Sound 0 off, 1 on
PIN      = 12      # GPIO Pin for PWM motor control
PAUSE    = 60      # Display each Earthquake for X seconds
DISPLAY  = 0       # 0 Turn off LCD at exit, 1 Leave LCD on after exit
NEOPIXEL = 0       # 1 use Neopixel, 0 don't use Neopixel
WAV = "/home/pi/earthquakepi/earthquake.wav"  # Path to Sound file
########### END OF USER VARIABLES

if NEOPIXEL:
   import ledbar

GPIO.setmode(GPIO.BCM)  # Using BCM Pin layout
GPIO.setup(PIN, GPIO.OUT)
GPIO.output(PIN, False)

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
    cmd = "/usr/bin/aplay -q "+ str(val)
    if DEBUG:
	print(cmd)
    os.system(cmd)
    #proc = subprocess.call(['/usr/bin/aplay', WAV], stderr=subprocess.PIPE)
    return

def motor(mag): # Run Motor
    pulse = 1
    speed = int(mag * 3 + 20)  # Min 20 max 50
    duration = int(10 - mag)    # 2 sec to 20 sec
    sec = 0.1
    
    p = GPIO.PWM(PIN, 50)  # channel=PIN frequency=50Hz
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
    GPIO.output(PIN, True)
    time.sleep(int(mag))
    GPIO.output(PIN, False)
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

    # timeout in seconds
    socket.setdefaulttimeout(90)

    if NEOPIXEL:
        strip = ledbar.init()

    lcd = RPi_I2C_driver.lcd()
    if DEBUG:
        lcd.backlight(1)
        lcd.lcd_clear()
        lcd.lcd_display_string('EarthquakePi',1)
        lcd.lcd_display_string('DEBUG ON',2)
        lcd.lcd_display_string('All Times are UTC',3)
	print "DEBUG MODE"
        print "STARTUP"
        if NEOPIXEL:
            ledbar.bargraph(strip,9)
	motor(MINMAG)
	volume(6)
	sound(WAV)
	PAUSE = 10
    
    utcnow = datetime.datetime.utcnow()
    utcnow_15 = utcnow - datetime.timedelta(minutes = 15)
    starttime = utcnow_15.strftime('%Y-%m-%dT%H:%M:%S')
    endtime = utcnow.strftime('%Y-%m-%dT%H:%M:%S')

    URL = "http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime="+starttime+"&endtime="+endtime+"&minmagnitude="+str(MINMAG)

    print URL

    response = urllib2.urlopen(URL)
    data = json.load(response)   
    if DEBUG:
        print "--------------"
        print data
        print "--------------"

    cnt = 0
    for feature in data['features']:
        if DEBUG:
            print feature['properties']['mag']
            print feature['properties']['time']
            print feature['properties']['place']
            print feature['geometry']['coordinates']
            print feature['properties']['title']
            print "--------------"

        try:
            tm  = feature['properties']['time']
            mag = feature['properties']['mag']
            title = feature['properties']['title']
            loc = feature['geometry']['coordinates']
    
	    tm = tm/1000
            utime = datetime.datetime.utcfromtimestamp(int(tm)).strftime('%Y-%m-%d %H:%M:%S')
	    lines = re.findall(r'.{1,19}(?:\s+|$)', title)
    
	    # LED BAR
	    if NEOPIXEL:
                # Color wipe animations.
                if (int(mag) < 4):
                    ledbar.leds(strip, LED_BRIGHTNESS,0,0)     # Green
                elif (int(mag) > 6):
                    ledbar.leds(strip, 0,LED_BRIGHTNESS,0)     # Red
                else:
                    ledbar.leds(strip, LED_BRIGHTNESS,LED_BRIGHTNESS,0) # Yellow
    
                ledbar.bargraph(strip,mag)
	    
	    # LCD
	    pos = 1
	    blink(lcd)
	    for line in lines:
	        lcd.lcd_display_string(line,pos)
	        pos = pos + 1 
	    lcd.lcd_display_string(utime,pos)
    	
	    for line in lines:
	        print("> "+ str(line))
	    print("> "+ str(utime))
    	
	    # Rumble Motor
	    motor(mag)

	    # Sound
	    if AUDIO:
	        volume(mag)
                sound(WAV)
	    cnt = cnt + 1
	    time.sleep(PAUSE)
	    if NEOPIXEL:
	        ledbar.colorWipe(strip, ledbar.Color(0, 0, 0))  # Black wipe
    
        except NameError:
            print "No "+str(MINMAG)+" magnitude earthquakes in past 15 minutes"
            if DEBUG:
                print(traceback.format_exc())
        except Exception as e:
            print "Unexpected error:", sys.exc_info()[0]
            if DEBUG:
                print(traceback.format_exc())

    # END FOR LOOP
    if NEOPIXEL:
        ledbar.colorWipe(strip, ledbar.Color(0, 0, 0))  # Black wipe

    if (cnt == 0):
        lcd.backlight(DISPLAY)
        lcd.lcd_clear()
        lcd.lcd_display_string('EarthquakePi',1)
        lcd.lcd_display_string('No quakes in 15 min',2)
        lcd.lcd_display_string(utcnow.strftime('%Y-%m-%dT%H:%M:%S'),3)
	time.sleep(PAUSE)
	
    if DEBUG:
        print "END OF RUN"

