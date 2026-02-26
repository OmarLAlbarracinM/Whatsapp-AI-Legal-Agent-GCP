import asyncio
import logging
import time
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.api_core.client_options import ClientOptions
from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_to_agent_sync(session_id: str, user_text: str) -> str:
    """Lógica sincrónica: envía mensaje al agente Dialogflow CX y retorna la respuesta."""
    client_options = ClientOptions(
        api_endpoint=f"{settings.LOCATION}-dialogflow.googleapis.com"
    )
    session_client = dialogflow.SessionsClient(client_options=client_options)

    session_path = (
        f"projects/{settings.PROJECT_ID}"
        f"/locations/{settings.LOCATION}"
        f"/agents/{settings.AGENT_ID}"
        f"/sessions/{session_id}"
    )

    logger.debug("Enviando a Dialogflow CX | session=%s | endpoint=%s-dialogflow.googleapis.com",
                 session_id, settings.LOCATION)

    text_input = dialogflow.TextInput(text=user_text)
    query_input = dialogflow.QueryInput(text=text_input, language_code="es")

    request = dialogflow.DetectIntentRequest(
        session=session_path,
        query_input=query_input,
    )

    start = time.time()
    response = session_client.detect_intent(request=request)
    elapsed = time.time() - start

    logger.info("Respuesta de Dialogflow CX recibida | session=%s | latencia=%.2fs", session_id, elapsed)

    responses = []
    for message in response.query_result.response_messages:
        if message.text and message.text.text:
            responses.append(message.text.text[0])

    if not responses:
        logger.warning("Dialogflow CX no devolvió mensajes de texto | session=%s", session_id)
        return "No obtuve respuesta del agente."

    return "\n".join(responses)


async def send_to_agent(session_id: str, user_text: str) -> str:
    """Envía un mensaje al agente Dialogflow CX y retorna la respuesta (async)."""
    logger.info("Iniciando llamada al agente | session=%s | text=%.100s", session_id, user_text)
    try:
        result = await asyncio.to_thread(_send_to_agent_sync, session_id, user_text)
        return result
    except Exception:
        logger.exception("Error en llamada a Dialogflow CX | session=%s", session_id)
        return "Lo siento, hubo un error procesando tu solicitud. Por favor intenta de nuevo."
