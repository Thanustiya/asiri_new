# backend/models/database.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import uuid
import enum
from backend.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    WAITING_AGENT = "waiting_agent"
    WITH_AGENT = "with_agent"
    CLOSED = "closed"


class MessageRole(str, enum.Enum):
    USER = "user"
    BOT = "bot"
    AGENT = "agent"
    SYSTEM = "system"


class Channel(str, enum.Enum):
    WEB = "web"
    WHATSAPP = "whatsapp"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel = Column(Enum(Channel), default=Channel.WEB)
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    user_name = Column(String, nullable=True)
    user_phone = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    whatsapp_number = Column(String, nullable=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    messages = relationship("Message", back_populates="session", order_by="Message.created_at")
    agent = relationship("Agent", back_populates="sessions")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    confidence = Column(Integer, nullable=True)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_online = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ChatSession", back_populates="agent")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_default_agent()


async def seed_default_agent():
    """Create a default agent if none exists."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Agent))
        agents = result.scalars().all()
        if not agents:
            agent = Agent(
                name="BML Support Team",
                email="agent@bmlcollege.com",
                password_hash=pwd_context.hash("bml@agent2024"),
                is_active=True
            )
            session.add(agent)
            await session.commit()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()