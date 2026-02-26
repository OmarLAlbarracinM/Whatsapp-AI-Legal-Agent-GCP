import asyncio
import traceback
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.api_core.client_options import ClientOptions
from app.core.config import settings


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

    text_input = dialogflow.TextInput(text=user_text)
    query_input = dialogflow.QueryInput(text=text_input, language_code="es")

    request = dialogflow.DetectIntentRequest(
        session=session_path,
        query_input=query_input,
    )

    response = session_client.detect_intent(request=request)

    responses = []
    for message in response.query_result.response_messages:
        if message.text and message.text.text:
            responses.append(message.text.text[0])

    return "\n".join(responses) if responses else "No obtuve respuesta del agente."


async def send_to_agent(session_id: str, user_text: str) -> str:
    """Envía un mensaje al agente Dialogflow CX y retorna la respuesta (async)."""
    try:
        return await asyncio.to_thread(_send_to_agent_sync, session_id, user_text)
    except Exception as e:
        print(f"[agent_service] ERROR: {e}")
        print(traceback.format_exc())
        return "Lo siento, hubo un error procesando tu solicitud. Por favor intenta de nuevo."
