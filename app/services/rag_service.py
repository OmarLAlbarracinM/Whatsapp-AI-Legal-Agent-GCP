from google.cloud import discoveryengine_v1beta as discoveryengine
from app.core.config import settings

class RAGService:
    def __init__(self):
        # Usamos las variables centralizadas en settings
        self.project_id = settings.PROJECT_ID
        self.location = settings.LOCATION
        self.data_store_id = settings.DATA_STORE_ID
        self.client = discoveryengine.SearchServiceClient()

    def get_legal_context(self, query: str) -> str:
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

        response = self.client.search(request)
        
        context_chunks = []
        for result in response.results:
            data = result.document.derived_struct_data
            # Extraemos el snippet que Google generó del PDF legal
            snippet = data.get('snippets', [{}])[0].get('snippet', "")
            context_chunks.append(snippet)
            
        return "\n\n".join(context_chunks)