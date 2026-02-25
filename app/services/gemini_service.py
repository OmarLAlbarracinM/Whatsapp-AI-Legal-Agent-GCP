from app.services.agent_service import ConversationalAgentService
from app.core.logger import logger

agent_service = ConversationalAgentService()


def process_user_message(history, user_text, user_id: str = None):
    """Maneja el chat usando el Conversational Agent."""
    logger.info(f"Enviando mensaje al Conversational Agent: user_id={user_id}")
    
    if not user_id:
        logger.warning("user_id no proporcionado al process_user_message")
        user_id = "unknown"
    
    response = agent_service.send_message_to_agent(user_id, user_text)
    logger.info("Respuesta del Agent recibida")
    return response


def process_user_message_agent(history, user_text, user_id: str = None):
    """Alias para compatibilidad."""
    return process_user_message(history, user_text, user_id)