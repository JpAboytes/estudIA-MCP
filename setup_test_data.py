#!/usr/bin/env python3
"""
Script para configurar datos de prueba en Supabase
Obtiene IDs reales y crea registros necesarios para testing
"""

import asyncio
import sys
from pathlib import Path
import uuid

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from src.supabase_client import supabase_client


async def setup_test_data():
    """Configurar datos de prueba"""
    print("\n" + "="*70)
    print("🔧 CONFIGURACIÓN DE DATOS DE PRUEBA")
    print("="*70)
    
    try:
        # 1. Obtener o crear un classroom
        print("\n📚 Paso 1: Verificando classrooms...")
        classrooms = await asyncio.to_thread(
            lambda: supabase_client.client.table('classrooms')
            .select('id, name, code')
            .limit(5)
            .execute()
        )
        
        if classrooms.data and len(classrooms.data) > 0:
            classroom = classrooms.data[0]
            classroom_id = classroom['id']
            print(f"   ✅ Classroom encontrado:")
            print(f"      ID: {classroom_id}")
            print(f"      Name: {classroom.get('name', 'N/A')}")
            print(f"      Code: {classroom.get('code', 'N/A')}")
        else:
            print("   ⚠️  No se encontraron classrooms")
            print("   💡 Crea un classroom primero desde tu aplicación")
            return None
        
        # 2. Obtener o crear un documento de prueba
        print("\n📄 Paso 2: Verificando classroom_documents...")
        documents = await asyncio.to_thread(
            lambda: supabase_client.client.table('classroom_documents')
            .select('id, title, classroom_id')
            .eq('classroom_id', classroom_id)
            .limit(5)
            .execute()
        )
        
        document_id = None
        
        if documents.data and len(documents.data) > 0:
            document = documents.data[0]
            document_id = document['id']
            print(f"   ✅ Documento encontrado:")
            print(f"      ID: {document_id}")
            print(f"      Title: {document.get('title', 'N/A')}")
        else:
            print("   ℹ️  No hay documentos en este classroom")
            print("   💡 Intentando crear un documento de prueba...")
            
            # Obtener el primer usuario para owner_user_id
            users = await asyncio.to_thread(
                lambda: supabase_client.client.table('users')
                .select('id')
                .limit(1)
                .execute()
            )
            
            if users.data and len(users.data) > 0:
                owner_id = users.data[0]['id']
                
                # Crear documento de prueba
                doc_data = {
                    'classroom_id': classroom_id,
                    'owner_user_id': owner_id,
                    'title': 'Documento de Prueba - Introducción a IA',
                    'description': 'Documento generado automáticamente para testing',
                    'status': 'ready',
                    'embedding_ready': True,
                    'chunk_count': 0,
                    'storage_path': 'test/intro-ia.pdf',
                    'original_filename': 'intro-ia.pdf'
                }
                
                result = await asyncio.to_thread(
                    lambda: supabase_client.client.table('classroom_documents')
                    .insert(doc_data)
                    .execute()
                )
                
                if result.data:
                    document_id = result.data[0]['id']
                    print(f"   ✅ Documento creado:")
                    print(f"      ID: {document_id}")
                else:
                    print("   ❌ No se pudo crear el documento")
                    return None
            else:
                print("   ❌ No se encontraron usuarios")
                print("   💡 Necesitas al menos un usuario en la tabla 'users'")
                return None
        
        # 3. Verificar chunks existentes
        print("\n🧩 Paso 3: Verificando chunks existentes...")
        chunks = await asyncio.to_thread(
            lambda: supabase_client.client.table('classroom_document_chunks')
            .select('id, chunk_index')
            .eq('classroom_document_id', document_id)
            .execute()
        )
        
        chunk_count = len(chunks.data) if chunks.data else 0
        print(f"   📊 Chunks existentes: {chunk_count}")
        
        # 4. Crear archivo de configuración para tests
        print("\n📝 Paso 4: Generando archivo de configuración...")
        
        config_content = f"""# Configuración de IDs para testing
# Generado automáticamente por setup_test_data.py

CLASSROOM_ID = "{classroom_id}"
DOCUMENT_ID = "{document_id}"

# Información adicional
CLASSROOM_NAME = "{classroom.get('name', 'N/A')}"
DOCUMENT_TITLE = "{document.get('title', 'N/A') if documents.data and len(documents.data) > 0 else 'Documento de Prueba - Introducción a IA'}"
EXISTING_CHUNKS = {chunk_count}
"""
        
        with open('test_config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("   ✅ Archivo 'test_config.py' creado")
        
        # 5. Mostrar resumen
        print("\n" + "="*70)
        print("✅ CONFIGURACIÓN COMPLETADA")
        print("="*70)
        print("\n📋 Datos disponibles para testing:")
        print(f"   • Classroom ID: {classroom_id}")
        print(f"   • Document ID: {document_id}")
        print(f"   • Chunks existentes: {chunk_count}")
        
        print("\n💡 Siguiente paso:")
        print("   Ejecuta: python test_with_real_data.py")
        print("   O importa estos IDs en tus tests:")
        print("   >>> from test_config import CLASSROOM_ID, DOCUMENT_ID")
        
        return {
            'classroom_id': classroom_id,
            'document_id': document_id,
            'chunk_count': chunk_count
        }
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Ejecutar configuración"""
    await setup_test_data()


if __name__ == "__main__":
    asyncio.run(main())
