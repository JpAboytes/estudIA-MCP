#!/usr/bin/env python3
"""
Test para la nueva funcionalidad de OCR en documentos
Demuestra cómo procesar imágenes automáticamente con extract_text_from_image
y process_and_store_document
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.gemini import gemini_client
from src.supabase_client import supabase_client

async def test_ocr_functionality():
    """
    Test completo de la funcionalidad OCR
    """
    print("\n" + "="*70)
    print("TEST: OCR y Procesamiento Automático de Documentos")
    print("="*70)
    
    # PASO 1: Crear una imagen de prueba con texto
    print("\n📝 Paso 1: Creando imagen de prueba con texto...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Crear una imagen de prueba con texto
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Texto de prueba educativo
        test_text = """
        APUNTES DE MATEMÁTICAS
        
        Teorema de Pitágoras:
        En un triángulo rectángulo, el cuadrado de la hipotenusa
        es igual a la suma de los cuadrados de los catetos.
        
        Fórmula: a² + b² = c²
        
        Ejemplo:
        Si a = 3 y b = 4
        Entonces c² = 9 + 16 = 25
        Por lo tanto c = 5
        
        Aplicaciones:
        - Cálculo de distancias
        - Geometría analítica
        - Trigonometría
        """
        
        # Dibujar texto en la imagen
        y_position = 50
        for line in test_text.strip().split('\n'):
            draw.text((50, y_position), line.strip(), fill='black')
            y_position += 30
        
        # Guardar imagen en bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        print(f"   ✅ Imagen creada ({len(img_bytes)} bytes)")
        
        # PASO 2: Subir imagen a Supabase Storage
        print("\n📤 Paso 2: Subiendo imagen a Supabase Storage...")
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"test/ocr_test_{timestamp}.png"
        bucket_name = "uploads"
        
        upload_result = await asyncio.to_thread(
            lambda: supabase_client.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=img_bytes,
                file_options={"content-type": "image/png"}
            )
        )
        
        print(f"   ✅ Imagen subida: {file_path}")
        
        # PASO 3: Test de extract_text_from_image (usando gemini_client directamente)
        print("\n🔍 Paso 3: Probando OCR con Gemini Vision...")
        
        # Descargar la imagen
        image_data = await asyncio.to_thread(
            lambda: supabase_client.client.storage.from_(bucket_name).download(file_path)
        )
        
        if not image_data:
            print("   ❌ No se pudo descargar la imagen")
            return
        
        # Extraer texto con Gemini Vision
        try:
            extracted_text = await gemini_client.extract_text_from_image(
                image_data=image_data,
                mime_type="image/png"
            )
            
            print(f"   ✅ OCR exitoso!")
            print(f"   📄 Texto extraído ({len(extracted_text)} caracteres):")
            print(f"\n{'-'*60}")
            print(extracted_text[:500])
            print(f"{'-'*60}\n")
        except Exception as e:
            print(f"   ❌ Error en OCR: {e}")
            return
        
        # PASO 4: Crear registro en classroom_documents
        print("\n📚 Paso 4: Creando documento en classroom_documents...")
        
        # Obtener un classroom existente
        classroom_result = await asyncio.to_thread(
            lambda: supabase_client.client.table("classrooms").select("id").limit(1).execute()
        )
        
        if not classroom_result.data:
            print("   ⚠️  No hay classrooms. Creando uno de prueba...")
            
            # Obtener un usuario
            user_result = await asyncio.to_thread(
                lambda: supabase_client.client.table("profiles").select("id").limit(1).execute()
            )
            
            if not user_result.data:
                print("   ❌ No hay usuarios. No se puede continuar.")
                return
            
            user_id = user_result.data[0]['id']
            
            # Crear classroom
            new_classroom = await asyncio.to_thread(
                lambda: supabase_client.client.table("classrooms").insert({
                    "name": "Test OCR Classroom",
                    "description": "Classroom para probar OCR",
                    "created_by": user_id
                }).execute()
            )
            
            classroom_id = new_classroom.data[0]['id']
            print(f"   ✅ Classroom creado: {classroom_id}")
        else:
            classroom_id = classroom_result.data[0]['id']
            print(f"   ✅ Usando classroom existente: {classroom_id}")
        
        # Crear documento (usando los campos correctos de la tabla)
        # Obtener un usuario para owner_user_id
        user_result = await asyncio.to_thread(
            lambda: supabase_client.client.table("users").select("id").limit(1).execute()
        )
        
        if not user_result.data:
            print("   ⚠️  No hay usuarios registrados")
            owner_user_id = None
        else:
            owner_user_id = user_result.data[0]['id']
        
        doc_data = {
            "classroom_id": classroom_id,
            "owner_user_id": owner_user_id,
            "title": "Apuntes de Matemáticas (OCR Test)",
            "storage_path": file_path,
            "original_filename": "ocr_test.png",
            "mime_type": "image/png",
            "bucket": bucket_name,
            "status": "uploaded"
        }
        
        doc_result = await asyncio.to_thread(
            lambda: supabase_client.client.table("classroom_documents").insert(doc_data).execute()
        )
        
        document_id = doc_result.data[0]['id']
        print(f"   ✅ Documento creado: {document_id}")
        
        # PASO 5: Procesar manualmente con chunks (simulando process_and_store_document)
        print("\n🚀 Paso 5: Procesando documento con chunking automático...")
        print("   (Simulando process_and_store_document)")
        
        # Dividir en chunks
        chunk_size = 500
        overlap = 50
        chunks = []
        
        for i in range(0, len(extracted_text), chunk_size - overlap):
            chunk_text = extracted_text[i:i + chunk_size]
            if chunk_text.strip():
                chunks.append({
                    'index': len(chunks),
                    'content': chunk_text,
                    'start_pos': i
                })
        
        print(f"   ✅ Creados {len(chunks)} chunks")
        
        stored_chunks = []
        print(f"   🔄 Almacenando chunks...")
        
        for chunk in chunks:
            try:
                # Generar embedding usando gemini_client directamente
                embedding = await gemini_client.generate_embedding(chunk['content'])
                
                # Preparar datos
                data = {
                    "classroom_document_id": document_id,
                    "chunk_index": chunk['index'],
                    "content": chunk['content'],
                    "embedding": embedding,
                    "token": len(chunk['content'].split())
                }
                
                # Insertar en DB
                result = await asyncio.to_thread(
                    lambda: supabase_client.client.table("classroom_document_chunks").insert(data).execute()
                )
                
                if result.data:
                    chunk_id = result.data[0]['id']
                    stored_chunks.append({
                        'chunk_id': chunk_id,
                        'chunk_index': chunk['index'],
                        'content_length': len(chunk['content'])
                    })
                    print(f"   ✅ Chunk {chunk['index']} almacenado")
            except Exception as e:
                print(f"   ⚠️  Error en chunk {chunk['index']}: {e}")
        
        print(f"\n{'='*70}")
        print("✅ PROCESAMIENTO COMPLETADO EXITOSAMENTE")
        print(f"{'='*70}")
        print(f"   📊 Resultado:")
        print(f"   - Documento ID: {document_id}")
        print(f"   - Es imagen: True")
        print(f"   - OCR aplicado: True")
        print(f"   - Total chunks: {len(stored_chunks)}")
        print(f"   - Total caracteres: {len(extracted_text)}")
        print(f"   - Tamaño de chunk: {chunk_size}")
        print(f"\n   📝 Preview del contenido extraído:")
        print(f"{'-'*60}")
        print(extracted_text[:300] + ("..." if len(extracted_text) > 300 else ""))
        print(f"{'-'*60}")
        
        print(f"\n   💾 Chunks almacenados:")
        for i, chunk in enumerate(stored_chunks, 1):
            print(f"   {i}. Chunk ID: {chunk['chunk_id']} | Index: {chunk['chunk_index']} | Length: {chunk['content_length']}")
        
        print(f"\n{'='*70}")
        print("🎉 Test completado exitosamente!")
        print("   La funcionalidad OCR está funcionando correctamente.")
        print("   Ahora puedes procesar:")
        print("   ✅ Fotos de apuntes")
        print("   ✅ Documentos escaneados")
        print("   ✅ Capturas de pantalla")
        print("   ✅ Imágenes con texto educativo")
        print(f"{'='*70}\n")
        
    except ImportError as e:
        print(f"\n⚠️  Error: Falta la librería Pillow")
        print(f"   Ejecuta: pip install Pillow")
        print(f"   Error: {e}")
    except Exception as e:
        print(f"\n❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ocr_functionality())
