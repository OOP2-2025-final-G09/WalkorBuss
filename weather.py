# 天気API
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

def get_weather():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "Okazaki,jp",
        "units": "metric",
        "appid": API_KEY,
        "lang": "ja"
    }

    res = requests.get(url, params=params)
    data = res.json()
    #print(data)

    weather = data["weather"][0]["description"]
    temp = data["main"]["temp"]

    return weather, temp
