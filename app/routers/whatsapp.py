import logging
from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.services.agent_service import send_to_agent
from app.services.whatsapp_service import send_whatsapp_message

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")

    if mode == "subscribe" and token == settings.VERIFY_TOKEN:
        logger.info("Webhook verificado correctamente")
        return Response(content=params.get("hub.challenge"), media_type="text/plain")

    logger.warning("Verificación de webhook fallida | mode=%s | token_recibido=%s", mode, token)
    return Response(content="Error de verificación", status_code=403)


@router.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        # WhatsApp también envía eventos de estado (enviado, entregado, leído)
        if "statuses" in value:
            status = value["statuses"][0]
            logger.info(
                "Evento de estado | status=%s | message_id=%s | recipient=%s",
                status.get("status"),
                status.get("id"),
                status.get("recipient_id"),
            )
            return {"status": "ok"}

        if "messages" not in value:
            logger.debug("Webhook recibido sin mensajes ni estados | value_keys=%s", list(value.keys()))
            return {"status": "ok"}

        message = value["messages"][0]
        user_number = message.get("from")
        msg_type = message.get("type")

        logger.info("Mensaje recibido | from=%s | type=%s", user_number, msg_type)

        # Solo procesamos mensajes de texto
        if msg_type != "text":
            logger.warning(
                "Tipo de mensaje no soportado, ignorando | from=%s | type=%s",
                user_number,
                msg_type,
            )
            return {"status": "ok"}

        user_text = message["text"]["body"]
        logger.info("Texto del mensaje | from=%s | text=%.100s", user_number, user_text)

        response_text = await send_to_agent(user_number, user_text)
        logger.info("Respuesta del agente lista | from=%s | response=%.100s", user_number, response_text)

        await send_whatsapp_message(user_number, response_text)

    except KeyError as e:
        logger.error("Campo inesperado en payload de WhatsApp | campo_faltante=%s", e)
    except Exception as e:
        logger.exception("Error inesperado procesando webhook | error=%s", e)

    return {"status": "ok"}
