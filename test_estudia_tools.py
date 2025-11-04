#!/usr/bin/env python3
"""
Test de las herramientas de EstudIA MCP Server (NotebookLM)
"""

import asyncio
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from src.gemini import gemini_client
from src.supabase_client import supabase_client


async def test_generate_embedding():
    """Test de generación de embeddings"""
    print("\n" + "="*70)
    print("TEST 1: generate_embedding")
    print("="*70)
    
    print("\n📝 Test 1.1: Generar embedding de texto válido")
    text = "Introducción a la Inteligencia Artificial para estudiantes universitarios"
    
    try:
        embedding = await gemini_client.generate_embedding(text)
        
        print(f"\n✅ Resultado:")
        print(f"   Success: True")
        print(f"   Dimensiones: {len(embedding)}")
        print(f"   Modelo: {config.GEMINI_EMBED_MODEL}")
        print(f"   Vector (primeros 5): {embedding[:5]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n📝 Test 1.2: Texto vacío (debe fallar)")
    try:
        embedding = await gemini_client.generate_embedding("")
        print(f"   ⚠️  No falló como se esperaba")
    except Exception as e:
        print(f"   ✅ Error esperado: {type(e).__name__}")
    
    return True


async def test_store_document_chunk():
    """Test de almacenamiento de chunks"""
    print("\n" + "="*70)
    print("TEST 2: store_document_chunk")
    print("="*70)
    
    print("\n📝 Test 2.1: Almacenar chunk con embedding")
    text = ("La Inteligencia Artificial es una rama de la ciencia de la computación "
            "que se enfoca en crear sistemas capaces de realizar tareas que normalmente "
            "requieren inteligencia humana, como el reconocimiento de voz, la visión por "
            "computadora y la toma de decisiones.")
    
    # Nota: Necesitarás tener un classroom_document_id válido de tu base de datos
    # Este es un test de ejemplo, reemplaza con un ID real
    classroom_document_id = "0185c8b6-6774-4cd2-b0aa-76a018f072a7"  # UUID ejemplo
    
    try:
        # Paso 1: Generar embedding
        print("   🔄 Generando embedding...")
        embedding = await gemini_client.generate_embedding(text)
        print(f"   ✅ Embedding generado ({len(embedding)} dims)")
        
        # Paso 2: Preparar datos
        data = {
            "classroom_document_id": classroom_document_id,
            "chunk_index": 0,
            "content": text,
            "embedding": embedding
        }
        
        # Paso 3: Insertar en Supabase
        print("   💾 Insertando en Supabase (tabla: classroom_document_chunks)...")
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table("classroom_document_chunks").insert(data).execute()
        )
        
        if result.data:
            chunk_id = result.data[0]['id']
            print(f"\n✅ Chunk almacenado exitosamente")
            print(f"   Chunk ID: {chunk_id}")
            print(f"   Document ID: {classroom_document_id}")
            print(f"   Index: 0")
        else:
            print(f"   ⚠️  No se recibieron datos")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   Hint: Verifica que tengas un classroom_document_id válido")
        print(f"   O crea un documento primero en la tabla classroom_documents")
    
    return True


async def test_search_similar_chunks():
    """Test de búsqueda de chunks similares"""
    print("\n" + "="*70)
    print("TEST 3: search_similar_chunks")
    print("="*70)
    
    print("\n📝 Test 3.1: Búsqueda de chunks en un classroom")
    query = "¿Qué es la inteligencia artificial?"
    
    # Nota: Necesitarás tener un classroom_id válido de tu base de datos
    classroom_id = "e643da82-5a63-4de7-a29b-4e15a047ec4e"  # UUID ejemplo
    
    try:
        # Paso 1: Generar embedding del query
        print(f"   🔄 Generando embedding del query...")
        embedding = await gemini_client.generate_embedding(query)
        print(f"   ✅ Embedding generado ({len(embedding)} dims)")
        
        # Paso 2: Buscar chunks similares usando RPC
        print(f"   🔍 Buscando chunks (threshold={config.SIMILARITY_THRESHOLD})...")
        
        result = await asyncio.to_thread(
            lambda: supabase_client.client.rpc(
                'match_classroom_chunks',
                {
                    'query_embedding': embedding,
                    'filter_classroom_id': classroom_id,
                    'match_threshold': config.SIMILARITY_THRESHOLD,
                    'match_count': 5
                }
            ).execute()
        )
        
        chunks = result.data if result.data else []
        
        print(f"\n✅ Búsqueda completada")
        print(f"   Chunks encontrados: {len(chunks)}")
        print(f"   Query: {query}")
        print(f"   Classroom ID: {classroom_id}")
        
        if len(chunks) > 0:
            print(f"\n   📄 Primeros resultados:")
            for i, chunk in enumerate(chunks[:3], 1):
                print(f"      {i}. Chunk #{chunk.get('chunk_index', '?')}")
                print(f"         Similitud: {chunk.get('similarity', 0):.3f}")
                print(f"         Content preview: {chunk.get('content', '')[:80]}...")
        else:
            print(f"   ℹ️  No se encontraron chunks")
            print(f"   💡 Verifica que:")
            print(f"      - El classroom_id sea válido")
            print(f"      - Haya chunks insertados en ese classroom")
            print(f"      - La función RPC 'match_classroom_chunks' exista en Supabase")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   Hint: Verifica que la función RPC exista en Supabase")
    
    return True


async def main():
    """Ejecutar todos los tests"""
    print("\n" + "🧪"*35)
    print(" "*20 + "TEST SUITE: EstudIA MCP (NotebookLM)")
    print("🧪"*35 + "\n")
    
    try:
        # Test 1: Generate embedding
        await test_generate_embedding()
        
        # Test 2: Store chunk
        await test_store_document_chunk()
        
        # Test 3: Search similar chunks
        await test_search_similar_chunks()
        
        print("\n" + "="*70)
        print("✅ TESTS COMPLETADOS")
        print("="*70)
        print("\n💡 Notas importantes:")
        print("   - Reemplaza los UUIDs de ejemplo con IDs reales de tu base de datos")
        print("   - Asegúrate de tener:")
        print("     1. Un classroom creado en la tabla 'classrooms'")
        print("     2. Un documento en 'classroom_documents'")
        print("     3. La función RPC 'match_classroom_chunks' en Supabase")
        print("\n   - Para crear la función RPC, ejecuta este SQL en Supabase:")
        print("""
     CREATE OR REPLACE FUNCTION match_classroom_chunks(
       query_embedding vector(768),
       filter_classroom_id uuid,
       match_threshold float DEFAULT 0.6,
       match_count int DEFAULT 5
     )
     RETURNS TABLE (
       id bigint,
       classroom_document_id uuid,
       chunk_index int,
       content text,
       similarity float
     )
     LANGUAGE plpgsql
     AS $$
     BEGIN
       RETURN QUERY
       SELECT
         cdc.id,
         cdc.classroom_document_id,
         cdc.chunk_index,
         cdc.content,
         1 - (cdc.embedding <=> query_embedding) AS similarity
       FROM classroom_document_chunks cdc
       INNER JOIN classroom_documents cd ON cdc.classroom_document_id = cd.id
       WHERE cd.classroom_id = filter_classroom_id
         AND 1 - (cdc.embedding <=> query_embedding) > match_threshold
       ORDER BY similarity DESC
       LIMIT match_count;
     END;
     $$;
        """)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
