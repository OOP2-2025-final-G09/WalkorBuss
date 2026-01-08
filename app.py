from flask import Flask, render_template
from weather import get_weather

# judge.py から判定ロジックを読み込む
from judge import judge_walk_or_bus

from calculator import get_next_bus_from_json


app = Flask(__name__)

@app.route("/")
def index():
    # 1. 天気を取得
    weather, temp = get_weather()
    
    # 2. 判定ロジックを実行してデータを取得
    judgment_data = judge_walk_or_bus()

    # 3. 画面(index.html)にデータを渡す
    # ここで 'judgment=judgment_data' とすることで、HTML側で 'judgment' として使えるようになる
    return render_template(
        "index.html",
        weather=weather,
        temp=temp,
        judgment=judgment_data 
    )

if __name__ == "__main__":
    app.run(debug=True)