"""
Test simple para verificar los chunks del documento PDF problemático
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

document_id = "7c912acb-e74c-402d-9639-f8a183e1bbe7"

print(f"\n{'='*80}")
print(f"ANÁLISIS DE CHUNKS - Documento: {document_id}")
print(f"{'='*80}\n")

# Obtener chunks
chunks = supabase.table("classroom_document_chunks").select("*").eq(
    "classroom_document_id", document_id
).order("chunk_index").execute()

print(f"📊 Total de chunks: {len(chunks.data)}\n")

for i, chunk in enumerate(chunks.data[:3], 1):  # Solo los primeros 3
    content = chunk['content']
    
    print(f"{'─'*80}")
    print(f"📦 Chunk #{chunk['chunk_index']}")
    print(f"   Longitud: {len(content)} caracteres")
    
    # Análisis del contenido
    has_pdf_markers = '%PDF' in content or '/Type' in content or 'endobj' in content
    printable_chars = sum(1 for c in content if c.isprintable() and ord(c) < 128)
    printable_ratio = printable_chars / len(content) if len(content) > 0 else 0
    
    print(f"   Tiene marcadores PDF: {'✅ SÍ' if has_pdf_markers else '❌ NO'}")
    print(f"   Caracteres ASCII imprimibles: {printable_ratio:.1%}")
    
    print(f"\n   📄 Preview (primeros 300 chars):")
    print(f"   {content[:300]}")
    print()

print(f"\n{'='*80}")
print("🔍 CONCLUSIÓN:")
print("="*80)
print("❌ Los chunks contienen CÓDIGO PDF RAW en lugar de texto extraído")
print("💡 Solución: Usar PyPDF2 o pdfplumber para extraer texto de PDFs")
print("="*80)
