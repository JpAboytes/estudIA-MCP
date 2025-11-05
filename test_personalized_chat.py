#!/usr/bin/env python3
"""
Script de prueba para chat_with_classroom_assistant con contexto de usuario
"""

import asyncio
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.main import ChatRequest, _chat_with_classroom_assistant_impl
from src.config import config
from src.supabase_client import supabase_client
from src.gemini import gemini_client

# Importar la implementación interna del chat
async def test_chat_with_user_context():
    """
    Probar el chat con contexto de usuario personalizado
    """
    
    print("="*70)
    print("🧪 TEST: Chat con Contexto de Usuario")
    print("="*70)
    
    try:
        # PASO 1: Buscar un usuario con contexto
        print("\n📋 PASO 1: Buscando usuario con contexto...")
        
        users = await asyncio.to_thread(
            lambda: supabase_client.client.table('users')
            .select('id, name, user_context')
            .not_.is_('user_context', 'null')
            .limit(1)
            .execute()
        )
        
        if not users.data or len(users.data) == 0:
            print("⚠️  No hay usuarios con contexto. Buscando cualquier usuario...")
            users = await asyncio.to_thread(
                lambda: supabase_client.client.table('users')
                .select('id, name, user_context')
                .limit(1)
                .execute()
            )
        
        if not users.data or len(users.data) == 0:
            print("❌ No se encontraron usuarios en la base de datos")
            return
        
        user = users.data[0]
        user_id = user['id']
        user_name = user.get('name', 'Usuario')
        user_context = user.get('user_context', '')
        
        print(f"✅ Usuario encontrado: {user_name}")
        print(f"   ID: {user_id}")
        if user_context:
            print(f"   📝 Contexto: {user_context[:150]}...")
        else:
            print(f"   ⚠️  Sin contexto personalizado")
        
        # PASO 2: Buscar un classroom con documentos
        print(f"\n📚 PASO 2: Buscando classroom con documentos...")
        
        classrooms = await asyncio.to_thread(
            lambda: supabase_client.client.table('classroom_documents')
            .select('classroom_id')
            .eq('embedding_ready', True)
            .limit(1)
            .execute()
        )
        
        if not classrooms.data or len(classrooms.data) == 0:
            print("❌ No se encontraron classrooms con documentos")
            print("   💡 Sube documentos a un classroom primero")
            return
        
        classroom_id = classrooms.data[0]['classroom_id']
        print(f"✅ Classroom encontrado: {classroom_id}")
        
        # PASO 3: Hacer preguntas de prueba
        print(f"\n💬 PASO 3: Probando chat con diferentes preguntas...")
        print("="*70)
        
        test_questions = [
            "¿Qué temas principales se cubren en este curso?",
            "Explícame el concepto más importante de este material",
            "¿Podrías darme ejemplos prácticos de lo que estamos estudiando?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*70}")
            print(f"PREGUNTA {i}: {question}")
            print(f"{'='*70}")
            
            # Crear request
            request = ChatRequest(
                message=question,
                classroom_id=classroom_id,
                user_id=user_id,
                session_id=None
            )
            
            # Llamar al chat
            result = await _chat_with_classroom_assistant_impl(request)
            
            if result.get('success'):
                data = result.get('data', {})
                response = data.get('response', '')
                chunks_ref = data.get('chunks_referenced', 0)
                personalized = data.get('personalized', False)
                documents = data.get('documents', [])
                document_ids = data.get('document_ids', [])
                
                print(f"\n✅ RESPUESTA {'PERSONALIZADA' if personalized else 'ESTÁNDAR'}:")
                print(f"{'='*70}")
                print(response[:500] + ("..." if len(response) > 500 else ""))
                
                print(f"\n📊 ESTADÍSTICAS:")
                print(f"   - Chunks referenciados: {chunks_ref}")
                print(f"   - Documentos únicos: {len(document_ids)}")
                
                if personalized:
                    print(f"   🎯 Respuesta adaptada según el contexto del usuario")
                else:
                    print(f"   ℹ️  Respuesta sin personalización (usuario sin contexto)")
                
                # Mostrar información de documentos para preview
                if documents:
                    print(f"\n📄 DOCUMENTOS REFERENCIADOS (para preview):")
                    print(f"{'='*70}")
                    for i, doc in enumerate(documents, 1):
                        print(f"\n{i}. {doc['title']}")
                        print(f"   📎 ID: {doc['document_id']}")
                        print(f"   📂 Archivo: {doc['filename']}")
                        print(f"   📊 Relevancia: {doc['relevance_score']:.3f}")
                        print(f"   🔗 Storage: {doc['bucket']}/{doc['storage_path']}")
                        print(f"   📑 Chunks usados: {len(doc['chunks_used'])}")
                        if doc.get('description'):
                            print(f"   📝 Descripción: {doc['description'][:100]}...")
            else:
                print(f"❌ Error: {result.get('error', 'Desconocido')}")
            
            # Pausa entre preguntas
            if i < len(test_questions):
                print(f"\n⏸️  Esperando 2 segundos antes de la siguiente pregunta...")
                await asyncio.sleep(2)
        
        print(f"\n{'='*70}")
        print("✅ Prueba completada")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()


