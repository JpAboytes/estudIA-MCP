# 🔄 Actualización: store_document_chunks

## 📋 Resumen de Cambios

La función de almacenamiento de documentos ha sido mejorada significativamente para simplificar su uso y hacerla más intuitiva.

### ❌ Versión Anterior (problemática)

```python
# Antes: El usuario tenía que:
# 1. Dividir el documento manualmente en chunks
# 2. Pasar cada chunk con su índice y contenido
# 3. Hacer múltiples llamadas a la función

await store_document_chunk(
    classroom_document_id="xxx-xxx-xxx",
    chunk_index=0,
    content="Primer chunk del documento...",
    token_count=150
)

await store_document_chunk(
    classroom_document_id="xxx-xxx-xxx",
    chunk_index=1,
    content="Segundo chunk del documento...",
    token_count=145
)
# ... y así sucesivamente
```

**Problemas:**
- 🚫 El usuario tenía que hacer el chunking manualmente
- 🚫 Múltiples llamadas a la función
- 🚫 Difícil de usar y propenso a errores
- 🚫 El usuario debía calcular tokens e índices

### ✅ Versión Nueva (mejorada)

```python
# Ahora: Solo necesitas el ID del documento
# La función hace TODO automáticamente:

result = await store_document_chunks(
    classroom_document_id="xxx-xxx-xxx",
    chunk_size=1000,        # Opcional: tamaño de cada chunk
    chunk_overlap=200       # Opcional: overlap entre chunks
)

# ¡Eso es todo! 🎉
```

**Ventajas:**
- ✅ Una sola llamada a la función
- ✅ Chunking automático del documento
- ✅ Generación automática de embeddings para cada chunk
- ✅ Almacenamiento automático en la base de datos
- ✅ Control de solapamiento entre chunks para mejor contexto
- ✅ Cálculo automático de tokens

## 🔧 Cómo Funciona Internamente

### Flujo del Proceso

```
1. 📄 Obtener metadatos del documento de classroom_documents
   └─ Extrae el bucket y storage_path por el ID del documento

2. 📥 Descargar contenido desde Supabase Storage
   ├─ Descarga el archivo usando bucket y storage_path
   ├─ Decodifica según el mime_type (text/plain soportado)
   └─ PDFs requieren extracción previa de texto

3. ✂️  Dividir en chunks inteligentemente
   ├─ Respeta el tamaño máximo (chunk_size)
   ├─ Aplica overlap entre chunks (chunk_overlap)
   └─ Evita cortar palabras a la mitad

4. 🧠 Generar embeddings
   └─ Para cada chunk, genera su vector de embedding

5. 💾 Almacenar todo en classroom_document_chunks
   └─ Inserta cada chunk con su embedding en la base de datos
```

## 📝 Uso Detallado

### Ejemplo Completo

```python
from src.main import store_document_chunks

async def procesar_documento():
    # 1. Primero, sube el documento a classroom_documents
    doc_data = {
        "classroom_id": "tu-classroom-id",
        "name": "Mi Documento.pdf",
        "content": "Contenido completo del documento...",
        "file_type": "application/pdf"
    }
    
    doc_result = await supabase_client.client.table("classroom_documents").insert(doc_data).execute()
    document_id = doc_result.data[0]['id']
    
    # 2. Procesa el documento automáticamente
    result = await store_document_chunks(
        classroom_document_id=document_id,
        chunk_size=1000,      # 1000 caracteres por chunk
        chunk_overlap=200     # 200 caracteres de overlap
    )
    
    # 3. Verifica el resultado
    if result["success"]:
        print(f"✅ Documento procesado en {result['total_chunks']} chunks")
        for chunk in result['chunks']:
            print(f"   - Chunk {chunk['chunk_index']}: {chunk['chunk_id']}")
    else:
        print(f"❌ Error: {result['error']}")
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `classroom_document_id` | `str` | **Requerido** | UUID del documento en `classroom_documents` |
| `chunk_size` | `int` | `1000` | Tamaño máximo de caracteres por chunk |
| `chunk_overlap` | `int` | `200` | Caracteres de solapamiento entre chunks consecutivos |

### Respuesta

```python
{
    "success": True,
    "message": "Documento procesado y almacenado en 5 chunks",
    "classroom_document_id": "xxx-xxx-xxx",
    "total_chunks": 5,
    "chunks": [
        {
            "chunk_id": "chunk-id-1",
            "chunk_index": 0,
            "content_length": 987
        },
        # ... más chunks
    ],
    "document_length": 4523,
    "chunk_size": 1000,
    "chunk_overlap": 200
}
```

## 🎯 Recomendaciones de Uso

### Tamaño de Chunks

- **Documentos pequeños (< 5KB):** `chunk_size=500`, `chunk_overlap=100`
- **Documentos medianos (5KB - 50KB):** `chunk_size=1000`, `chunk_overlap=200` (default)
- **Documentos grandes (> 50KB):** `chunk_size=2000`, `chunk_overlap=300`

### Overlap

El overlap es importante para:
- Mantener contexto entre chunks
- Mejorar la búsqueda semántica
- Evitar perder información en los bordes

**Regla general:** El overlap debe ser 15-20% del chunk_size

## 🧪 Testing

Ejecuta el test incluido:

```bash
python test_store_document_chunks.py
```

Este test:
1. Crea un documento de prueba
2. Lo procesa con `store_document_chunks`
3. Verifica que los chunks se guardaron correctamente
4. Muestra estadísticas detalladas

## 🔍 Búsqueda de Chunks

Después de almacenar los chunks, puedes buscarlos usando:

```python
# Buscar chunks similares a una consulta
result = await search_similar_chunks(
    query_text="¿Qué es la inteligencia artificial?",
    classroom_id="tu-classroom-id",
    limit=5
)

