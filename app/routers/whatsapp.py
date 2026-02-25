from fastapi import APIRouter, Request, BackgroundTasks
from app.services.whatsapp_service import send_whatsapp_message
from app.services.gemini_service import process_user_message
from app.services.firestore_service import save_message
from app.services.security_service import verify_whatsapp_signature
from app.core.config import settings
from app.core.logger import logger

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.get("/webhook")
async def verify_webhook(request: Request):
    """Verifica el webhook de WhatsApp (GET)."""
    try:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        logger.info(f"🔐 Webhook verification: mode={mode}")
        
        if mode == "subscribe" and token == settings.VERIFY_TOKEN:
            logger.info("✅ Webhook verificado correctamente")
            return int(challenge)
        else:
            logger.warning("❌ Token de verificación inválido")
            return {"error": "Unauthorized"}, 403
    except Exception as e:
        logger.exception(f"❌ Error en verification webhook: {e}")
        return {"error": "Internal Server Error"}, 500


@router.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """Recibe mensajes de WhatsApp (POST)."""
    try:
        # Obtener raw body para verificación de firma
        raw_body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256")
        
        # ✅ VALIDAR FIRMA DE WHATSAPP
        if not verify_whatsapp_signature(raw_body.decode(), signature):
            logger.warning("❌ Firma de webhook inválida, rechazando")
            return {"error": "Invalid signature"}, 403
        
        body = await request.json()
        logger.info(f"📨 Webhook POST recibido")
        
        # Validar que sea un mensaje
        if body.get("object") != "whatsapp_business_account":
            logger.debug("No es un mensaje de WhatsApp, ignorando")
            return {"status": "ok"}
        
        # Extraer información del mensaje
        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                for message in messages:
                    user_phone = message.get("from")
                    message_type = message.get("type")
                    message_text = None
                    
                    # Procesar según tipo de mensaje
                    if message_type == "text":
                        message_text = message.get("text", {}).get("body", "")
                    else:
                        logger.info(f"⚠️ Tipo de mensaje no soportado: {message_type}")
                        continue
                    
                    if message_text and user_phone:
                        logger.info(f"📨 Mensaje recibido: from={user_phone}, text={message_text[:50]}")
                        
                        # ✅ PROCESAR EN BACKGROUND CON user_id
                        background_tasks.add_task(
                            handle_ai_logic,
                            user_phone,
                            message_text
                        )
        
        return {"status": "received"}
        
    except Exception as e:
        logger.exception(f"❌ Error en handle_webhook: {e}")
        return {"status": "error", "message": str(e)}, 500


async def handle_ai_logic(user_phone: str, user_text: str):
    """Procesa el mensaje con IA (ejecuta en background)."""
    try:
        logger.info(f"🚀 Iniciando procesamiento: user={user_phone}")
        
        # ✅ PASAR user_id (user_phone) AL AGENT
        bot_reply = process_user_message(None, user_text, user_id=user_phone)
        
        # Guardar en Firestore (opcional)
        save_message(user_phone, "user", user_text)
        save_message(user_phone, "model", bot_reply)
        
        # Enviar respuesta
        success = send_whatsapp_message(user_phone, bot_reply)
        
        if success:
            logger.info(f"✅ Procesamiento completado: user={user_phone}")
        else:
            logger.error(f"❌ Error enviando respuesta: user={user_phone}")
        
    except Exception as e:
        logger.exception(f"❌ Error en lógica de IA: user={user_phone}")
        try:
            send_whatsapp_message(user_phone, "Lo siento, hubo un error. Intenta de nuevo.")
        except:
            logger.exception(f"Error enviando mensaje de error a {user_phone}")