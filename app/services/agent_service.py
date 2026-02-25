from google.cloud import dialogflow_v3 as dialogflow
from app.core.config import settings
from app.core.logger import logger
import uuid

class ConversationalAgentService:
    def __init__(self):
        self.project_id = settings.PROJECT_ID
        self.agent_id = settings.AGENT_ID  # Necesitas agregar esto a config.py
        self.location = settings.LOCATION
        
        self.client = dialogflow.SessionsClient()
        logger.info(f"Agent Service inicializado con agent_id={self.agent_id}")
    
    def send_message_to_agent(self, user_id: str, user_message: str) -> str:
        """Envía un mensaje al Conversational Agent y retorna la respuesta."""
        try:
            # Crear sesión única por usuario (mantiene contexto)
            session_id = user_id  # Usar el número de WhatsApp como session ID
            session_path = self.client.session_path(
                project=self.project_id,
                location=self.location,
                agent=self.agent_id,
                session=session_id,
            )
            
            # Crear request con el mensaje del usuario
            text_input = dialogflow.TextInput(text=user_message)
            request_input = dialogflow.QueryInput(text=text_input, language_code="es")
            
            request = dialogflow.DetectIntentRequest(
                session=session_path,
                query_input=request_input,
            )
            
            logger.info(f"Enviando mensaje al Agent user={user_id}")
            response = self.client.detect_intent(request=request)
            
            # Extraer la respuesta
            agent_response = response.query_result.response_messages[0].text.text[0]
            
            logger.info(f"Respuesta del Agent recibida user={user_id}")
            return agent_response
            
        except Exception as e:
            logger.exception(f"Error comunicando con Agent user={user_id}")
            return "Lo siento, hubo un error procesando tu solicitud. Por favor intenta de nuevo."