from fastapi import FastAPI
from app.routers import whatsapp
from app.core.logger import setup_logging

setup_logging()

app = FastAPI(title="Abogado Bot API", version="1.0.0")

# Incluir rutas
app.include_router(whatsapp.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)