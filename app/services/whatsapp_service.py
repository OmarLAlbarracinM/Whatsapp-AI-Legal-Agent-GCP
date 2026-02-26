import asyncio
import logging
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_sync(to: str, text: str):
    """Envío sincrónico a WhatsApp Business API."""
    url = f"https://graph.facebook.com/v18.0/{settings.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    logger.info("Mensaje enviado a WhatsApp | to=%s | status_code=%s", to, response.status_code)


async def send_whatsapp_message(to: str, text: str):
    """Envía un mensaje de texto a WhatsApp Business API (async)."""
    logger.info("Enviando mensaje a WhatsApp | to=%s | text=%.100s", to, text)
    try:
        await asyncio.to_thread(_send_sync, to, text)
    except requests.exceptions.HTTPError as e:
        logger.error("Error HTTP enviando a WhatsApp | to=%s | status=%s | response=%s",
                     to, e.response.status_code, e.response.text)
    except requests.exceptions.RequestException as e:
        logger.error("Error de red enviando a WhatsApp | to=%s | error=%s", to, e)
