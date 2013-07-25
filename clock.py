#!/usr/bin/python

#############
# RasPi Weather Station v2
# copyright 2013, Modular Programming Systems Inc
# released as GPL3
#
#############

from Adafruit_CharLCD import Adafruit_CharLCD
from time import sleep, strftime
from datetime import datetime
import RPi.GPIO as GPIO
import requests
import re

API_KEY="..."
WEATHER_INTERVAL=3
WEATHER_STATION="..."
DISPLAY_CYCLE_SECONDS=5

lcd = Adafruit_CharLCD()
lcd.begin(16,2)

def clean_weather(weather):
    weather=re.sub(" ","",weather)
    weather=re.sub("Mostly","M",weather)
    weather=re.sub("Partly","P",weather)
    weather=re.sub("Scattered","Scat",weather)
    weather=re.sub("Light","Lt",weather)
    return weather

def clean_wind(wind):
    wind=re.sub("North","N",wind)
    wind=re.sub("South","S",wind)
    wind=re.sub("East","E",wind)
    wind=re.sub("West","W",wind)
    return wind

def historical(actual,diff):
    diff['d5'],diff['d4'],diff['d3'],diff['d2']=diff['d4'],diff['d3'],diff['d2'],diff['d1']
    diff['d1']=actual
    diff['d5']=actual-diff['d5']
    if diff['d5']>0:
        diff['d5']="+"+str(diff['d5'])+"/h"
    else:
        diff['d5']=str(diff['d5'])+"/h"
    return diff

def minmaxtemp(actual,current):
    if (datetime.now()-current["mintime"]).days>0:
        current["mintime"]=datetime.now()
        current["mintemp"]=200
    if (datetime.now()-current["maxtime"]).days>0:
        current["maxtime"]=datetime.now()
        current["maxtemp"]=-200
    if actual<current["mintemp"]:
        current["mintemp"]=actual
        current["mintime"]=datetime.now()
    if actual>current["maxtemp"]:
        current["maxtemp"]=actual
        current["maxtime"]=datetime.now()
    return current["mintemp"],current["mintime"],current["maxtemp"],current["maxtime"]

def get_weather(current):
    r=requests.get("http://api.wunderground.com/api/"+API_KEY+"/conditions/alerts/q/pws:"+WEATHER_STATION+".json")
    actualtemp=float(r.json()["current_observation"]["temp_f"])

    current["tempdiff"]=historical(actualtemp,current["tempdiff"])
    current["mintemp"],current["mintime"],current["maxtemp"],current["maxtime"]=minmaxtemp(actualtemp,current)

    feel=float(r.json()["current_observation"]["feelslike_f"])
    if feel<actualtemp-1 or feel>actualtemp+1:
        current["temps"]=str(int(actualtemp))+"/"+str(int(feel))
    else:
        current["temps"]=str(actualtemp)+"F"

    weather=clean_weather(r.json()["current_observation"]["weather"])

    wind_dir=clean_wind(r.json()["current_observation"]["wind_dir"])
    wind_speed=int(r.json()["current_observation"]["wind_mph"])
    wind="w:"+wind_dir+" "+str(wind_speed)

    humidity="humid:"+r.json()["current_observation"]["relative_humidity"]

    UV="UV: "+str(int(r.json()["current_observation"]["UV"]))

    rain='rn: '+r.json()["current_observation"]["precip_1hr_in"]+'"'

    mintemp="Min: "+str(current["mintemp"])
    maxtemp="Max: "+str(current["maxtemp"])

    current["weather_list"]=[weather,wind,humidity,UV,rain,mintemp,maxtemp]

    return current


try:
    current={}
    current["temps"]="Please"
    current["tempdiff"]={}
    current["tempdiff"]["d1"]=0
    current["tempdiff"]["d2"]=0
    current["tempdiff"]["d3"]=0
    current["tempdiff"]["d4"]=0
    current["tempdiff"]["d5"]=0
    current["mintemp"]=200  #impossibly high temp
    current["maxtemp"]=-200  #impossibly low temp
    current["mintime"]=current["maxtime"]=datetime(2000,1,1,12,0,0)  #old time
    current["weather_list"]=['wait']
    i=0

    while True:
        lcd.clear()
        if int(datetime.now().strftime("%M")) % WEATHER_INTERVAL==0 and int(datetime.now().strftime("%S"))==0:
            current=get_weather(current)
        tempdiff=current["tempdiff"]["d5"]
        lcd.message(datetime.now().strftime('%H:%M:%S'))
        lcd.setCursor(10,0)
        lcd.message(str(tempdiff))
        lcd.setCursor(0,1)
        if int(datetime.now().strftime("%S"))%DISPLAY_CYCLE_SECONDS == 0:
            i+=1
        lcd.message(current["temps"]+"  "+current["weather_list"][i%len(current["weather_list"])])
        sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()

