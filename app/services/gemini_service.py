import vertexai
from vertexai.generative_models import GenerativeModel
from app.core.config import settings
from app.services.rag_service import RAGService

vertexai.init(project=settings.PROJECT_ID, location=settings.LOCATION)

rag_service = RAGService()

model = GenerativeModel(
    "gemini-2.0-flash-lite",
    system_instruction=[
        "Eres un asistente legal experto del bufete de abogados en Bogotá.",
        "Tu tono es profesional, cordial y eficiente.",
        "Habla siempre en español colombiano formal.",
        "Utiliza la información del 'CONTEXTO LEGAL' proporcionado para responder.",
        "Solo habla de terminos legales relacionados permisos notariales, poderes autenticados, permisos de salida de menores y citas con abogados.",
        "Si la respuesta no está en el CONTEXTO LEGAL, di que no tienes esa información y ofrécele una cita con un abogado.",
        "No hables de otros temas, y si el usuario insiste, dile que no puedes ayudarle con eso."
    ],
)


def process_user_message(history, user_text):
    """Maneja el chat integrando RAG (Retrieval-Augmented Generation)."""
    
    # 1. Recuperar contexto legal de los PDFs en Vertex AI Search
    contexto_legal = rag_service.get_legal_context(user_text)
    
    # 2. Construir el prompt enriquecido con el contexto
    prompt_enriquecido = f"""
    CONTEXTO LEGAL:
    {contexto_legal}
    
    PREGUNTA DEL USUARIO:
    {user_text}
    """
    
    chat = model.start_chat(history=history)
    response = chat.send_message(prompt_enriquecido)
    
    return response.text