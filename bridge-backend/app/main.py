import socketio
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import auth, chats, lesson_plans, reviews, specialists, task_requests, users
from app.socket.chat_handlers import sio

app = FastAPI(title="Bridge API", version="1.0.0")

# Static files — serve uploaded media
MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"
MEDIA_DIR.mkdir(exist_ok=True)
(MEDIA_DIR / "avatars").mkdir(exist_ok=True)
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(specialists.router)
app.include_router(reviews.router)
app.include_router(chats.router)
app.include_router(task_requests.router)
app.include_router(lesson_plans.router)
app.include_router(users.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


# Mount Socket.io — this is the ASGI app that Uvicorn must serve
# Start with: uvicorn app.main:application --reload --port 8000
application = socketio.ASGIApp(sio, other_asgi_app=app)
