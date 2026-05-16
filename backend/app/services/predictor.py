import joblib
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "win_probability_model.pkl")

model = joblib.load(MODEL_PATH)
print(f"Model loaded from {MODEL_PATH}")

def predict_win_probability(game_state):
    score_home = game_state['scoreHome']
    score_away = game_state['scoreAway']
    period = game_state['period']
    total_seconds_remaining = game_state['total_seconds_remaining']

    score_margin = score_home - score_away
    total_score = score_home + score_away
    home_is_leading = 1 if score_margin > 0 else 0
    margin_x_time = score_margin * total_seconds_remaining
    is_close_game = 1 if abs(score_margin) <= 5 else 0

    features = pd.DataFrame([{
        'period': period,
        'scoreHome': score_home,
        'scoreAway': score_away,
        'score_margin': score_margin,
        'total_seconds_remaining': total_seconds_remaining,
        'total_score': total_score,
        'home_is_leading': home_is_leading,
        'margin_x_time': margin_x_time,
        'is_close_game': is_close_game
    }])

    probability = model.predict_proba(features)[0][1]
    return round(float(probability), 4)
