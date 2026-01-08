# 天気API
import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "Toyota,jp",
        "units": "metric",
        "appid": WEATHER_API_KEY,
        "lang": "ja"
    }

    res = requests.get(url, params=params)
    data = res.json()
    #print(data)

    weather = data["weather"][0]["main"]
    temp = data["main"]["temp"]

    return weather, temp
