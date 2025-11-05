#!/usr/bin/env python3
"""
Test script para validar source_document_ids en generate_resources
Prueba diferentes escenarios con documentos específicos
"""

import asyncio
from src.main import _generate_resources_impl
from src.supabase_client import supabase_client


async def get_classroom_documents(classroom_id: str):
    """Helper para obtener documentos de un classroom"""
    print(f"\n🔍 Obteniendo documentos del classroom {classroom_id}...")
    
    result = await asyncio.to_thread(
        lambda: supabase_client.client.table("classroom_documents")
        .select("id, title, original_filename")
        .eq("classroom_id", classroom_id)
        .limit(5)  # Solo primeros 5 para el test
        .execute()
    )
    
    docs = result.data if result.data else []
    print(f"✅ Encontrados {len(docs)} documentos:")
    for i, doc in enumerate(docs, 1):
        print(f"   {i}. {doc['title']} (ID: {doc['id'][:8]}...)")
    
    return docs


async def test_with_specific_documents():
    """
    Test 1: Generar recurso usando documentos específicos (válidos)
    """
    print("\n" + "="*80)
    print("TEST 1: Generar PDF con documentos específicos (VÁLIDOS)")
    print("="*80)
    
    classroom_id = "56ee7bd1-1a68-4fad-b02f-98d7f37de039"  # Matematicas
    user_id = "2c34a63f-21db-434e-8fc0-5d3b13a0de28"
    
    # Obtener documentos disponibles
    docs = await get_classroom_documents(classroom_id)
    
    if len(docs) < 2:
        print("\n❌ No hay suficientes documentos para el test")
        return None
    
    # Usar solo los primeros 2 documentos
    selected_doc_ids = [docs[0]['id'], docs[1]['id']]
    
    print(f"\n📋 Usando {len(selected_doc_ids)} documentos específicos:")
    print(f"   1. {docs[0]['title']}")
    print(f"   2. {docs[1]['title']}")
    
    test_params = {
        "classroom_id": classroom_id,
        "resource_type": "pdf",
        "user_id": user_id,
        "topic": "Recurso basado en documentos específicos",
        "source_document_ids": selected_doc_ids  # ✅ IDs específicos
    }
    
    print("\n🚀 Ejecutando generación...\n")
    result = await _generate_resources_impl(**test_params)
    
    print("\n📊 Resultado:")
    print("-" * 80)
    
    if result.get("success"):
        print("✅ ÉXITO - Recurso generado con documentos específicos")
        print(f"   - Título: {result.get('title')}")
        print(f"   - Documentos fuente: {result.get('source_documents')}")
        print(f"   - Tamaño: {result.get('file_size_bytes')} bytes")
        print(f"   - Secciones: {result.get('sections_count')}")
        
        # Validar que use solo los documentos solicitados
        if result.get('source_documents') == len(selected_doc_ids):
            print(f"\n✅ VALIDACIÓN OK: Usó exactamente {len(selected_doc_ids)} documentos")
        else:
            print(f"\n⚠️  ADVERTENCIA: Se esperaban {len(selected_doc_ids)} documentos, pero usó {result.get('source_documents')}")
    else:
        print("❌ ERROR")
        print(f"   Error: {result.get('error')}")
    
    print("\n" + "="*80)
    return result


async def test_with_invalid_document_ids():
    """
    Test 2: Generar recurso con IDs de documentos inválidos (no existen)
    """
    print("\n" + "="*80)
    print("TEST 2: Generar PDF con IDs de documentos INVÁLIDOS")
    print("="*80)
    
    classroom_id = "56ee7bd1-1a68-4fad-b02f-98d7f37de039"
    user_id = "2c34a63f-21db-434e-8fc0-5d3b13a0de28"
    
    # IDs falsos que no existen
    fake_doc_ids = [
        "00000000-0000-0000-0000-000000000001",
        "00000000-0000-0000-0000-000000000002"
    ]
    
    print(f"\n📋 Usando {len(fake_doc_ids)} IDs FALSOS:")
    for doc_id in fake_doc_ids:
        print(f"   - {doc_id}")
    
    test_params = {
        "classroom_id": classroom_id,
        "resource_type": "pdf",
        "user_id": user_id,
        "topic": "Test con IDs inválidos",
        "source_document_ids": fake_doc_ids  # ❌ IDs que no existen
    }
    
    print("\n🚀 Ejecutando generación...\n")
    result = await _generate_resources_impl(**test_params)
    
    print("\n📊 Resultado:")
    print("-" * 80)
    
    if not result.get("success"):
        print("✅ VALIDACIÓN OK - Error esperado detectado correctamente")
        print(f"   Error: {result.get('error')}")
    else:
        print("❌ PROBLEMA - Debería haber fallado con IDs inválidos")
        print(f"   Documentos usados: {result.get('source_documents')}")
    
    print("\n" + "="*80)
    return result


