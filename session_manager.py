"""
Session Manager for BML Chatbot
Handles conversation sessions for web and WhatsApp channels.
Uses SQLite for persistence (lightweight, no server needed).
"""

import sqlite3
import json
import uuid
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

DB_PATH = "chatbot.db"


@dataclass
class Session:
    session_id: str
    channel: str          # 'web' or 'whatsapp'
    identifier: str       # user IP or WhatsApp number
    created_at: float
    last_active: float
    assigned_agent: Optional[str] = None
    status: str = "bot"   # 'bot', 'waiting', 'with_agent', 'closed'
    metadata: str = "{}"  # JSON string for extra info (name, email, etc.)


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            channel TEXT NOT NULL,
            identifier TEXT NOT NULL,
            created_at REAL NOT NULL,
            last_active REAL NOT NULL,
            assigned_agent TEXT,
            status TEXT DEFAULT 'bot',
            metadata TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            sender TEXT NOT NULL,     -- 'user', 'bot', 'agent'
            message TEXT NOT NULL,
            timestamp REAL NOT NULL,
            intent TEXT,
            confidence REAL,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        );

        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_online INTEGER DEFAULT 0,
            created_at REAL NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
        CREATE INDEX IF NOT EXISTS idx_sessions_identifier ON sessions(identifier);
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized")


class SessionManager:
    """Manages chat sessions for web and WhatsApp users."""

    def create_session(self, channel: str, identifier: str) -> Session:
        conn = get_db()
        try:
            now = time.time()
            session_id = str(uuid.uuid4())
            session = Session(
                session_id=session_id,
                channel=channel,
                identifier=identifier,
                created_at=now,
                last_active=now
            )
            conn.execute(
                """INSERT INTO sessions (session_id, channel, identifier, created_at, last_active, status, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (session.session_id, session.channel, session.identifier,
                 session.created_at, session.last_active, session.status, session.metadata)
            )
            conn.commit()
            return session
        finally:
            conn.close()

    def get_session(self, session_id: str) -> Optional[Session]:
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if not row:
                return None
            return Session(**dict(row))
        finally:
            conn.close()

    def get_or_create_by_identifier(self, identifier: str, channel: str) -> Session:
        """Get existing active session or create a new one (for WhatsApp)."""
        conn = get_db()
        try:
            # Find recent active session (within last 24 hours)
            cutoff = time.time() - 86400
            row = conn.execute(
                """SELECT * FROM sessions WHERE identifier = ? AND channel = ?
                   AND last_active > ? AND status != 'closed'
                   ORDER BY last_active DESC LIMIT 1""",
                (identifier, channel, cutoff)
            ).fetchone()
            if row:
                return Session(**dict(row))
        finally:
            conn.close()
        return self.create_session(channel, identifier)

    def update_session(self, session_id: str, **kwargs):
        if not kwargs:
            return
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [session_id]
        conn = get_db()
        try:
            conn.execute(
                f"UPDATE sessions SET {set_clause} WHERE session_id = ?", values
            )
            conn.commit()
        finally:
            conn.close()

    def touch_session(self, session_id: str):
        """Update last_active timestamp."""
        self.update_session(session_id, last_active=time.time())

    def save_message(self, session_id: str, sender: str, message: str,
                     intent: str = None, confidence: float = None):
        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO messages (session_id, sender, message, timestamp, intent, confidence)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (session_id, sender, message, time.time(), intent, confidence)
            )
            conn.commit()
        finally:
            conn.close()

    def get_conversation_history(self, session_id: str, limit: int = 50) -> list:
        conn = get_db()
        try:
            rows = conn.execute(
                """SELECT sender, message, timestamp, intent FROM messages
                   WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?""",
                (session_id, limit)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_waiting_sessions(self) -> list:
        """Get all sessions waiting for a human agent."""
        conn = get_db()
        try:
            rows = conn.execute(
                """SELECT s.*, 
                   (SELECT message FROM messages WHERE session_id = s.session_id 
                    ORDER BY timestamp DESC LIMIT 1) as last_message
                   FROM sessions s WHERE s.status IN ('waiting', 'with_agent')
                   ORDER BY s.last_active DESC"""
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def assign_agent(self, session_id: str, agent_id: str):
        self.update_session(session_id,
                            assigned_agent=agent_id,
                            status='with_agent',
                            last_active=time.time())

    def close_session(self, session_id: str):
        self.update_session(session_id, status='closed')

    def set_waiting(self, session_id: str):
        self.update_session(session_id, status='waiting', last_active=time.time())

    def update_metadata(self, session_id: str, key: str, value: str):
        session = self.get_session(session_id)
        if session:
            try:
                meta = json.loads(session.metadata)
            except Exception:
                meta = {}
            meta[key] = value
            self.update_session(session_id, metadata=json.dumps(meta))


# Singleton
_session_manager = None

def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager