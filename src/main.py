#!/usr/bin/env python3
"""
Servidor MCP para EstudIA usando FastMCP
Sistema similar a NotebookLM para gestión de documentos educativos por aula
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Importar nuestros módulos
from .config import config
from .gemini import gemini_client
from .supabase_client import supabase_client

# Crear instancia del servidor FastMCP
mcp = FastMCP("EstudIA MCP Server", version="2.0.0")

# ====== MODELOS DE DATOS ======

class ChatRequest(BaseModel):
    """Modelo para solicitud de chat"""
    message: str = Field(..., description="Mensaje del usuario")
    classroom_id: str = Field(..., description="ID del aula/classroom")
    user_id: Optional[str] = Field(None, description="ID del usuario para mantener contexto")
    session_id: Optional[str] = Field(None, description="ID de sesión para el chat")

# ====== HERRAMIENTAS MCP ======

@mcp.tool()
async def generate_embedding(text: str) -> Dict[str, Any]:
    """
    Genera un embedding vector a partir de texto usando Google Gemini.
    
    Convierte texto en un vector numérico de alta dimensionalidad
    que captura el significado semántico del contenido.
    
    Args:
        text: El texto para convertir en embedding
        
    Returns:
        Dict con el embedding generado, dimensiones y metadata
    """
    print(f"\n{'='*60}")
    print("🎯 TOOL: generate_embedding")
    print(f"{'='*60}")
    print(f"📥 Input: {len(text) if text else 0} caracteres")
    
    if not text or not text.strip():
        print("❌ Validación fallida: texto vacío")
        return {
            "success": False,
            "error": "El texto no puede estar vacío"
        }
    
    try:
        print(f"🔄 Generando embedding con Gemini...")
        print(f"   📐 Modelo: {config.GEMINI_EMBED_MODEL}")
        print(f"   📊 Dimensiones: {config.EMBED_DIM}")
        
        # Generar embedding usando el cliente existente
        embedding = await gemini_client.generate_embedding(text)
        actual_dim = len(embedding)
        
        print(f"✅ Embedding generado exitosamente ({actual_dim} dims)")
        
        return {
            "success": True,
            "embedding": embedding,
            "dimension": actual_dim,
            "text_length": len(text),
            "model": config.GEMINI_EMBED_MODEL,
            "text_preview": text[:100] + ("..." if len(text) > 100 else "")
        }
    
    except Exception as e:
        error_details = str(e)
        print(f"❌ ERROR generando embedding: {error_details}")
        
        return {
            "success": False,
            "error": f"Error generando embedding: {error_details}"
        }


@mcp.tool()
async def store_document_chunk(
    classroom_document_id: str,
    chunk_index: int,
    content: str,
    token_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    Almacena un chunk/fragmento de documento con su embedding en classroom_document_chunks.
    
    Esta función debe usarse después de subir un documento a classroom_documents.
    El documento se divide en chunks para búsqueda semántica eficiente.
    
    Args:
        classroom_document_id: UUID del documento en classroom_documents
        chunk_index: Índice del chunk (0, 1, 2, ...)
        content: Contenido de texto del chunk
        token_count: Número de tokens del chunk (opcional)
        
    Returns:
        Dict con el resultado de la operación y el ID del chunk creado
    """
    print(f"\n{'='*60}")
    print("🎯 TOOL: store_document_chunk")
    print(f"{'='*60}")
    print(f"📥 Parámetros:")
    print(f"   - classroom_document_id: {classroom_document_id}")
    print(f"   - chunk_index: {chunk_index}")
    print(f"   - content length: {len(content)} caracteres")
    print(f"   - token_count: {token_count or 'auto'}")
    
    # Paso 1: Generar embedding del chunk
    print("   🔄 PASO 1: Generando embedding del chunk...")
    embedding_result = await generate_embedding(content)
    
    if not embedding_result.get("success"):
        print(f"   ❌ Fallo al generar embedding")
        return embedding_result
    
    print(f"   ✅ Embedding generado ({embedding_result.get('dimension')} dims)")
    
    try:
        # Paso 2: Preparar datos para insertar
        print("   🔄 PASO 2: Preparando datos para Supabase...")
        data = {
            "classroom_document_id": classroom_document_id,
            "chunk_index": chunk_index,
            "content": content,
            "embedding": embedding_result["embedding"]
        }
        
        if token_count is not None:
            data["token"] = token_count
        
        # Paso 3: Insertar en Supabase
        print(f"   💾 PASO 3: Insertando en tabla 'classroom_document_chunks'...")
        
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table("classroom_document_chunks").insert(data).execute()
        )
        
        print(f"   ✅ INSERT ejecutado exitosamente")
        
        if not result.data:
            raise Exception("No se recibieron datos de Supabase después de insertar")
        
        chunk_id = result.data[0]['id']
        
        print(f"✅ Chunk almacenado exitosamente")
        print(f"   🆔 Chunk ID: {chunk_id}")
        print(f"   📄 Document ID: {classroom_document_id}")
        print(f"   #️⃣  Index: {chunk_index}")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": "Chunk almacenado exitosamente",
            "chunk_id": chunk_id,
            "classroom_document_id": classroom_document_id,
            "chunk_index": chunk_index,
            "embedding_dimension": embedding_result["dimension"],
            "content_length": len(content)
        }
    
    except Exception as e:
        error_details = str(e)
        print(f"\n❌ ERROR almacenando chunk: {error_details}")
        
        return {
            "success": False,
            "error": f"Error almacenando chunk: {error_details}"
        }


