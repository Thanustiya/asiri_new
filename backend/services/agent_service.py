# backend/services/agent_service.py
"""
Human Agent Service
- Checks working hours
- Manages session handover queue
- Notifies agents via WebSocket
"""

import pytz
from datetime import datetime
from typing import Dict, Set, Optional
import asyncio
import json
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

# Connected WebSocket clients
# {agent_id: websocket_instance}
connected_agents: Dict[str, object] = {}

# Pending sessions waiting for agent
# {session_id: {session_info}}
pending_queue: Dict[str, dict] = {}


def is_working_hours() -> bool:
    """Check if current time is within UK working hours."""
    tz = pytz.timezone(settings.TIMEZONE)
    now = datetime.now(tz)
    is_weekday = now.weekday() in settings.WORKING_DAYS
    is_in_hours = settings.WORKING_HOURS_START <= now.hour < settings.WORKING_HOURS_END
    return is_weekday and is_in_hours


def get_working_hours_message() -> str:
    """Return appropriate message based on working hours."""
    tz = pytz.timezone(settings.TIMEZONE)
    now = datetime.now(tz)
    
    if is_working_hours():
        return (
            "✅ Our team is currently **online**.\n"
            "You'll be connected to an advisor shortly!"
        )
    else:
        day_name = now.strftime("%A")
        time_str = now.strftime("%I:%M %p")
        return (
            f"⏰ Our team is currently **offline**.\n\n"
            f"Today is {day_name}, {time_str} (UK time).\n\n"
            "**Working Hours:** Mon–Fri, 9:00 AM – 5:00 PM (UK time)\n\n"
            "We'll get back to you as soon as possible.\n\n"
            "You can also reach us at:\n"
            "📧 info@bmlcollege.com\n"
            "📞 +44 (0) 121 523 0141"
        )


async def add_to_queue(session_id: str, user_name: str, last_message: str, channel: str):
    """Add a session to the agent queue and notify agents."""
    pending_queue[session_id] = {
        "session_id": session_id,
        "user_name": user_name or "Anonymous",
        "last_message": last_message,
        "channel": channel,
        "queued_at": datetime.utcnow().isoformat()
    }
    await notify_agents({
        "type": "new_session",
        "session": pending_queue[session_id]
    })
    logger.info(f"Session {session_id} added to agent queue")


def remove_from_queue(session_id: str):
    """Remove a session from the pending queue."""
    pending_queue.pop(session_id, None)


async def notify_agents(message: dict):
    """Broadcast a message to all connected agent WebSockets."""
    if not connected_agents:
        return
    disconnected = []
    for agent_id, ws in connected_agents.items():
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            disconnected.append(agent_id)
    for aid in disconnected:
        connected_agents.pop(aid, None)


async def notify_session(session_id: str, message: dict, session_websockets: dict):
    """Send a message to a specific chat session's WebSocket."""
    ws = session_websockets.get(session_id)
    if ws:
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            pass


def get_queue() -> list:
    return list(pending_queue.values())


def has_available_agent() -> bool:
    return len(connected_agents) > 0