#!/usr/bin/env python3
"""
Test completo de EstudIA MCP Server
Prueba las funciones base (NO las herramientas MCP)

Las herramientas MCP (@mcp.tool) solo funcionan cuando el servidor está corriendo
y son llamadas por Claude/IA. Este script prueba las funciones reales.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from src.gemini import gemini_client
from src.supabase_client import supabase_client


def print_header(title: str):
    """Imprime un header visual"""
    print("\n" + "="*80)
    print(f"🧪 {title}")
    print("="*80 + "\n")


def print_result(success: bool, message: str):
    """Imprime el resultado de un test"""
    icon = "✅" if success else "❌"
    print(f"\n{icon} {message}\n")


async def test_1_generate_embedding():
    """Test 1: Generar embedding de texto"""
    print_header("TEST 1: generate_embedding")
    
    try:
        text = "La inteligencia artificial es una rama de la informática que busca crear sistemas inteligentes."
        print(f"📝 Texto a procesar: '{text[:60]}...'")
        
        # Generar embedding
        embedding = await gemini_client.generate_embedding(text)
        
        print_result(True, f"Embedding generado: {len(embedding)} dimensiones")
        return embedding
        
    except Exception as e:
        print_result(False, f"Error: {e}")
        return None


async def test_2_get_classroom_id():
    """Test 2: Obtener un classroom_id válido de la base de datos"""
    print_header("TEST 2: Obtener classroom_id")
    
    try:
        print("🔍 Buscando classrooms en la base de datos...")
        
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table('classrooms')
            .select('id, name, subject')
            .limit(1)
            .execute()
        )
        
        if result.data and len(result.data) > 0:
            classroom = result.data[0]
            classroom_id = classroom['id']
            classroom_name = classroom.get('name', 'Sin nombre')
            
            print_result(True, f"Classroom encontrado: '{classroom_name}' (ID: {classroom_id})")
            return classroom_id
        else:
            print_result(False, "No hay classrooms en la base de datos")
            print("💡 Crea uno primero con:")
            print("   INSERT INTO classrooms (name, subject, code) VALUES ('Test', 'Prueba', 'TEST-001');")
            return None
            
    except Exception as e:
        print_result(False, f"Error: {e}")
        return None


async def test_3_get_document_id(classroom_id: str):
    """Test 3: Obtener un document_id válido"""
    print_header("TEST 3: Obtener document_id")
    
    try:
        print(f"🔍 Buscando documentos en classroom {classroom_id}...")
        
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table('classroom_documents')
            .select('id, title')
            .eq('classroom_id', classroom_id)
            .limit(1)
            .execute()
        )
        
        if result.data and len(result.data) > 0:
            doc = result.data[0]
            doc_id = doc['id']
            doc_title = doc.get('title', 'Sin título')
            
            print_result(True, f"Documento encontrado: '{doc_title}' (ID: {doc_id})")
            return doc_id
        else:
            print_result(False, "No hay documentos en este classroom")
            print("💡 Será necesario crear uno para el test de store_document_chunk")
            return None
            
    except Exception as e:
        print_result(False, f"Error: {e}")
        return None


async def test_4_store_document_chunk(classroom_id: str):
    """Test 4: Almacenar un chunk con embedding"""
    print_header("TEST 4: store_document_chunk")
    
    try:
        # Obtener un usuario real de la base de datos
        print("👤 Obteniendo usuario válido...")
        user_result = await asyncio.to_thread(
            lambda: supabase_client.client.table('users')
            .select('id')
            .limit(1)
            .execute()
        )
        
        if not user_result.data or len(user_result.data) == 0:
            print_result(False, "No hay usuarios en la tabla users. Crea uno primero.")
            return False
        
        owner_user_id = user_result.data[0]['id']
        print(f"✅ Usuario encontrado: {owner_user_id}")
        
        # Crear documento de prueba
        print("\n📄 Creando documento de prueba...")
        
        doc_data = {
            "classroom_id": classroom_id,
            "owner_user_id": owner_user_id,
            "storage_path": f"test/doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "title": "Documento de prueba - EstudIA",
            "original_filename": "test_doc.txt",
            "status": "processing"
        }
        
        doc_result = await asyncio.to_thread(
            lambda: supabase_client.client.table('classroom_documents')
            .insert(doc_data)
            .execute()
        )
        
        if not doc_result.data:
            print_result(False, "No se pudo crear el documento de prueba")
            return False
        
        document_id = doc_result.data[0]['id']
        print(f"✅ Documento creado: {document_id}")
        
        # Ahora almacenar chunks
        chunks = [
            "Las redes neuronales artificiales son modelos computacionales inspirados en el cerebro humano.",
            "El aprendizaje supervisado requiere datos etiquetados para entrenar modelos.",
            "Los algoritmos de clustering agrupan datos similares sin supervisión previa."
        ]
        
        print(f"\n📦 Almacenando {len(chunks)} chunks...")
        
        for i, chunk_content in enumerate(chunks):
            print(f"\n   Chunk {i+1}/{len(chunks)}: '{chunk_content[:50]}...'")
            
            # Generar embedding
            embedding = await gemini_client.generate_embedding(chunk_content)
            
            # Insertar chunk
            chunk_data = {
                "classroom_document_id": document_id,
                "chunk_index": i,
                "content": chunk_content,
                "embedding": embedding,
                "token": len(chunk_content.split())
            }
            
            chunk_result = await asyncio.to_thread(
                lambda cd=chunk_data: supabase_client.client.table('classroom_document_chunks')
                .insert(cd)
                .execute()
            )
            
            if chunk_result.data:
                chunk_id = chunk_result.data[0]['id']
                print(f"   ✅ Chunk almacenado: ID {chunk_id}")
        
        # Actualizar documento
        await asyncio.to_thread(
            lambda: supabase_client.client.table('classroom_documents')
            .update({
                "status": "ready",
                "embedding_ready": True,
                "chunk_count": len(chunks)
            })
            .eq('id', document_id)
            .execute()
        )
        
        print_result(True, f"Documento procesado con {len(chunks)} chunks")
        return True
        
    except Exception as e:
        print_result(False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_5_search_similar_chunks(classroom_id: str):
    """Test 5: Buscar chunks similares"""
    print_header("TEST 5: search_similar_chunks")
    
    try:
        queries = [
            "¿Qué son las redes neuronales?",
            "Explícame el aprendizaje supervisado",
            "¿Cómo funciona el clustering?"
        ]
        
        for query in queries:
            print(f"\n🔍 Query: '{query}'")
            
            # Generar embedding
            embedding = await gemini_client.generate_embedding(query)
            
            # Buscar usando RPC
            result = await asyncio.to_thread(
                lambda: supabase_client.client.rpc(
                    'match_classroom_chunks',
                    {
                        'query_embedding': embedding,
                        'filter_classroom_id': classroom_id,
                        'match_threshold': 0.5,
                        'match_count': 3
                    }
                ).execute()
            )
            
            chunks = result.data if result.data else []
            
            if chunks:
                print(f"   ✅ Encontrados {len(chunks)} chunks:")
                for i, chunk in enumerate(chunks, 1):
                    similarity = chunk.get('similarity', 0)
                    content = chunk.get('content', '')
                    print(f"      {i}. Similitud: {similarity:.3f} - '{content[:60]}...'")
            else:
                print(f"   ⚠️  No se encontraron chunks (puede ser que similarity < 0.5)")
        
        print_result(True, "Búsqueda semántica completada")
        return True
        
    except Exception as e:
        print_result(False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_6_get_classroom_info(classroom_id: str):
    """Test 6: Obtener información del classroom"""
    print_header("TEST 6: get_classroom_info")
    
    try:
        print(f"📊 Obteniendo información de classroom {classroom_id}...")
        
        # Obtener classroom
        classroom = await asyncio.to_thread(
            lambda: supabase_client.client.table('classrooms')
            .select('*')
            .eq('id', classroom_id)
            .single()
            .execute()
        )
        
        if not classroom.data:
            print_result(False, "Classroom no encontrado")
            return False
        
        # Obtener documentos
        documents = await asyncio.to_thread(
            lambda: supabase_client.client.table('classroom_documents')
            .select('id, title, status, chunk_count, embedding_ready')
            .eq('classroom_id', classroom_id)
            .execute()
        )
        
        docs = documents.data if documents.data else []
        total_chunks = sum(doc.get('chunk_count', 0) for doc in docs)
        ready_docs = len([d for d in docs if d.get('embedding_ready')])
        
        print(f"\n📋 Información del classroom:")
        print(f"   Nombre: {classroom.data.get('name')}")
        print(f"   Materia: {classroom.data.get('subject')}")
        print(f"   Código: {classroom.data.get('code')}")
        print(f"\n📊 Estadísticas:")
        print(f"   Total documentos: {len(docs)}")
        print(f"   Documentos listos: {ready_docs}")
        print(f"   Total chunks: {total_chunks}")
        
        if len(docs) > 0:
            print(f"\n📄 Documentos:")
            for doc in docs[:5]:  # Mostrar máximo 5
                status_icon = "✅" if doc.get('embedding_ready') else "⏳"
                title = doc.get('title', 'Sin título')
                chunks = doc.get('chunk_count', 0)
                print(f"   {status_icon} {title} ({chunks} chunks)")
        
        print_result(True, "Información obtenida correctamente")
        return True
        
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


async def main():
    """Ejecutar todos los tests"""
    print("\n" + "🎯"*40)
    print(" "*30 + "ESTUDIA MCP SERVER - TEST COMPLETO")
    print("🎯"*40 + "\n")
    
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Configuración:")
    print(f"   - Modelo: {config.GEMINI_MODEL}")
    print(f"   - Embeddings: {config.GEMINI_EMBED_MODEL} ({config.EMBED_DIM} dims)")
    print(f"   - Threshold: {config.SIMILARITY_THRESHOLD}")
    
    try:
        # Test 1: Generar embedding
        embedding = await test_1_generate_embedding()
        if not embedding:
            print("⚠️  No se pudo continuar sin embeddings")
            return
        
        await asyncio.sleep(1)
        
        # Test 2: Obtener classroom
        classroom_id = await test_2_get_classroom_id()
        if not classroom_id:
            print("⚠️  No se puede continuar sin un classroom")
            return
        
        await asyncio.sleep(1)
        
        # Test 3: Obtener document (opcional)
        document_id = await test_3_get_document_id(classroom_id)
        
        await asyncio.sleep(1)
        
        # Test 4: Store document chunk
        await test_4_store_document_chunk(classroom_id)
        
        await asyncio.sleep(1)
        
        # Test 5: Search similar chunks
        await test_5_search_similar_chunks(classroom_id)
        
        await asyncio.sleep(1)
        
        # Test 6: Get classroom info
        await test_6_get_classroom_info(classroom_id)
        
        # Resumen final
        print("\n" + "="*80)
        print("✅ TESTS COMPLETADOS")
        print("="*80)
        print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
