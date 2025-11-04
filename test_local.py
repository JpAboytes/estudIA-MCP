"""
Script para probar el servidor estudIA-MCP en modo local
Sin necesidad de Claude Desktop
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

# Inicializar clientes
print("🔧 Inicializando clientes...\n")

# Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)
print(f"✓ Supabase conectado: {supabase_url[:30]}...")

# Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
print(f"✓ Gemini API configurada\n")

def test_generate_embedding():
    """Prueba 1: Generar embedding"""
    print("=" * 60)
    print("Prueba 1: Generar Embedding")
    print("=" * 60)
    
    text = "La inteligencia artificial está transformando la educación"
    print(f"📝 Texto: {text}\n")
    
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document",
        output_dimensionality=768,
    )
    
    embedding = result['embedding']
    print(f"✓ Embedding generado")
    print(f"  Modelo: models/gemini-embedding-001")
    print(f"  Dimensiones: {len(embedding)}")
    print(f"  Primeros 5 valores: {embedding[:5]}\n")
    
    return embedding


def test_store_embedding():
    """Prueba 2: Almacenar documento en Supabase"""
    print("=" * 60)
    print("Prueba 2: Almacenar Documento en Supabase")
    print("=" * 60)
    
    text = "Python es un lenguaje de programación versátil y poderoso"
    # Ejemplo de UUID - reemplaza con un UUID válido de tu tabla classrooms
    classroom_id = "123e4567-e89b-12d3-a456-426614174000"  
    print(f"📝 Texto: {text}")
    print(f"🏫 Classroom ID (UUID): {classroom_id}\n")
    
    # Generar embedding
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document",
        output_dimensionality=768,

    )
    
    embedding = result['embedding']
    
    # Almacenar en Supabase tabla documents
    data = {
        "content": text,
        "embedding": embedding,
        "classroom_id": classroom_id
    }
    
    result = supabase.table("documents").insert(data).execute()
    print(f"✓ Documento almacenado en Supabase")
    print(f"  ID: {result.data[0]['id']}")
    print(f"  Classroom ID: {result.data[0]['classroom_id']}")
    print(f"  Contenido: {result.data[0]['content'][:50]}...\n")
    
    return result.data[0]['id']


def test_search_similar():
    """Prueba 3: Búsqueda por similitud"""
    print("=" * 60)
    print("Prueba 3: Búsqueda por Similitud")
    print("=" * 60)
    
    query = "aprender a programar"
    print(f"🔍 Búsqueda: {query}\n")
    
    # Generar embedding de la consulta
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=query,
        task_type="retrieval_query",
        output_dimensionality=768,
    )
    
    query_embedding = result['embedding']
    
    try:
        # Buscar documentos similares
        search_result = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.5,
                'match_count': 3
            }
        ).execute()
        
        print(f"✓ Búsqueda completada")
        print(f"  Documentos encontrados: {len(search_result.data)}\n")
        
        if search_result.data:
            for i, doc in enumerate(search_result.data, 1):
                print(f"  {i}. Similitud: {doc.get('similarity', 0):.3f}")
                print(f"     Contenido: {doc.get('content', '')[:60]}...")
                print()
        else:
            print("  No se encontraron documentos similares")
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {str(e)}")
        print("   Asegúrate de ejecutar supabase_setup.sql primero\n")


def test_batch_insert():
    """Prueba 4: Insertar múltiples documentos"""
    print("=" * 60)
    print("Prueba 4: Inserción Múltiple de Documentos")
    print("=" * 60)
    
    # Ejemplos de UUIDs - reemplaza con UUIDs válidos de tu tabla classrooms
    uuid1 = "123e4567-e89b-12d3-a456-426614174000"
    uuid2 = "123e4567-e89b-12d3-a456-426614174001"
    
    documents = [
        {
            "text": "Machine Learning permite a las computadoras aprender de los datos",
            "classroom_id": uuid1
        },
        {
            "text": "Deep Learning usa redes neuronales profundas",
            "classroom_id": uuid1
        },
        {
            "text": "Natural Language Processing ayuda a las máquinas a entender el lenguaje",
            "classroom_id": uuid2
        }
    ]
    
    print(f"📚 Insertando {len(documents)} documentos...\n")
    
    for i, doc in enumerate(documents, 1):
        # Generar embedding
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=doc["text"],
            task_type="retrieval_document",
            output_dimensionality=768,
        )
        
        # Preparar datos
        data = {
            "content": doc["text"],
            "embedding": result['embedding'],
            "classroom_id": doc["classroom_id"]
        }
        
        # Insertar en tabla documents
        supabase.table("documents").insert(data).execute()
        print(f"  ✓ Documento {i} (classroom {doc['classroom_id'][:8]}...): {doc['text'][:40]}...")
    
    print(f"\n✓ {len(documents)} documentos insertados exitosamente\n")


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "🚀" * 30)
    print("  estudIA-MCP - Modo de Prueba Local")
    print("🚀" * 30 + "\n")
    
    try:
        # Ejecutar pruebas
        test_generate_embedding()
        input("Presiona Enter para continuar...")
        
        test_store_embedding()
        input("Presiona Enter para continuar...")
        
        test_search_similar()
        input("Presiona Enter para continuar...")
        
        test_batch_insert()
        
        print("=" * 60)
        print("✅ Todas las pruebas completadas")
        print("=" * 60)
        print("\n💡 Ahora puedes:")
        print("  1. Integrar con Claude Desktop usando claude_desktop_config.json")
        print("  2. Usar las funciones directamente en tus scripts Python")
        print("  3. Explorar la tabla 'documents' en Supabase")
        print("  4. Filtrar búsquedas por classroom_id\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Verifica tu configuración en .env y que Supabase esté configurado\n")


if __name__ == "__main__":
    main()