async def test_comparison_with_without_context():
    """
    Comparar respuestas con y sin contexto de usuario
    """
    
    print("\n" + "="*70)
    print("🔬 TEST: Comparación CON vs SIN Contexto de Usuario")
    print("="*70)
    
    try:
        # Buscar classroom
        classrooms = await asyncio.to_thread(
            lambda: supabase_client.client.table('classroom_documents')
            .select('classroom_id')
            .eq('embedding_ready', True)
            .limit(1)
            .execute()
        )
        
        if not classrooms.data:
            print("❌ No hay classrooms con documentos")
            return
        
        classroom_id = classrooms.data[0]['classroom_id']
        
        # Buscar usuario con contexto
        users = await asyncio.to_thread(
            lambda: supabase_client.client.table('users')
            .select('id, name, user_context')
            .not_.is_('user_context', 'null')
            .limit(1)
            .execute()
        )
        
        if not users.data:
            print("⚠️  No hay usuarios con contexto para comparar")
            return
        
        user_id = users.data[0]['id']
        user_name = users.data[0].get('name', 'Usuario')
        
        print(f"👤 Usuario: {user_name}")
        print(f"📚 Classroom: {classroom_id}")
        
        question = "Explícame este tema de forma clara"
        
        print(f"\n❓ Pregunta: {question}")
        print("="*70)
        
        # SIN contexto (user_id = None)
        print(f"\n1️⃣  RESPUESTA SIN CONTEXTO DE USUARIO:")
        print("-"*70)
        request_without = ChatRequest(
            message=question,
            classroom_id=classroom_id,
            user_id=None
        )
        result_without = await _chat_with_classroom_assistant_impl(request_without)
        if result_without.get('success'):
            print(result_without['data']['response'][:300] + "...")
        
        # CON contexto
        print(f"\n2️⃣  RESPUESTA CON CONTEXTO DE USUARIO:")
        print("-"*70)
        request_with = ChatRequest(
            message=question,
            classroom_id=classroom_id,
            user_id=user_id
        )
        result_with = await _chat_with_classroom_assistant_impl(request_with)
        if result_with.get('success'):
            print(result_with['data']['response'][:300] + "...")
            
        print(f"\n{'='*70}")
        print("🔍 ANÁLISIS:")
        print(f"   - Respuesta sin contexto: {len(result_without.get('data', {}).get('response', ''))} caracteres")
        print(f"   - Respuesta con contexto: {len(result_with.get('data', {}).get('response', ''))} caracteres")
        print(f"   - Personalizada: {result_with.get('data', {}).get('personalized', False)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Función principal"""
    print("\n🚀 Iniciando pruebas del chat personalizado...")
    
    # Test 1: Chat con contexto
    await test_chat_with_user_context()
    
    # Test 2: Comparación
    print("\n" + "="*70)
    await test_comparison_with_without_context()
    
    print("\n✅ Todas las pruebas completadas")

if __name__ == "__main__":
    asyncio.run(main())
