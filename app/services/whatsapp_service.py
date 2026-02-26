import asyncio
import requests
from app.core.config import settings


def _send_sync(to: str, text: str):
    """Envío sincrónico a WhatsApp Business API."""
    url = f"https://graph.facebook.com/v18.0/{settings.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()


async def send_whatsapp_message(to: str, text: str):
    """Envía un mensaje de texto a WhatsApp Business API (async)."""
    try:
        await asyncio.to_thread(_send_sync, to, text)
    except requests.exceptions.RequestException as e:
        print(f"Error enviando mensaje a WhatsApp: {e}")
        
