from google.cloud import firestore
from app.core.config import settings
from app.core.logger import logger

# Inicialización del cliente de BD (Singleton a nivel de módulo)
try:
    db = firestore.Client(project=settings.PROJECT_ID)
    logger.info("✅ Firestore client inicializado")
except Exception as e:
    logger.warning(f"⚠️ Firestore no disponible: {e}. Modo sin persistencia.")
    db = None


def get_chat_history(user_number: str) -> list:
    """Recupera historial de chat del usuario."""
    if not db:
        logger.debug("Firestore no disponible, retornando historial vacío")
        return []
    
    try:
        logger.info(f"📖 Recuperando historial: user={user_number}")
        
        docs = db.collection("chats").document(user_number).collection("messages") \
                 .order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
        
        history = []
        for doc in reversed(list(docs)):
            data = doc.to_dict()
            history.append({
                "role": data.get("role", "user"),
                "text": data.get("text", "")
            })
        
        logger.info(f"✅ Historial recuperado: user={user_number}, items={len(history)}")
        return history
        
    except Exception as e:
        logger.exception(f"❌ Error recuperando historial: user={user_number}")
        return []


def save_message(user_number: str, role: str, text: str):
    """Guarda un mensaje en la subcolección del usuario."""
    if not db:
        logger.debug("Firestore no disponible, skip save_message")
        return
    
    try:
        logger.debug(f"💾 Guardando mensaje: user={user_number}, role={role}")
        
        db.collection("chats").document(user_number).collection("messages").add({
            "role": role,
            "text": text,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        logger.debug(f"✅ Mensaje guardado: user={user_number}")
        
    except Exception as e:
        logger.exception(f"❌ Error guardando en Firestore: user={user_number}")