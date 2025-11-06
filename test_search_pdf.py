"""
Test para verificar que ahora se puede buscar en el documento
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from supabase import create_client

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)

document_id = "7c912acb-e74c-402d-9639-f8a183e1bbe7"

print(f"\n{'='*80}")
print("TEST: Búsqueda en chunks del documento PDF")
print(f"{'='*80}\n")

# Obtener todos los chunks
chunks = supabase.table("classroom_document_chunks").select(
    "chunk_index, content"
).eq("classroom_document_id", document_id).order("chunk_index").execute()

print(f"📊 Total de chunks: {len(chunks.data)}\n")

# Buscar términos específicos
search_terms = ["security", "network", "CIA", "cybersecurity", "assessment"]

print("🔍 Búsqueda de términos clave:\n")

for term in search_terms:
    found_in = []
    for chunk in chunks.data:
        if term.lower() in chunk['content'].lower():
            found_in.append(chunk['chunk_index'])
    
    status = "✅" if found_in else "❌"
    print(f"   {status} '{term}': Encontrado en chunks {found_in if found_in else 'ninguno'}")

print(f"\n{'='*80}")
print("📄 CONTENIDO COMPLETO DEL DOCUMENTO:")
print(f"{'='*80}\n")

full_text = "\n".join([chunk['content'] for chunk in chunks.data])
print(full_text[:1000] + "...")

print(f"\n{'='*80}")
print(f"✅ Total: {len(full_text)} caracteres extraídos correctamente")
print(f"{'='*80}\n")
