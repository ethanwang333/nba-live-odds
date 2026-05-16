import sys
sys.path.append('.')
from app.services.predictor import predict_win_probability
from app.services.redis_client import redis_client
from app.db.database import engine
from sqlalchemy import text

# test redis
try:
    redis_client.ping()
    print("Redis connected")
except Exception as e:
    print(f"Redis failed: {e}")

# test postgres
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Postgres connected")
except Exception as e:
    print(f"Postgres failed: {e}")

test_game = {
    'scoreHome': 27,
    'scoreAway': 38,
    'period': 2,
    'total_seconds_remaining': 1400.0
}

prob = predict_win_probability(test_game)
print(f"Home team win probability: {prob}")
print(f"Away team win probability: {round(1 - prob, 4)}")