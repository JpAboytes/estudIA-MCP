# Nuevas Herramientas de Embeddings y Almacenamiento

Este documento describe las tres nuevas herramientas agregadas al servidor MCP de FiscAI para manejo de embeddings y almacenamiento de documentos.

## 🎯 Resumen

Se agregaron **3 nuevas herramientas** que permiten:

1. **`generate_embedding`** - Generar vectores de embeddings desde texto
2. **`store_document`** - Almacenar documentos con embeddings en Supabase
3. **`search_similar_documents`** - Buscar documentos similares usando embeddings

## 📋 Herramientas Implementadas

### 1. `generate_embedding`

**Propósito:** Convierte texto en un vector numérico (embedding) que captura su significado semántico.

**Parámetros:**
- `text` (str, requerido): El texto a convertir en embedding

**Retorna:**
```json
{
  "success": true,
  "embedding": [0.123, -0.456, ...],  // Vector de números
  "dimension": 768,
  "text_length": 150,
  "model": "gemini-embedding-001",
  "text_preview": "Preview del texto..."
}
```

**Ejemplo de uso:**
```python
result = await generate_embedding(
    text="Régimen Simplificado de Confianza para pequeños negocios"
)

if result['success']:
    embedding_vector = result['embedding']
    print(f"Dimensiones: {result['dimension']}")
```

**Características:**
- ✅ Usa Google Gemini Embeddings (`gemini-embedding-001`)
- ✅ Respeta la configuración de dimensiones en `config.EMBED_DIM`
- ✅ Logging detallado del proceso
- ✅ Manejo robusto de errores con hints útiles

---

### 2. `store_document`

**Propósito:** Genera el embedding de un texto y lo almacena en la base de datos de Supabase junto con metadata.

**Parámetros:**
- `text` (str, requerido): Contenido del documento
- `classroom_id` (str, opcional): UUID del classroom para filtrado
- `title` (str, opcional): Título del documento
- `scope` (str, opcional): Categoría del documento (ej: "regimenes", "obligaciones")
- `source_url` (str, opcional): URL de origen del documento

**Retorna:**
```json
{
  "success": true,
  "message": "Documento almacenado exitosamente",
  "document_id": "uuid-del-documento",
  "classroom_id": "uuid-del-classroom",
  "title": "Título del documento",
  "scope": "regimenes",
  "embedding_dimension": 768,
  "content_preview": "Preview del contenido..."
}
```

**Ejemplo de uso:**
```python
result = await store_document(
    text="El RESICO es un régimen fiscal para pequeños contribuyentes...",
    title="Información sobre RESICO",
    scope="regimenes",
    source_url="https://www.sat.gob.mx/resico"
)

if result['success']:
    doc_id = result['document_id']
    print(f"Documento guardado con ID: {doc_id}")
```

**Características:**
- ✅ Genera automáticamente el embedding del texto
- ✅ Soporta metadata opcional para mejor organización
- ✅ Filtrado por classroom_id para multi-tenancy
- ✅ Validación de errores de dimensiones y claves foráneas

---

### 3. `search_similar_documents`

**Propósito:** Busca documentos similares en la base de datos usando búsqueda semántica por embeddings.

**Parámetros:**
- `query_text` (str, requerido): Texto de consulta para buscar
- `classroom_id` (str, opcional): Filtrar por classroom específico
- `limit` (int, opcional): Número máximo de resultados (default: 5)
- `threshold` (float, opcional): Umbral de similitud 0-1 (default: 0.6)

**Retorna:**
```json
{
  "success": true,
  "query": "¿Qué régimen me conviene?",
  "results": [
    {
      "id": "uuid",
      "title": "RESICO - Régimen Simplificado",
      "content": "El RESICO es...",
      "scope": "regimenes",
      "source_url": "https://...",
      "similarity": 0.89
    }
  ],
  "count": 5,
  "threshold_used": 0.6,
  "embedding_dimension": 768
}
```

**Ejemplo de uso:**
```python
result = await search_similar_documents(
    query_text="¿Qué régimen fiscal me conviene para mi negocio pequeño?",
    limit=5,
    threshold=0.7
)

if result['success']:
    for doc in result['results']:
        print(f"{doc['title']} - Similitud: {doc['similarity']:.2f}")
```

**Características:**
- ✅ Búsqueda global o filtrada por classroom
- ✅ Control de threshold de similitud
- ✅ Usa funciones RPC de Supabase (`match_documents`, `match_documents_by_classroom`)
- ✅ Retorna documentos ordenados por similitud

---

## 🔧 Configuración Requerida

### Variables de Entorno

Estas herramientas usan las variables de entorno ya configuradas en tu proyecto:

```env
# Gemini AI
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_EMBED_MODEL=gemini-embedding-001

# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key

# Configuración de embeddings
EMBED_DIM=768
SIMILARITY_THRESHOLD=0.6
TOPK_DOCUMENTS=6
```

### Tabla en Supabase

