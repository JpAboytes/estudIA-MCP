import os
from typing import Optional
from dotenv import load_dotenv
from fastmcp import FastMCP
import google.generativeai as genai
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

# Inicializar FastMCP
mcp = FastMCP("estudIA-MCP")

# Variables globales para clientes
supabase_client: Optional[Client] = None
gemini_model = None


def initialize_clients():
    """Inicializa los clientes de Supabase y Gemini"""
    global supabase_client, gemini_model
    
    # Configurar Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        supabase_client = create_client(supabase_url, supabase_key)
        print("✓ Supabase client initialized")
    else:
        print("⚠ Warning: SUPABASE_URL or SUPABASE_KEY not found in environment")
    
    # Configurar Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        # Usar el modelo de embeddings actualizado de Google Gemini
        gemini_model = "models/gemini-embedding-001"
        print("✓ Gemini API initialized")
        print(f"  Modelo: {gemini_model}")
    else:
        print("⚠ Warning: GEMINI_API_KEY not found in environment")


@mcp.tool()
def generate_embedding(text: str) -> dict:
    """
    Genera un embedding vector a partir de texto usando Google Gemini.
    
    Args:
        text: El texto para convertir en embedding
        
    Returns:
        Un diccionario con el embedding y metadata
    """
    if not gemini_model:
        return {
            "error": "Gemini API no está configurada. Verifica tu GEMINI_API_KEY"
        }
    
    try:
        # Generar embedding usando Gemini
        result = genai.embed_content(
            model=gemini_model,
            content=text,
            task_type="retrieval_document",
            output_dimensionality=768,
        )
        
        embedding = result['embedding']
        
        return {
            "success": True,
            "embedding": embedding,
            "dimension": len(embedding),
            "text_length": len(text),
            "model": gemini_model
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generando embedding: {str(e)}"
        }


@mcp.tool()
def store_document(text: str, classroom_id: str = None) -> dict:
    """
    Genera un embedding y lo almacena en la tabla documents de Supabase.
    
    Args:
        text: El texto del documento para convertir en embedding
        classroom_id: UUID del classroom al que pertenece el documento (opcional)
        
    Returns:
        Resultado de la operación
    """
    if not supabase_client:
        return {
            "error": "Supabase client no está configurado. Verifica SUPABASE_URL y SUPABASE_KEY"
        }
    
    # Generar embedding
    embedding_result = generate_embedding(text)
    
    if not embedding_result.get("success"):
        return embedding_result
    
    try:
        # Preparar datos para insertar
        data = {
            "content": text,
            "embedding": embedding_result["embedding"]
        }
        
        # Agregar classroom_id si se proporciona (debe ser UUID válido)
        if classroom_id is not None:
            data["classroom_id"] = classroom_id
        
        # Insertar en Supabase tabla documents
        result = supabase_client.table("documents").insert(data).execute()
        
        return {
            "success": True,
            "message": "Documento almacenado exitosamente",
            "document_id": result.data[0]["id"],
            "classroom_id": result.data[0].get("classroom_id"),
            "content_preview": text[:100] + "..." if len(text) > 100 else text
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error almacenando documento en Supabase: {str(e)}"
        }


@mcp.tool()
def search_similar_documents(
    query_text: str,
    classroom_id: str = None,
    limit: int = 5,
    threshold: float = 0.7
) -> dict:
    """
    Busca documentos similares usando búsqueda por similitud de embeddings.
    
    Args:
        query_text: Texto de consulta
        classroom_id: UUID del classroom para filtrar (opcional)
        limit: Número máximo de resultados (default: 5)
        threshold: Umbral mínimo de similitud 0-1 (default: 0.7)
        
    Returns:
        Documentos similares encontrados
    """
    if not supabase_client:
        return {
            "error": "Supabase client no está configurado"
        }
    
    # Generar embedding de la consulta
    embedding_result = generate_embedding(query_text)
    
    if not embedding_result.get("success"):
        return embedding_result
    
    try:
        # Si se proporciona classroom_id, usar la función optimizada
        if classroom_id is not None:
            result = supabase_client.rpc(
                'match_documents_by_classroom',
                {
                    'query_embedding': embedding_result["embedding"],
                    'match_threshold': threshold,
                    'match_count': limit,
                    'filter_classroom_id': classroom_id
                }
            ).execute()
            
            return {
                "success": True,
                "query": query_text,
                "classroom_id": classroom_id,
                "results": result.data if result.data else [],
                "count": len(result.data) if result.data else 0,
                "threshold_used": threshold
            }
        
        # Búsqueda general sin filtro de classroom
        result = supabase_client.rpc(
            'match_documents',
            {
                'query_embedding': embedding_result["embedding"],
                'match_threshold': threshold,
                'match_count': limit
            }
        ).execute()
        
        return {
            "success": True,
            "query": query_text,
            "results": result.data if result.data else [],
            "count": len(result.data) if result.data else 0,
            "threshold_used": threshold
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error en búsqueda: {str(e)}",
            "note": "Asegúrate de tener configuradas las funciones match_documents en Supabase"
        }


def main():
    """Punto de entrada principal"""
    initialize_clients()
    print("🚀 estudIA-MCP Server iniciado")
    print("📚 Tools disponibles:")
    print("  - generate_embedding: Genera embeddings desde texto")
    print("  - store_document: Almacena documentos con embeddings en Supabase")
    print("  - search_similar_documents: Búsqueda por similitud de documentos")
    mcp.run()


if __name__ == "__main__":
    main()
