#!/usr/bin/python3

import datetime
import requests
import os
import json
from functools import reduce

APPID = "<openweathermapapikey>"
LOCATION = "<locationcode>"
API= "https://api.openweathermap.org/data/2.5/"
CURRENT = "weather"
FORECAST = "forecast"
CACHEFILE = os.path.expanduser("~/.cache/weather")

current_request = "{}{}?id={}&APPID={}&units=metric".format(API, CURRENT, LOCATION, APPID)
forecast_request = "{}{}?id={}&APPID={}&units=metric".format(API, FORECAST, LOCATION, APPID)

r = requests.get(current_request)
current = json.loads(r.text)

current_day = datetime.datetime.utcfromtimestamp(current['dt']).strftime("%a")
current_tmp = round(current['main']['temp'])
current_prs = round(current['main']['pressure'])
current_wnd = round(current['wind']['speed'])
current_hum = round(current['main']['humidity'])
current_wth = current['weather'][0]['main']
current_ico = current['weather'][0]['icon']

r = requests.get(forecast_request)
forecast = json.loads(r.text)

threehours = iter(forecast['list'])
days = {}
for x in threehours:
    day = datetime.datetime.utcfromtimestamp(x['dt']).strftime("%a")
    if day not in days:
        days[day] = {'temp': [], 'weather': [], 'pressure': [], 'wind': [], 'humidity': []}
    temp = x['main']['temp']
    pressure = x['main']['pressure']
    humidity = x['main']['humidity']
    wind = x['wind']['speed']
    weather = x['weather'][0]

    days[day]['temp'].append(temp)
    days[day]['pressure'].append(pressure)
    days[day]['humidity'].append(humidity)
    days[day]['wind'].append(wind)
    days[day]['weather'].append(weather)

fd = open(CACHEFILE, "w")
fd.write("{} {} {} {} {} {} {}\n".format(current_day, current_tmp, current_prs, current_wnd, current_hum, current_wth, current_ico))
for day, val in days.items():
    avg_temp = round(reduce(lambda x,y : x+y, val['temp'])/len(val['temp']))
    avg_pres = round(reduce(lambda x,y : x+y, val['pressure'])/len(val['pressure']))
    avg_wind = round(reduce(lambda x,y : x+y, val['wind'])/len(val['wind']))
    avg_humi = round(reduce(lambda x,y : x+y, val['humidity'])/len(val['humidity']))

    min_temp = round(min(val['temp']))
    min_pres = round(min(val['pressure']))
    min_wind = round(min(val['wind']))
    min_humi = round(min(val['humidity']))

    max_temp = round(max(val['temp']))
    max_pres = round(max(val['pressure']))
    max_wind = round(max(val['wind']))
    max_humi = round(max(val['humidity']))

    # just figure out the most weather type for the day (or whatever the first is)
    top = 0
    ttype = ''
    ticon = ''
    counts = {}
    for t in val['weather']:
        type = t['main']
        icon = t['icon']
        if type in counts:
            counts[type] += 1
        else:
            counts[type] = 1

        if counts[type] > top:
            top = counts[type]
            ttype = type
            ticon = icon


    fd.write("{} {}/{} {} {} {} {} {}\n".format(day, min_temp, max_temp, avg_pres, avg_wind, avg_humi, ttype, ticon))
fd.close()
