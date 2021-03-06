# earthquakepi
Shake &amp; Rattle Raspberry Pi when an earthquake occurs

Version 2.0 -- Converted to Python3

There are a number of earthquake detector projects for the raspberry pi. These are good for anyone living in an area prone to earthquakes or for those that want to try to detect distant quakes themselves. 

This project is not focused on detecting quakes, but uses USGS earthquake data to make an interesting little alerting system.  Sure, you can always go to your PC and browse the USGS maps for the latest data, but you are a Maker and this is a project for Makers!


What does it do?
•	It collects the USGS earthquake data for the past 15 minutes. 
•	It rattles its box and flashes its lights to the magnitude of the quake
•	It displays location, magnitude and other data on a small LCD screen
•	It plays earthquake sounds (optionally)

You set the minimum magnitude level you wish it to alarm on. But note, if you set to below 2.0, it will probably go off almost constantly!


## Update
2018-11: A test program is now included so you can easily test each optional feature of the earthquake box.  

```
cd /home/pi/earthquakepi
sudo python test.py
```

2019-06: Updated all the Adafruit drivers and converted to Python3. You have to start with fresh install to apply this. No changes to hardware are needed, but all software, including OS must be updated.


See EarthquakePi.pdf for construction details.