✅ **Tu proyecto usa la tabla `fiscai_documents`** (no `documents`).

La tabla debe tener esta estructura:

```sql
CREATE TABLE fiscai_documents (
  id SERIAL PRIMARY KEY,  -- O UUID según tu diseño
  content TEXT NOT NULL,
  embedding VECTOR(768),  -- Debe coincidir con EMBED_DIM
  title TEXT NOT NULL,    -- Requerido en tu base de datos
  scope TEXT,
  source_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para búsqueda rápida
CREATE INDEX ON fiscai_documents USING ivfflat (embedding vector_cosine_ops);
```

**Nota:** El campo `title` es **requerido** en tu base de datos actual.

### Funciones RPC en Supabase

Para `search_similar_documents`, necesitas estas funciones SQL:

**1. match_documents (búsqueda global):**

```sql
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding VECTOR(768),
  match_threshold FLOAT,
  match_count INT
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  title TEXT,
  scope TEXT,
  source_url TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    documents.id,
    documents.content,
    documents.title,
    documents.scope,
    documents.source_url,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

**2. match_documents_by_classroom (búsqueda filtrada):**

```sql
CREATE OR REPLACE FUNCTION match_documents_by_classroom(
  query_embedding VECTOR(768),
  match_threshold FLOAT,
  match_count INT,
  filter_classroom_id UUID
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  title TEXT,
  scope TEXT,
  source_url TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    documents.id,
    documents.content,
    documents.title,
    documents.scope,
    documents.source_url,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE 
    classroom_id = filter_classroom_id
    AND 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

---

## 🧪 Pruebas

Se incluye un archivo de prueba `test_new_tools.py` que verifica:

1. ✅ Generación de embeddings válidos
2. ✅ Almacenamiento de documentos con/sin metadata
3. ✅ Búsqueda de documentos similares

**Ejecutar las pruebas:**

```powershell
python test_new_tools.py
```

---

## 🔄 Integración con el Proyecto Actual

Las nuevas herramientas se integran perfectamente con tu arquitectura existente:

### ✅ Usa tu sistema de configuración
```python
from .config import config

# Accede a:
config.GEMINI_API_KEY
config.GEMINI_EMBED_MODEL
config.EMBED_DIM
config.SIMILARITY_THRESHOLD
```

### ✅ Usa tus clientes existentes
```python
from .gemini import gemini_client
from .supabase_client import supabase_client

# Reutiliza los métodos existentes:
embedding = await gemini_client.generate_embedding(text)
docs = await supabase_client.search_similar_documents(embedding, limit)
```

### ✅ Sigue tu patrón de herramientas
```python
@mcp.tool()
async def generate_embedding(text: str) -> Dict[str, Any]:
    """Docstring descriptiva"""
    print(f"{'='*60}")  # Logging consistente
    # ... implementación
    return {"success": True, "data": ...}
```

---

## 📊 Flujo de Trabajo Típico

### Caso de Uso: Agregar nuevo contenido fiscal

```python
# 1. Generar y almacenar documento
result = await store_document(
    text="Contenido sobre obligaciones fiscales...",
    title="Obligaciones del RESICO",
    scope="obligaciones",
    source_url="https://www.sat.gob.mx/..."
)

# 2. Buscar documentos relacionados
search_result = await search_similar_documents(
    query_text="¿Cuáles son mis obligaciones fiscales?",
    limit=5
)

# 3. Usar en RAG (tu flujo actual)
# Los documentos encontrados se pueden usar en get_fiscal_advice
```

---

## ⚠️ Notas Importantes

### Dimensiones de Embeddings

- El modelo `gemini-embedding-001` genera embeddings de **768 dimensiones** por defecto
- Asegúrate de que `EMBED_DIM=768` en tu `.env`
- La tabla y funciones de Supabase deben usar `VECTOR(768)`

### Manejo de Errores

Todas las herramientas retornan:
- `success: true/false` - Indica si la operación fue exitosa
- `error` - Mensaje de error si falló
- `hint` - Sugerencia para resolver el problema

### Performance

- Las búsquedas son rápidas gracias al índice IVFFlat en Supabase
- El threshold por defecto (0.6) es un buen balance entre precisión y recall
- Ajusta el `limit` según tus necesidades (5-10 es típico)

---

## 🎉 Beneficios

1. **Reutilización de código**: Usa tu infraestructura existente
2. **Logging consistente**: Mismo formato que tus otras herramientas
3. **Manejo robusto de errores**: Mensajes claros y hints útiles
4. **Flexible**: Soporta metadata opcional y filtrado
5. **Escalable**: Preparado para multi-tenancy con classroom_id

---

## 📚 Referencias

- [Google Gemini Embeddings](https://ai.google.dev/docs/embeddings_guide)
- [Supabase Vector Search](https://supabase.com/docs/guides/ai/vector-columns)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

---

**Última actualización:** 3 de noviembre, 2025
**Versión:** 1.0.0
