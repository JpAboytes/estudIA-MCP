#!/usr/bin/env python3
"""
Test para la función mejorada store_document_chunks
Ahora solo necesitas pasar el ID del documento y se hace todo automáticamente
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.main import _store_document_chunks_impl
from src.supabase_client import supabase_client

async def test_store_document_chunks():
    """
    Test de almacenamiento automático de chunks
    """
    print("\n" + "="*70)
    print("TEST: store_document_chunks - Versión mejorada")
    print("="*70)
    
    # PASO 1: Crear un documento de ejemplo en classroom_documents
    print("\n📝 Paso 1: Creando documento de prueba...")
    
    test_content = """
    La Inteligencia Artificial (IA) es una rama de la ciencia de la computación 
    que se enfoca en crear sistemas capaces de realizar tareas que normalmente 
    requieren inteligencia humana. Estas tareas incluyen el reconocimiento de voz, 
    la visión por computadora, la toma de decisiones, y la comprensión del lenguaje natural.
    
    El aprendizaje automático es un subcampo de la IA que permite a las computadoras 
    aprender y mejorar a partir de la experiencia sin ser explícitamente programadas. 
    Los algoritmos de aprendizaje automático pueden identificar patrones en datos y 
    hacer predicciones basadas en esos patrones.
    
    Las redes neuronales artificiales son modelos computacionales inspirados en el 
    funcionamiento del cerebro humano. Están compuestas por capas de nodos interconectados 
    que procesan información y pueden aprender a realizar tareas complejas como el 
    reconocimiento de imágenes y la traducción de idiomas.
    
    El procesamiento del lenguaje natural (PLN) es otra área importante de la IA que 
    se centra en la interacción entre computadoras y lenguaje humano. Los sistemas de 
    PLN pueden analizar, entender y generar texto de manera similar a como lo hacen 
    los humanos.
    """
    
    try:
        # Paso 1a: Subir el archivo de texto al Storage
        print("   🔄 Subiendo archivo a Supabase Storage...")
        
        # Nombre único para el archivo
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"test/chunks_test_{timestamp}.txt"
        
        # Subir archivo
        bucket_name = "uploads"  # Usar el bucket que existe
        file_bytes = test_content.strip().encode('utf-8')
        upload_result = await asyncio.to_thread(
            lambda: supabase_client.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": "text/plain"}
            )
        )
        
        print(f"   ✅ Archivo subido a Storage ({bucket_name}): {file_path}")
        
        # Paso 1b: Crear el registro en classroom_documents
        print("   🔄 Creando registro en classroom_documents...")
        
        # Necesitamos un classroom_id y owner_user_id válidos
        # Primero, obtengamos un classroom existente
        classroom_result = await asyncio.to_thread(
            lambda: supabase_client.client.table("classrooms").select("id").limit(1).execute()
        )
        
        if not classroom_result.data:
            print("   ⚠️  No hay classrooms en la BD. Creando uno...")
            # Obtener un user_id válido
            user_result = await asyncio.to_thread(
                lambda: supabase_client.client.table("profiles").select("id").limit(1).execute()
            )
            
            if not user_result.data:
                print("   ❌ No hay usuarios en la BD. No se puede continuar con el test.")
                return
            
            user_id = user_result.data[0]['id']
            
            # Crear un classroom de prueba
            classroom_data = {
                "name": "Test Classroom for Chunks",
                "description": "Classroom temporal para test de chunks",
                "created_by": user_id
            }
            
            new_classroom = await asyncio.to_thread(
                lambda: supabase_client.client.table("classrooms").insert(classroom_data).execute()
            )
            
            classroom_id = new_classroom.data[0]['id']
            owner_user_id = user_id
            print(f"   ✅ Classroom creado: {classroom_id}")
        else:
            classroom_id = classroom_result.data[0]['id']
            
            # Obtener el owner del classroom
            classroom_full = await asyncio.to_thread(
                lambda: supabase_client.client.table("classrooms").select("created_by").eq("id", classroom_id).single().execute()
            )
            owner_user_id = classroom_full.data['created_by']
        
        doc_data = {
            "classroom_id": classroom_id,
            "owner_user_id": owner_user_id,
            "bucket": bucket_name,
            "storage_path": file_path,
            "original_filename": f"chunks_test_{timestamp}.txt",
            "mime_type": "text/plain",
            "title": "Test AI Document - Chunks",
            "status": "uploaded"
        }
        
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table("classroom_documents").insert(doc_data).execute()
        )
        
        if not result.data:
            print("❌ Error: No se pudo crear el documento de prueba")
            return
        
        document_id = result.data[0]['id']
        print(f"✅ Documento creado con ID: {document_id}")
        print(f"   Contenido: {len(test_content)} caracteres")
        
        # PASO 2: Procesar el documento con la nueva función
        print("\n📦 Paso 2: Procesando documento con store_document_chunks...")
        print("   (Se dividirá automáticamente en chunks y se generarán embeddings)")
        
        chunk_result = await _store_document_chunks_impl(
            classroom_document_id=document_id,
            chunk_size=500,  # Chunks pequeños para este test
            chunk_overlap=100  # Overlap de 100 caracteres
        )
        
        if chunk_result.get("success"):
            print("\n✅ ¡Proceso completado exitosamente!")
            print(f"\n📊 Resultados:")
            print(f"   - Total de chunks creados: {chunk_result['total_chunks']}")
            print(f"   - Tamaño del documento: {chunk_result['document_length']} caracteres")
            print(f"   - Tamaño de chunk: {chunk_result['chunk_size']} caracteres")
            print(f"   - Overlap: {chunk_result['chunk_overlap']} caracteres")
            
            print(f"\n📝 Detalles de chunks:")
            for i, chunk in enumerate(chunk_result['chunks'], 1):
                print(f"   Chunk {i}:")
                print(f"      - ID: {chunk['chunk_id']}")
                print(f"      - Index: {chunk['chunk_index']}")
                print(f"      - Tamaño: {chunk['content_length']} caracteres")
        else:
            print(f"\n❌ Error: {chunk_result.get('error')}")
        
        # PASO 3: Verificar que los chunks se guardaron correctamente
        print("\n🔍 Paso 3: Verificando chunks en la base de datos...")
        
        verify_result = await asyncio.to_thread(
            lambda: supabase_client.client.table("classroom_document_chunks")
            .select("id, chunk_index, content")
            .eq("classroom_document_id", document_id)
            .order("chunk_index")
            .execute()
        )
        
        if verify_result.data:
            print(f"✅ Se encontraron {len(verify_result.data)} chunks en la base de datos")
            for chunk in verify_result.data:
                preview = chunk['content'][:100].replace('\n', ' ')
                print(f"   Chunk {chunk['chunk_index']}: {preview}...")
        else:
            print("⚠️  No se encontraron chunks en la base de datos")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETADO")
        print("="*70)
        
        # Cleanup opcional
        print("\n🧹 Información de limpieza:")
        print(f"   Document ID: {document_id}")
        print(f"   Storage Path: {file_path}")
        print(f"   Para limpiar manualmente, elimina:")
        print(f"   1. El registro en classroom_documents")
        print(f"   2. Los chunks en classroom_document_chunks")
        print(f"   3. El archivo en Storage")
        
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Iniciando test de store_document_chunks...")
    print("="*70)
    asyncio.run(test_store_document_chunks())
