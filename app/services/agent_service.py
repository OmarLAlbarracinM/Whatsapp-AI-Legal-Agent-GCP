from google.cloud.dialogflow_v3 import SessionsClient, TextInput, QueryInput, DetectIntentRequest
from app.core.config import settings
from app.core.logger import logger


class ConversationalAgentService:
    def __init__(self):
        self.project_id = settings.PROJECT_ID
        self.agent_id = settings.AGENT_ID
        self.location = settings.LOCATION
        
        try:
            self.client = SessionsClient()
            logger.info(f"✅ Conversational Agent inicializado: agent_id={self.agent_id}")
        except Exception as e:
            logger.exception(f"❌ Error inicializando Agent Service: {e}")
            self.client = None
    
    def send_message_to_agent(self, user_id: str, user_message: str) -> str:
        """Envía un mensaje al Conversational Agent y retorna la respuesta."""
        if not self.client or not self.agent_id:
            logger.error("Agent Service no está disponible")
            return "Lo siento, el servicio no está disponible. Intenta más tarde."
        
        try:
            # Usar el número de WhatsApp como session ID (mantiene contexto)
            session_id = user_id
            session_path = self.client.session_path(
                project=self.project_id,
                location=self.location,
                agent=self.agent_id,
                session=session_id,
            )
            
            # Crear request
            text_input = TextInput(text=user_message)
            request_input = QueryInput(text=text_input, language_code="es")
            
            request = DetectIntentRequest(
                session=session_path,
                query_input=request_input,
            )
            
            logger.info(f"📤 Enviando mensaje al Agent: user={user_id}, query={user_message[:50]}")
            
            # Agregar timeout
            response = self.client.detect_intent(request=request, timeout=30)
            
            # Extraer la respuesta
            if response.query_result.response_messages:
                agent_response = response.query_result.response_messages[0].text.text[0]
                logger.info(f"📥 Respuesta del Agent recibida: user={user_id}")
            else:
                agent_response = "No entendí tu pregunta. ¿Puedes reformularla?"
                logger.warning(f"⚠️ Agent no retornó respuesta: user={user_id}")
            
            return agent_response
            
        except Exception as e:
            logger.exception(f"❌ Error comunicando con Agent: user={user_id}, error={str(e)}")
            return "Lo siento, hubo un error procesando tu solicitud. Por favor intenta de nuevo."