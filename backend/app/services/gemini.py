import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def ask_gemini(question: str, game_context: dict) -> str:
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

        players_home = game_context.get('players', {}).get('homeTeam', [])
        players_away = game_context.get('players', {}).get('awayTeam', [])

        home_stats = ", ".join([f"{p['name']} {p['points']}pts" for p in players_home[:3]])
        away_stats = ", ".join([f"{p['name']} {p['points']}pts" for p in players_away[:3]])

        home_prob = round(game_context.get('home_win_probability', 0) * 100, 1)
        away_prob = round(100 - home_prob, 1)

        prompt = (
            f"NBA game: {game_context.get('awayTeam')} {game_context.get('scoreAway')} "
            f"@ {game_context.get('homeTeam')} {game_context.get('scoreHome')}, "
            f"Q{game_context.get('period')} {game_context.get('gameClockFormatted')} left. "
            f"Win prob: {game_context.get('homeTeam')} {home_prob}% / {game_context.get('awayTeam')} {away_prob}%. "
            f"Top scorers: {game_context.get('homeTeam')}: {home_stats} | {game_context.get('awayTeam')}: {away_stats}. "
            f"Question: {question} "
            f"Answer in 2 sentences max."
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=10
            )
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']

    except Exception as e:
        print(f"Gemini error: {e}")
        return "Sorry, I couldn't get an answer right now."