from fastapi import FastAPI
from app.routes.games import router
import app.services.redis_client

app = FastAPI()
app.include_router(router)