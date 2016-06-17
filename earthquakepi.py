#!/usr/bin/env python
# EARTHQUAKE 

# Uses LCD 20x4 I2C code from 
# https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
# 
# Expects LCD I2C on 0x27 address
#
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
# Version 1.3 2016.06.12 - LCD updates
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
LOG      = 1       # Log Earthquake data for past 15 min
MINMAG   = 1.0     # Minimum magnitude to alert on
AUDIO    = 1       # Sound 0 off, 1 on
MOTOR    = 1	   # Vibrate Motor 0 off, 1 on
MOTORPIN = 16      # GPIO Pin for PWM motor control
NEOPIXEL = 1       # 1 use Neopixel, 0 don't use Neopixel
NEO_BRIGHTNESS = 64 # Set to 0 for darkest and 255 for brightest
## OTHER SETTINGS
PAUSE    = 60      # Display each Earthquake for X seconds
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
    #proc = subprocess.call(['/usr/bin/aplay', WAV], stderr=subprocess.PIPE)
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
	if MOTOR:
	    motor(4)
	if AUDIO:
	    volume(6)
	    sound(WAV)
	PAUSE = 10
    
    utcnow = datetime.datetime.utcnow()
    utcnow_15 = utcnow - datetime.timedelta(minutes = 15)
    utcnow_30 = utcnow - datetime.timedelta(minutes = 30)
    starttime = utcnow_30.strftime('%Y-%m-%dT%H:%M:%S')
    endtime = utcnow_15.strftime('%Y-%m-%dT%H:%M:%S')

    URL = "http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime="+starttime+"&endtime="+endtime+"&minmagnitude="+str(MINMAG)

    if LOG:
	print URL

    # Call USGS API. timeout in seconds (USGS response time can be slow!)
    try:
        tmout = 120
        #socket.setdefaulttimeout(tmout)
        response = urllib2.urlopen(URL, timeout=tmout)
        data = json.load(response)   
        if DEBUG:
            print "--------------"
            print data
            print "--------------"
    except:
	print "timeout waiting for USGS"
    
    cnt = 0
    for feature in data['features']:
        if LOG:
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
    
	    # Rumble Motor
	    if MOTOR:
	        motor(mag)

	    # LED BAR
	    if NEOPIXEL:
                # Color wipe animations.
                if (int(mag) < 4):
                    ledbar.leds(strip, NEO_BRIGHTNESS,0,0)     # Green
                elif (int(mag) > 6):
                    ledbar.leds(strip, 0,NEO_BRIGHTNESS,0)     # Red
                else:
                    ledbar.leds(strip, NEO_BRIGHTNESS,NEO_BRIGHTNESS,0) # Yellow
    
                ledbar.bargraph(strip,mag)
	    
	    # LCD 20 x 4 DISPLAY
	    pos = 1
            lcd.lcd_clear()
	    blink(lcd)
	    for line in lines:
	        lcd.lcd_display_string(line,pos)
	        pos = pos + 1 
	    lcd.lcd_display_string(utime,pos)
    	
	    for line in lines:
	        print("> "+ str(line))
	    print("> "+ str(utime))
    	
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
            print(traceback.format_exc()) # TEMPY
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
	if LOG:
	    print "No quakes in past 15 min"
	
    if DEBUG:
        print "END OF RUN"

