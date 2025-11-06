"""
Test para re-procesar el documento PDF con la nueva lógica de extracción
"""
import asyncio
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from src.main import _store_document_chunks_impl
from supabase import create_client

# Cliente de Supabase
supabase = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)

document_id = "7c912acb-e74c-402d-9639-f8a183e1bbe7"

async def test_reprocess_pdf():
    print(f"\n{'='*80}")
    print("TEST: Re-procesar documento PDF con extracción correcta")
    print(f"{'='*80}\n")
    
    # Paso 1: Eliminar chunks antiguos
    print("🗑️  Paso 1: Eliminando chunks antiguos...")
    result = supabase.table("classroom_document_chunks").delete().eq(
        "classroom_document_id", document_id
    ).execute()
    print(f"   ✅ Eliminados {len(result.data) if result.data else 0} chunks antiguos\n")
    
    # Paso 2: Re-procesar documento
    print("🔄 Paso 2: Re-procesando documento con nueva lógica...")
    result = await _store_document_chunks_impl(
        classroom_document_id=document_id,
        chunk_size=1000,
        chunk_overlap=100
    )
    
    print(f"\n{'='*80}")
    print("✅ RESULTADO:")
    print(f"{'='*80}")
    print(f"   Success: {result.get('success')}")
    print(f"   Chunks creados: {result.get('chunks_created', 0)}")
    print(f"   Total caracteres: {result.get('total_characters', 0):,}")
    
    if result.get('error'):
        print(f"   ❌ Error: {result.get('error')}")
    
    # Paso 3: Verificar los nuevos chunks
    print(f"\n{'='*80}")
    print("🔍 Paso 3: Verificando chunks nuevos...")
    print(f"{'='*80}\n")
    
    chunks = supabase.table("classroom_document_chunks").select(
        "chunk_index, content"
    ).eq("classroom_document_id", document_id).order("chunk_index").limit(3).execute()
    
    for chunk in chunks.data:
        content = chunk['content']
        
        # Análisis
        has_pdf_markers = '%PDF' in content or '/Type' in content or 'endobj' in content
        words = [w for w in content.split() if any(c.isalpha() for c in w)]
        
        print(f"📦 Chunk #{chunk['chunk_index']}")
        print(f"   Longitud: {len(content)} chars")
        print(f"   Palabras: {len(words)}")
        print(f"   Tiene marcadores PDF: {'❌ SÍ (MAL)' if has_pdf_markers else '✅ NO (BIEN)'}")
        print(f"   Preview: {content[:200]}...")
        print()
    
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(test_reprocess_pdf())