async def test_with_mixed_document_ids():
    """
    Test 3: Generar recurso con mezcla de IDs válidos e inválidos
    """
    print("\n" + "="*80)
    print("TEST 3: Generar PDF con MEZCLA de IDs (válidos + inválidos)")
    print("="*80)
    
    classroom_id = "56ee7bd1-1a68-4fad-b02f-98d7f37de039"
    user_id = "2c34a63f-21db-434e-8fc0-5d3b13a0de28"
    
    # Obtener un documento válido
    docs = await get_classroom_documents(classroom_id)
    
    if len(docs) < 1:
        print("\n❌ No hay documentos para el test")
        return None
    
    # Mezclar 1 ID válido + 1 ID inválido
    mixed_ids = [
        docs[0]['id'],  # ✅ Válido
        "00000000-0000-0000-0000-999999999999"  # ❌ Inválido
    ]
    
    print(f"\n📋 Usando mezcla de IDs:")
    print(f"   1. {docs[0]['id'][:8]}... ✅ (válido - {docs[0]['title']})")
    print(f"   2. 00000000... ❌ (inválido)")
    
    test_params = {
        "classroom_id": classroom_id,
        "resource_type": "pdf",
        "user_id": user_id,
        "topic": "Test con IDs mezclados",
        "source_document_ids": mixed_ids
    }
    
    print("\n🚀 Ejecutando generación...\n")
    result = await _generate_resources_impl(**test_params)
    
    print("\n📊 Resultado:")
    print("-" * 80)
    
    if result.get("success"):
        print("✅ Recurso generado (usando solo documentos válidos)")
        print(f"   - Documentos solicitados: {len(mixed_ids)}")
        print(f"   - Documentos usados: {result.get('source_documents')}")
        print(f"   - Tamaño: {result.get('file_size_bytes')} bytes")
        
        if result.get('source_documents') == 1:
            print("\n✅ VALIDACIÓN OK: Usó solo el documento válido")
        else:
            print(f"\n⚠️  Se esperaba 1 documento válido")
    else:
        print("❌ ERROR")
        print(f"   Error: {result.get('error')}")
    
    print("\n" + "="*80)
    return result


async def test_with_wrong_classroom_documents():
    """
    Test 4: Intentar usar documentos de otro classroom (seguridad)
    """
    print("\n" + "="*80)
    print("TEST 4: Generar PDF con documentos de OTRO classroom (seguridad)")
    print("="*80)
    
    # Usar classroom de Matematicas pero intentar acceder a docs de otro classroom
    classroom_id = "56ee7bd1-1a68-4fad-b02f-98d7f37de039"  # Matematicas
    user_id = "2c34a63f-21db-434e-8fc0-5d3b13a0de28"
    
    # Obtener documentos de OTRO classroom (si existe)
    print(f"\n🔍 Buscando documentos de otros classrooms...")
    
    all_classrooms = await asyncio.to_thread(
        lambda: supabase_client.client.table("classrooms")
        .select("id, name")
        .limit(5)
        .execute()
    )
    
    other_classroom = None
    for cr in all_classrooms.data:
        if cr['id'] != classroom_id:
            other_classroom = cr
            break
    
    if not other_classroom:
        print("⚠️  No hay otro classroom disponible para el test")
        return None
    
    print(f"✅ Encontrado otro classroom: {other_classroom['name']}")
    
    # Obtener documentos del otro classroom
    other_docs = await asyncio.to_thread(
        lambda: supabase_client.client.table("classroom_documents")
        .select("id, title")
        .eq("classroom_id", other_classroom['id'])
        .limit(1)
        .execute()
    )
    
    if not other_docs.data:
        print("⚠️  El otro classroom no tiene documentos")
        return None
    
    wrong_doc_id = other_docs.data[0]['id']
    wrong_doc_title = other_docs.data[0]['title']
    
    print(f"\n📋 Intentando usar documento de otro classroom:")
    print(f"   - Classroom solicitado: Matematicas")
    print(f"   - Documento: {wrong_doc_title} (del classroom {other_classroom['name']})")
    
    test_params = {
        "classroom_id": classroom_id,  # Matematicas
        "resource_type": "pdf",
        "user_id": user_id,
        "topic": "Test de seguridad",
        "source_document_ids": [wrong_doc_id]  # ❌ Doc de otro classroom
    }
    
    print("\n🚀 Ejecutando generación...\n")
    result = await _generate_resources_impl(**test_params)
    
    print("\n📊 Resultado:")
    print("-" * 80)
    
    if not result.get("success"):
        print("✅ SEGURIDAD OK - Bloqueó acceso a documento de otro classroom")
        print(f"   Error: {result.get('error')}")
    else:
        print("❌ PROBLEMA DE SEGURIDAD - Permitió usar documento de otro classroom")
        print(f"   Esto NO debería suceder")
    
    print("\n" + "="*80)
    return result


async def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "🧪" * 40)
    print("SUITE DE TESTS: source_document_ids")
    print("🧪" * 40)
    
    tests = [
        ("Test 1: Documentos específicos válidos", test_with_specific_documents),
        ("Test 2: IDs inválidos", test_with_invalid_document_ids),
        ("Test 3: Mezcla de IDs", test_with_mixed_document_ids),
        ("Test 4: Seguridad (docs de otro classroom)", test_with_wrong_classroom_documents),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Error en {test_name}: {e}")
            results.append((test_name, None))
        
        await asyncio.sleep(1)  # Pequeña pausa entre tests
    
    # Resumen final
    print("\n" + "="*80)
    print("📋 RESUMEN DE TESTS")
    print("="*80)
    
    for test_name, result in results:
        if result is None:
            status = "⏭️  OMITIDO"
        elif result.get("success"):
            status = "✅ ÉXITO"
        else:
            status = "❌ ERROR"
        
        print(f"{status} - {test_name}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
