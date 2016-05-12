#!/usr/bin/env python
# EARTHQUAKE 

# Install Adafruit LCD lib & dependencies from
#    https://github.com/adafruit/Adafruit_Python_CharLCD
#
# Also install:
# $ sudo apt-get install python-pip python-dev
#
# Usage:
# $ sudo nohup python -u ./earthquakepi.py &
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

from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

############ USER VARIABLES
DEBUG = 1        # Debug 0 off 1 on
MINMAG = 1.0	 # Minimum magnitude to alert on
AUDIO  = 1       # Sound 0 off 1 on
QUIET  = [ 00, 07 ] # Don't play audio between midnight & 7:59AM
WAV = "/home/pi/earthquake.wav"  # Path to Sound file
PIN = 12	 # GPIO Pin for PWM motor control
TIMEOUT = 60	 # Timeout waiting for response from URL
########### END OF USER VARIABLES


GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.OUT)

## METHODS

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

def isQuiet():  # Quiet time no sound
        if AUDIO:
            hour = time.strftime('%H')
            if int(hour) >= QUIET[0] and int(hour) < QUIET[1]:
                return(1)
            else:
                return(0)
        return(1)

def exit():
    """
    Exit handler, which clears all custom chars and shuts down the display.
    """
    try:
        lcd = Adafruit_CharLCDPlate()
        #lcd.backlight(lcd.OFF)
        #clearChars(lcd)
        #lcd.stop()
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

    lcd = Adafruit_CharLCDPlate()
    lcd.backlight(lcd.ON)
    if DEBUG:
        lcd.clear()
        lcd.message('EarthquakePi\n')
        lcd.message('DEBUG ON')
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
	    for line in lines:
	        lcd.message(line)
	    lcd.message(utime)
    	
	    for line in lines:
	        print("> "+ str(line))
	    print("> "+ str(utime))
    	
	    # Sound
            if (not isQuiet()):
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

