#!/usr/bin/env python3
"""
Test de las nuevas herramientas de embeddings y almacenamiento
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
    print("TEST 1: generate_embedding (usando gemini_client)")
    print("="*70)
    
    # Test 1: Texto válido
    print("\n📝 Test 1.1: Generar embedding de texto válido")
    text = "Régimen Simplificado de Confianza para pequeños negocios en México"
    
    try:
        embedding = await gemini_client.generate_embedding(text)
        
        print(f"\n✅ Resultado:")
        print(f"   Success: True")
        print(f"   Dimensiones: {len(embedding)}")
        print(f"   Modelo: {config.GEMINI_EMBED_MODEL}")
        print(f"   Vector (primeros 5): {embedding[:5]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Texto vacío (debe fallar)
    print("\n📝 Test 1.2: Texto vacío (debe fallar)")
    try:
        embedding = await gemini_client.generate_embedding("")
        print(f"   ⚠️  No falló como se esperaba")
    except Exception as e:
        print(f"   ✅ Error esperado: {type(e).__name__}")
    
    return True


async def test_store_document():
    """Test de almacenamiento de documentos"""
    print("\n" + "="*70)
    print("TEST 2: store_document (usando clientes directos)")
    print("="*70)
    
    print("\n📝 Test 2.1: Almacenar documento con metadata completa")
    text = ("El Régimen Simplificado de Confianza (RESICO) es un régimen fiscal "
            "diseñado para personas físicas con actividad empresarial y con ingresos "
            "menores a 3.5 millones de pesos anuales.")
    
    try:
        # Paso 1: Generar embedding
        print("   🔄 Generando embedding...")
        embedding = await gemini_client.generate_embedding(text)
        print(f"   ✅ Embedding generado ({len(embedding)} dims)")
        
        # Paso 2: Preparar datos
        data = {
            "content": text,
            "embedding": embedding,
            "title": "Información sobre RESICO",
            "scope": "regimenes",
            "source_url": "https://www.sat.gob.mx/consulta/23972/conoce-el-regimen-simplificado-de-confianza"
        }
        
        # Paso 3: Insertar en Supabase
        print("   💾 Insertando en Supabase (tabla: documents)...")
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table("documents").insert(data).execute()
        )
        
        if result.data:
            doc_id = result.data[0]['id']
            print(f"\n✅ Documento almacenado exitosamente")
            print(f"   Document ID: {doc_id}")
            print(f"   Title: {data['title']}")
            print(f"   Scope: {data['scope']}")
        else:
            print(f"   ⚠️  No se recibieron datos")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   Hint: Verifica que la tabla 'documents' exista en Supabase")
    
    # Test 2: Documento básico sin metadata
    print("\n📝 Test 2.2: Almacenar documento básico (sin metadata)")
    text = ("Las obligaciones fiscales incluyen presentar declaraciones mensuales "
            "y anuales, emitir facturas electrónicas (CFDI) y llevar contabilidad.")
    
    try:
        embedding = await gemini_client.generate_embedding(text)
        data = {"content": text, "embedding": embedding}
        
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table("documents").insert(data).execute()
        )
        
        if result.data:
            print(f"   ✅ Document ID: {result.data[0]['id']}")
        else:
            print(f"   ⚠️  Sin datos en respuesta")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return True


async def test_search_similar_documents():
    """Test de búsqueda de documentos similares"""
    print("\n" + "="*70)
    print("TEST 3: search_similar_documents (usando supabase_client)")
    print("="*70)
    
    print("\n📝 Test 3.1: Búsqueda global de documentos")
    query = "¿Qué régimen fiscal me conviene para mi negocio pequeño?"
    
    try:
        # Paso 1: Generar embedding del query
        print(f"   🔄 Generando embedding del query...")
        embedding = await gemini_client.generate_embedding(query)
        print(f"   ✅ Embedding generado ({len(embedding)} dims)")
        
        # Paso 2: Buscar documentos similares
        print(f"   🔍 Buscando documentos (threshold={config.SIMILARITY_THRESHOLD})...")
        documents = await supabase_client.search_similar_documents(
            embedding=embedding,
            limit=5,
            threshold=config.SIMILARITY_THRESHOLD
        )
        
        print(f"\n✅ Búsqueda completada")
        print(f"   Documentos encontrados: {len(documents)}")
        print(f"   Query: {query}")
        print(f"   Threshold usado: {config.SIMILARITY_THRESHOLD}")
        
        if len(documents) > 0:
            print(f"\n   📄 Primeros resultados:")
            for i, doc in enumerate(documents[:3], 1):
                print(f"      {i}. {doc.get('title', 'Sin título')}")
                print(f"         Similitud: {doc.get('similarity', 0):.3f}")
                print(f"         Scope: {doc.get('scope', 'N/A')}")
        else:
            print(f"   ℹ️  No se encontraron documentos")
            print(f"   💡 Prueba con threshold más bajo o inserta documentos primero")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   Hint: Verifica que las funciones RPC existan en Supabase")
    
    # Test 2: Búsqueda con threshold alto
    print("\n📝 Test 3.2: Búsqueda con threshold alto (0.8)")
    query = "obligaciones fiscales para nuevos contribuyentes"
    
    try:
        embedding = await gemini_client.generate_embedding(query)
        documents = await supabase_client.search_similar_documents(
            embedding=embedding,
            limit=3,
            threshold=0.8
        )
        
        print(f"   ✅ Búsqueda completada")
        print(f"   Documentos encontrados: {len(documents)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return True


async def main():
    """Ejecutar todos los tests"""
    print("\n" + "🧪"*35)
    print(" "*20 + "TEST SUITE: Nuevas Herramientas MCP")
    print("🧪"*35 + "\n")
    
    try:
        # Test 1: Generate embedding
        await test_generate_embedding()
        
        # Test 2: Store document
        await test_store_document()
        
        # Test 3: Search similar documents
        await test_search_similar_documents()
        
        print("\n" + "="*70)
        print("✅ TESTS COMPLETADOS")
        print("="*70)
        print("\n💡 Notas importantes:")
        print("   - Si store_document falla, verifica que:")
        print("     1. SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY estén configuradas")
        print("     2. La tabla 'documents' exista en Supabase")
        print("     3. Las dimensiones del vector coincidan con la configuración")
        print("\n   - Si search_similar_documents no encuentra documentos:")
        print("     1. Asegúrate de haber insertado documentos primero")
        print("     2. Verifica que las funciones RPC existan en Supabase")
        print("     3. Prueba con un threshold más bajo (ej: 0.3)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
