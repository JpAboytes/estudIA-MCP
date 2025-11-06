"""
Test para analizar los chunks del documento 7c912acb-e74c-402d-9639-f8a183e1bbe7
y verificar por qué el texto no se está scrapeando bien
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configurar cliente de Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

def analyze_document_chunks(document_id: str):
    """Analiza los chunks de un documento específico"""
    
    print(f"\n{'='*80}")
    print(f"ANÁLISIS DE CHUNKS PARA DOCUMENTO: {document_id}")
    print(f"{'='*80}\n")
    
    # 1. Obtener información del documento
    print("1️⃣ INFORMACIÓN DEL DOCUMENTO:")
    print("-" * 80)
    
    doc_response = supabase.table("classroom_documents").select("*").eq("id", document_id).execute()
    
    if not doc_response.data:
        print(f"❌ No se encontró el documento con ID: {document_id}")
        return
    
    document = doc_response.data[0]
    print(f"   📄 Nombre: {document.get('name', 'N/A')}")
    print(f"   📁 Tipo: {document.get('type', 'N/A')}")
    print(f"   📊 Estado OCR: {document.get('ocr_status', 'N/A')}")
    print(f"   🔗 URL Storage: {document.get('storage_url', 'N/A')}")
    print(f"   📝 Tiene contenido directo: {'Sí' if document.get('content') else 'No'}")
    if document.get('content'):
        content_preview = document.get('content')[:200]
        print(f"   👀 Preview del contenido: {content_preview}...")
    
    # 2. Obtener los chunks
    print(f"\n2️⃣ CHUNKS GENERADOS:")
    print("-" * 80)
    
    chunks_response = supabase.table("classroom_document_chunks").select(
        "id, chunk_index, content, token_count"
    ).eq("classroom_document_id", document_id).order("chunk_index").execute()
    
    if not chunks_response.data:
        print(f"   ❌ No se encontraron chunks para este documento")
        return
    
    chunks = chunks_response.data
    print(f"   📊 Total de chunks: {len(chunks)}")
    print(f"\n   {'='*76}")
    
    # Analizar cada chunk
    total_tokens = 0
    total_chars = 0
    chunks_with_garbage = []
    chunks_with_valid_text = []
    
    for i, chunk in enumerate(chunks, 1):
        chunk_index = chunk.get('chunk_index', 'N/A')
        content = chunk.get('content', '')
        token_count = chunk.get('token_count', 0)
        char_count = len(content)
        
        total_tokens += token_count
        total_chars += char_count
        
        # Detectar si el chunk parece tener "basura" (caracteres raros)
        # Calculamos el porcentaje de caracteres ASCII imprimibles
        printable_chars = sum(1 for c in content if c.isprintable() and ord(c) < 128)
        printable_ratio = printable_chars / char_count if char_count > 0 else 0
        
        # Contar palabras válidas (secuencias de letras)
        words = [w for w in content.split() if any(c.isalpha() for c in w)]
        word_count = len(words)
        
        is_garbage = printable_ratio < 0.5 or word_count < 5
        
        if is_garbage:
            chunks_with_garbage.append(i)
        else:
            chunks_with_valid_text.append(i)
        
        print(f"\n   📦 Chunk #{chunk_index} (ID: {chunk['id'][:8]}...)")
        print(f"      • Caracteres: {char_count}")
        print(f"      • Tokens: {token_count}")
        print(f"      • Palabras: {word_count}")
        print(f"      • ASCII imprimible: {printable_ratio:.1%}")
        print(f"      • Estado: {'❌ BASURA/NO LEGIBLE' if is_garbage else '✅ TEXTO VÁLIDO'}")
        
        # Mostrar preview del contenido
        preview_length = 150
        preview = content[:preview_length].replace('\n', ' ').replace('\r', '')
        print(f"      • Preview: {preview}{'...' if len(content) > preview_length else ''}")
        
        # Si parece basura, mostrar caracteres especiales
        if is_garbage:
            special_chars = [c for c in set(content) if not c.isprintable() or ord(c) >= 128]
            print(f"      • Caracteres especiales encontrados: {len(special_chars)}")
            if special_chars:
                sample = ''.join(special_chars[:20])
                print(f"      • Muestra: {repr(sample)}")
    
    # 3. Resumen del análisis
    print(f"\n3️⃣ RESUMEN DEL ANÁLISIS:")
    print("-" * 80)
    print(f"   📊 Total chunks: {len(chunks)}")
    print(f"   ✅ Chunks con texto válido: {len(chunks_with_valid_text)} ({len(chunks_with_valid_text)/len(chunks)*100:.1f}%)")
    print(f"   ❌ Chunks con basura: {len(chunks_with_garbage)} ({len(chunks_with_garbage)/len(chunks)*100:.1f}%)")
    print(f"   📝 Total caracteres: {total_chars:,}")
    print(f"   🔢 Total tokens: {total_tokens:,}")
    print(f"   📊 Promedio chars/chunk: {total_chars/len(chunks):.0f}")
    print(f"   📊 Promedio tokens/chunk: {total_tokens/len(chunks):.0f}")
    
    if chunks_with_garbage:
        print(f"\n   ⚠️  PROBLEMA DETECTADO:")
        print(f"      El documento parece tener chunks con contenido no legible.")
        print(f"      Esto puede deberse a:")
        print(f"      • PDF con codificación incorrecta")
        print(f"      • Imagen que necesita OCR")
        print(f"      • Extracción de texto fallida")
        print(f"      • Archivo corrupto")
        
        if document.get('type') in ['application/pdf', 'pdf']:
            print(f"\n   💡 RECOMENDACIÓN:")
            print(f"      Este es un PDF. Considera:")
            print(f"      1. Verificar si es un PDF escaneado (requiere OCR)")
            print(f"      2. Usar una librería diferente para extraer texto (PyMuPDF, pdfplumber)")
            print(f"      3. Aplicar OCR con Tesseract o Google Vision API")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    document_id = "7c912acb-e74c-402d-9639-f8a183e1bbe7"
    analyze_document_chunks(document_id)
