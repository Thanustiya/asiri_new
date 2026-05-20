from fastapi import HTTPException
import requests
import os

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"


def send_whatsapp_message(to: str, message: str):
    """
    Send message via Meta WhatsApp Cloud API
    """

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()


def parse_whatsapp_incoming(data: dict):
    """
    Parse Meta WhatsApp webhook payload
    """

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return None

        message = value["messages"][0]

        return {
            "sender": message["from"],
            "message": message["text"]["body"] if message["type"] == "text" else ""
        }

    except Exception as e:
        print("Webhook parsing error:", e)
        return None