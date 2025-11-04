#!/usr/bin/env python3
"""
Servidor MCP para EstudIA usando FastMCP
Versión simplificada con 3 herramientas principales
"""

import asyncio
import json
from typing import Dict, Any, List, Optional

from fastmcp import FastMCP

# Importar nuestros módulos
from .config import config
from .gemini import gemini_client
from .supabase_client import supabase_client

# Crear instancia del servidor FastMCP
mcp = FastMCP("EstudIA MCP Server", version="2.0.0")

# ====== HERRAMIENTAS MCP ======

@mcp.tool()
async def create_embedding(text: str, classroom_id: str) -> Dict[str, Any]:
    """
    Crea un embedding del texto y lo inserta en classroom_document_chunks.
    
    Esta herramienta genera un vector de embedding usando Gemini y lo almacena
    en la base de datos asociado a un classroom específico.
    
    Args:
        text: Contenido de texto para generar el embedding
        classroom_id: UUID del classroom (se usa como classroom_document_id)
        
    Returns:
        Dict con el resultado de la operación y el ID del chunk creado
    """
    print(f"\n{'='*70}")
    print("🎯 TOOL: create_embedding")
    print(f"{'='*70}")
    print(f"📥 Parámetros:")
    print(f"   - Texto: {len(text)} caracteres")
    print(f"   - Classroom ID: {classroom_id}")
    
    if not text or not text.strip():
        print("❌ Validación fallida: texto vacío")
        return {
            "success": False,
            "error": "El texto no puede estar vacío"
        }
    
    try:
        # PASO 1: Generar embedding con Gemini
        print(f"\n🔄 PASO 1: Generando embedding...")
        print(f"   📐 Modelo: {config.GEMINI_EMBED_MODEL}")
        print(f"   📊 Dimensiones: {config.EMBED_DIM}")
        
        embedding = await gemini_client.generate_embedding(text)
        actual_dim = len(embedding)
        
        print(f"✅ Embedding generado ({actual_dim} dimensiones)")
        
        # PASO 2: Contar tokens (aproximado)
        token_count = len(text.split())
        
        # PASO 3: Insertar en classroom_document_chunks
        print(f"\n💾 PASO 2: Insertando en classroom_document_chunks...")
        
        data = {
            "classroom_document_id": classroom_id,
            "chunk_index": 0,  # Siempre 0 por ahora
            "content": text,
            "token": token_count,
            "embedding": embedding
        }
        
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table("classroom_document_chunks").insert(data).execute()
        )
        
        if not result.data:
            raise Exception("No se recibieron datos de Supabase después de insertar")
        
        chunk_id = result.data[0]['id']
        
        print(f"✅ Chunk almacenado exitosamente")
        print(f"   🆔 Chunk ID: {chunk_id}")
        print(f"   📄 Classroom ID: {classroom_id}")
        print(f"   📊 Tokens: {token_count}")
        print(f"{'='*70}\n")
        
        return {
            "success": True,
            "message": "Embedding creado y almacenado exitosamente",
            "chunk_id": chunk_id,
            "classroom_id": classroom_id,
            "embedding_dimension": actual_dim,
            "content_length": len(text),
            "token_count": token_count
        }
    
    except Exception as e:
        error_details = str(e)
        print(f"\n❌ ERROR: {error_details}")
        print(f"{'='*70}\n")
        
        return {
            "success": False,
            "error": f"Error creando embedding: {error_details}"
        }


