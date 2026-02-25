from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import whatsapp
from app.core.config import settings
from app.core.logger import logger

# Crear aplicación FastAPI
app = FastAPI(
    title="Abogado Bot Backend",
    description="Backend para chatbot legal en WhatsApp usando Conversational Agent de GCP",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(whatsapp.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Abogado Bot Backend",
        "environment": settings.ENV,
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Healthcheck endpoint para monitoreo."""
    return {
        "status": "healthy",
        "project_id": settings.PROJECT_ID,
        "agent_id": settings.AGENT_ID[:20] + "..." if settings.AGENT_ID else "NOT SET"
    }


@app.on_event("startup")
async def startup_event():
    """Ejecuta al iniciar la aplicación."""
    logger.info(f"🚀 Abogado Bot Backend iniciado")
    logger.info(f"   Entorno: {settings.ENV}")
    logger.info(f"   Proyecto GCP: {settings.PROJECT_ID}")
    logger.info(f"   Agente: {settings.AGENT_ID[:20]}..." if settings.AGENT_ID else "   ⚠️ AGENT_ID NO CONFIGURADO")


@app.on_event("shutdown")
async def shutdown_event():
    """Ejecuta al cerrar la aplicación."""
    logger.info("🛑 Abogado Bot Backend cerrado")