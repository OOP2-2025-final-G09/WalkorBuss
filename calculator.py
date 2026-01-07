import json
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_JSON_PATH = Path(__file__).resolve().parent / "data/bus_timetable.json"


def load_shuttle_data(json_path: str | Path = DEFAULT_JSON_PATH) -> dict:
    json_path = Path(json_path)
    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _first_bus_of_day(shuttle: dict, date_key: str) -> tuple[str | None, str]:
    """(始発HH:MM or None, 運行区分)"""
    code = shuttle["service_by_date"].get(date_key, "OFF")
    if code == "OFF":
        return None, "OFF"

    hhmm_list = shuttle["timetables"][code]["ait_to_yakusa"]["list"]
    if not hhmm_list:
        return None, code

    return hhmm_list[0], code


def get_next_bus_info(
    shuttle: dict,
    now: datetime | None = None,
    search_next_days: int = 7
) -> dict:
    """
    戻り値例:
    { "nextBusTime": "15:42", "minutesUntilNextBus": 7 }

    追加情報も入れてます（デバッグ用）:
    service: "A"/"B"/"C"/"OFF"
    date: "YYYY-MM-DD"
    """
    if now is None:
        now = datetime.now()

    date_key = now.strftime("%Y-%m-%d")
    code = shuttle["service_by_date"].get(date_key, "OFF")

    # 今日が運休なら、次に運行する日を探す
    if code == "OFF":
        for i in range(1, search_next_days + 1):
            d = (now.date() + timedelta(days=i)).isoformat()
            first_time, next_code = _first_bus_of_day(shuttle, d)
            if first_time is not None:
                hh, mm = map(int, first_time.split(":"))
                first_dt = datetime.fromisoformat(d).replace(hour=hh, minute=mm, second=0, microsecond=0)
                diff_min = int((first_dt - now).total_seconds() // 60)
                return {
                    "nextBusTime": first_time,
                    "minutesUntilNextBus": diff_min,
                    "service": next_code,
                    "date": d
                }
        return {"nextBusTime": None, "minutesUntilNextBus": None, "service": "OFF", "date": date_key}

    # 今日のダイヤで次の便を探す
    hhmm_list = shuttle["timetables"][code]["ait_to_yakusa"]["list"]
    for hhmm in hhmm_list:
        hh, mm = map(int, hhmm.split(":"))
        candidate = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if candidate >= now:
            diff_min = int((candidate - now).total_seconds() // 60)
            return {
                "nextBusTime": hhmm,
                "minutesUntilNextBus": diff_min,
                "service": code,
                "date": date_key
            }

    # 今日の最終便後 → 次に運行する日を探す
    for i in range(1, search_next_days + 1):
        d = (now.date() + timedelta(days=i)).isoformat()
        first_time, next_code = _first_bus_of_day(shuttle, d)
        if first_time is not None:
            hh, mm = map(int, first_time.split(":"))
            first_dt = datetime.fromisoformat(d).replace(hour=hh, minute=mm, second=0, microsecond=0)
            diff_min = int((first_dt - now).total_seconds() // 60)
            return {
                "nextBusTime": first_time,
                "minutesUntilNextBus": diff_min,
                "service": next_code,
                "date": d
            }

    return {"nextBusTime": None, "minutesUntilNextBus": None, "service": code, "date": date_key}


def get_next_bus_from_json(
    now: datetime | None = None,
    json_path: str | Path = DEFAULT_JSON_PATH
) -> dict:
    """JSON読み込み込みで nextBusTime を返す便利関数"""
    shuttle = load_shuttle_data(json_path)
    return get_next_bus_info(shuttle, now=now)


# デバッグ
if __name__ == "__main__":
    debug_now = datetime.fromisoformat("2026-01-07 09:10:50.811545")
    print(get_next_bus_from_json(now=debug_now))
