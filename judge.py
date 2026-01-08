# 判断ロジック
import json
import os
from datetime import datetime, timedelta

# 設定：所要時間
WALK_MINUTES = 15      # 徒歩で駅までかかる時間
BUS_RIDE_MINUTES = 7   # バス乗車時間（+7分と指定あり）

def load_json(filename):
    """JSONファイルを読み込む"""
    filepath = os.path.join("data", filename)
    if not os.path.exists(filepath):
        filepath = filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_next_schedule(current_dt, timetable):
    """
    指定時刻以降の直近の時刻を取得
    timetable: ["HH:MM", ...] のリスト
    return: datetimeオブジェクト, 文字列"HH:MM"
    """
    current_time_str = current_dt.strftime("%H:%M")
    
    for time_str in timetable:
        if time_str > current_time_str:
            # 文字列をdatetimeに変換（日付はcurrent_dtと同じ）
            hour, minute = map(int, time_str.split(':'))
            target_dt = current_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return target_dt, time_str
            
    return None, None # その日の便は終了

def judge_walk_or_bus():
    now = datetime.now()
    
    # テスト用（必要に応じてコメントアウトを外して時刻を固定）
    # now = now.replace(hour=14, minute=55, second=0)

    # 1. データの読み込み
    bus_table = load_json("bus_timetable.json")
    train_okazaki_table = load_json("train_okazaki.json")
    
    # 2. 現在時刻に最も近い（未来の）電車を取得 = A1
    train_dt, train_str = get_next_schedule(now, train_okazaki_table)
    
    if not train_dt:
        return {"decision": "運行終了", "reason": "本日の電車は終了しました。", "details": []}

    # 3. バスと徒歩の「駅到着時刻」を計算
    
    # --- 徒歩の場合 ---
    arrival_walk_dt = now + timedelta(minutes=WALK_MINUTES)
    
    # --- バスの場合 ---
    bus_dep_dt, bus_dep_str = get_next_schedule(now, bus_table)
    
    if bus_dep_dt:
        arrival_bus_dt = bus_dep_dt + timedelta(minutes=BUS_RIDE_MINUTES)
    else:
        arrival_bus_dt = None # バスがない
        
    # 4. 判定ロジック：A1（電車）に間に合うか？
    
    # 徒歩判定
    # 電車時刻 > 到着時刻 なら間に合う
    can_walk = arrival_walk_dt <= train_dt
    wait_walk = int((train_dt - arrival_walk_dt).total_seconds() / 60) if can_walk else -1
    
    # バス判定
    if arrival_bus_dt:
        can_bus = arrival_bus_dt <= train_dt
        wait_bus = int((train_dt - arrival_bus_dt).total_seconds() / 60) if can_bus else -1
    else:
        can_bus = False
        wait_bus = -1

    # 5. 結果の整形
    
    # メッセージ作成用関数
    def get_status_msg(can_make_it, wait_time):
        if can_make_it:
            return f"待ち時間{wait_time}分"
        else:
            return "無理"

    walk_msg = get_status_msg(can_walk, wait_walk)
    bus_msg = get_status_msg(can_bus, wait_bus)

    # 最終的なレコメンド
    decision = ""
    reason = ""

    # 両方無理な場合（A1は見送り、次の電車を探すべきだが、今回はA1に対する判定を表示）
    if not can_walk and not can_bus:
        decision = "ダッシュか次へ"
        reason = f"次の電車({train_str})には、徒歩もバスも間に合いません。"
    
    # 両方乗れる場合
    elif can_walk and can_bus:
        decision = "どちらでもOK"
        reason = f"次の電車({train_str})に間に合います。<br>徒歩だと{wait_walk}分待ち、バスだと{wait_bus}分待ちです。"
        
    # バスだけ乗れる場合
    elif can_bus:
        decision = "バスに乗れ！"
        reason = f"徒歩だと{train_str}に間に合いません。<br>バスなら間に合います（駅で{wait_bus}分待ち）。"
        
    # 徒歩だけ乗れる場合（バスのタイミングが悪い時など）
    elif can_walk:
        decision = "歩け！"
        reason = f"次のバスを待つと{train_str}に間に合いませんが、今歩けば間に合います（駅で{wait_walk}分待ち）。"

    # 詳細データ（HTML表示用）
    result = {
        "decision": decision,
        "reason": reason,
        "next_train": train_str,
        "walk_status": walk_msg,   # "待ち時間2分" or "無理"
        "bus_status": bus_msg,     # "待ち時間5分" or "無理"
        "bus_dep_time": bus_dep_str if bus_dep_str else "なし"
    }
    
    return result