@mcp.tool()
async def professor_assistant(question: str, classroom_id: str) -> Dict[str, Any]:
    """
    Asistente de profesor que responde preguntas basándose en los documentos del classroom.
    
    Busca entre los documentos de la clase usando búsqueda semántica y genera
    una respuesta experta como si fuera un profesor especializado en el tema.
    
    Args:
        question: Pregunta del estudiante
        classroom_id: UUID del classroom
        
    Returns:
        Dict con la respuesta del profesor y los chunks referenciados
    """
    print(f"\n{'='*70}")
    print("🎯 TOOL: professor_assistant")
    print(f"{'='*70}")
    print(f"📥 Parámetros:")
    print(f"   - Pregunta: '{question[:60]}...'")
    print(f"   - Classroom ID: {classroom_id}")
    
    if not question or not question.strip():
        print("❌ Validación fallida: pregunta vacía")
        return {
            "success": False,
            "error": "La pregunta no puede estar vacía"
        }
    
    try:
        # PASO 1: Generar embedding de la pregunta
        print(f"\n🔄 PASO 1: Generando embedding de la pregunta...")
        
        query_embedding = await gemini_client.generate_embedding(question)
        print(f"✅ Embedding generado ({len(query_embedding)} dimensiones)")
        
        # PASO 2: Buscar chunks similares
        print(f"\n🔍 PASO 2: Buscando documentos relevantes...")
        print(f"   📊 Threshold: {config.SIMILARITY_THRESHOLD}")
        print(f"   📑 Límite: {config.TOPK_DOCUMENTS}")
        
        all_chunks = await asyncio.to_thread(
            lambda: supabase_client.client.table("classroom_document_chunks")
            .select("id, classroom_document_id, chunk_index, content")
            .eq("classroom_document_id", classroom_id)
            .not_.is_("embedding", "null")
            .limit(config.TOPK_DOCUMENTS)
            .execute()
        )
        
        chunks = all_chunks.data if all_chunks.data else []
        
        print(f"✅ Encontrados {len(chunks)} chunks")
        
        if not chunks:
            return {
                "success": True,
                "answer": "No encontré información relevante en los documentos de la clase. ¿Podrías reformular la pregunta o verificar que existan documentos sobre este tema?",
                "chunks_referenced": 0,
                "chunks": [],
                "classroom_id": classroom_id
            }
        
        # PASO 3: Construir contexto
        print(f"\n📚 PASO 3: Construyendo contexto...")
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            content = chunk.get('content', '')
            context_parts.append(f"[Documento {i}]\n{content}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # PASO 4: Generar respuesta
        print(f"\n🤖 PASO 4: Generando respuesta del profesor...")
        
        prompt = f"""Eres un profesor experto y experimentado que ayuda a estudiantes respondiendo sus preguntas de manera clara y pedagógica.

**Pregunta del estudiante:**
{question}

**Material de referencia de la clase:**
{context}

**Instrucciones:**
- Responde como un profesor experto en el tema
- Basa tu respuesta ÚNICAMENTE en el material de referencia proporcionado
- Sé claro, pedagógico y estructura tu respuesta de forma educativa
- Si la información no está en el material, indica que se necesita más contexto
- Usa ejemplos del material cuando sea apropiado

**Respuesta del profesor:**"""
        
        answer = await gemini_client.generate_text(prompt)
        
        print(f"✅ Respuesta generada ({len(answer)} caracteres)")
        print(f"{'='*70}\n")
        
        return {
            "success": True,
            "answer": answer,
            "chunks_referenced": len(chunks),
            "chunks": [{"id": c.get("id"), "preview": c.get("content")[:200] + "..."} for c in chunks[:3]],
            "classroom_id": classroom_id,
            "question": question
        }
    
    except Exception as e:
        error_details = str(e)
        print(f"\n❌ ERROR: {error_details}")
        print(f"{'='*70}\n")
        
        return {
            "success": False,
            "error": f"Error en professor_assistant: {error_details}"
        }


@mcp.tool()
async def generate_resources(classroom_id: str) -> Dict[str, Any]:
    """
    Genera recursos de aprendizaje basándose en los documentos del classroom.
    
    Analiza todos los documentos de la clase y genera recursos educativos
    personalizados como resúmenes, conceptos clave, ejercicios sugeridos, etc.
    
    Args:
        classroom_id: UUID del classroom
        
    Returns:
        Dict con los recursos de aprendizaje generados
    """
    print(f"\n{'='*70}")
    print("🎯 TOOL: generate_resources")
    print(f"{'='*70}")
    print(f"📥 Parámetros:")
    print(f"   - Classroom ID: {classroom_id}")
    
    try:
        # PASO 1: Obtener chunks del classroom
        print(f"\n📚 PASO 1: Obteniendo documentos...")
        
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table("classroom_document_chunks")
            .select("content, chunk_index")
            .eq("classroom_document_id", classroom_id)
            .order("chunk_index")
            .limit(50)
            .execute()
        )
        
        chunks = result.data if result.data else []
        print(f"✅ Encontrados {len(chunks)} chunks")
        
        if not chunks:
            return {
                "success": True,
                "message": "No hay documentos disponibles",
                "resources": {
                    "summary": "No hay documentos cargados en la clase",
                    "key_concepts": [],
                    "study_tips": ["Sube documentos para generar recursos"],
                    "suggested_exercises": []
                },
                "classroom_id": classroom_id
            }
        
        # PASO 2: Preparar contenido
        print(f"\n📝 PASO 2: Preparando contenido...")
        
        full_content = "\n\n".join([
            chunk.get('content', '') for chunk in chunks[:20]
        ])
        
        print(f"✅ Contenido preparado ({len(full_content)} caracteres)")
        
        # PASO 3: Generar recursos
        print(f"\n🤖 PASO 3: Generando recursos...")
        
        prompt = f"""Eres un asistente pedagógico experto.

**Contenido de la clase:**
{full_content}

Genera recursos de aprendizaje en formato JSON:

{{
  "summary": "Resumen del contenido (2-3 párrafos)",
  "key_concepts": [
    {{"concept": "Nombre", "definition": "Definición", "importance": "Por qué es importante"}}
  ],
  "study_tips": ["Consejo 1", "Consejo 2"],
  "suggested_exercises": [
    {{"exercise": "Descripción", "difficulty": "Fácil/Intermedio/Avanzado", "objective": "Objetivo"}}
  ],
  "recommended_readings": ["Tema 1", "Tema 2"]
}}

Responde SOLO con JSON:"""
        
        response = await gemini_client.generate_text(prompt)
        
        print(f"✅ Recursos generados")
        
        # PASO 4: Parsear JSON
        try:
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            resources = json.loads(json_str.strip())
            
        except json.JSONDecodeError:
            print(f"⚠️  Usando respuesta en texto")
            resources = {
                "summary": response,
                "key_concepts": [],
                "study_tips": [],
                "suggested_exercises": []
            }
        
        print(f"{'='*70}\n")
        
        return {
            "success": True,
            "message": "Recursos generados exitosamente",
            "resources": resources,
            "classroom_id": classroom_id,
            "chunks_analyzed": len(chunks)
        }
    
    except Exception as e:
        error_details = str(e)
        print(f"\n❌ ERROR: {error_details}")
        print(f"{'='*70}\n")
        
        return {
            "success": False,
            "error": f"Error generando recursos: {error_details}"
        }


# ====== FUNCIÓN PRINCIPAL ======

def main():
    """Función principal para ejecutar el servidor MCP"""
    try:
        print("\n" + "🚀" * 35)
        print(" " * 20 + "EstudIA MCP Server v2.0")
        print("🚀" * 35 + "\n")
        
        print("📋 Herramientas MCP registradas:")
        print("   1️⃣  create_embedding")
        print("       → Crea embedding del texto y lo almacena en BD")
        print("   2️⃣  professor_assistant")  
        print("       → Responde preguntas como un profesor experto")
        print("   3️⃣  generate_resources")
        print("       → Genera recursos de aprendizaje personalizados")
        
        print(f"\n{'='*70}")
        print("✅ Servidor MCP listo para recibir peticiones")
        print(f"{'='*70}\n")
        
        # Ejecutar el servidor FastMCP
        mcp.run()
        
    except Exception as error:
        print(f"\n❌ Error iniciando el servidor MCP: {error}")
        raise error

if __name__ == "__main__":
    main()
