import requests
from app.core.config import settings
from app.core.logger import logger

def send_whatsapp_message(to: str, text: str):
    """Envía un mensaje de texto a WhatsApp Business API."""
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
    
    try:
        logger.info("Enviando mensaje WhatsApp to=%s", to)
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status() # Lanza error si falla la petición HTTP
        logger.info("Mensaje WhatsApp enviado ok to=%s status=%s", to, response.status_code)
    except requests.exceptions.RequestException as e:
        logger.exception("Error enviando mensaje a WhatsApp to=%s", to)
        
