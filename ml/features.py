import glob
import pandas as pd
import re
import os

def clock_to_seconds(clock_str):
    if pd.isna(clock_str):
        return None
    match = re.match(r'PT(\d+)M([\d.]+)S', str(clock_str))
    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return (minutes * 60) + seconds
    return None


all_files = glob.glob("../data/raw/pbp/*.csv")
pbp = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)
print(f"Play-by-play rows: {len(pbp)}")
print(f"Play-by-play columns: {pbp.columns.tolist()}")


game_logs = pd.read_csv("../data/raw/game_logs.csv")
print(f"\nGame log rows: {len(game_logs)}")

home_games = game_logs[game_logs["MATCHUP"].str.contains("vs\.")].copy()
print(f"Home team rows: {len(home_games)}")


home_games["home_team_won"] = home_games["WL"].map({"W": 1, "L": 0})

home_games = home_games[["GAME_ID", "home_team_won"]]

home_games["GAME_ID"] = home_games["GAME_ID"].astype(str).str.zfill(10)
pbp["gameId"] = pbp["gameId"].astype(str).str.zfill(10)


merged = pbp.merge(home_games, left_on="gameId", right_on="GAME_ID", how="inner")
merged = merged.drop(columns=["GAME_ID"])  # drop duplicate ID column
print(f"\nMerged rows: {len(merged)}")
print(f"home_team_won value counts:\n{merged['home_team_won'].value_counts()}")

merged = merged[[
    'gameId', 'period', 'clock',
    'scoreHome', 'scoreAway',
    'actionType',        # type of event -- shot, foul, rebound etc
    'isFieldGoal',       # 1 if this action was a field goal attempt
    'shotResult',        # Made or Missed
    'pointsTotal',       # points scored on this play
    'teamTricode',       # which team did this action
    'home_team_won'
]]
merged[['scoreHome', 'scoreAway']] = merged[['scoreHome', 'scoreAway']].apply(pd.to_numeric, errors='coerce')
merged[['scoreHome', 'scoreAway']] = (
    merged.groupby('gameId')[['scoreHome', 'scoreAway']].ffill()
)
merged['score_margin'] = merged['scoreHome'] - merged['scoreAway']


merged['seconds_remaining_in_period'] = merged['clock'].apply(clock_to_seconds)


merged['period'] = merged['period']
merged['total_seconds_remaining'] = (
    (4 - merged['period']).clip(lower=0) * 720 
    + merged['seconds_remaining_in_period'].fillna(0)
)

merged = merged.dropna(subset=['score_margin', 'total_seconds_remaining'])
merged = merged[merged['period'] <= 4]


os.makedirs("../data/processed", exist_ok=True)
merged.to_csv("../data/processed/pbp_combined.csv", index=False)
print(f"Saved {len(merged)} rows to pbp_combined.csv")