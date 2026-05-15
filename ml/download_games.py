# ml/download_games.py
# Downloads all game logs for 5 seasons and saves to CSV
# Run this first — it gives you game IDs needed for play-by-play

import pandas as pd
import time
import os
from nba_api.stats.endpoints import leaguegamefinder

# --- Config ---
SEASONS = [
    "2019-20",  # includes bubble season — model will handle this
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
]

# Path is relative to where you run the script from
# Run this from inside the ml/ folder
OUTPUT_DIR = "../data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Download ---
all_games = []

for season in SEASONS:
    print(f"Fetching {season}...")
    
    try:
        finder = leaguegamefinder.LeagueGameFinder(
            season_nullable=season,
            season_type_nullable="Regular Season",
            league_id_nullable="00"  # 00 = NBA (not G-League)
        )
        
        df = finder.get_data_frames()[0]
        df["SEASON"] = season  # add season column so we know which year
        all_games.append(df)
        
        print(f"  ✓ {len(df)} game records found")
        
    except Exception as e:
        print(f"  ✗ Failed for {season}: {e}")
    
    # Always sleep between API calls — respect the rate limit
    time.sleep(2)

# --- Combine and clean ---
games_df = pd.concat(all_games, ignore_index=True)

# Remove duplicate games (each game appears twice — once per team)
# We keep both rows because each team's perspective is useful
# But we save unique game IDs separately
print(f"\nTotal rows: {len(games_df)}")
print(f"Unique games: {games_df['GAME_ID'].nunique()}")
print(f"Columns: {list(games_df.columns)}")

# --- Save ---
games_path = os.path.join(OUTPUT_DIR, "game_logs.csv")
games_df.to_csv(games_path, index=False)
print(f"\n✓ Saved game logs → {games_path}")

# Save just the unique game IDs — used by download_pbp.py
game_ids = games_df["GAME_ID"].unique()
ids_path = os.path.join(OUTPUT_DIR, "game_ids.csv")
pd.Series(game_ids, name="GAME_ID").to_csv(ids_path, index=False)
print(f"✓ Saved game IDs → {ids_path}")
print(f"✓ Total unique games to fetch play-by-play for: {len(game_ids)}")