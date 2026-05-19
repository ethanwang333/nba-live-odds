from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.games import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://nba-live-odds.vercel.app"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)