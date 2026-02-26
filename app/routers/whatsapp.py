from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.services.agent_service import send_to_agent
from app.services.whatsapp_service import send_whatsapp_message

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == settings.VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(content="Error de verificación", status_code=403)

@router.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
        entry = body['entry'][0]['changes'][0]['value']

        if 'messages' in entry:
            user_number = entry['messages'][0]['from']
            user_text = entry['messages'][0]['text']['body']

            response_text = await send_to_agent(user_number, user_text)

            await send_whatsapp_message(user_number, response_text)

    except Exception as e:
        print(f"Error procesando webhook: {e}")

    return {"status": "ok"}