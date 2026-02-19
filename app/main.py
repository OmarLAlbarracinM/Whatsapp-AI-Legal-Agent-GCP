from fastapi import FastAPI
from app.routers import whatsapp
from app.core.logger import setup_logging

setup_logging()

app = FastAPI(title="Abogado Bot API", version="1.0.0")

# Incluir rutas
app.include_router(whatsapp.router)

from google.cloud import discoveryengine_v1beta as discoveryengine

# Configura tus datos aquí para la prueba
project_id = "TU_ID_DE_PROYECTO_TEXTO" 
location = "us"

client = discoveryengine.DataStoreServiceClient(
    client_options={"api_endpoint": "us-discoveryengine.googleapis.com"}
)
parent = f"projects/{project_id}/locations/{location}/collections/default_collection"

print(f"--- Listando Data Stores disponibles en {project_id} ({location}) ---")
try:
    response = client.list_data_stores(parent=parent)
    found = False
    for ds in response:
        found = True
        print(f"✅ Encontrado: {ds.name}")
        print(f"👉 ID exacto para tu ENV: {ds.name.split('/')[-1]}")
    if not found:
        print("❌ No se encontraron Data Stores en esta ubicación. Verifica el Project ID.")
except Exception as e:
    print(f"⚠️ Error al conectar: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)