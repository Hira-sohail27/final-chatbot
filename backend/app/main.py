from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongo import init_indexes
from app.routers import auth, chat, conversations


@asynccontextmanager
async def lifespan(app):
    await init_indexes()
    yield


app = FastAPI(title="AI Chatbot", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[settings.cors_origin], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)
