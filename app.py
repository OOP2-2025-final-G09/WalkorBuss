# Flaskサーバー
from flask import Flask, render_template
from weather import get_weather

app = Flask(__name__)

@app.route("/")
def index():
    weather, temp = get_weather()
    return render_template(
        "index.html",
        weather=weather,  # これでweatherがindex.htmlで使えるようになる
        temp=temp  # これでtempがindex.htmlで使えるようになる
    )

if __name__ == "__main__":
    app.run(debug=True)


