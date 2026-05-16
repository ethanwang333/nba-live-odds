from nba_api.live.nba.endpoints import scoreboard
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
        seconds = float(match.group(2))
        seconds_in_period = (minutes * 60) + seconds
        total = (4 - period) * 720 + seconds_in_period
        return max(float(total), 0.0)
    return 0.0

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

        data = {
            'gameId': game_id,
            'homeTeam': game['homeTeam']['teamTricode'],
            'awayTeam': game['awayTeam']['teamTricode'],
            'scoreHome': score_home,
            'scoreAway': score_away,
            'period': period,
            'gameClock': clock,
            'total_seconds_remaining': total_seconds,
            'home_win_probability': probability,
            'away_win_probability': round(1 - probability, 4),
            'gameStatus': 2
        }

        redis_client.set(f"game:{game_id}", json.dumps(data))
        active_ids.append(game_id)

        print(f"  {data['awayTeam']} @ {data['homeTeam']} | "
              f"{data['scoreAway']}-{data['scoreHome']} | "
              f"Q{period} | "
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