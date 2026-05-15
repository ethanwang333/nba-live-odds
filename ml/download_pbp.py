# ml/download_pbp.py
# Downloads play-by-play using nba_api PlayByPlayV3
# Safe to stop and restart -- resume logic skips already downloaded games

import pandas as pd
import time
import os
from nba_api.stats.endpoints import playbyplayv3

# --- Config ---
IDS_PATH   = "../data/raw/game_ids.csv"
OUTPUT_DIR = "../data/raw/pbp"
SLEEP_TIME = 2
RETRY_WAIT = 60    # wait a full minute on failure -- gives API time to recover
MAX_RETRIES = 3

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Load and normalize game IDs ---
game_ids = (
    pd.read_csv(IDS_PATH)["GAME_ID"]
    .astype(str)
    .str.zfill(10)
    .tolist()
)
total = len(game_ids)
print(f"Total games to fetch: {total}")

# --- Resume logic ---
already_done = set(
    f.replace(".csv", "").zfill(10)
    for f in os.listdir(OUTPUT_DIR)
    if f.endswith(".csv")
)

remaining = [gid for gid in game_ids if gid not in already_done]
print(f"Already downloaded: {len(already_done)}")
print(f"Remaining: {len(remaining)}")

if not remaining:
    print("All games already downloaded. Nothing to do.")
    exit()

est_minutes = (len(remaining) * SLEEP_TIME) / 60
print(f"Estimated time: {est_minutes:.0f} minutes ({est_minutes/60:.1f} hours)")
print("Starting download... safe to stop with Ctrl+C and resume later\n")

# --- Download loop ---
failed = []

for i, game_id in enumerate(remaining, 1):

    if i % 50 == 0 or i == 1:
        pct = (i / len(remaining)) * 100
        done_total = len(already_done) + i
        print(f"[{done_total}/{total}] {pct:.1f}% complete -- game {game_id}")

    for attempt in range(MAX_RETRIES):
        try:
            pbp = playbyplayv3.PlayByPlayV3(game_id=game_id)
            df = pbp.get_data_frames()[0]

            if len(df) > 0:
                out_path = os.path.join(OUTPUT_DIR, f"{game_id}.csv")
                df.to_csv(out_path, index=False)

            break  # success

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"  Retry {attempt + 1} for {game_id}: {e} -- waiting {RETRY_WAIT}s")
                time.sleep(RETRY_WAIT)
            else:
                print(f"  Skipping {game_id} after {MAX_RETRIES} attempts: {e}")
                failed.append(game_id)

    time.sleep(SLEEP_TIME)

# --- Summary ---
total_downloaded = len(os.listdir(OUTPUT_DIR))
print(f"\nDownload complete")
print(f"Total files in pbp/: {total_downloaded}")

if failed:
    print(f"\n{len(failed)} games failed -- saving to failed_games.csv")
    pd.Series(failed, name="GAME_ID").to_csv(
        "../data/raw/failed_games.csv", index=False
    )
    print("Run this script again to retry failed games")
else:
    print("No failures -- all games downloaded successfully")