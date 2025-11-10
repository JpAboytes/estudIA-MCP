<div align="center">

# 📚 EstudIA MCP Server

Servidor MCP (Model Context Protocol) y API educativa para gestión inteligente de documentos por aula (classroom), búsqueda semántica, OCR, personalización automática del perfil del estudiante y asistente conversacional con RAG.

**Estado:** Activo · **Versión:** 2.0.0 · **Stack principal:** Python · FastMCP · Supabase · Google Gemini

</div>

---

## 🧠 Visión General

EstudIA MCP convierte un conjunto de documentos educativos (PDF, imágenes, texto plano) en una base de conocimiento consultable mediante:

1. Ingesta automática y chunking con embeddings.
2. OCR para imágenes (apuntes, pizarrón, capturas) usando Gemini Vision.
3. Búsqueda semántica enfocada por aula (classroom) vía funciones RPC en Supabase.
4. Chat contextual estilo NotebookLM que cita internamente los fragmentos relevantes sin exponer datos técnicos.
5. Personalización dinámica del estudiante mediante análisis de conversaciones (actualización incremental del `user_context`).
6. Herramientas MCP accesibles para agentes o integraciones externas + API HTTP opcional para pruebas rápidas.

---

## ✨ Características Clave

- 🔍 Búsqueda semántica de chunks por aula (`search_similar_chunks`).
- 🧩 Procesamiento y almacenamiento automatizado de documentos (`store_document_chunks`).
- 🖼️ OCR inteligente para imágenes con Gemini Vision (ver `OCR_FUNCTIONALITY.md`).
- 💬 Asistente contextual personalizado por aula (`chat_with_classroom_assistant`).
- 👤 Actualización automática del perfil del estudiante (`analyze_and_update_user_context`).
- 🧠 Generación de embeddings consistente vía Gemini (`generate_embedding`).
- 📦 Arquitectura MCP: cada herramienta lista para ser invocada por clientes compatibles.
- 🧪 Suite de tests (`test_*.py`) para validar ingestión, contexto y herramientas.

---

## 🏗️ Arquitectura (Alto Nivel)

```mermaid
flowchart LR
    A[Upload Documento
    (Supabase Storage)] --> B[Registro
    classroom_documents]
    B --> C[store_document_chunks()
    - OCR si imagen
    - PyPDF2 si PDF
    - Limpieza texto
    - Chunk + Embeddings]
    C --> D[(classroom_document_chunks)]
    D --> E[search_similar_chunks() RPC]
    E --> F[chat_with_classroom_assistant]
    F --> G[Gemini LLM]
    H[cubicle_messages] --> I[analyze_and_update_user_context]
    I --> J[(users.user_context)]
    G --> F
```

**Componentes principales:**

- `Gemini`: Generación de texto, embeddings y OCR.
- `Supabase`: Persistencia (usuarios, documentos, chunks, mensajes) y RPCs de búsqueda vectorial.
- `FastMCP`: Registro y exposición de herramientas y prompts.
- `FastAPI` (opcional): Capa HTTP para pruebas manuales.

---

## 📁 Estructura del Repositorio

| Ruta | Descripción |
|------|-------------|
| `src/main.py` | Registro de herramientas MCP y lógica principal. |
| `src/gemini.py` | Cliente Gemini (texto, embeddings, OCR, análisis). |
| `src/supabase_client.py` | Funciones de acceso y búsquedas contra Supabase. |
| `src/http_server.py` | API REST opcional (FastAPI). |
| `src/config.py` | Carga y validación de variables de entorno. |
| `src/modelDemo/` | Scripts y dataset de ejemplo ML (legado). |
| `server.py` | Entry de deployment (exporta `mcp`). |
| `run_server.py` | Arranque rápido del servidor MCP. |
| `run_http_server.py` | Arranque rápido de la API HTTP. |
| `CONTEXT_UPDATE_TOOL.md` | Documentación de la herramienta de contexto. |
| `OCR_FUNCTIONALITY.md` | Documentación de OCR. |
| `STORE_DOCUMENT_CHUNKS_UPDATE.md` | Evolución del flujo de chunking. |

---

## 🔐 Variables de Entorno

Crear `.env` en la raíz (sin comillas):

```env
SUPABASE_URL=https://TU_PROYECTO.supabase.co
SUPABASE_SERVICE_ROLE_KEY=super-secreto
GEMINI_API_KEY=ya_lo_sabes
PORT=8000
NODE_ENV=development
GEMINI_MODEL=gemini-2.0-flash
GEMINI_EMBED_MODEL=gemini-embedding-001
EMBED_DIM=768
SIMILARITY_THRESHOLD=0.6
TOPK_DOCUMENTS=6
```

> Nunca publiques `SUPABASE_SERVICE_ROLE_KEY` ni `GEMINI_API_KEY`. Usa gestores de secretos en producción.

---

## 🧩 Instalación (Local)

