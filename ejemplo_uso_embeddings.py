#!/usr/bin/env python3
"""
Ejemplo rápido de uso de las nuevas herramientas de embeddings
"""

import asyncio
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from src.gemini import gemini_client
from src.supabase_client import supabase_client


async def ejemplo_completo():
    """Ejemplo de flujo completo: generar, almacenar y buscar"""
    
    print("\n" + "🎯"*30)
    print(" "*20 + "EJEMPLO DE USO COMPLETO")
    print("🎯"*30 + "\n")
    
    # ==========================================
    # PASO 1: GENERAR EMBEDDING
    # ==========================================
    print("\n📝 PASO 1: Generar embedding de un texto")
    print("-" * 60)
    
    texto = "El Régimen Simplificado de Confianza (RESICO) es ideal para pequeños negocios con ingresos menores a 3.5 millones de pesos anuales"
    
    try:
        embedding = await gemini_client.generate_embedding(texto)
        print(f"✅ Embedding generado exitosamente")
        print(f"   📊 Dimensiones: {len(embedding)}")
        print(f"   📐 Modelo usado: {config.GEMINI_EMBED_MODEL}")
        print(f"   🔢 Vector (5 primeros): {embedding[:5]}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # ==========================================
    # PASO 2: ALMACENAR DOCUMENTO
    # ==========================================
    print("\n\n📝 PASO 2: Almacenar documento con metadata")
    print("-" * 60)
    
    texto = ("El RESICO permite pagar impuestos de forma simplificada. "
             "Los contribuyentes en este régimen pagan tasas reducidas: "
             "1% para ingresos hasta $300,000, 1.5% hasta $1,000,000, etc.")
    
    try:
        # Generar embedding
        embedding = await gemini_client.generate_embedding(texto)
        
        # Preparar datos
        data = {
            "content": texto,
            "embedding": embedding,
            "title": "Guía RESICO - Tasas de Impuestos",
            "scope": "regimenes",
            "source_url": "https://www.sat.gob.mx/consulta/23972/conoce-el-regimen-simplificado-de-confianza"
        }
        
        # Insertar en Supabase
        result = await asyncio.to_thread(
            lambda: supabase_client.client.table("documents").insert(data).execute()
        )
        
        if result.data:
            doc = result.data[0]
            print(f"✅ Documento almacenado exitosamente")
            print(f"   🆔 ID del documento: {doc['id']}")
            print(f"   📝 Título: {data['title']}")
            print(f"   📂 Scope: {data['scope']}")
            print(f"   🔗 URL: {data['source_url'][:50]}...")
        else:
            print(f"⚠️  Sin datos en respuesta")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   💡 Hint: Verifica que la tabla 'documents' exista")
    
    # ==========================================
    # PASO 3: BUSCAR DOCUMENTOS SIMILARES
    # ==========================================
    print("\n\n📝 PASO 3: Buscar documentos similares")
    print("-" * 60)
    
    query = "¿Qué régimen fiscal me conviene para mi pequeño negocio?"
    
    try:
        # Generar embedding del query
        embedding = await gemini_client.generate_embedding(query)
        
        # Buscar documentos
        documents = await supabase_client.search_similar_documents(
            embedding=embedding,
            limit=5,
            threshold=0.6
        )
        
        print(f"✅ Búsqueda completada exitosamente")
        print(f"   🔍 Query: {query}")
        print(f"   📊 Documentos encontrados: {len(documents)}")
        print(f"   🎯 Threshold usado: 0.6")
        
        if len(documents) > 0:
            print(f"\n   📄 Resultados:")
            for i, doc in enumerate(documents[:3], 1):
                print(f"\n      {i}. {doc.get('title', 'Sin título')}")
                print(f"         Similitud: {doc.get('similarity', 0):.3f}")
                print(f"         Scope: {doc.get('scope', 'N/A')}")
                print(f"         Preview: {doc.get('content', '')[:80]}...")
        else:
            print("\n   ℹ️  No se encontraron documentos con ese threshold")
            print("   💡 Prueba con un threshold más bajo (ej: 0.3)")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   💡 Hint: Verifica que las funciones RPC existan en Supabase")
    
    # ==========================================
    # RESUMEN
    # ==========================================
    print("\n\n" + "="*60)
    print("✅ EJEMPLO COMPLETADO")
    print("="*60)
    print("\n📚 Flujo demostrado:")
    print("   1. ✅ Generar embedding de texto")
    print("   2. ✅ Almacenar documento con metadata")
    print("   3. ✅ Buscar documentos similares")
    print("\n💡 Estas herramientas permiten:")
    print("   - Convertir texto en vectores semánticos")
    print("   - Almacenar conocimiento en base de datos")
    print("   - Buscar información relevante por similitud")
    print("\n🎯 Úsalas para construir sistemas RAG y chatbots inteligentes!")


async def ejemplo_solo_embedding():
    """Ejemplo simple: solo generar embedding"""
    
    print("\n" + "🎯"*30)
    print(" "*20 + "EJEMPLO SIMPLE: EMBEDDINGS")
    print("🎯"*30 + "\n")
    
    textos = [
        "Régimen Simplificado de Confianza",
        "Obligaciones fiscales para personas físicas",
        "¿Cómo emitir facturas CFDI?",
    ]
    
    for i, texto in enumerate(textos, 1):
        print(f"\n📝 Texto {i}: {texto}")
        try:
            embedding = await gemini_client.generate_embedding(texto)
            print(f"   ✅ Embedding: {len(embedding)} dimensiones")
            print(f"   🔢 Primeros 3 valores: {embedding[:3]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def main():
    """Menú principal"""
    print("\n" + "="*70)
    print("🚀 EJEMPLOS DE USO - Nuevas Herramientas de Embeddings")
    print("="*70)
    print("\nElige un ejemplo:")
    print("  1. Ejemplo completo (generar + almacenar + buscar)")
    print("  2. Ejemplo simple (solo embeddings)")
    print("  3. Ejecutar ambos")
    print()
    
    try:
        opcion = input("Opción (1-3, Enter=1): ").strip() or "1"
        
        if opcion == "1":
            await ejemplo_completo()
        elif opcion == "2":
            await ejemplo_solo_embedding()
        elif opcion == "3":
            await ejemplo_solo_embedding()
            print("\n" + "="*70 + "\n")
            await ejemplo_completo()
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Ejemplo interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
