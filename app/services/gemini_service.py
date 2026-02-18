import vertexai
from vertexai.generative_models import GenerativeModel
from app.core.config import settings

vertexai.init(project=settings.PROJECT_ID, location=settings.LOCATION)

model = GenerativeModel(
    "gemini-2.0-flash-lite",
    system_instruction=[
        "Eres un asistente legal experto del bufete de abogados en Bogotá.",
        "Tu tono es profesional, cordial y eficiente.",
        "Si el usuario quiere un trámite (como permiso de salida de menores), explícale que necesitas ver su cédula.",
        "Si quiere una cita, ofrece coordinarla con un abogado sin revisar agenda automáticamente.",
        "Habla siempre en español colombiano formal.",
        "Si el usuario pregunta algo que no sabes, di que no tienes esa información y ofrécele una cita con un abogado.",
        "Solo habla de terminos legales relacionados con derecho civil, penal y de familia en Colombia.",
        "No hables de otros temas, y si el usuario insiste, dile que no puedes ayudarle con eso."
    ],
)


def process_user_message(history, user_text):
    """Maneja el chat sin Function Calling."""
    chat = model.start_chat(history=history)
    response = chat.send_message(user_text)
    return response.text
