"""
WhatsApp Handler for BML Chatbot
Uses Twilio WhatsApp Business API for message delivery.
Same NLP engine powers both web and WhatsApp channels.
"""

import logging
import time
from typing import Optional
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from nlp_engine import get_engine
from session_manager import get_session_manager
from human_agent import get_agent_manager, is_within_working_hours

logger = logging.getLogger(__name__)

# Twilio config (loaded from env vars in main.py)
_twilio_config = {
    "account_sid": None,
    "auth_token": None,
    "whatsapp_number": None  # e.g. "whatsapp:+14155238886" (Twilio sandbox)
}


def init_twilio(account_sid: str, auth_token: str, whatsapp_number: str):
    """Initialize Twilio credentials."""
    _twilio_config["account_sid"] = account_sid
    _twilio_config["auth_token"] = auth_token
    _twilio_config["whatsapp_number"] = whatsapp_number
    logger.info("Twilio WhatsApp initialized")


def get_twilio_client() -> Optional[Client]:
    if _twilio_config["account_sid"] and _twilio_config["auth_token"]:
        return Client(_twilio_config["account_sid"], _twilio_config["auth_token"])
    return None


def format_whatsapp_response(response_text: str, options: list) -> str:
    """
    Format bot response for WhatsApp.
    WhatsApp doesn't support buttons via TwiML — we use numbered quick replies.
    """
    message = response_text

    if options:
        message += "\n\n━━━━━━━━━━━━━━━━\n"
        message += "📌 *Quick Options:*\n"
        for i, option in enumerate(options[:5], 1):  # Max 5 options
            # Strip emoji for cleaner WhatsApp display, or keep them
            message += f"*{i}.* {option}\n"
        message += "\n_Reply with a number or type your question_"

    return message


def format_interactive_list(title: str, options: list) -> dict:
    """
    Format for WhatsApp Interactive List Message (requires WhatsApp Business API approval).
    This is a helper for when you upgrade to full API.
    """
    rows = []
    for i, opt in enumerate(options[:10], 1):
        rows.append({
            "id": f"opt_{i}",
            "title": opt[:24],  # WhatsApp title limit
            "description": ""
        })
    return {
        "type": "list",
        "header": {"type": "text", "text": "BML College"},
        "body": {"text": title},
        "footer": {"text": "BML College AI Assistant"},
        "action": {
            "button": "View Options",
            "sections": [{"title": "Options", "rows": rows}]
        }
    }


def parse_option_selection(text: str, last_options: list) -> Optional[str]:
    """
    Check if user replied with a number corresponding to an option.
    e.g. "1" → first option text
    """
    text = text.strip()
    if text.isdigit():
        idx = int(text) - 1
        if 0 <= idx < len(last_options):
            return last_options[idx]
    return None


def send_whatsapp_message(to_number: str, message: str) -> bool:
    """Send a WhatsApp message via Twilio."""
    client = get_twilio_client()
    if not client:
        logger.warning("Twilio not configured - message not sent")
        return False

    try:
        # Ensure number has whatsapp: prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"

        client.messages.create(
            from_=_twilio_config["whatsapp_number"],
            to=to_number,
            body=message
        )
        logger.info(f"WhatsApp message sent to {to_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return False


class WhatsAppHandler:
    """Handles incoming WhatsApp messages and returns TwiML responses."""

    def __init__(self):
        self.engine = get_engine()
        self.sm = get_session_manager()
        self.am = get_agent_manager()
        # Cache last options per number: {wa_number: [options]}
        self.last_options_cache: dict = {}

    def handle_incoming(self, from_number: str, body: str) -> str:
        """
        Process incoming WhatsApp message.
        Returns TwiML response string.
        """
        # Clean the number
        clean_number = from_number.replace("whatsapp:", "")

        # Get or create session
        session = self.sm.get_or_create_by_identifier(clean_number, "whatsapp")
        session_id = session.session_id

        # Update last active
        self.sm.touch_session(session_id)

        # Save user message
        self.sm.save_message(session_id, "user", body)

        # Check if session is with human agent
        if session.status == "with_agent":
            return self._handle_agent_session(session_id, session.assigned_agent, body, clean_number)

        if session.status == "waiting":
            return self._generate_twiml(
                "⏳ You're in the queue waiting for an advisor. We'll connect you shortly!\n\n"
                "Type *menu* to use the AI assistant while you wait.",
                []
            )

        # Check if user is selecting from numbered options
        last_options = self.last_options_cache.get(clean_number, [])
        selected = parse_option_selection(body, last_options)
        if selected:
            body = selected  # Process as if they typed the option

        # Reset to main menu
        if body.strip().lower() in ['menu', 'start', 'hi', 'hello', 'hey', '0']:
            body = 'hello'

        # Process with NLP engine
        result = self.engine.process_message(body)
        tag = result.get('tag', 'fallback')
        confidence = result.get('confidence', 0)

        # Save processed message intent
        self.sm.save_message(session_id, "bot", result['response'], tag, confidence)

        # Handle agent transfer request
        if result.get('action') == 'transfer_to_agent' or tag == 'human_agent':
            transfer_result = self.am.request_agent_transfer(session_id)
            response_text = transfer_result['message']
            options = transfer_result.get('options', [])
        else:
            response_text = result['response']
            options = result.get('options', [])

        # Cache options for next message
        if options:
            self.last_options_cache[clean_number] = options

        # Format and return
        formatted = format_whatsapp_response(response_text, options)
        return self._generate_twiml(formatted, [])

    def _handle_agent_session(self, session_id: str, agent_id: str,
                               body: str, from_number: str) -> str:
        """Route message to human agent."""
        import asyncio
        # Store message
        self.sm.save_message(session_id, "user", body)

        # Notify agent (async - fire and forget)
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(
                self.am.send_to_agent(agent_id, {
                    "type": "user_message",
                    "session_id": session_id,
                    "message": body,
                    "channel": "whatsapp",
                    "timestamp": time.time()
                })
            )
        except Exception as e:
            logger.warning(f"Could not notify agent: {e}")

        # Acknowledge receipt
        return self._generate_twiml("✅ Message received. The advisor will reply shortly.", [])

    def _generate_twiml(self, message: str, media_urls: list = None) -> str:
        """Generate TwiML XML response."""
        resp = MessagingResponse()
        msg = resp.message()
        msg.body(message)
        if media_urls:
            for url in media_urls:
                msg.media(url)
        return str(resp)

    def send_agent_message_to_whatsapp(self, to_number: str, message: str,
                                        agent_name: str = "BML Advisor") -> bool:
        """Send agent message to WhatsApp user."""
        formatted = f"👤 *{agent_name}:*\n{message}"
        return send_whatsapp_message(f"whatsapp:{to_number}", formatted)


# Singleton
_wa_handler = None

def get_whatsapp_handler() -> WhatsAppHandler:
    global _wa_handler
    if _wa_handler is None:
        _wa_handler = WhatsAppHandler()
    return _wa_handler