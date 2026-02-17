import requests
from app.core.config import settings

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
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status() # Lanza error si falla la petición HTTP
    except requests.exceptions.RequestException as e:
        print(f"Error enviando mensaje a WhatsApp: {e}")
        
