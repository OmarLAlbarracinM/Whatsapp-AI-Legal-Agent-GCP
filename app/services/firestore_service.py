from google.cloud import firestore
from vertexai.generative_models import Content, Part
from app.core.config import settings

# Inicialización del cliente de BD (Singleton a nivel de módulo)
db = firestore.Client(project=settings.PROJECT_ID)

def get_chat_history(user_number: str) -> list:
    """Recupera los últimos 10 mensajes y los formatea para Gemini."""
    docs = db.collection("chats").document(user_number).collection("messages") \
             .order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
    
    history = []
    # Firestore devuelve del más nuevo al más viejo, invertimos para el chat
    for doc in reversed(list(docs)):
        data = doc.to_dict()
        # Convertimos el diccionario a objetos de Vertex AI
        history.append(Content(role=data['role'], parts=[Part.from_text(data['text'])]))
    
    return history

def save_message(user_number: str, role: str, text: str):
    """Guarda un mensaje en la subcolección del usuario."""
    try:
        db.collection("chats").document(user_number).collection("messages").add({
            "role": role,
            "text": text,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print(f"❌ Error al guardar en Firestore: {e}")