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
# $ sudo python setup.py install
# $ sudo apt-get install aplay 
# $ sudo apt-get install i2c-tools
#
# Usage via cron: 
# $ crontab -e
# 0,15,30,45 08-23 * * * sudo python -u ./earthquakepi.py >/home/pi/earth.log 2>&1
#
#
# Version 1.0 2016.05.01 - Initial release
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
DEBUG = 1        # Debug 0 off 1 on
MINMAG = 1.0	 # Minimum magnitude to alert on
AUDIO  = 1       # Sound 0 off 1 on
WAV = "/home/pi/earthquake.wav"  # Path to Sound file
PIN = 12	 # GPIO Pin for PWM motor control
TIMEOUT = 60	 # Timeout waiting for response from URL
########### END OF USER VARIABLES


GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.OUT)

## METHODS BELOW

def volume(val): # Set Volume based on Magnitude
    vol = str((int(val) * 5) + 50)
    cmd = "sudo amixer sset PCM,0 "+str(vol)+"%"
    if DEBUG:
	print(cmd)
    os.system(cmd)
    return

def sound(val): # Play a sound
    time.sleep(1)
    cmd = "/usr/bin/aplay "+ str(val)
    if DEBUG:
	print(cmd)
    os.system(cmd)
    #proc = subprocess.call(['/usr/bin/aplay', WAV], stderr=subprocess.PIPE)
    return

def exit():
    """
    Exit handler, which clears all custom chars and shuts down the display.
    """
    try:
        lcd = RPi_I2C_driver.lcd()
    except:
        # avoids ugly KeyboardInterrupt trace on console...
        pass


#####


#####
# MAIN HERE
if __name__ == '__main__':
    atexit.register(exit)

    # timeout in seconds
    socket.setdefaulttimeout(TIMEOUT)

    lcd = RPi_I2C_driver.lcd()
    lcd.backlight(1)
    if DEBUG:
        lcd.lcd_clear()
        lcd.lcd_display_string('EarthquakePi',1)
        lcd.lcd_display_string('DEBUG ON',2)
	print "DEBUG MODE"
        print "STARTUP"
	volume(6)
	sound(WAV)
    
    utcnow = datetime.datetime.utcnow()
    utcnow_15 = utcnow - datetime.timedelta(minutes = 15)
    starttime = utcnow_15.strftime('%Y-%m-%dT%H:%M:%S')
    endtime = utcnow.strftime('%Y-%m-%dT%H:%M:%S')

    URL = "http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime="+starttime+"&endtime="+endtime+"&minmagnitude="+str(MINMAG)

    if DEBUG:
	print URL

    response = urllib2.urlopen(URL)
    data = json.load(response)   
    if DEBUG:
        print data
        print "--------------"


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
    
	    # LCD
	    pos = 1
	    for line in lines:
	        lcd.lcd_display_string(line,pos)
	        pos = pos + 1 
	    lcd.lcd_display_string(utime,pos)
    	
	    for line in lines:
	        print("> "+ str(line))
	    print("> "+ str(utime))
    	
	    # Sound
	    volume(mag)
            sound(WAV)
    
	    # Rumble Motor
	    pulse = 1
            speed = int(mag * 5 + 50)  # Min 50 max 100
            duration = int(10 - mag)    # 2 sec to 20 sec
            sec = 0.1
    
            p = GPIO.PWM(PIN, 50)  # channel=PIN frequency=50Hz
            p.start(0)
            p.ChangeDutyCycle(speed)
            time.sleep(0.1)
            for dc in range(speed, -1, -(duration)):
                  p.ChangeDutyCycle(dc)
                  time.sleep(pulse)
                  pulse = pulse + sec
            p.stop()
            GPIO.cleanup()
        except NameError:
            print "No "+str(MINMAG)+" magnitude earthquakes in past 15 minutes"
            if DEBUG:
                print(traceback.format_exc())
        except Exception as e:
            print "Unexpected error:", sys.exc_info()[0]
            if DEBUG:
                print(traceback.format_exc())
	if DEBUG:
	    print "END OF RUN"

