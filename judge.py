import json
import os
from datetime import datetime, timedelta
from calculator import get_next_bus_from_json

# 設定
WALK_MINUTES = 15      # 徒歩所要時間
BUS_RIDE_MINUTES = 7   # バス乗車時間

def load_json(filename):
    filepath = os.path.join("data", filename)
    if not os.path.exists(filepath):
        filepath = filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_dt_from_str(base_dt, time_str):
    """HH:MM文字列をdatetimeオブジェクトに変換"""
    hour, minute = map(int, time_str.split(':'))
    return base_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

def find_catchable_train(now, timetable, arrival_walk, arrival_bus):
    """
    徒歩またはバスのどちらかで間に合う、直近の電車を探す
    """
    current_time_str = now.strftime("%H:%M")

    # 時刻表をループして探す
    for time_str in timetable:
        # そもそも現在時刻より前の電車は無視（念のため）
        if time_str < current_time_str:
            continue

        train_dt = get_dt_from_str(now, time_str)

        # 判定: 徒歩で間に合う OR バスで間に合う？
        can_walk = arrival_walk <= train_dt

        can_bus = False
        if arrival_bus:
            can_bus = arrival_bus <= train_dt

        # どちらか一方で間に合うなら、これをターゲット電車とする
        if can_walk or can_bus:
            return train_dt, time_str

    return None, None

def get_status_text(can_make_it, wait_time):
    if can_make_it:
        return f"待ち {wait_time}分"
    else:
        return "間に合わない"

def judge_walk_or_bus():
    now = datetime.now()

    # --- 1. バスと徒歩の「駅到着時刻」を先に確定させる ---

    # 徒歩到着時刻
    arrival_walk_dt = now + timedelta(minutes=WALK_MINUTES)

    # バス到着時刻
    bus_data = get_next_bus_from_json(now)
    bus_time_str = bus_data.get("nextBusTime")

    arrival_bus_dt = None
    if bus_time_str:
        bus_dep_dt = get_dt_from_str(now, bus_time_str)
        arrival_bus_dt = bus_dep_dt + timedelta(minutes=BUS_RIDE_MINUTES)

    # --- 2. 方面ごとに「乗れる電車」を探す ---
    train_files = {
        "okazaki": "train_okazaki.json",
        "kozoji": "train_kozoji.json"
    }

    results = {}

    for key, file in train_files.items():
        timetable = load_json(file)

        # ★ここが変更点: 単なる「次の電車」ではなく「間に合う電車」を探す
        train_dt, train_str = find_catchable_train(now, timetable, arrival_walk_dt, arrival_bus_dt)

        if train_dt:
            # その電車に対する待ち時間を再計算
            is_walk_ok = arrival_walk_dt <= train_dt
            wait_walk = int((train_dt - arrival_walk_dt).total_seconds() / 60) if is_walk_ok else -1

            is_bus_ok = False
            wait_bus = -1
            if arrival_bus_dt:
                is_bus_ok = arrival_bus_dt <= train_dt
                wait_bus = int((train_dt - arrival_bus_dt).total_seconds() / 60) if is_bus_ok else -1

            results[key] = {
                "next_train": train_str,
                "walk_status": get_status_text(is_walk_ok, wait_walk),
                "bus_status": get_status_text(is_bus_ok, wait_bus),
                "can_walk": is_walk_ok,
                "can_bus": is_bus_ok
            }
        else:
            # 終電後など、どうやっても間に合う電車がない場合
            results[key] = {
                "next_train": "終了",
                "walk_status": "-",
                "bus_status": "-",
                "can_walk": False,
                "can_bus": False
            }

    # --- 3. シンプル判定（PR #10より）：二者択一の判定 ---
    simple_decision = "判断中..."
    simple_mode = "neutral"  # walk / bus / neutral
    simple_reason = ""

    minutes_until_bus = bus_data.get("minutesUntilNextBus")

    if minutes_until_bus is None:
        simple_decision = "歩け！"
        simple_mode = "walk"
        simple_reason = "今日はもうバスがありません。"
    else:
        # バスまでの待ち時間と歩く時間を単純比較
        if minutes_until_bus <= WALK_MINUTES:
            simple_decision = "バスに乗れ！"
            simple_mode = "bus"
            simple_reason = f"バスは {minutes_until_bus}分後、歩くと{WALK_MINUTES}分かかります。"
        else:
            simple_decision = "歩け！"
            simple_mode = "walk"
            simple_reason = f"歩けば{WALK_MINUTES}分、バスは {minutes_until_bus}分後です。"

    return {
        # --- シンプル判定用（二者択一） ---
        "simple_decision": simple_decision,
        "simple_mode": simple_mode,
        "simple_reason": simple_reason,

        # --- バス情報 ---
        "bus_dep_time": bus_time_str if bus_time_str else "終了",
        "minutes_until_bus": minutes_until_bus,

        # --- 方面別データ（詳細情報） ---
        "okazaki": results["okazaki"],
        "kozoji": results["kozoji"]
    }

if __name__ == "__main__":
    print(judge_walk_or_bus())