from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.services.redis_client import redis_client
from app.services.gemini import ask_gemini
import json
import asyncio

router = APIRouter()

def get_game_with_history(game_id):
    data = redis_client.get(f"game:{game_id}")
    if not data:
        return None
    game = json.loads(data)
    history_raw = redis_client.get(f"game:{game_id}:history")
    game['history'] = json.loads(history_raw) if history_raw else []
    return game

@router.get("/games/live")
def get_live_games():
    active_ids = redis_client.get("active_games")
    if not active_ids:
        return {"games": []}
    game_ids = json.loads(active_ids)
    games = []
    for game_id in game_ids:
        game = get_game_with_history(game_id)
        if game:
            games.append(game)
    return {"games": games}

@router.get("/games/{game_id}")
def get_game(game_id: str):
    game = get_game_with_history(game_id)
    if not game:
        return {"error": "Game not found"}
    return game

class ChatRequest(BaseModel):
    question: str
    game_id: str

@router.post("/chat")
async def chat(request: ChatRequest):
    game_data = redis_client.get(f"game:{request.game_id}")
    if not game_data:
        game_context = {}
    else:
        game_context = json.loads(game_data)
    answer = await ask_gemini(request.question, game_context)
    return {"answer": answer}

@router.websocket("/ws/games")
async def websocket_games(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            active_ids = redis_client.get("active_games")
            if active_ids:
                game_ids = json.loads(active_ids)
                games = []
                for game_id in game_ids:
                    game = get_game_with_history(game_id)
                    if game:
                        games.append(game)
                await websocket.send_json({"games": games})
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected")