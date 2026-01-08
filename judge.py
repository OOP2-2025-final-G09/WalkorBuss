import json
import os
from datetime import datetime, timedelta
from calculator import get_next_bus_from_json  # バス時刻取得はここに任せる

# 設定：所要時間
WALK_MINUTES = 12      # 徒歩で駅までかかる時間
BUS_RIDE_MINUTES = 7   # バス乗車時間

def load_json(filename):
    """単純なリスト形式の電車時刻表JSONを読み込む"""
    filepath = os.path.join("data", filename)
    if not os.path.exists(filepath):
        # dataフォルダになければカレントディレクトリを探す
        filepath = filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_next_train(current_dt, timetable):
    """
    指定時刻以降の直近の電車時刻を取得
    timetable: ["HH:MM", ...] のリスト
    return: datetimeオブジェクト, 文字列"HH:MM"
    """
    current_time_str = current_dt.strftime("%H:%M")
    
    for time_str in timetable:
        if time_str > current_time_str:
            hour, minute = map(int, time_str.split(':'))
            # 日付またぎは考慮せず、当日として扱う
            target_dt = current_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return target_dt, time_str
            
    return None, None

def check_connection(arrival_dt, train_dt):
    """到着時刻と電車時刻を比較して、間に合うかと待ち時間を返す"""
    if not arrival_dt or not train_dt:
        return False, -1
    
    if arrival_dt <= train_dt:
        wait_time = int((train_dt - arrival_dt).total_seconds() / 60)
        return True, wait_time
    else:
        return False, -1

def get_status_text(can_make_it, wait_time):
    """表示用のテキストを生成"""
    if can_make_it:
        return f"待ち {wait_time}分"
    else:
        return "間に合わない"

def judge_walk_or_bus():
    now = datetime.now()
    
    # --- 1. バス情報の取得 (calculator.pyを使用) ---
    bus_data = get_next_bus_from_json(now)
    bus_time_str = bus_data.get("nextBusTime") # "HH:MM" or None
    
    # バス到着時刻の計算
    if bus_time_str:
        bh, bm = map(int, bus_time_str.split(':'))
        bus_dep_dt = now.replace(hour=bh, minute=bm, second=0, microsecond=0)
        arrival_bus_dt = bus_dep_dt + timedelta(minutes=BUS_RIDE_MINUTES)
    else:
        bus_dep_dt = None
        arrival_bus_dt = None

    # --- 2. 徒歩到着時刻の計算 ---
    arrival_walk_dt = now + timedelta(minutes=WALK_MINUTES)

    # --- 3. 電車情報の取得と判定 (岡崎 & 高蔵寺) ---
    train_files = {
        "okazaki": "train_okazaki.json",
        "kozoji": "train_kozoji.json"
    }
    
    results = {}

    for key, file in train_files.items():
        # 時刻表読み込み
        timetable = load_json(file)
        # 次の電車を取得
        train_dt, train_str = get_next_train(now, timetable)
        
        # 判定
        can_walk, wait_walk = check_connection(arrival_walk_dt, train_dt)
        can_bus, wait_bus = check_connection(arrival_bus_dt, train_dt)
        
        results[key] = {
            "next_train": train_str if train_str else "終了",
            "walk_status": get_status_text(can_walk, wait_walk),
            "bus_status": get_status_text(can_bus, wait_bus),
            "can_walk": can_walk,
            "can_bus": can_bus
        }

    # --- 4. メインの判断 (Decision) ---
    # 基本的に岡崎行きを基準にメインメッセージを決める（または両方考慮）
    main_target = results["okazaki"]
    
    decision = "判断中..."
    reason = ""

    # --- A. シンプル判定（徒歩 vs バスだけ）---
    simple_decision = "判断中..."
    simple_mode = "neutral"  # walk / bus / neutral
    simple_reason = ""

    minutes_until_bus = bus_data.get("minutesUntilNextBus")

    if minutes_until_bus is None:
        simple_decision = "歩け！"
        simple_mode = "walk"
        simple_reason = "今日はもうバスがありません。"
    else:
        if minutes_until_bus <= WALK_MINUTES:
            simple_decision = "バスに乗れ！"
            simple_mode = "bus"
            simple_reason = f"バスは {minutes_until_bus}分後、歩くと{WALK_MINUTES}分かかります。"
        else:
            simple_decision = "歩け！"
            simple_mode = "walk"
            simple_reason = f"歩けば{WALK_MINUTES}分、バスは {minutes_until_bus}分後です。"

    # --- 5. 結果を返す ---
    return {
    # --- 上の大判定用 ---
    "simple_decision": simple_decision,
    "simple_mode": simple_mode,
    "simple_reason": simple_reason,

    # --- 既存 ---
    "decision": decision,
    "reason": reason,
    "bus_dep_time": bus_time_str if bus_time_str else "終了",
    "minutes_until_bus": minutes_until_bus,

    "okazaki": results["okazaki"],
    "kozoji": results["kozoji"]
    }

    


# デバッグ用
if __name__ == "__main__":
    print(judge_walk_or_bus())