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

        def format_players(players):
            lines = []
            for p in players[:5]:
                foul_note = " (foul trouble)" if p.get('fouls', 0) >= 4 else ""
                lines.append(
                    f"{p['name']}: {p['points']}pts {p['rebounds']}reb {p['assists']}ast {p['fouls']}fl{foul_note}"
                )
            return ", ".join(lines)

        home_stats = format_players(players_home)
        away_stats = format_players(players_away)

        home_prob = round(game_context.get('home_win_probability', 0) * 100, 1)
        away_prob = round(100 - home_prob, 1)

        score_home = game_context.get('scoreHome', 0)
        score_away = game_context.get('scoreAway', 0)
        margin = score_home - score_away
        margin_text = f"{game_context.get('homeTeam')} leads by {abs(margin)}" if margin > 0 else f"{game_context.get('awayTeam')} leads by {abs(margin)}" if margin < 0 else "tied"

        prompt = (
            f"You are an expert NBA analyst. Answer concisely in 2-3 sentences using the stats below. "
            f"Consider overall impact — points, rebounds, assists, foul trouble — not just scoring.\n\n"
            f"Game: {game_context.get('awayTeam')} {score_away} @ {game_context.get('homeTeam')} {score_home} "
            f"({margin_text}), Q{game_context.get('period')} {game_context.get('gameClockFormatted')} left.\n"
            f"Win probability: {game_context.get('homeTeam')} {home_prob}% / {game_context.get('awayTeam')} {away_prob}%.\n"
            f"{game_context.get('homeTeam')} players: {home_stats}\n"
            f"{game_context.get('awayTeam')} players: {away_stats}\n\n"
            f"Question: {question}"
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