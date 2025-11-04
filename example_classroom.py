"""
Ejemplos de uso con el esquema de documents y classroom_id
"""

from dotenv import load_dotenv
import os
import google.generativeai as genai
from supabase import create_client

# Cargar configuración
load_dotenv()

# Inicializar clientes
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("=" * 60)
print("📚 Ejemplos de Uso - Documents con Classroom")
print("=" * 60 + "\n")

# =============================================================================
# EJEMPLO 1: Almacenar documentos de diferentes classrooms
# =============================================================================

print("EJEMPLO 1: Almacenar documentos por classroom\n")

# UUIDs de ejemplo - reemplaza con UUIDs válidos de tu tabla classrooms
uuid_classroom_1 = "123e4567-e89b-12d3-a456-426614174000"
uuid_classroom_2 = "123e4567-e89b-12d3-a456-426614174001"

documents_classroom_1 = [
    "Python es un lenguaje de programación de alto nivel",
    "Las variables en Python no necesitan declaración de tipo",
    "Los loops for en Python son muy versátiles"
]

documents_classroom_2 = [
    "JavaScript es el lenguaje de la web",
    "React es una biblioteca de JavaScript para interfaces",
    "Node.js permite ejecutar JavaScript en el servidor"
]

# Insertar documentos del classroom 1
print(f"📝 Insertando documentos del Classroom {uuid_classroom_1[:8]}...")
for i, doc in enumerate(documents_classroom_1, 1):
    embedding = genai.embed_content(
        model="models/embedding-001",
        content=doc,
        task_type="retrieval_document"
    )['embedding']
    
    supabase.table("documents").insert({
        "content": doc,
        "embedding": embedding,
        "classroom_id": uuid_classroom_1
    }).execute()
    print(f"  ✓ Doc {i}: {doc[:40]}...")

# Insertar documentos del classroom 2
print(f"\n📝 Insertando documentos del Classroom {uuid_classroom_2[:8]}...")
for i, doc in enumerate(documents_classroom_2, 1):
    embedding = genai.embed_content(
        model="models/embedding-001",
        content=doc,
        task_type="retrieval_document"
    )['embedding']
    
    supabase.table("documents").insert({
        "content": doc,
        "embedding": embedding,
        "classroom_id": uuid_classroom_2
    }).execute()
    print(f"  ✓ Doc {i}: {doc[:40]}...")

# =============================================================================
# EJEMPLO 2: Búsqueda general (todos los classrooms)
# =============================================================================

print("\n" + "=" * 60)
print("EJEMPLO 2: Búsqueda general en todos los classrooms\n")

query = "¿Qué es un lenguaje de programación?"
print(f"🔍 Consulta: {query}\n")

query_embedding = genai.embed_content(
    model="models/embedding-001",
    content=query,
    task_type="retrieval_query"
)['embedding']

results = supabase.rpc('match_documents', {
    'query_embedding': query_embedding,
    'match_threshold': 0.5,
    'match_count': 5
}).execute()

print(f"✓ Encontrados {len(results.data)} documentos:\n")
for i, doc in enumerate(results.data, 1):
    print(f"{i}. Similitud: {doc['similarity']:.3f}")
    print(f"   Contenido: {doc['content'][:60]}...")
    print()

# =============================================================================
# EJEMPLO 3: Búsqueda filtrada por classroom_id (método 1)
# =============================================================================

print("=" * 60)
print("EJEMPLO 3: Búsqueda solo en Classroom específico\n")

query = "loops y variables"
classroom_filter = uuid_classroom_1  # Usar UUID del classroom 1

print(f"🔍 Consulta: {query}")
print(f"🏫 Classroom: {classroom_filter[:8]}...\n")

query_embedding = genai.embed_content(
    model="models/embedding-001",
    content=query,
    task_type="retrieval_query"
)['embedding']

# Primero buscar, luego filtrar
all_results = supabase.rpc('match_documents', {
    'query_embedding': query_embedding,
    'match_threshold': 0.3,
    'match_count': 10
}).execute()

# Obtener documentos completos y filtrar
doc_ids = [doc['id'] for doc in all_results.data]
filtered_docs = supabase.table("documents")\
    .select("*")\
    .in_("id", doc_ids)\
    .eq("classroom_id", classroom_filter)\
    .execute()

print(f"✓ Encontrados {len(filtered_docs.data)} documentos del Classroom {classroom_filter[:8]}...\n")
for i, doc in enumerate(filtered_docs.data, 1):
    # Obtener similitud del resultado original
    similarity = next((r['similarity'] for r in all_results.data if r['id'] == doc['id']), 0)
    print(f"{i}. Similitud: {similarity:.3f} | Classroom: {doc['classroom_id']}")
    print(f"   Contenido: {doc['content'][:60]}...")
    print()

# =============================================================================
# EJEMPLO 4: Usando la función match_documents_by_classroom (si la creaste)
# =============================================================================

print("=" * 60)
print("EJEMPLO 4: Búsqueda optimizada con match_documents_by_classroom\n")

try:
    query = "bibliotecas y frameworks"
    classroom_filter = uuid_classroom_2  # Usar UUID del classroom 2
    
    print(f"🔍 Consulta: {query}")
    print(f"🏫 Classroom: {classroom_filter[:8]}...\n")
    
    query_embedding = genai.embed_content(
        model="models/embedding-001",
        content=query,
        task_type="retrieval_query"
    )['embedding']
    
    results = supabase.rpc('match_documents_by_classroom', {
        'query_embedding': query_embedding,
        'match_threshold': 0.3,
        'match_count': 5,
        'filter_classroom_id': classroom_filter
    }).execute()
    
    print(f"✓ Encontrados {len(results.data)} documentos del Classroom {classroom_filter[:8]}...\n")
    for i, doc in enumerate(results.data, 1):
        print(f"{i}. Similitud: {doc['similarity']:.3f} | Classroom: {doc['classroom_id']}")
        print(f"   Contenido: {doc['content'][:60]}...")
        print()
        
except Exception as e:
    print(f"⚠️  La función match_documents_by_classroom no está disponible")
    print(f"   Ejecuta el SQL adicional en supabase_setup.sql para crearla\n")

# =============================================================================
# EJEMPLO 5: Obtener todos los documentos de un classroom
# =============================================================================

print("=" * 60)
print("EJEMPLO 5: Listar todos los documentos de un classroom\n")

classroom_id = uuid_classroom_1  # Usar UUID del classroom 1
docs = supabase.table("documents")\
    .select("*")\
    .eq("classroom_id", classroom_id)\
    .execute()

print(f"📚 Documentos del Classroom {classroom_id[:8]}...:\n")
for i, doc in enumerate(docs.data, 1):
    print(f"{i}. ID: {doc['id']}")
    print(f"   Contenido: {doc['content'][:60]}...")
    print(f"   Embedding: {len(doc['embedding'])} dimensiones")
    print()

# =============================================================================
# RESUMEN
# =============================================================================

print("=" * 60)
print("✅ RESUMEN")
print("=" * 60)
print()
print("✓ Documentos insertados en múltiples classrooms")
print("✓ Búsqueda general funcionando")
print("✓ Filtrado por classroom_id funcionando")
print("✓ Función de similitud usando tu schema actual")
print()
print("💡 Ahora puedes integrar esto con Claude Desktop!")
