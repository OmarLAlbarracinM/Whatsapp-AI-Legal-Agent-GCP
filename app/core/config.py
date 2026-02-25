import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Google Cloud
    PROJECT_ID = os.getenv("PROJECT_ID", "")
    LOCATION = os.getenv("LOCATION", "us-central1")
    AGENT_ID = os.getenv("AGENT_ID", "")
    
    # WhatsApp
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    ENV = os.getenv("ENV", "development")
    
    def validate(self):
        """Valida que las variables críticas estén configuradas."""
        errors = []
        
        if not self.PROJECT_ID:
            errors.append("❌ PROJECT_ID no configurado en .env")
        if not self.AGENT_ID:
            errors.append("❌ AGENT_ID no configurado en .env")
        if not self.VERIFY_TOKEN:
            errors.append("⚠️ VERIFY_TOKEN no configurado en .env")
        if not self.WHATSAPP_TOKEN:
            errors.append("⚠️ WHATSAPP_TOKEN no configurado en .env")
        
        if errors:
            for error in errors:
                print(error)
        
        return len(errors) == 0


settings = Settings()

# Validar al importar
if settings.ENV == "production":
    if not settings.validate():
        raise Exception("Configuración incompleta. Revisa las variables de entorno.")