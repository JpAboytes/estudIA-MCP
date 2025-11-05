#!/usr/bin/env python3
"""
Test script para generate_resources
Prueba la generación de PDF y PPT
"""

import asyncio
from src.main import _generate_resources_impl

async def test_generate_pdf():
    """
    Test para generar un PDF de recursos educativos
    """
    print("\n" + "="*80)
    print("TEST: Generar Recurso PDF")
    print("="*80 + "\n")
    
    # Parámetros de prueba - ajusta según tus datos reales
    test_params = {
        "classroom_id": "56ee7bd1-1a68-4fad-b02f-98d7f37de039",  # Matematicas
        "resource_type": "pdf",
        "user_id": "2c34a63f-21db-434e-8fc0-5d3b13a0de28",  # pablo.dessens@cetys.edu.mx
        "topic": "Introducción al tema",  # Opcional
        "source_document_ids": None  # Opcional - None para usar todos los docs del classroom
    }
    
    print("📋 Parámetros del test:")
    for key, value in test_params.items():
        print(f"   {key}: {value}")
    
    print("\n🚀 Ejecutando generación de PDF...\n")
    
    result = await _generate_resources_impl(**test_params)
    
    print("\n📊 Resultado:")
    print("-" * 80)
    
    if result.get("success"):
        print("✅ ÉXITO - PDF generado correctamente")
        print(f"\n📄 Detalles del recurso:")
        print(f"   - ID: {result.get('resource_id')}")
        print(f"   - Título: {result.get('title')}")
        print(f"   - Tipo: {result.get('resource_type')}")
        print(f"   - Ruta: {result.get('storage_path')}")
        print(f"   - Bucket: {result.get('bucket')}")
        print(f"   - Tamaño: {result.get('file_size_bytes')} bytes")
        print(f"   - Secciones: {result.get('sections_count')}")
        print(f"   - Conceptos: {result.get('concepts_count')}")
        print(f"   - Documentos fuente: {result.get('source_documents')}")
        print(f"\n🔗 URL pública:")
        print(f"   {result.get('public_url')}")
    else:
        print("❌ ERROR - No se pudo generar el PDF")
        print(f"   Error: {result.get('error')}")
    
    print("\n" + "="*80 + "\n")
    return result


async def test_generate_ppt():
    """
    Test para generar un PowerPoint de recursos educativos
    """
    print("\n" + "="*80)
    print("TEST: Generar Recurso PowerPoint")
    print("="*80 + "\n")
    
    # Parámetros de prueba
    test_params = {
        "classroom_id": "56ee7bd1-1a68-4fad-b02f-98d7f37de039",  # Matematicas
        "resource_type": "ppt",
        "user_id": "2c34a63f-21db-434e-8fc0-5d3b13a0de28",  # pablo.dessens@cetys.edu.mx
        "topic": "Presentación del tema",  # Opcional
        "source_document_ids": None
    }
    
    print("📋 Parámetros del test:")
    for key, value in test_params.items():
        print(f"   {key}: {value}")
    
    print("\n🚀 Ejecutando generación de PowerPoint...\n")
    
    result = await _generate_resources_impl(**test_params)
    
    print("\n📊 Resultado:")
    print("-" * 80)
    
    if result.get("success"):
        print("✅ ÉXITO - PowerPoint generado correctamente")
        print(f"\n📊 Detalles del recurso:")
        print(f"   - ID: {result.get('resource_id')}")
        print(f"   - Título: {result.get('title')}")
        print(f"   - Tipo: {result.get('resource_type')}")
        print(f"   - Ruta: {result.get('storage_path')}")
        print(f"   - Bucket: {result.get('bucket')}")
        print(f"   - Tamaño: {result.get('file_size_bytes')} bytes")
        print(f"   - Secciones: {result.get('sections_count')}")
        print(f"   - Conceptos: {result.get('concepts_count')}")
        print(f"   - Documentos fuente: {result.get('source_documents')}")
        print(f"\n🔗 URL pública:")
        print(f"   {result.get('public_url')}")
    else:
        print("❌ ERROR - No se pudo generar el PowerPoint")
        print(f"   Error: {result.get('error')}")
    
    print("\n" + "="*80 + "\n")
    return result


async def main():
    """Función principal para ejecutar los tests"""
    print("\n" + "="*80)
    print("🧪 SUITE DE TESTS - generate_resources")
    print("="*80)
    
    print("\n⚠️  IMPORTANTE: Antes de ejecutar este test:")
    print("   1. Edita este archivo y reemplaza 'TU_CLASSROOM_ID' y 'TU_USER_ID'")
    print("   2. Asegúrate de que el classroom tenga documentos cargados")
    print("   3. Ejecuta create_generated_resources_table.sql en Supabase")
    print("   4. Crea el bucket 'generated-resources' en Supabase Storage")
    print("   5. Instala las dependencias: pip install reportlab python-pptx")
    
    input("\n👉 Presiona Enter para continuar o Ctrl+C para salir...")
    
    # Test 1: Generar PDF
    await test_generate_pdf()
    
    # Test 2: Generar PPT
    await test_generate_ppt()
    
    print("\n" + "="*80)
    print("✅ Suite de tests completada")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
