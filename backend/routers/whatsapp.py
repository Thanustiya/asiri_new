from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from datetime import datetime

from models.database import (
    get_db, ChatSession, Message, SessionStatus, MessageRole, Channel
)

from services.whatsapp_service import (
    parse_whatsapp_incoming,
    send_whatsapp_message
)

from services.nlp_engine import nlp_engine
from services.ollama_service import ollama_service
from services.agent_service import (
    is_working_hours, get_working_hours_message, add_to_queue
)
from services.knowledge_base import COLLEGE_KNOWLEDGE

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])
logger = logging.getLogger(__name__)


@router.get("/webhook")
async def verify_webhook():
    """Meta webhook health check"""
    return {"status": "WhatsApp webhook active"}


@router.post("/webhook")
async def receive_whatsapp(request: Request, db: AsyncSession = Depends(get_db)):
    """Meta WhatsApp Cloud API webhook"""

    data = await request.json()
    parsed = parse_whatsapp_incoming(data)

    if not parsed:
        return {"status": "ignored"}

    from_number = parsed["sender"]
    message_body = parsed["message"]

    logger.info(f"WhatsApp from {from_number}: {message_body}")

    # Get session
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.whatsapp_number == from_number)
        .where(ChatSession.status != SessionStatus.CLOSED)
        .order_by(ChatSession.created_at.desc())
    )
    session = result.scalar_one_or_none()

    # Create session if not found
    if not session:
        session = ChatSession(
            channel=Channel.WHATSAPP,
            whatsapp_number=from_number,
            user_name=from_number,
            status=SessionStatus.ACTIVE
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

        # Send welcome message
        welcome = COLLEGE_KNOWLEDGE["welcome"]["response"].replace("**", "").replace("•", "-")
        send_whatsapp_message(from_number, welcome)

    # Process message
    response_text = await _process_message(session, message_body, db)

    # Send response via Meta API
    if response_text:
        send_whatsapp_message(from_number, response_text)

    return {"status": "ok"}


async def _process_message(session, message: str, db: AsyncSession) -> str:
    """
    Core bot logic
    """

    user_msg = Message(
        session_id=session.id,
        role=MessageRole.USER,
        content=message
    )
    db.add(user_msg)

    # Agent mode
    if session.status == SessionStatus.WITH_AGENT:
        return ""

    # Human request
    if nlp_engine.is_human_request(message):
        session.status = SessionStatus.WAITING_AGENT
        await db.commit()
        await add_to_queue(session.id, session.user_name, message, "whatsapp")
        return get_working_hours_message()

    # Farewell
    if nlp_engine.is_farewell(message):
        response, _ = nlp_engine.get_response("bye")
        session.status = SessionStatus.CLOSED
        session.closed_at = datetime.utcnow()
        await db.commit()
        return response

    # AI/NLP response
    intent, confidence, needs_ollama = nlp_engine.classify(message)

    if not needs_ollama and intent != "fallback":
        response, _ = nlp_engine.get_response(intent)
    else:
        history = []
        response = await ollama_service.generate(message, history)
        if not response:
            response, _ = nlp_engine.get_response("fallback")

    # Save bot message
    bot_msg = Message(
        session_id=session.id,
        role=MessageRole.BOT,
        content=response,
        intent=intent,
        confidence=confidence
    )
    db.add(bot_msg)

    session.updated_at = datetime.utcnow()
    await db.commit()

    return response