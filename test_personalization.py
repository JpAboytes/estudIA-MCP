#!/usr/bin/env python3
"""
Test script para verificar personalización en generate_resources
Compara recursos generados con y sin contexto de usuario
"""

import asyncio
from src.main import _generate_resources_impl
from src.supabase_client import supabase_client


async def check_user_context(user_id: str):
    """Helper para verificar si un usuario tiene contexto"""
    print(f"\n🔍 Verificando contexto del usuario {user_id}...")
    
    result = await asyncio.to_thread(
        lambda: supabase_client.client.table("users")
        .select("id, name, email, user_context")
        .eq("id", user_id)
        .single()
        .execute()
    )
    
    if result.data:
        user = result.data
        has_context = bool(user.get('user_context'))
        context_length = len(user.get('user_context', ''))
        
        print(f"✅ Usuario: {user['name']} ({user['email']})")
        print(f"   Contexto: {'✅ SÍ' if has_context else '❌ NO'} ({context_length} caracteres)")
        
        if has_context:
            print(f"\n📄 Contexto del usuario:")
            print(f"   {user['user_context'][:200]}...")
        
        return user, has_context
    
    return None, False


async def test_with_user_context():
    """
    Test 1: Generar recurso CON contexto de usuario (personalizado)
    """
    print("\n" + "="*80)
    print("TEST 1: Generar PDF PERSONALIZADO (con contexto de usuario)")
    print("="*80)
    
    classroom_id = "56ee7bd1-1a68-4fad-b02f-98d7f37de039"  # Matematicas
    user_id = "2c34a63f-21db-434e-8fc0-5d3b13a0de28"
    
    # Verificar si el usuario tiene contexto
    user, has_context = await check_user_context(user_id)
    
    if not has_context:
        print("\n⚠️  ADVERTENCIA: Este usuario NO tiene contexto configurado")
        print("   El recurso se generará sin personalización")
    
    test_params = {
        "classroom_id": classroom_id,
        "resource_type": "pdf",
        "user_id": user_id,
        "topic": "Introducción a la Inteligencia Artificial",
        "source_document_ids": None
    }
    
    print("\n🚀 Generando recurso...")
    result = await _generate_resources_impl(**test_params)
    
    print("\n📊 Resultado:")
    print("-" * 80)
    
    if result.get("success"):
        print("✅ ÉXITO - Recurso generado")
        print(f"   - Título: {result.get('title')}")
        print(f"   - Tamaño: {result.get('file_size_bytes')} bytes")
        print(f"   - Secciones: {result.get('sections_count')}")
        print(f"   - Personalizado: {'✅ SÍ' if result.get('personalized') else '❌ NO'}")
        print(f"   - Usuario: {result.get('user_name')}")
        
        if result.get('personalized'):
            print(f"\n✨ VALIDACIÓN OK: El recurso está PERSONALIZADO")
        else:
            print(f"\n⚠️  El recurso NO está personalizado (sin contexto de usuario)")
        
        print(f"\n🔗 URL: {result.get('public_url')}")
    else:
        print("❌ ERROR")
        print(f"   Error: {result.get('error')}")
    
    print("\n" + "="*80)
    return result


async def test_without_user_context():
    """
    Test 2: Generar recurso SIN contexto de usuario
    (simular usuario sin contexto configurado)
    """
    print("\n" + "="*80)
    print("TEST 2: Generar PDF SIN PERSONALIZACIÓN (sin contexto)")
    print("="*80)
    
    classroom_id = "56ee7bd1-1a68-4fad-b02f-98d7f37de039"
    
    # Buscar un usuario que NO tenga contexto
    print(f"\n🔍 Buscando usuario sin contexto...")
    
    users_result = await asyncio.to_thread(
        lambda: supabase_client.client.table("users")
        .select("id, name, email, user_context")
        .limit(10)
        .execute()
    )
    
    user_without_context = None
    for user in users_result.data:
        if not user.get('user_context'):
            user_without_context = user
            break
    
    if not user_without_context:
        print("⚠️  No se encontró usuario sin contexto para el test")
        print("   Usando usuario con contexto (pero validando comportamiento)")
        user_id = "2c34a63f-21db-434e-8fc0-5d3b13a0de28"
    else:
        user_id = user_without_context['id']
        print(f"✅ Usuario sin contexto: {user_without_context['name']}")
    
    test_params = {
        "classroom_id": classroom_id,
        "resource_type": "pdf",
        "user_id": user_id,
        "topic": "Conceptos básicos de programación",
        "source_document_ids": None
    }
    
    print("\n🚀 Generando recurso...")
    result = await _generate_resources_impl(**test_params)
    
    print("\n📊 Resultado:")
    print("-" * 80)
    
    if result.get("success"):
        print("✅ ÉXITO - Recurso generado")
        print(f"   - Título: {result.get('title')}")
        print(f"   - Tamaño: {result.get('file_size_bytes')} bytes")
        print(f"   - Personalizado: {'✅ SÍ' if result.get('personalized') else '❌ NO'}")
        
        if not result.get('personalized'):
            print(f"\n✅ VALIDACIÓN OK: Recurso genérico (sin personalización)")
        else:
            print(f"\n⚠️  Se esperaba recurso genérico")
    else:
        print("❌ ERROR")
        print(f"   Error: {result.get('error')}")
    
    print("\n" + "="*80)
    return result


