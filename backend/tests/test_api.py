import time
import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import leaguegamefinder

def run_test():
    print("--- 🏀 NBA API Connection Test ---")
    
    # Test 1: Current Scoreboard (Live Data Check)
    try:
        sb = scoreboard.ScoreBoard()
        data = sb.get_dict()
        games = data['scoreboard']['games']
        print(f"✅ Scoreboard connected. Found {len(games)} games today.")
    except Exception as e:
        print(f"❌ Scoreboard failed: {e}")

    # Small pause to respect API rate limits
    time.sleep(1)

    # Test 2: Historical Data Check (Lakers Team ID: 1610612747)
    try:
        game_finder = leaguegamefinder.LeagueGameFinder(team_id_nullable='1610612747')
        df = game_finder.get_data_frames()[0]
        print(f"✅ Historical data pull successful. Last 5 Lakers games:")
        # Show just the key info: Date, Matchup, and Result
        print(df[['GAME_DATE', 'MATCHUP', 'WL']].head())
    except Exception as e:
        print(f"❌ Historical pull failed: {e}")

if __name__ == "__main__":
    run_test()