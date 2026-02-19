from google.cloud import firestore
from vertexai.generative_models import Content, Part
from app.core.config import settings
from app.core.logger import logger

# Inicialización del cliente de BD (Singleton a nivel de módulo)
db = firestore.Client(project=settings.PROJECT_ID)


def get_chat_history(user_number: str) -> list:
    try:
        logger.info("Recuperando historial user=%s", user_number)
        docs = db.collection("chats").document(user_number).collection("messages") \
                 .order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
        
        history = []
        for doc in reversed(list(docs)):
            data = doc.to_dict()
            role = "model" if data['role'] == "assistant" else data['role'] 
            history.append(Content(role=role, parts=[Part.from_text(data['text'])]))
        logger.info("Historial recuperado user=%s items=%s", user_number, len(history))
        return history
    except Exception as e:
        logger.exception("Error recuperando historial user=%s", user_number)
        return [] 


def save_message(user_number: str, role: str, text: str):
    """Guarda un mensaje en la subcolección del usuario."""
    try:
        logger.info("Guardando mensaje user=%s role=%s", user_number, role)
        db.collection("chats").document(user_number).collection("messages").add({
            "role": role,
            "text": text,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        logger.exception("Error al guardar en Firestore user=%s", user_number)