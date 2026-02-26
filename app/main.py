import logging
from fastapi import FastAPI
from app.core.logger import setup_logging
from app.core.config import settings
from app.routers import whatsapp

setup_logging()
logger = logging.getLogger(__name__)

_REQUIRED_VARS = ["PROJECT_ID", "LOCATION", "VERIFY_TOKEN", "WHATSAPP_TOKEN", "PHONE_NUMBER_ID", "AGENT_ID"]

def _validate_config():
    missing = [var for var in _REQUIRED_VARS if not getattr(settings, var)]
    if missing:
        logger.critical("Variables de entorno faltantes: %s — la app puede no funcionar correctamente", missing)
    else:
        logger.info("Configuración validada | vars=%s", _REQUIRED_VARS)

app = FastAPI(title="Abogado Bot API", version="1.0.0")
app.include_router(whatsapp.router)

@app.on_event("startup")
async def on_startup():
    logger.info("Iniciando Abogado Bot API")
    _validate_config()
    logger.info("Servidor listo para recibir mensajes")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
