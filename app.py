# Flaskサーバー
from flask import Flask, render_template
from weather import get_weather
from calculator import get_next_bus_from_json 

app = Flask(__name__)

@app.route("/")
def index():
    weather, temp = get_weather()
    bus = get_next_bus_from_json() 

    return render_template(
        "index.html",
        weather=weather,
        temp=temp,
        nextBusTime=bus["nextBusTime"],
        minutesUntilNextBus=bus["minutesUntilNextBus"],
    )

if __name__ == "__main__":
    app.run(debug=True)