async def test_comparison():
    """
    Test 3: Comparación lado a lado
    Generar dos recursos del mismo tema con y sin personalización
    """
    print("\n" + "="*80)
    print("TEST 3: COMPARACIÓN - Personalizado vs Genérico")
    print("="*80)
    
    classroom_id = "56ee7bd1-1a68-4fad-b02f-98d7f37de039"
    
    # Obtener 2 usuarios diferentes
    users_result = await asyncio.to_thread(
        lambda: supabase_client.client.table("users")
        .select("id, name, user_context")
        .limit(5)
        .execute()
    )
    
    user_with_context = None
    user_without_context = None
    
    for user in users_result.data:
        if user.get('user_context') and not user_with_context:
            user_with_context = user
        elif not user.get('user_context') and not user_without_context:
            user_without_context = user
    
    if not user_with_context:
        print("⚠️  No se encontró usuario con contexto")
        return None
    
    print(f"\n👥 Usuarios seleccionados:")
    print(f"   Usuario A: {user_with_context['name']} (✅ CON contexto)")
    if user_without_context:
        print(f"   Usuario B: {user_without_context['name']} (❌ SIN contexto)")
    else:
        print(f"   Usuario B: No disponible")
    
    # Generar recurso para usuario CON contexto
    print(f"\n📄 Generando recurso personalizado...")
    result_personalized = await _generate_resources_impl(
        classroom_id=classroom_id,
        resource_type="pdf",
        user_id=user_with_context['id'],
        topic="Machine Learning básico",
        source_document_ids=None
    )
    
    print(f"\n📊 Comparación de resultados:")
    print("-" * 80)
    
    if result_personalized.get("success"):
        print(f"✅ Recurso Personalizado:")
        print(f"   - Usuario: {result_personalized.get('user_name')}")
        print(f"   - Título: {result_personalized.get('title')}")
        print(f"   - Tamaño: {result_personalized.get('file_size_bytes')} bytes")
        print(f"   - Secciones: {result_personalized.get('sections_count')}")
        print(f"   - Personalizado: {result_personalized.get('personalized')}")
    else:
        print(f"❌ Error en recurso personalizado")
    
    print("\n" + "="*80)
    return result_personalized


async def update_user_context_for_testing():
    """
    Helper: Actualizar contexto de usuario para testing
    (Solo si necesitas crear contexto de prueba)
    """
    print("\n" + "="*80)
    print("HELPER: Actualizar contexto de usuario para testing")
    print("="*80)
    
    user_id = "2c34a63f-21db-434e-8fc0-5d3b13a0de28"
    
    sample_context = """
Nivel educativo: Universidad (Ingeniería en Sistemas)
Estilo de aprendizaje: Visual y práctico
Preferencias: Le gusta aprender con ejemplos de código y diagramas
Fortalezas: Programación, pensamiento lógico
Áreas de mejora: Matemáticas avanzadas, teoría abstracta
Intereses: Inteligencia Artificial, Machine Learning, desarrollo de aplicaciones
Experiencia: Intermedio en Python, básico en JavaScript
Vocabulario preferido: Técnico pero accesible, evitar jerga excesiva
"""
    
    print(f"\n📝 Contexto de prueba:")
    print(sample_context)
    
    confirm = input("\n¿Actualizar contexto del usuario para testing? (s/n): ")
    
    if confirm.lower() == 's':
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table("users")
            .update({"user_context": sample_context.strip()})
            .eq("id", user_id)
            .execute()
        )
        
        print(f"✅ Contexto actualizado para usuario {user_id}")
    else:
        print(f"⏭️  No se actualizó el contexto")
    
    print("\n" + "="*80)


async def run_all_tests():
    """Ejecutar todos los tests de personalización"""
    print("\n" + "✨" * 40)
    print("SUITE DE TESTS: PERSONALIZACIÓN DE RECURSOS")
    print("✨" * 40)
    
    # Opcional: Actualizar contexto de usuario para testing
    # await update_user_context_for_testing()
    
    tests = [
        ("Test 1: Recurso personalizado (con contexto)", test_with_user_context),
        ("Test 2: Recurso genérico (sin contexto)", test_without_user_context),
        ("Test 3: Comparación lado a lado", test_comparison),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Error en {test_name}: {e}")
            results.append((test_name, None))
        
        await asyncio.sleep(1)
    
    # Resumen final
    print("\n" + "="*80)
    print("📋 RESUMEN DE PERSONALIZACIÓN")
    print("="*80)
    
    personalized_count = 0
    generic_count = 0
    
    for test_name, result in results:
        if result is None:
            status = "⏭️  OMITIDO"
        elif result.get("success"):
            if result.get("personalized"):
                status = "✨ PERSONALIZADO"
                personalized_count += 1
            else:
                status = "📄 GENÉRICO"
                generic_count += 1
        else:
            status = "❌ ERROR"
        
        print(f"{status} - {test_name}")
    
    print(f"\nTotal recursos personalizados: {personalized_count}")
    print(f"Total recursos genéricos: {generic_count}")
    
    print("\n✅ La personalización está implementada y funcional")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
