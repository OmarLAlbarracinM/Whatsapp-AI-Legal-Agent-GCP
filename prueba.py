from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.api_core.client_options import ClientOptions

def test_agent_with_adc():
    # Datos de tu proyecto obtenidos de tus capturas
    project_id = "project-f22e31d1-87f4-4f24-96b"
    location_id = "us-central1"
    agent_id = "edbf26f9-0e31-4cb1-8b60-242960c22e39"
    session_id = "sesion-ds-bogota" # ID único de prueba
    
    # El cliente busca las credenciales de 'gcloud' por sí solo
    client_options = ClientOptions(api_endpoint=f"{location_id}-dialogflow.googleapis.com")
    session_client = dialogflow.SessionsClient(client_options=client_options)

    # Ruta de la sesión
    session_path = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}/sessions/{session_id}"

    # Texto de prueba
    text_input = dialogflow.TextInput(text="Hola, ¿en qué me puedes ayudar?")
    query_input = dialogflow.QueryInput(text=text_input, language_code="es")
    
    request = dialogflow.DetectIntentRequest(
        session=session_path, 
        query_input=query_input
    )

    try:
        response = session_client.detect_intent(request=request)
        print("Respuesta del agente:")
        for message in response.query_result.response_messages:
            if message.text:
                print(f" -> {message.text.text[0]}")
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    test_agent_with_adc()