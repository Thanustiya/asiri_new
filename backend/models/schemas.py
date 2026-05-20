# backend/models/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ChannelEnum(str, Enum):
    web = "web"
    whatsapp = "whatsapp"


class StatusEnum(str, Enum):
    active = "active"
    waiting_agent = "waiting_agent"
    with_agent = "with_agent"
    closed = "closed"


class MessageRoleEnum(str, Enum):
    user = "user"
    bot = "bot"
    agent = "agent"
    system = "system"


# ── Chat ─────────────────────────────────────────────
class StartSessionRequest(BaseModel):
    channel: ChannelEnum = ChannelEnum.web
    user_name: Optional[str] = None
    whatsapp_number: Optional[str] = None


class StartSessionResponse(BaseModel):
    session_id: str
    welcome_message: str
    quick_replies: List[str]


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    message: str
    intent: Optional[str] = None
    confidence: Optional[int] = None
    quick_replies: List[str] = []
    status: str = "active"
    transferred_to_agent: bool = False


class MessageOut(BaseModel):
    id: str
    role: MessageRoleEnum
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: str
    channel: ChannelEnum
    status: StatusEnum
    user_name: Optional[str]
    messages: List[MessageOut] = []
    created_at: datetime

    class Config:
        from_attributes = True


# ── Agent ─────────────────────────────────────────────
class AgentLoginRequest(BaseModel):
    email: str
    password: str


class AgentLoginResponse(BaseModel):
    access_token: str
    agent_id: str
    name: str


class AgentMessageRequest(BaseModel):
    session_id: str
    message: str


class SessionSummary(BaseModel):
    id: str
    channel: str
    status: str
    user_name: Optional[str]
    last_message: Optional[str]
    created_at: datetime
    message_count: int


# ── WhatsApp ──────────────────────────────────────────
class WhatsAppIncoming(BaseModel):
    From: str
    Body: str
    MessageSid: Optional[str] = None
    ProfileName: Optional[str] = None