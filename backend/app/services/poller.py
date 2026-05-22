from nba_api.live.nba.endpoints import scoreboard, boxscore
from app.services.redis_client import redis_client
from app.services.predictor import predict_win_probability
import json
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.nba.com/",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.nba.com",
    "x-nba-stats-token": "true",
    "x-nba-stats-origin": "stats",
}

def clock_to_seconds(clock_str, period):
    if not clock_str:
        return 0.0
    match = re.match(r'PT(\d+)M([\d.]+)S', str(clock_str))
    if match:
        minutes = int(match.group(1))
        seconds = int(float(match.group(2)))
        seconds_in_period = (minutes * 60) + seconds
        # cap period at 4 for regular time
        capped_period = min(period, 4)
        total = max(0, (4 - capped_period) * 720 + seconds_in_period)
        return float(total)
    return 0.0

def format_clock(clock_str):
    if not clock_str:
        return "--"
    match = re.match(r'PT(\d+)M([\d.]+)S', str(clock_str))
    if match:
        minutes = int(match.group(1))
        seconds = int(float(match.group(2)))
        return f"{minutes}:{seconds:02d}"
    return "--"

def get_top_players(game_id):
    try:
        box = boxscore.BoxScore(game_id=game_id, headers=HEADERS)
        box_data = box.get_dict()
        game = box_data['game']

        result = {"homeTeam": [], "awayTeam": []}

        for side in ["homeTeam", "awayTeam"]:
            players = game[side]["players"]
            active = [p for p in players if p.get("played") == "1"]
            active.sort(key=lambda p: p["statistics"]["points"], reverse=True)
            top5 = active[:5]
            result[side] = [
                {
                    "name": p["nameI"],
                    "points": p["statistics"]["points"],
                    "rebounds": p["statistics"]["reboundsTotal"],
                    "assists": p["statistics"]["assists"],
                    "fouls": p["statistics"]["foulsPersonal"],
                    "minutes": p["statistics"]["minutesCalculated"].replace("PT", "").replace("M", ""),
                }
                for p in top5
            ]
        return result
    except Exception as e:
        print(f"  Boxscore error for {game_id}: {e}")
        return {"homeTeam": [], "awayTeam": []}

def poll_once():
    board = scoreboard.ScoreBoard(headers=HEADERS)
    games = board.games.get_dict()

    active_ids = []

    for game in games:
        if game['gameStatus'] != 2:
            continue

        game_id = game['gameId']
        score_home = game['homeTeam']['score']
        score_away = game['awayTeam']['score']
        period = game['period']
        clock = game['gameClock']

        total_seconds = clock_to_seconds(clock, period)

        game_state = {
            'scoreHome': score_home,
            'scoreAway': score_away,
            'period': period,
            'total_seconds_remaining': total_seconds
        }

        probability = predict_win_probability(game_state)

        players = get_top_players(game_id)

        # --- persist history in Redis ---
        history_key = f"game:{game_id}:history"
        history_raw = redis_client.get(history_key)
        history = json.loads(history_raw) if history_raw else []

        new_point = {
            "time": total_seconds,
            "home": probability,
            "away": round(1 - probability, 4)
        }

        # only append if probability actually changed to avoid duplicate points
        if not history or history[-1]["home"] != probability:
            history.append(new_point)
            redis_client.set(history_key, json.dumps(history))

        data = {
            'gameId': game_id,
            'homeTeam': game['homeTeam']['teamTricode'],
            'awayTeam': game['awayTeam']['teamTricode'],
            'scoreHome': score_home,
            'scoreAway': score_away,
            'period': period,
            'gameClock': clock,
            'gameClockFormatted': format_clock(clock),
            'total_seconds_remaining': total_seconds,
            'home_win_probability': probability,
            'away_win_probability': round(1 - probability, 4),
            'gameStatus': 2,
            'players': players,
        }

        redis_client.set(f"game:{game_id}", json.dumps(data))
        active_ids.append(game_id)

        print(f"  {data['awayTeam']} @ {data['homeTeam']} | "
              f"{data['scoreAway']}-{data['scoreHome']} | "
              f"Q{period} {data['gameClockFormatted']} | "
              f"Home win prob: {probability}")

    redis_client.set("active_games", json.dumps(active_ids))
    print(f"Stored {len(active_ids)} live games in Redis")

def start_polling(interval=5):
    print("Poller started -- polling every 5 seconds")
    while True:
        try:
            poll_once()
        except Exception as e:
            print(f"Poll error: {e}")
        time.sleep(interval)

if __name__ == "__main__":
    start_polling()