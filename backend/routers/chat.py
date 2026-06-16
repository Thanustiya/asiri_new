# backend/routers/chat.py
"""
Chat API — REST + WebSocket
Handles session creation, messaging, and real-time communication.
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict
import json
import logging
import asyncio
from datetime import datetime

from models.database import get_db, ChatSession, Message, SessionStatus, MessageRole, Channel
from models.schemas import StartSessionRequest, StartSessionResponse, ChatRequest, ChatResponse
from services.nlp_engine import nlp_engine
from services.ollama_service import ollama_service
from services.agent_service import (
    is_working_hours, get_working_hours_message, add_to_queue,
    remove_from_queue, notify_agents, notify_session, connected_agents
)
from services.knowledge_base import COLLEGE_KNOWLEDGE

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# Active WebSocket connections for chat sessions {session_id: websocket}
session_websockets: Dict[str, WebSocket] = {}

AI_UNABLE_MARKERS = (
    "i don't know",
    "i do not know",
    "i'm not sure",
    "i am not sure",
    "i cannot answer",
    "i can't answer",
    "not enough information",
    "i don't have enough information",
    "i do not have enough information",
    "i don't have access",
    "i do not have access",
    "unable to answer",
)


def _ai_needs_handover(response: str | None) -> bool:
    if not response or not response.strip():
        return True
    text = response.lower()
    return any(marker in text for marker in AI_UNABLE_MARKERS)


# ── Start Session ──────────────────────────────────────────────────────────────
@router.post("/start", response_model=StartSessionResponse)
async def start_session(
    request: StartSessionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session and return welcome message."""
    session = ChatSession(
        channel=Channel(request.channel.value),
        user_name=request.user_name,
        status=SessionStatus.ACTIVE
    )
    db.add(session)

    await db.flush()

    welcome = COLLEGE_KNOWLEDGE["welcome"]
    welcome_msg = Message(
        session_id=session.id,
        role=MessageRole.BOT,
        content=welcome["response"],
        intent="welcome",
        confidence=100
    )
    db.add(welcome_msg)
    await db.commit()
    await db.refresh(session)

    return StartSessionResponse(
        session_id=session.id,
        welcome_message=welcome["response"],
        quick_replies=welcome["quick_replies"]
    )


