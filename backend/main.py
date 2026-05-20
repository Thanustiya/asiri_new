# backend/main.py
"""
BML College AI Chatbot — Backend
FastAPI + WebSocket + Ollama phi3 + Human Agent Handover + WhatsApp
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os

from config import settings
from models.database import init_db
from routers.chat import router as chat_router
from routers.agent import router as agent_router
from routers.whatsapp import router as whatsapp_router

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting BML College Chatbot...")
    await init_db()
    logger.info("✅ Database initialised")
    yield
    logger.info("🛑 Shutting down...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered chatbot for BML College UK & International",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(whatsapp_router)

# ── Serve frontend files ──────────────────────────────────────────────────────
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_index():
    index = os.path.join(frontend_path, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return HTMLResponse("<h1>BML College Chatbot API</h1><p><a href='/api/docs'>API Docs</a></p>")


@app.get("/agent", response_class=HTMLResponse, include_in_schema=False)
async def serve_agent():
    agent_html = os.path.join(frontend_path, "agent-dashboard.html")
    if os.path.exists(agent_html):
        return FileResponse(agent_html)
    return HTMLResponse("<h1>Agent Dashboard</h1>")


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    from services.ollama_service import ollama_service
    ollama_ok = await ollama_service.is_available()
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ollama": "connected" if ollama_ok else "offline (using KB fallback)",
        "model": settings.OLLAMA_MODEL
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        ws_ping_interval=30,
        ws_ping_timeout=60
    )