@mcp.tool()
async def search_similar_chunks(
    query_text: str,
    classroom_id: str,
    limit: int = 5,
    threshold: Optional[float] = None
) -> Dict[str, Any]:
    """
    Busca chunks/fragmentos de documentos similares usando búsqueda semántica por embeddings.
    
    Genera un embedding del query y busca los chunks más similares
    SOLO dentro del classroom especificado usando distancia coseno.
    
    Args:
        query_text: Texto de consulta para buscar chunks similares
        classroom_id: UUID del classroom para filtrar (OBLIGATORIO)
        limit: Número máximo de resultados (default: 5)
        threshold: Umbral mínimo de similitud 0-1 (default: 0.6 desde config)
        
    Returns:
        Dict con los chunks similares encontrados y metadata
    """
    print(f"\n{'='*60}")
    print("🎯 TOOL: search_similar_chunks")
    print(f"{'='*60}")
    print(f"📥 Parámetros:")
    print(f"   - Query: '{query_text[:50]}...'")
    print(f"   - classroom_id: {classroom_id}")
    print(f"   - limit: {limit}")
    print(f"   - threshold: {threshold or config.SIMILARITY_THRESHOLD}")
    
    # Usar threshold de config si no se proporciona
    if threshold is None:
        threshold = config.SIMILARITY_THRESHOLD
    
    print(f"\n🔍 Iniciando búsqueda en classroom {classroom_id}...")
    
    # Paso 1: Generar embedding del query
    print("   🔄 PASO 1: Generando embedding del query...")
    embedding_result = await generate_embedding(query_text)
    
    if not embedding_result.get("success"):
        print(f"   ❌ Fallo al generar embedding")
        return embedding_result
    
    print(f"   ✅ Embedding del query generado ({embedding_result.get('dimension')} dims)")
    
    try:
        # Paso 2: Buscar chunks usando función RPC
        print(f"   🔄 PASO 2: Buscando chunks en Supabase...")
        print(f"   📞 Usando match_classroom_chunks RPC")
        
        # Llamar función RPC de Supabase para búsqueda semántica
        result = await asyncio.to_thread(
            lambda: supabase_client.client.rpc(
                'match_classroom_chunks',
                {
                    'query_embedding': embedding_result["embedding"],
                    'filter_classroom_id': classroom_id,
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()
        )
        
        print(f"   ✅ RPC ejecutado")
        chunks = result.data if result.data else []
        count = len(chunks)
        
        print(f"✅ Búsqueda completada: {count} chunks encontrados")
        if count > 0:
            print(f"   📄 Chunk IDs: {[chunk.get('id') for chunk in chunks[:3]]}")
            print(f"   📊 Similitudes: {[round(chunk.get('similarity', 0), 3) for chunk in chunks[:3]]}")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "query": query_text,
            "classroom_id": classroom_id,
            "results": chunks,
            "count": count,
            "threshold_used": threshold,
            "embedding_dimension": embedding_result["dimension"]
        }
    
    except Exception as e:
        error_details = str(e)
        print(f"\n❌ ERROR en búsqueda: {error_details}")
        
        hint = "Verifica que la función RPC 'match_classroom_chunks' exista en Supabase"
        if "function" in error_details.lower() and "does not exist" in error_details.lower():
            hint = "La función match_classroom_chunks no existe. Debes crearla en Supabase."
        
        print(f"   💡 {hint}")
        print(f"{'='*60}\n")
        
        return {
            "success": False,
            "error": f"Error en búsqueda: {error_details}",
            "hint": hint
        }


@mcp.tool()
async def chat_with_classroom_assistant(request: ChatRequest) -> Dict[str, Any]:
    """
    Chat con el asistente de EstudIA especializado en los documentos del aula.
    
    Proporciona respuestas contextualizadas basándose en los documentos
    subidos al classroom específico. Similar a NotebookLM.
    
    Args:
        request: Objeto con message, classroom_id, user_id opcional y session_id opcional
    
    Returns:
        Dict con la respuesta del asistente y los chunks referenciados
    """
    try:
        print(f"\n{'='*60}")
        print("💬 Chat con asistente de classroom")
        print(f"{'='*60}")
        print(f"   - Message: {request.message[:50]}...")
        print(f"   - Classroom ID: {request.classroom_id}")
        print(f"   - User ID: {request.user_id or 'Anonymous'}")
        
        # Generar embedding para encontrar chunks relevantes
        embedding = await gemini_client.generate_embedding(request.message)
        
        # Buscar chunks relevantes en el classroom
        search_result = await search_similar_chunks(
            query_text=request.message,
            classroom_id=request.classroom_id,
            limit=5,
            threshold=0.5
        )
        
        relevant_chunks = search_result.get('results', []) if search_result.get('success') else []
        
        print(f"   📚 Chunks encontrados: {len(relevant_chunks)}")
        
        # Construir contexto con los chunks
        context_blocks = []
        for i, chunk in enumerate(relevant_chunks, start=1):
            content = chunk.get('content', '')
            doc_id = chunk.get('classroom_document_id', 'Unknown')
            chunk_idx = chunk.get('chunk_index', 0)
            similarity = chunk.get('similarity', 0)
            
            block = f"[Chunk {i} - Doc: {doc_id}, Index: {chunk_idx}, Similitud: {similarity:.3f}]\n{content}"
            context_blocks.append(block)
        
        context = "\n\n---\n\n".join(context_blocks) if context_blocks else "No se encontraron documentos relevantes."
        
        # Obtener respuesta del asistente con contexto
        print(f"   🤖 Generando respuesta con Gemini...")
        
        prompt = f"""Eres un asistente educativo que ayuda a estudiantes respondiendo preguntas basándote en los documentos de su aula.

**Pregunta del estudiante:**
{request.message}

**Documentos relevantes del aula:**
{context}

**Instrucciones:**
- Responde basándote ÚNICAMENTE en la información de los documentos proporcionados
- Si la información no está en los documentos, indícalo claramente
- Sé claro, conciso y educativo
- Cita específicamente qué chunk/documento usaste si es relevante
- Si no hay documentos relevantes, sugiere reformular la pregunta o subir documentos sobre el tema
"""
        
        # Generar respuesta con Gemini
        response = await gemini_client.generate_text(prompt)
        
        print(f"   ✅ Respuesta generada")
        print(f"{'='*60}\n")
        
        return {
            'success': True,
            'data': {
                'response': response,
                'chunks_referenced': len(relevant_chunks),
                'chunks': relevant_chunks[:3],  # Solo las 3 más relevantes
                'classroom_id': request.classroom_id
            },
            'message': "Respuesta del asistente generada"
        }
        
    except Exception as error:
        print(f"❌ Error en chat: {error}")
        return {
            'success': False,
            'error': str(error),
            'message': "Error en el chat con el asistente"
        }


@mcp.tool()
async def get_classroom_info(classroom_id: str) -> Dict[str, Any]:
    """
    Obtener información del classroom y sus documentos.
    
    Args:
        classroom_id: UUID del classroom
    
    Returns:
        Dict con información del classroom y estadísticas
    """
    try:
        # Obtener información del classroom
        classroom = await asyncio.to_thread(
            lambda: supabase_client.client.table('classrooms')
            .select('*')
            .eq('id', classroom_id)
            .single()
            .execute()
        )
        
        if not classroom.data:
            return {
                'success': False,
                'error': 'Classroom no encontrado',
                'message': f'No se encontró el classroom {classroom_id}'
            }
        
        # Obtener documentos del classroom
        documents = await asyncio.to_thread(
            lambda: supabase_client.client.table('classroom_documents')
            .select('id, title, description, status, chunk_count, created_at')
            .eq('classroom_id', classroom_id)
            .execute()
        )
        
        docs_data = documents.data if documents.data else []
        total_chunks = sum(doc.get('chunk_count', 0) for doc in docs_data)
        
        return {
            'success': True,
            'data': {
                'classroom': classroom.data,
                'documents': docs_data,
                'stats': {
                    'total_documents': len(docs_data),
                    'total_chunks': total_chunks,
                    'ready_documents': len([d for d in docs_data if d.get('embedding_ready')]),
                }
            },
            'message': f'Información del classroom {classroom.data.get("name", classroom_id)}'
        }
        
    except Exception as error:
        return {
            'success': False,
            'error': str(error),
            'message': 'Error obteniendo información del classroom'
        }


# ====== FUNCIÓN PRINCIPAL ======

def main():
    """Función principal para ejecutar el servidor MCP"""
    try:
        print("🚀 Iniciando EstudIA MCP Server con FastMCP...")
        print("📋 Herramientas registradas:")
        print("   ✅ generate_embedding - Generar embeddings de texto")
        print("   ✅ store_document_chunk - Almacenar chunk con embedding")
        print("   ✅ search_similar_chunks - Buscar chunks similares en classroom")
        print("   ✅ chat_with_classroom_assistant - Chat con asistente del aula")
        print("   ✅ get_classroom_info - Información del classroom")
        print("🎯 Servidor MCP listo para recibir peticiones...")
        
        # Ejecutar el servidor FastMCP
        mcp.run()
        
    except Exception as error:
        print(f"❌ Error iniciando el servidor MCP: {error}")
        raise error

if __name__ == "__main__":
    main()
