from vertexai.generative_models import Tool, FunctionDeclaration

calendar_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="consultar_disponibilidad",
            description="Consulta la disponibilidad del abogado en una fecha (YYYY-MM-DD).",
            parameters={
                "type": "object",
                "properties": {"fecha": {"type": "string", "description": "Fecha YYYY-MM-DD"}},
                "required": ["fecha"]
            },
        )
    ]
)