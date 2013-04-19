#version 1

#!/usr/bin/python

from Adafruit_CharLCD import Adafruit_CharLCD
from time import sleep, strftime
from datetime import datetime
import RPi.GPIO as GPIO
import requests
import re

API_KEY="..."
WEATHER_INTERVAL=3
WEATHER_STATION="..."

lcd = Adafruit_CharLCD()
lcd.begin(16,2)

def clean_weather(weather):
    weather=re.sub(" ","",weather)
    if re.search("Mostly",weather):
        weather=re.sub("Mostly","M",weather)
    if re.search("Partly",weather):
        weather=re.sub("Partly","P",weather)
    if re.search("Scattered",weather):
        weather=re.sub("Scattered","Scat",weather)
    if re.search("Light",weather):
        weather=re.sub("Light","Lt",weather)
    return weather

def get_temp(diff):
    diff['d5'],diff['d4'],diff['d3'],diff['d2']=diff['d4'],diff['d3'],diff['d2'],diff['d1']
    r=requests.get("http://api.wunderground.com/api/"+API_KEY+"/conditions/q/pws:"+WEATHER_STATION+".json")
    actual=float(r.json()["current_observation"]["temp_f"])
    diff['d1']=actual
    diff['d5']=actual-diff['d5']
    if diff['d5']>0:
        diff['d5']="+"+str(diff['d5'])+"/h"
    else:
        diff['d5']=str(diff['d5'])+"/h"
    feel=float(r.json()["current_observation"]["feelslike_f"])
    if feel<actual-1 or feel>actual+1:
        temps=str(actual)+"/"+str(int(feel))
    else:
        temps=str(actual)+"F"
    weather=r.json()["current_observation"]["weather"]
    weather=clean_weather(weather)
    return temps,weather,diff


try:
    temps,weather="Please","Wait"
    diff={}
    diff['d1']=diff['d2']=diff['d3']=diff['d4']=diff['d5']=0

    while True:
        lcd.clear()
        if int(datetime.now().strftime("%M")) % WEATHER_INTERVAL==0 and int(datetime.now().strftime("%S"))==0:
            temps,weather,diff=get_temp(diff)
        lcd.message(datetime.now().strftime('%H:%M:%S'))
        lcd.setCursor(10,0)
        lcd.message(str(diff['d5']))
        lcd.setCursor(0,1)
        lcd.message(temps+"  "+weather)
        sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()

