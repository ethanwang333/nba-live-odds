from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss
from xgboost import XGBClassifier
import joblib
import pandas as pd
import os
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

OUTPUT_DIR = "../data/processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)
data_path = os.path.join(OUTPUT_DIR, "pbp_combined.csv")

df = pd.read_csv(data_path)
df['total_score'] = df['scoreHome'] + df['scoreAway']
df['home_is_leading'] = (df['score_margin'] > 0).astype(int)
df['margin_x_time'] = df['score_margin'] * df['total_seconds_remaining']
df['is_close_game'] = (df['score_margin'].abs() <= 5).astype(int)
feature_cols = [
    'period',
    'scoreHome',
    'scoreAway', 
    'score_margin',
    'total_seconds_remaining',
    'total_score',
    'home_is_leading',
    'margin_x_time',
    'is_close_game'
]
Y = df['home_team_won']
# split by game ID not by row
game_ids = df['gameId'].unique()
train_ids = game_ids[:int(len(game_ids) * 0.8)]
test_ids = game_ids[int(len(game_ids) * 0.8):]

train = df[df['gameId'].isin(train_ids)]
test = df[df['gameId'].isin(test_ids)]

X_train = train[feature_cols]
X_test = test[feature_cols]
Y_train = train['home_team_won']
Y_test = test['home_team_won']

model = LogisticRegression(max_iter = 1000)
model.fit(X_train, Y_train)
pred = model.predict(X_test)
prob = model.predict_proba(X_test)


print(f"Accuracy: {accuracy_score(Y_test, pred):.4f}")
print(f"Log loss: {log_loss(Y_test, prob):.4f}")
print(f"Brier score: {brier_score_loss(Y_test, prob[:, 1]):.4f}")




xgb_model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    use_label_encoder=False,
    eval_metric='logloss',
    random_state=42
)
xgb_model.fit(X_train, Y_train)
xgb_pred = xgb_model.predict(X_test)
xgb_prob = xgb_model.predict_proba(X_test)


os.makedirs("../ml/models", exist_ok=True)
joblib.dump(xgb_model, "models/win_probability_model.pkl")
print("XGBoost model saved")

print(f"\nXGBoost results:")
print(f"Accuracy: {accuracy_score(Y_test, xgb_pred):.4f}")
print(f"Log loss: {log_loss(Y_test, xgb_prob):.4f}")
print(f"Brier score: {brier_score_loss(Y_test, xgb_prob[:, 1]):.4f}")


prob_true, prob_pred = calibration_curve(Y_test, xgb_prob[:, 1], n_bins=10)

plt.figure(figsize=(8, 6))
plt.plot(prob_pred, prob_true, marker='o', label='XGBoost')
plt.plot([0, 1], [0, 1], linestyle='--', label='Perfect calibration')
plt.xlabel("Predicted probability")
plt.ylabel("Actual win rate")
plt.title("Model calibration curve")
plt.legend()
plt.tight_layout()
plt.savefig("models/calibration_curve.png")
plt.show()
print("Calibration curve saved")