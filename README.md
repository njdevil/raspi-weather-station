raspi-weather-station
=====================

LCD Weather Station for RasPi
using Adafruit_CharLCD package to display on 16x2 LCD screen

Overview
=======
Weather Station will retrieve via the Internet the JSON object of your preferred Weather Underground Personal Weather Station.

Due to API limitations, this is currently set to retrieve every 3 minutes.  With a different plan, you can have it update as required, but does the temp really change that much in 3 minutes?

LCD display is as follows:
Top Left: 24hr time with Seconds
Top Right: Temperature Change per 15min (5 cycles of the retrieval)
Bottom Left: Current Temp (and Wind Chill/Heat Index as available)
Bottom Right: Truncated Current Conditions (PCloudy instead of Partly Cloudy)


Historical
=======
Historical data is stored for 5 cycles of the retrieval time and the change in temperature is calculated from this.


Outstanding Task
========
Need to use the Adafruit library to display a custom character instead of the current "/h" after the Temperature Change.  A nice 1/4 graphic smooshed into 1 cell would be great!