# Los resultados incluyen los chunks más relevantes con sus embeddings
```

## 📚 Relación con Otras Funciones

```
store_document_chunks()
    ↓
    ├─→ generate_embedding()     # Genera embeddings
    └─→ supabase_client          # Almacena en DB
    
search_similar_chunks()
    ↓
    └─→ Usa los chunks almacenados para búsqueda semántica
```

## ⚠️ Notas Importantes

1. **Prerequisito:** El documento debe existir en `classroom_documents` y estar subido al Storage de Supabase
2. **Tipos de archivo soportados:**
   - ✅ **text/plain** - Archivos de texto plano (completamente soportado)
   - ⚠️ **application/pdf** - PDFs (requiere extracción previa de texto y guardarlo en `text_excerpt`)
   - ⚠️ Otros formatos requieren procesamiento adicional
3. **Límites:** Ten en cuenta los límites de rate de la API de Gemini para embeddings
4. **Chunks existentes:** Si ya existen chunks para un documento, considera eliminarlos primero
5. **Encoding:** La función maneja automáticamente el encoding UTF-8
6. **Storage:** El documento debe estar en el bucket especificado en la columna `bucket` (por defecto: `classroom-documents`)

## 🐛 Troubleshooting

### Error: "No se encontró el documento"
- Verifica que el `classroom_document_id` sea correcto
- Asegúrate de que el documento existe en la tabla `classroom_documents`

### Error: "El documento no tiene información de storage"
- Verifica que el documento tenga valores en las columnas `bucket` y `storage_path`
- Asegúrate de que el archivo fue subido correctamente al Storage de Supabase

### Error: "Error descargando archivo desde Storage"
- Verifica que el archivo existe en el bucket especificado
- Revisa los permisos de acceso al Storage
- Confirma que el `storage_path` es correcto

### Error: "PDF processing no implementado"
- Para PDFs, primero extrae el texto usando una librería como `PyPDF2` o `pdfplumber`
- Guarda el texto extraído en la columna `text_excerpt` de `classroom_documents`
- O procesa el PDF por separado antes de llamar esta función

### Error: "No se pudo decodificar el archivo como texto"
- Verifica que el archivo sea de tipo texto (text/plain)
- Para otros formatos, convierte el contenido a texto plano primero
- Asegúrate de que el encoding del archivo sea UTF-8

### Chunks no aparecen en búsquedas
- Verifica que los embeddings se generaron correctamente
- Revisa los logs para ver si hubo errores al generar embeddings
- Asegúrate de que la tabla `classroom_document_chunks` tiene la columna `embedding` configurada correctamente

## 📞 Soporte

Para problemas o preguntas sobre esta función, revisa:
- `src/main.py` - Implementación de la función
- `test_store_document_chunks.py` - Ejemplos de uso
- Logs del servidor MCP para debugging
