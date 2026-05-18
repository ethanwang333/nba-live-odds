import glob
import pandas as pd
import numpy as np
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


def compute_team_win_rates(game_logs):
    """
    Computes per-team rolling win rates from game logs.
    Returns one row per game with home and away win rate features.
    
    Key detail: uses shift(1) so each game's win rate is computed
    from results BEFORE that game -- no data leakage.
    """
    df = game_logs.copy()

    # normalize GAME_ID to 10-digit string for consistent joining
    df['GAME_ID'] = df['GAME_ID'].astype(str).str.zfill(10)

    # sort by team and date so rolling calculations go in order
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values(['TEAM_ABBREVIATION', 'GAME_DATE']).reset_index(drop=True)

    # binary win column
    df['win'] = (df['WL'] == 'W').astype(int)

    # compute running win rate per team per season
    # shift(1) means: for each game, use results from all PREVIOUS games only
    df['season_win_pct'] = (
        df.groupby(['TEAM_ABBREVIATION', 'SEASON'])['win']
        .transform(lambda x: x.shift(1).expanding().mean())
    )

    # last 10 games win rate
    df['l10_win_pct'] = (
        df.groupby(['TEAM_ABBREVIATION', 'SEASON'])['win']
        .transform(lambda x: x.shift(1).rolling(10, min_periods=1).mean())
    )

    # fill NaN for first game of season with 0.5 (neutral prior)
    df['season_win_pct'] = df['season_win_pct'].fillna(0.5)
    df['l10_win_pct'] = df['l10_win_pct'].fillna(0.5)

    # separate home and away rows
    # "vs." in MATCHUP = home team, "@" = away team
    home = df[df['MATCHUP'].str.contains('vs\.')].copy()
    away = df[df['MATCHUP'].str.contains('@')].copy()

    home = home[['GAME_ID', 'TEAM_ABBREVIATION', 'season_win_pct', 'l10_win_pct']].copy()
    away = away[['GAME_ID', 'TEAM_ABBREVIATION', 'season_win_pct', 'l10_win_pct']].copy()

    home.columns = ['GAME_ID', 'home_team', 'home_win_pct', 'home_l10_win_pct']
    away.columns = ['GAME_ID', 'away_team', 'away_win_pct', 'away_l10_win_pct']

    # join home and away into one row per game
    win_rates = home.merge(away, on='GAME_ID', how='inner')

    # win percentage differential -- positive means home team is stronger
    win_rates['win_pct_diff'] = win_rates['home_win_pct'] - win_rates['away_win_pct']
    win_rates['l10_win_pct_diff'] = win_rates['home_l10_win_pct'] - win_rates['away_l10_win_pct']

    return win_rates


def build_features(pbp_path, game_logs_path):
    """
    Loads play-by-play and game logs, engineers all features,
    and returns a clean dataframe ready for model training.
    """
    print("Loading play-by-play data...")
    pbp = pd.read_csv(pbp_path)
    pbp['gameId'] = pbp['gameId'].astype(str).str.zfill(10)

    print("Loading game logs...")
    game_logs = pd.read_csv(game_logs_path)
    game_logs['GAME_ID'] = game_logs['GAME_ID'].astype(str).str.zfill(10)

    # --- base features already in pbp_combined ---
    # score_margin, total_seconds_remaining, period, scoreHome, scoreAway
    # home_team_won already joined during features.py phase 1

    # --- playoff flag ---
    # game IDs starting with 0042 are playoff games
    pbp['is_playoff'] = pbp['gameId'].str.startswith('0042').astype(int)
    print(f"Playoff rows: {pbp['is_playoff'].sum():,} / {len(pbp):,} total")

    # --- team win rates ---
    print("Computing team win rates (this takes a minute)...")
    win_rates = compute_team_win_rates(game_logs)
    print(f"Win rate table: {len(win_rates)} games")

    # join win rates onto play-by-play by game ID
    pbp = pbp.merge(win_rates[['GAME_ID', 'home_win_pct', 'away_win_pct',
                                'win_pct_diff', 'home_l10_win_pct',
                                'away_l10_win_pct', 'l10_win_pct_diff']],
                    left_on='gameId', right_on='GAME_ID', how='left')

    # fill any missing win rates with neutral 0.5
    for col in ['home_win_pct', 'away_win_pct', 'win_pct_diff',
                 'home_l10_win_pct', 'away_l10_win_pct', 'l10_win_pct_diff']:
        pbp[col] = pbp[col].fillna(0.5)

    # drop the duplicate GAME_ID column from the merge
    if 'GAME_ID' in pbp.columns:
        pbp = pbp.drop(columns=['GAME_ID'])

    print(f"Final dataset: {len(pbp):,} rows, {len(pbp.columns)} columns")
    return pbp


if __name__ == "__main__":
    PBP_PATH = "../data/processed/pbp_combined.csv"
    GAME_LOGS_PATH = "../data/raw/game_logs.csv"
    OUTPUT_PATH = "../data/processed/pbp_features.csv"

    df = build_features(PBP_PATH, GAME_LOGS_PATH)

    os.makedirs("../data/processed", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to {OUTPUT_PATH}")

    # quick sanity check
    print("\nSample of new feature columns:")
    sample_cols = ['gameId', 'score_margin', 'total_seconds_remaining',
                   'home_win_pct', 'away_win_pct', 'win_pct_diff',
                   'home_l10_win_pct', 'is_playoff', 'home_team_won']
    available = [c for c in sample_cols if c in df.columns]
    print(df[available].dropna().head(10).to_string())

    print("\nNull counts for new features:")
    new_cols = ['home_win_pct', 'away_win_pct', 'win_pct_diff',
                'home_l10_win_pct', 'away_l10_win_pct', 'l10_win_pct_diff', 'is_playoff']
    print(df[new_cols].isnull().sum())