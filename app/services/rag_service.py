from google.cloud import discoveryengine_v1beta as discoveryengine
from app.core.config import settings
from app.core.logger import logger
from google.api_core import exceptions

class RAGService:
    def __init__(self):
        # Usamos las variables centralizadas en settings
        self.project_id = settings.PROJECT_ID
        self.location = settings.RAG_LOCATION
        self.data_store_id = settings.DATA_STORE_ID
        
        # endpoint regional
        client_options = {
            "api_endpoint": "us-discoveryengine.googleapis.com"
        }
        
        logger.info(f"Conectando al Data Store '{self.data_store_id}' en la ubicación '{self.location}'")
        
        self.client = discoveryengine.SearchServiceClient(client_options=client_options)
    
    def get_legal_context(self, query: str) -> str:
        logger.info("Buscando contexto legal")
        # Definimos la ruta usando los settings cargados
        serving_config = self.client.serving_config_path(
            project=self.project_id,
            location=self.location,
            data_store=self.data_store_id,
            serving_config="default_search",
        )

        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=3,
        )
        
        try:
            logger.info(f"🔍 Ejecutando búsqueda RAG para query: {query[:50]}...")
            response = self.client.search(request)
            context_chunks = []
            
            for result in response.results:
                data = result.document.derived_struct_data
                
                # 1. Intentar con snippets (Búsqueda no estructurada estándar)
                snippets = data.get('snippets', [])
                if snippets:
                    context_chunks.append(snippets[0].get('snippet', ""))
                
                # 2. Intentar con segmentos extractivos (PDFs largos)
                elif 'extractive_segments' in data:
                    segments = data.get('extractive_segments', [])
                    for seg in segments:
                        context_chunks.append(seg.get('content', ""))

                # 3. Fallback para datos estructurados o formatos inesperados
                else:
                    logger.info(f"ℹ️ Estructura de datos alternativa: {data.keys()}")
                    # Convertimos el diccionario a string como último recurso
                    context_chunks.append(str(data))
            
            context = "\n\n".join(context_chunks)
            logger.info(f"✅ Búsqueda finalizada. Chunks encontrados: {len(context_chunks)}")
            return context

        except exceptions.GoogleAPICallError as e:
            # Errores específicos de la API de Google (permisos, cuotas, 404, etc.)
            logger.error(f"❌ Error de API en Discovery Engine: {e}")
            return "" # Retornamos vacío para que Gemini use su conocimiento base

        except Exception as e:
            # Error genérico (problemas de red, errores de parseo, etc.)
            logger.exception(f"⚠️ Error inesperado en RAGService: {e}")
            return ""
    