```powershell
git clone <repo-url>
cd estudIA-MCP
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Para la API HTTP (si no estuviera ya incluida en `requirements.txt`):

```powershell
pip install fastapi uvicorn[standard]
```

Crear archivo `.env` con las claves requeridas.

---

## 🚀 Ejecución

### Modo MCP (herramientas para agentes)

```powershell
python run_server.py
```

El objeto `mcp` expuesto en `server.py` permite también ejecutar:

```powershell
fastmcp run server.py
```

### Modo HTTP (pruebas REST)

```powershell
python run_http_server.py
```

Endpoints clave:

| Endpoint | Uso |
|----------|-----|
| `/health` | Estado y conectividad. |
| `/api/chat` | Chat con asistente contextual. |
| `/api/search` | Búsqueda semántica de documentos. |
| `/api/user-context` | Recuperar contexto del estudiante. |

---

## 🛠️ Herramientas MCP Destacadas

| Tool | Propósito |
|------|-----------|
| `generate_embedding(text)` | Obtiene embedding de un texto. |
| `store_document_chunks(classroom_document_id, chunk_size, chunk_overlap)` | Ingesta completa automática. |
| `search_similar_chunks(query_text, classroom_id)` | Recupera fragmentos relevantes. |
| `chat_with_classroom_assistant(request)` | Chat RAG personalizado (usa documentos + perfil). |
| `analyze_and_update_user_context(user_id, session_id)` | Actualiza perfil educativo. |

> Revisa `src/main.py` para parámetros y respuesta detallada de cada herramienta.

---

## 🔎 Flujo de Ingesta y Búsqueda

1. Subes archivo a Supabase Storage y creas registro en `classroom_documents`.
2. Llamas `store_document_chunks(classroom_document_id)`.
3. Se detecta tipo (imagen/PDF/texto) → OCR o extracción.
4. Limpieza, división en chunks y generación de embeddings.
5. Inserción en `classroom_document_chunks`.
6. Consulta con `search_similar_chunks` durante el chat.

---

## 🖼️ OCR (Gemini Vision)

- Soporta: JPG, JPEG, PNG, GIF, WEBP, BMP, HEIC/HEIF.
- Extrae texto estructurado (intenta mantener párrafos / tablas simples).
- Si PDF no tiene texto embebido, intenta fallback OCR.

Ver detalles y buenas prácticas en `OCR_FUNCTIONALITY.md`.

---

## 🧠 Personalización de Estudiantes

La herramienta `analyze_and_update_user_context` analiza toda la conversación (tabla `cubicle_messages`) y decide si incorpora nueva información relevante (nivel educativo, estilo de aprendizaje, intereses, objetivos, fortalezas, etc.).

Formato de respuesta y criterios: ver `CONTEXT_UPDATE_TOOL.md`.

---

## 🗄️ Esquema de Datos (Resumen)

| Tabla | Campos Clave | Función |
|-------|--------------|---------|
| `users` | `id`, `name`, `email`, `user_context` | Perfil + contexto enriquecido. |
| `classroom_documents` | `id`, `classroom_id`, `title`, `storage_path`, `mime_type` | Metadatos de documentos. |
| `classroom_document_chunks` | `id`, `classroom_document_id`, `chunk_index`, `content`, `embedding` | Fragmentos indexables. |
| `cubicle_messages` | `id`, `session_id`, `user_id`, `content`, `created_at` | Conversación para análisis. |

---

## 🧪 Pruebas

Instalar pytest si no está:

```powershell
pip install pytest
pytest -q
```

Tests relevantes:

- `test_store_document_chunks.py` — Ingesta y chunking.
- `test_search_pdf.py` / `test_pdf_chunks_simple.py` — Búsquedas y fragmentación.
- `test_user_context_update.py` — Actualización de contexto.
- `test_ocr_functionality.py` — Flujo OCR.

> Puedes exportar `TESTING=1` para omitir validaciones estrictas en `config.py` durante pruebas controladas.

---

## 🧯 Troubleshooting Rápido

| Problema | Causa Común | Solución |
|----------|-------------|----------|
| Variables faltantes | `.env` incompleto | Revisar sección Variables de Entorno. |
| RPC no existe | Función en Supabase no creada | Crear `match_classroom_chunks` / `match_documents`. |
| OCR vacío | Imagen ilegible | Mejorar iluminación / resolución. |
| Embedding error | Modelo/clave inválida | Verificar `GEMINI_API_KEY` y nombres de modelo. |
| Búsqueda sin resultados | Umbral muy alto | Ajustar `SIMILARITY_THRESHOLD` (0.5–0.6). |

---

## 📈 Roadmap Sugerido

- [ ] Normalizar nombres (remover referencias fiscales legadas).
- [ ] `.env.example` en el repositorio.
- [ ] Dockerfile + docker-compose para desarrollo rápido.
- [ ] CI (GitHub Actions) con lint + tests.
- [ ] Cache de embeddings para evitar recomputaciones.
- [ ] Batch ingest para múltiples documentos.
- [ ] Mejor soporte PDF escaneado multipágina.
- [ ] Métricas de uso (prometheus / logs estructurados).

---

## 🤝 Contribuir

1. Fork & branch descriptiva (`feat/ocr-batch`).
2. Añade tests para nueva lógica pública.
3. Ejecuta suite (`pytest -q`).
4. Haz PR incluyendo descripción clara y motivación.

Estilo: seguir convenciones existentes, mantener español técnico claro. Documenta cambios significativos en este README.

---

## 🛡️ Licencia

Si aún no hay licencia definida, se recomienda añadir una (MIT/Apache 2.0). Hasta entonces, el código se considera con derechos reservados del autor original.

---

## 📌 Resumen Rápido (TL;DR)

Sube documento → `store_document_chunks` → chunks + embeddings → `search_similar_chunks` → chat contextual y personalizable → contexto de estudiante se enriquece con `analyze_and_update_user_context`.

---

¿Necesitas añadir Docker / `.env.example` / scripts de utilidades? Pídelo y lo agrego enseguida.

---

<sub>README generado automáticamente analizando código y docs existentes (2025-11-09).</sub>