# ── Send Message ───────────────────────────────────────────────────────────────
@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process a user message and return bot response."""
    # Load session
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == request.session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # If the session has been handed over, don't auto-respond.
    if session.status in (SessionStatus.WITH_AGENT, SessionStatus.WAITING_AGENT):
        user_msg = Message(
            session_id=session.id,
            role=MessageRole.USER,
            content=request.message
        )
        db.add(user_msg)
        await db.commit()
        await notify_agents({
            "type": "user_message",
            "session_id": session.id,
            "message": request.message,
            "user_name": session.user_name
        })
        return ChatResponse(
            session_id=session.id,
            message=(
                "" if session.status == SessionStatus.WITH_AGENT
                else "Your message has been sent to an advisor. A team member will reply shortly."
            ),
            status=session.status.value
        )

    # Save user message
    user_msg = Message(
        session_id=session.id,
        role=MessageRole.USER,
        content=request.message
    )
    db.add(user_msg)

    # Get conversation history for Ollama context
    hist_result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.created_at)
    )
    history = [
        {"role": m.role.value, "content": m.content}
        for m in hist_result.scalars().all()
    ]

    # ── NLP Processing ─────────────────────────────────────────────────────
    # Check for human agent request first
    if nlp_engine.is_human_request(request.message):
        return await _handle_human_request(session, request.message, db)

    # Check for farewell
    if nlp_engine.is_farewell(request.message):
        return await _handle_farewell(session, db)

    # Classify intent
    intent, confidence, needs_ollama = nlp_engine.classify(request.message)

    kb_response, quick_replies = nlp_engine.get_response(intent)

    if not needs_ollama and intent != "fallback":
        # Fast path for customer support questions. Do not make visitors wait
        # for a local model when the site knowledge base already has the answer.
        bot_response = kb_response
    else:
        bot_response = await ollama_service.generate(request.message, history)
        if _ai_needs_handover(bot_response):
            return await _handle_ai_handover(session, request.message, db)

    # Save bot response
    bot_msg = Message(
        session_id=session.id,
        role=MessageRole.BOT,
        content=bot_response,
        intent=intent,
        confidence=confidence
    )
    db.add(bot_msg)
    session.updated_at = datetime.utcnow()
    await db.commit()

    return ChatResponse(
        session_id=session.id,
        message=bot_response,
        intent=intent,
        confidence=confidence,
        quick_replies=quick_replies,
        status=session.status.value
    )


async def _handle_ai_handover(session, user_message: str, db: AsyncSession) -> ChatResponse:
    response = (
        "I am not fully confident about that answer, so I am connecting you to an advisor. "
        "A team member will help you shortly."
    )
    session.status = SessionStatus.WAITING_AGENT
    session.updated_at = datetime.utcnow()

    bot_msg = Message(
        session_id=session.id,
        role=MessageRole.BOT,
        content=response,
        intent="human_agent",
        confidence=100
    )
    db.add(bot_msg)
    await db.commit()

    await add_to_queue(
        session_id=session.id,
        user_name=session.user_name or "Anonymous",
        last_message=user_message,
        channel=session.channel.value
    )

    return ChatResponse(
        session_id=session.id,
        message=response,
        intent="human_agent",
        confidence=100,
        quick_replies=[],
        status="waiting_agent",
        transferred_to_agent=True
    )


# ── Human request handler ──────────────────────────────────────────────────────
async def _handle_human_request(session, user_message: str, db: AsyncSession) -> ChatResponse:
    wh_msg = get_working_hours_message()
    session.status = SessionStatus.WAITING_AGENT
    session.updated_at = datetime.utcnow()

    bot_msg = Message(
        session_id=session.id,
        role=MessageRole.BOT,
        content=wh_msg,
        intent="human_agent",
        confidence=100
    )
    db.add(bot_msg)
    await db.commit()

    # Add to agent queue
    await add_to_queue(
        session_id=session.id,
        user_name=session.user_name or "Anonymous",
        last_message=user_message,
        channel=session.channel.value
    )

    return ChatResponse(
        session_id=session.id,
        message=wh_msg,
        intent="human_agent",
        confidence=100,
        quick_replies=[],
        status="waiting_agent",
        transferred_to_agent=True
    )


async def _handle_farewell(session, db: AsyncSession) -> ChatResponse:
    response, quick_replies = nlp_engine.get_response("bye")
    session.status = SessionStatus.CLOSED
    session.closed_at = datetime.utcnow()
    bot_msg = Message(
        session_id=session.id,
        role=MessageRole.BOT,
        content=response,
        intent="bye",
        confidence=100
    )
    db.add(bot_msg)
    await db.commit()
    return ChatResponse(
        session_id=session.id,
        message=response,
        quick_replies=quick_replies,
        status="closed"
    )


# ── WebSocket for real-time chat ───────────────────────────────────────────────
@router.websocket("/ws/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    session_websockets[session_id] = websocket
    logger.info(f"WebSocket connected: {session_id}")

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            msg_type = payload.get("type", "message")

            if msg_type == "message":
                # Process via the same logic as REST endpoint
                req = ChatRequest(
                    session_id=session_id,
                    message=payload.get("message", "")
                )

                # Send typing indicator
                await websocket.send_text(json.dumps({"type": "typing", "status": True}))

                try:
                    response = await send_message(req, db)
                    await websocket.send_text(json.dumps({
                        "type": "message",
                        "data": response.model_dump()
                    }))
                except Exception as e:
                    logger.error(f"WS message error: {e}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Something went wrong. Please try again."
                    }))

            elif msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    finally:
        session_websockets.pop(session_id, None)


# ── Get session history ────────────────────────────────────────────────────────
@router.get("/history/{session_id}")
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return [
        {
            "role": m.role.value,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]