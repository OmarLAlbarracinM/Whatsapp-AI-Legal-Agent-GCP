from fastapi import APIRouter, Request, Response, HTTPException, BackgroundTasks
from app.core.config import settings
from app.core.logger import logger
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


async def handle_ai_logic(user_number: str, user_text: str):
    """Lógica asíncrona para no bloquear el webhook de WhatsApp."""
    try:
        logger.info(f"🚀 Iniciando procesamiento para {user_number}")
        # 1. Recuperar historial (últimos 10 mensajes)
        history = get_chat_history(user_number)
        
        # 2. Procesar con IA (que ahora incluye RAG internamente)
        bot_reply = process_user_message(history, user_text)
        
        # 3. Guardar persistencia en Firestore
        save_message(user_number, "user", user_text)
        save_message(user_number, "model", bot_reply)
        
        # 4. Enviar respuesta final al usuario en Bogotá
        send_whatsapp_message(user_number, bot_reply)
        
        logger.info(f"✅ Respuesta enviada exitosamente a {user_number}")
    except Exception as e:
        logger.exception(f"❌ Error en lógica de IA: {e}")

@router.post("/webhook")
async def handle_messages(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
        logger.debug(f"Payload recibido: {body}") # Útil para debugging
        
        if 'messages' in body.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}):
            value = body['entry'][0]['changes'][0]['value']
            message = value['messages'][0]
            user_number = message['from']
            
            if message.get('type') == 'text':
                user_text = message['text']['body']
                logger.info(f"📩 Mensaje recibido de {user_number}: {user_text[:30]}...")
                background_tasks.add_task(handle_ai_logic, user_number, user_text)
            else:
                logger.warning(f"⚠️ Tipo de mensaje no soportado recibido de {user_number}")
                
    except Exception as e:
        logger.error(f"⚠️ Error en el webhook de entrada: {e}")
        
    return {"status": "ok"}