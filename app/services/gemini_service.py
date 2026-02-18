import vertexai
from vertexai.generative_models import GenerativeModel, Part
from app.core.config import settings
from app.utils.tools_def import calendar_tool
from app.services.calendar_service import consultar_disponibilidad
from app.core.config import settings


vertexai.init(project=settings.PROJECT_ID, location=settings.LOCATION)



model = GenerativeModel(
    "gemini-2.0-flash-lite",
    system_instruction=[
        "Eres un asistente legal experto del bufete de abogados en Bogotá.",
        "Tu tono es profesional, cordial y eficiente.",
        "Si el usuario quiere un trámite (como permiso de salida de menores), explícale que necesitas ver su cédula.",
        "Si quiere una cita, dile que revisarás la agenda.",
        "Habla siempre en español colombiano formal.",
        "REGLAS DE AGENDA IMPORTANTES:",
        "1. De Lunes a Viernes: Solo agendas citas después de las 6:00 PM.",
        "2. Sábados: Puedes agendar en cualquier horario laboral (8:00 AM a 5:00 PM).",
        "3. Domingos: El bufete está cerrado.",
        "Si el usuario pregunta algo que no sabes, di que no tienes esa información y ofrécele una cita con un abogado.",
        "Solo habla de terminos legales relacionados con derecho civil, penal y de familia en Colombia.",
        "No hables de otros temas, y si el usuario insiste, dile que no puedes ayudarle con eso."
    ],
    tools=[calendar_tool]
)


def process_user_message(history, user_text):
    """Maneja el chat y la lógica de Function Calling"""
    chat = model.start_chat(history=history)
    response = chat.send_message(user_text)
    
    # Manejo de Function Calling
    if response.candidates[0].content.parts[0].function_call:
        fn = response.candidates[0].content.parts[0].function_call
        if fn.name == "consultar_disponibilidad":
            # Llamamos a la lógica del calendario (importada de calendar_service)
            resultado = consultar_disponibilidad(fn.args["fecha"])
            
            # Devolvemos respuesta a Gemini
            response = chat.send_message(
                Part.from_function_response(
                    name="consultar_disponibilidad",
                    response={"content": resultado}
                )
            )
            
    return response.text
