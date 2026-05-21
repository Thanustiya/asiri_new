# backend/routers/agent.py
"""
Human Agent API
- Login / auth
- Real-time WebSocket dashboard
- Pick up sessions, reply to users
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict
import json
import logging
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from backend.models.database import get_db, Agent, ChatSession, Message, SessionStatus, MessageRole
from backend.models.schemas import AgentLoginRequest, AgentLoginResponse, AgentMessageRequest
from backend.services.agent_service import (
    connected_agents, pending_queue, remove_from_queue,
    notify_agents, get_queue
)
from backend.routers.chat import session_websockets
from backend.config import settings

router = APIRouter(prefix="/api/agent", tags=["agent"])
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours


# ── Auth helpers ───────────────────────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp": expire}, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Agent:
    payload = verify_token(credentials.credentials)
    agent_id = payload.get("sub")
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent or not agent.is_active:
        raise HTTPException(status_code=401, detail="Agent not found")
    return agent


# ── Login ──────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=AgentLoginResponse)
async def agent_login(request: AgentLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.email == request.email))
    agent = result.scalar_one_or_none()
    if not agent or not pwd_context.verify(request.password, agent.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    agent.is_online = True
    await db.commit()
    token = create_access_token({"sub": agent.id, "name": agent.name})
    return AgentLoginResponse(access_token=token, agent_id=agent.id, name=agent.name)


# ── Logout ─────────────────────────────────────────────────────────────────────
@router.post("/logout")
async def agent_logout(
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    agent.is_online = False
    await db.commit()
    connected_agents.pop(agent.id, None)
    return {"message": "Logged out"}


# ── Queue ──────────────────────────────────────────────────────────────────────
@router.get("/queue")
async def get_agent_queue(agent: Agent = Depends(get_current_agent)):
    return get_queue()


# ── Active sessions ────────────────────────────────────────────────────────────
@router.get("/sessions")
async def get_active_sessions(
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.agent_id == agent.id)
        .where(ChatSession.status == SessionStatus.WITH_AGENT)
        .order_by(ChatSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    output = []
    for s in sessions:
        msgs_result = await db.execute(
            select(Message)
            .where(Message.session_id == s.id)
            .order_by(Message.created_at)
        )
        msgs = msgs_result.scalars().all()
        last_msg = msgs[-1].content if msgs else ""
        output.append({
            "id": s.id,
            "channel": s.channel.value,
            "status": s.status.value,
            "user_name": s.user_name,
            "last_message": last_msg,
            "message_count": len(msgs),
            "created_at": s.created_at.isoformat(),
            "messages": [
                {"role": m.role.value, "content": m.content, "time": m.created_at.isoformat()}
                for m in msgs
            ]
        })
    return output


# ── Accept session ─────────────────────────────────────────────────────────────
@router.post("/accept/{session_id}")
async def accept_session(
    session_id: str,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.WITH_AGENT
    session.agent_id = agent.id
    session.updated_at = datetime.utcnow()
    remove_from_queue(session_id)

    # Notify user
    msg_text = (
        f"✅ You're now connected with **{agent.name}** from BML College!\n"
        "Feel free to ask your questions."
    )
    sys_msg = Message(
        session_id=session_id,
        role=MessageRole.SYSTEM,
        content=msg_text
    )
    db.add(sys_msg)
    await db.commit()

    # Push to user's WebSocket if connected
    ws = session_websockets.get(session_id)
    if ws:
        try:
            await ws.send_text(json.dumps({
                "type": "message",
                "data": {
                    "session_id": session_id,
                    "message": msg_text,
                    "status": "with_agent",
                    "quick_replies": []
                }
            }))
        except Exception:
            pass

    # Notify all agents
    await notify_agents({
        "type": "session_accepted",
        "session_id": session_id,
        "agent_name": agent.name
    })

    return {"message": "Session accepted", "session_id": session_id}


# ── Send message to user ───────────────────────────────────────────────────────
@router.post("/message")
async def agent_send_message(
    request: AgentMessageRequest,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ChatSession).where(ChatSession.id == request.session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msg = Message(
        session_id=request.session_id,
        role=MessageRole.AGENT,
        content=request.message
    )
    db.add(msg)
    session.updated_at = datetime.utcnow()
    await db.commit()

    # Push to user's WebSocket
    ws = session_websockets.get(request.session_id)
    if ws:
        try:
            await ws.send_text(json.dumps({
                "type": "agent_message",
                "data": {
                    "session_id": request.session_id,
                    "message": f"**{agent.name}:** {request.message}",
                    "status": "with_agent",
                    "quick_replies": []
                }
            }))
        except Exception:
            pass

    # WhatsApp reply
    if session.whatsapp_number:
        from services.whatsapp_service import send_whatsapp_message
        await send_whatsapp_message(
            session.whatsapp_number,
            f"{agent.name} (BML): {request.message}"
        )

    return {"message": "Sent"}


# ── Close session ──────────────────────────────────────────────────────────────
@router.post("/close/{session_id}")
async def close_session(
    session_id: str,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.CLOSED
    session.closed_at = datetime.utcnow()

    close_msg = Message(
        session_id=session_id,
        role=MessageRole.SYSTEM,
        content=(
            "This chat session has been closed by the advisor.\n"
            "Thank you for contacting BML College! 🎓\n"
            "📧 info@bmlcollege.com | 📞 +44 (0) 121 523 0141"
        )
    )
    db.add(close_msg)
    await db.commit()

    ws = session_websockets.get(session_id)
    if ws:
        try:
            await ws.send_text(json.dumps({
                "type": "session_closed",
                "message": close_msg.content
            }))
        except Exception:
            pass

    return {"message": "Session closed"}


# ── Agent WebSocket dashboard ──────────────────────────────────────────────────
@router.websocket("/ws/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str):
    await websocket.accept()
    connected_agents[agent_id] = websocket
    logger.info(f"Agent WebSocket connected: {agent_id}")

    # Send current queue immediately
    await websocket.send_text(json.dumps({
        "type": "queue_update",
        "queue": get_queue()
    }))

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            if payload.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        logger.info(f"Agent WebSocket disconnected: {agent_id}")
    finally:
        connected_agents.pop(agent_id, None)


# ── Stats ──────────────────────────────────────────────────────────────────────
@router.get("/stats")
async def get_stats(
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    total = await db.execute(select(func.count(ChatSession.id)))
    active = await db.execute(
        select(func.count(ChatSession.id)).where(ChatSession.status == SessionStatus.ACTIVE)
    )
    waiting = await db.execute(
        select(func.count(ChatSession.id)).where(ChatSession.status == SessionStatus.WAITING_AGENT)
    )
    return {
        "total_sessions": total.scalar(),
        "active_sessions": active.scalar(),
        "waiting_for_agent": waiting.scalar(),
        "agents_online": len(connected_agents),
        "queue_length": len(pending_queue)
    }