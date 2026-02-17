from fastapi import APIRouter, Request, Response, HTTPException
from app.core.config import settings
from app.services.firestore_service import get_chat_history, save_message
from app.services.gemini_service import process_user_message
from app.services.whatsapp_service import send_whatsapp_message

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == settings.VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(content="Error de verificación", status_code=403)

@router.post("/webhook")
async def handle_messages(request: Request):
    try:
        body = await request.json()
        entry = body['entry'][0]['changes'][0]['value']
        
        if 'messages' in entry:
            user_number = entry['messages'][0]['from']
            user_text = entry['messages'][0]['text']['body']
            
            # 1. Recuperar contexto
            history = get_chat_history(user_number)
            
            # 2. Procesar con IA
            bot_reply = process_user_message(history, user_text)
            
            # 3. Guardar y Responder
            save_message(user_number, "user", user_text)
            save_message(user_number, "model", bot_reply)
            send_whatsapp_message(user_number, bot_reply)
            
    except Exception as e:
        print(f"Error procesando webhook: {e}")
        # En producción, usa logging real, no print
        
    return {"status": "ok"}