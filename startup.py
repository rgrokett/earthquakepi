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
import socket
import RPi_I2C_driver


# Find local IP address
myip = ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])


lcd = RPi_I2C_driver.lcd()
lcd.backlight(1)
lcd.lcd_clear()
lcd.lcd_display_string('EarthquakePi',1)
lcd.lcd_display_string('READY',2)
lcd.lcd_display_string(myip,3)
time.sleep(5)
lcd.lcd_clear()
lcd.backlight(0)
