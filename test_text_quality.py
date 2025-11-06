"""
Test para verificar si el formato del texto afecta la búsqueda y resúmenes
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from supabase import create_client

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
document_id = "7c912acb-e74c-402d-9639-f8a183e1bbe7"

print(f"\n{'='*80}")
print("TEST: Verificación de calidad del texto extraído")
print(f"{'='*80}\n")

# Obtener un chunk
chunks = supabase.table("classroom_document_chunks").select("content").eq(
    "classroom_document_id", document_id
).order("chunk_index").limit(1).execute()

content = chunks.data[0]['content']

# Análisis
lines = content.split('\n')
words_per_line = [len(line.split()) for line in lines if line.strip()]
avg_words_per_line = sum(words_per_line) / len(words_per_line) if words_per_line else 0

print("📊 ANÁLISIS DEL FORMATO:")
print(f"   Total líneas: {len(lines)}")
print(f"   Promedio palabras por línea: {avg_words_per_line:.1f}")
print(f"   ¿Una palabra por línea? {'✅ SÍ' if avg_words_per_line < 2 else '❌ NO'}\n")

# Mostrar muestra original
print("📄 FORMATO ACTUAL (primeros 300 chars):")
print("-" * 80)
print(content[:300])
print("-" * 80)

# Mostrar cómo se vería limpio
cleaned = ' '.join(content.split())
print("\n✨ FORMATO LIMPIO (mismos 300 chars):")
print("-" * 80)
print(cleaned[:300])
print("-" * 80)

# Comparar longitudes
print(f"\n📏 COMPARACIÓN:")
print(f"   Original: {len(content)} caracteres")
print(f"   Limpio: {len(cleaned)} caracteres")
print(f"   Reducción: {100 - (len(cleaned)/len(content)*100):.1f}%")

print(f"\n💡 RECOMENDACIÓN:")
if avg_words_per_line < 2:
    print("   ⚠️  El PDF tiene palabras separadas línea por línea")
    print("   ✅ Se recomienda agregar limpieza de formato")
    print("   📝 Esto mejorará los resúmenes y ahorrará tokens")
else:
    print("   ✅ El formato está bien, no requiere limpieza")

print(f"\n{'='*80}\n")
