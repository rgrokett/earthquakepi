#!/usr/bin/env python
# STARTUP 

# Uses LCD 20x4 I2C code from 
# https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
# 
# Expects LCD I2C on 0x27 address
#
# Install:
# $ sudo apt-get update
# $ sudo apt-get install build-essential git
# $ sudo apt-get install python-dev python-smbus python-pip 
# $ sudo apt-get install i2c-tools
#
# Usage via cron: 
# $ crontab -e
# @reboot sudo python /home/pi/earthquakepi/startup.py >/dev/null 2>&1
#
#
# Version 1.0 2016.06.11 - Initial
#
# License: GPLv3, see: www.gnu.org/licenses/gpl-3.0.html
#


import time
import RPi_I2C_driver


## METHODS BELOW

lcd = RPi_I2C_driver.lcd()
lcd.backlight(1)
lcd.lcd_clear()
lcd.lcd_display_string('EarthquakePi',1)
lcd.lcd_display_string('READY',2)
time.sleep(5)
lcd.lcd_clear()
lcd.backlight(0)
