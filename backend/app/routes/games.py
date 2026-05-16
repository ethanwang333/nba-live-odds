from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.redis_client import redis_client
import json
import asyncio

router = APIRouter()

@router.get("/games/live")
def get_live_games():
    active_ids = redis_client.get("active_games")
    if not active_ids:
        return {"games": []}
    game_ids = json.loads(active_ids)
    games = []
    for game_id in game_ids:
        data = redis_client.get(f"game:{game_id}")
        if data:
            games.append(json.loads(data))
    return {"games": games}

@router.get("/games/{game_id}")
def get_game(game_id: str):
    data = redis_client.get(f"game:{game_id}")
    if not data:
        return {"error": "Game not found"}
    return json.loads(data)

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
                    data = redis_client.get(f"game:{game_id}")
                    if data:
                        games.append(json.loads(data))
                await websocket.send_json({"games": games})
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected")