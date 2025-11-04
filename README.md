# EstudIA MCP Server 📚# FiscAI MCP — FiscMCP



**Sistema tipo NotebookLM para gestión inteligente de documentos educativos por aula**README profesional (en español) para el proyecto FiscMCP. Este documento explica qué hace el proyecto, cómo instalarlo y ejecutarlo, cómo configurarlo y pasos de desarrollo y despliegue.



EstudIA es un servidor MCP (Model Context Protocol) que permite a estudiantes y profesores subir documentos educativos, procesarlos automáticamente y hacer preguntas sobre ellos usando IA. Similar a Google NotebookLM pero organizado por aulas/classrooms.## Descripción



## ✨ Características principalesFiscAI MCP (FiscMCP) es un servidor de herramientas (MCP) orientado a ofrecer asesoría fiscal y financiera para micro y pequeñas empresas en México. Combina:



- 📄 **Gestión de documentos por aula**: Cada classroom tiene sus propios documentos- Un motor de inteligencia artificial (Google Gemini) para generación de lenguaje y embeddings.

- 🤖 **Chat inteligente**: Pregunta sobre los documentos y obtén respuestas contextualizadas- Un backend de búsqueda semántica y almacenamiento (Supabase) para RAG (Retrieval-Augmented Generation).

- 🔍 **Búsqueda semántica**: Encuentra información relevante usando embeddings- Herramientas para: recomendaciones fiscales, chat asistido, análisis de riesgo, búsqueda de documentos, roadmap de formalización, predicción de crecimiento (modelo ML) y apertura de mapas (deep links).

- 🧩 **Procesamiento en chunks**: Los documentos se dividen en fragmentos para búsqueda eficiente

- 💬 **Asistente educativo**: IA especializada en responder preguntas académicasEl núcleo está implementado con `fastmcp` (instancia `mcp` en `src/main.py`) y ofrece además un servidor HTTP opcional (`src/http_server.py`) para probar endpoints REST.

- 📊 **Estadísticas por aula**: Visualiza documentos, chunks y estado de procesamiento

## Características principales

## 🏗️ Arquitectura

- Recomendaciones fiscales personalizadas gracias a RAG (embeddings + documentos relevantes).

```- Chat asistido con detección automática de intención (por ejemplo, abrir mapa para bancos o SAT).

EstudIA MCP Server- Búsqueda semántica de documentos fiscales en Supabase.

├── Google Gemini AI- Análisis de riesgo fiscal y generación de roadmap de formalización.

│   ├── Embeddings (text-embedding-004)- Predicción de crecimiento del negocio con un modelo entrenado (en `src/modelDemo`).

│   └── Chat/Generación (gemini-2.0-flash)- **NUEVO:** Herramientas de embeddings y almacenamiento (`generate_embedding`, `store_document`, `search_similar_documents`) - Ver [NUEVAS_HERRAMIENTAS.md](./NUEVAS_HERRAMIENTAS.md)

├── Supabase Database

│   ├── classrooms (aulas/salones)## Estructura del repositorio (resumen)

│   ├── classroom_documents (documentos subidos)

│   └── classroom_document_chunks (fragmentos con embeddings)- `run_server.py` — Entrypoint para ejecutar el servidor MCP (modo FastMCP).

└── FastMCP (Model Context Protocol)- `run_http_server.py` — Script para ejecutar el servidor HTTP (FastAPI + Uvicorn).

```- `server.py` — Archivo preparado para deployment (exporta `mcp` para detectores automáticos).

- `requirements.txt` — Dependencias del proyecto.

## 📋 Herramientas disponibles- `src/` — Código fuente principal:

  - `main.py` — Registro de herramientas MCP (`@mcp.tool()` y prompts `@mcp.prompt()`).

### 1. `generate_embedding`  - `http_server.py` — API REST para probar herramientas.

Genera un vector embedding de texto para búsqueda semántica.  - `gemini.py` — Cliente e integración con Google Gemini (LLM & embeddings).

  - `supabase_client.py` — Cliente para Supabase (búsqueda semántica, historial de chat, etc.).

```python  - `places.py` — Integración con Google Places para búsqueda de ubicaciones.

result = await generate_embedding(  - `config.py` — Carga de variables de entorno y validaciones.

    text="Introducción a la Inteligencia Artificial"  - `modelDemo/` — Datos y scripts de ejemplo para el modelo ML (entrenamiento y demo).

)- `test_*.py` — Suites de tests unitarios y de integración (varios archivos `test_*.py`).

# Returns: { success: True, embedding: [...], dimension: 768 }

```## Requisitos



### 2. `store_document_chunk`- Python 3.10+ (preferible).

Almacena un fragmento de documento con su embedding.- Pip.

- Acceso a las APIs externas usadas:

```python  - Google Gemini (clave `GEMINI_API_KEY`)

result = await store_document_chunk(  - Supabase (URL y service role key)

    classroom_document_id="uuid-del-documento",  - Google Places API (para búsqueda de lugares)

    chunk_index=0,

    content="Contenido del fragmento...",Dependencias listadas en `requirements.txt`. Adicionalmente para el servidor HTTP se recomienda instalar `fastapi` y `uvicorn[standard]`.

    token_count=150  # opcional

)## Variables de entorno (principales)

```

Configurar en un archivo `.env` en la raíz del proyecto o en el entorno del sistema:

### 3. `search_similar_chunks`

Busca fragmentos similares dentro de un classroom usando búsqueda semántica.- SUPABASE_URL — URL del proyecto Supabase.

- SUPABASE_SERVICE_ROLE_KEY — Service role key para Supabase (se usa para RPCs/privilegios).

```python- GEMINI_API_KEY — API key para Google Gemini.

result = await search_similar_chunks(- EXPO_PUBLIC_GOOGLE_MAPS_API_KEY o GOOGLE_MAPS_API_KEY — para `places`.

    query_text="¿Qué es el aprendizaje supervisado?",- PORT — Puerto para el servidor HTTP (por defecto `8000`).

    classroom_id="uuid-del-aula",- NODE_ENV — `development` o `production`.

    limit=5,- Opcionales:

    threshold=0.6  - GEMINI_MODEL — Nombre del modelo Gemini (por defecto `gemini-2.0-flash`).

)  - GEMINI_EMBED_MODEL — Modelo de embeddings (por defecto `gemini-embedding-001`).

```  - EMBED_DIM — Dimensionalidad del embedding (por defecto `768`).

  - SIMILARITY_THRESHOLD — Umbral de similitud (por defecto `0.6`).

### 4. `chat_with_classroom_assistant`  - TOPK_DOCUMENTS — Número de documentos a recuperar (por defecto `6`).

Chat con el asistente educativo del aula (tipo NotebookLM).

Importante: No publiques claves secretas en repositorios públicos. Usa secretos en tu plataforma de despliegue.

```python

result = await chat_with_classroom_assistant({## Instalación (local)

    "message": "Explícame el concepto de redes neuronales",

    "classroom_id": "uuid-del-aula",1. Clona el repositorio y navega a la carpeta:

    "user_id": "uuid-del-usuario"  # opcional

})```powershell

```cd C:\Users\Owner\Downloads\FiscMCP

```

### 5. `get_classroom_info`

Obtiene información y estadísticas de un classroom.2. (Opcional) Crea y activa un entorno virtual:



```python```powershell

result = await get_classroom_info(python -m venv .venv; .\.venv\Scripts\Activate.ps1

    classroom_id="uuid-del-aula"```

)

```3. Instala las dependencias:



## 🚀 Instalación```powershell

pip install -r requirements.txt

### Requisitos previos# Recomendado para la API HTTP (si vas a usarla):

- Python 3.10+pip install fastapi uvicorn[standard]

- Cuenta de Google Cloud (para Gemini API)```

- Proyecto Supabase configurado

4. Crea un archivo `.env` siguiendo la sección "Variables de entorno" y añade las claves necesarias.

### 1. Clonar repositorio

## Ejecución

```powershell

git clone https://github.com/JpAboytes/estudIA-MCP.gitHay dos modos principales para ejecutar el proyecto:

cd estudIA-MCP

```1) Servidor MCP (modo FastMCP)



### 2. Crear entorno virtual- Uso (desde la raíz del repo):



```powershell```powershell

python -m venv .venvpython run_server.py

.\.venv\Scripts\Activate.ps1```

```

Este script añade `src` al `PYTHONPATH` y ejecuta `main()` en `src/main.py`, que registra las herramientas y ejecuta `mcp.run()`.

### 3. Instalar dependencias

2) Servidor HTTP (FastAPI) — para probar endpoints REST

```powershell

pip install -r requirements.txt- Uso (desde la raíz del repo):

```

```powershell

### 4. Configurar variables de entornopython run_http_server.py

```

Crea un archivo `.env` en la raíz:

- El script usa `uvicorn` internamente y expondrá:

```env  - Health: http://localhost:8000/health

# Supabase  - Documentación interactiva (Swagger/OpenAPI): http://localhost:8000/docs

SUPABASE_URL=https://tu-proyecto.supabase.co  - Endpoints principales: `/api/fiscal-advice`, `/api/chat`, `/api/risk-analysis`, `/api/search`, `/api/user-context`.

SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key

Si cambias el puerto, define `PORT` en `.env`.

# Google Gemini

GEMINI_API_KEY=tu-api-key-de-gemini## Endpoints (ejemplos)



# Configuración (opcional)1) Health check

GEMINI_MODEL=gemini-2.0-flash

GEMINI_EMBED_MODEL=text-embedding-004```powershell

EMBED_DIM=768# Obtener estado

SIMILARITY_THRESHOLD=0.6Invoke-RestMethod -Method Get -Uri http://localhost:8000/health

PORT=8000```

NODE_ENV=development

```2) Solicitar recomendación fiscal (ejemplo)



### 5. Configurar base de datos Supabase```powershell

$body = @{ actividad = 'Ventas en línea'; ingresos_anuales = 300000; estado = 'CDMX' } | ConvertTo-Json

Ejecuta los scripts SQL en tu proyecto Supabase:Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/fiscal-advice -Body $body -ContentType 'application/json'

```

**Ver archivo:** `supabase_setup.sql` (incluido en el repositorio)

3) Chat con el asistente

## 🎮 Uso

```powershell

### Iniciar servidor MCP$body = @{ message = '¿Dónde está un Banorte cerca de Reforma?'; user_id = 'guest' } | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/chat -Body $body -ContentType 'application/json'

```powershell```

python run_server.py

```4) Búsqueda semántica de documentos



O usando FastMCP directamente:```powershell

$body = @{ query = 'beneficios régimen RESICO'; limit = 5 } | ConvertTo-Json

```powershellInvoke-RestMethod -Method Post -Uri http://localhost:8000/api/search -Body $body -ContentType 'application/json'

fastmcp run server.py```

```

## Cómo funciona (alto nivel)

## 🧪 Testing

- `src/main.py` registra múltiples herramientas como `@mcp.tool()` y prompts con `@mcp.prompt()` que implementan la lógica de negocio (RAG, chat, análisis de riesgo, roadmap, etc.).

Ejecutar los tests:- `src/gemini.py` encapsula la integración con Google Gemini: generación de embeddings, prompts, y lógica para el chat y RAG.

- `src/supabase_client.py` encapsula acceso a Supabase — incluye RPCs para búsqueda semántica (`match_fiscai_documents`) y tablas para historial de chat y usuarios.

```powershell- `src/places.py` usa Google Places APIs para búsquedas de establecimientos y genera `deepLink` para la app móvil (fiscai://...).

# Test completo de herramientas- `src/config.py` centraliza la configuración y valida variables de entorno críticas.

python test_estudia_tools.py

## Desarrollo y pruebas

# Tests simples

python test_simple.py- El repo contiene tests `test_*.py` para pruebas unitarias básicas. Puedes ejecutar los tests con `pytest`.

```

```powershell

## 📚 Flujo de trabajo típicopip install pytest

pytest -q

### 1. Crear un classroom```

```sql

INSERT INTO classrooms (name, subject, code) - Para desarrollo iterativo recomendamos usar un entorno virtual y reiniciar el servidor cuando cambies código.

VALUES ('IA 101', 'Inteligencia Artificial', 'IA101-2024');

```## Depuración y problemas comunes



### 2. Subir un documento- Error: "Faltan variables de entorno..." — Asegúrate de crear `.env` con `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `GEMINI_API_KEY` y `EXPO_PUBLIC_GOOGLE_MAPS_API_KEY` si usas `places`.

```sql- Error de Gemini: Verifica que `GEMINI_API_KEY` sea válida y que el modelo configurado exista en tu cuenta.

INSERT INTO classroom_documents (classroom_id, owner_user_id, storage_path, title)- Supabase: Si las funciones RPC fallan, verifica que los nombres (`match_fiscai_documents`, `match_documents`) existan en tu proyecto Supabase.

VALUES ('uuid-classroom', 'uuid-usuario', 'path/archivo.pdf', 'Introducción a IA');

```## Seguridad



### 3. Procesar documento en chunks- Nunca subas `SUPABASE_SERVICE_ROLE_KEY` ni `GEMINI_API_KEY` a repositorios públicos.

```python- Para producción, utiliza secretos gestionados por la plataforma de hosting (Vercel, Railway, Fly, AWS, etc.) en lugar de `.env` en disco.

# Dividir el documento en fragmentos (500-1000 palabras cada uno)

# Para cada chunk:## Despliegue (sugerencias rápidas)

await store_document_chunk(

    classroom_document_id="uuid-documento",- Plataformas recomendadas: Railway, Fly.io, Azure App Service, DigitalOcean App Platform.

    chunk_index=i,- Recomendación: desplegar el servidor HTTP (`run_http_server.py`) detrás de un proxy y gestionar secretos con el proveedor.

    content=chunk_text- Considerar usar contenedor Docker para portabilidad (Dockerfile no incluido — puede añadirse fácilmente).

)

```## Contribuir



### 4. Hacer preguntas- Abre issues para sugerencias o bugs.

```python- Fork + PR: agrega tests para cambios funcionales.

# Los estudiantes pueden preguntar sobre los documentos- Sigue el estilo de codificación existente y documenta cambios en `README.md` cuando alteres el comportamiento público.

response = await chat_with_classroom_assistant({

    "message": "¿Qué es una red neuronal?",## Siguientes pasos recomendados

    "classroom_id": "uuid-classroom"

})- Añadir un `Dockerfile` y `docker-compose` para facilitar despliegue local.

```- Añadir CI (GitHub Actions) que valide linting y tests.

- Añadir un ejemplo de `.env.example` con variables no sensibles (nombres de variables y descripciones).

## 🛠️ Estructura del proyecto- Mejorar la cobertura de tests para `src/gemini.py` (simular responses) y `src/supabase_client.py` (mock de RPCs).



```---

estudIA-MCP/

├── src/Resumen: he analizado la estructura y el código principal del proyecto (`src/main.py`, `src/http_server.py`, `src/gemini.py`, `src/supabase_client.py`, `src/places.py`, `src/config.py`) y he preparado este README en español con guías de instalación, configuración y uso. Si quieres, puedo:

│   ├── main.py                 # Servidor MCP principal (EstudIA)

│   ├── config.py               # Configuración- Añadir un archivo `.env.example` al repo con las variables de entorno listadas.

│   ├── gemini.py              # Cliente Google Gemini- Crear un `Dockerfile` y `docker-compose.yml` de ejemplo.

│   ├── supabase_client.py     # Cliente Supabase- Añadir un script de comprobación (makefile / ps1) para desarrollo local.

│   └── __init__.py

├── tests/Dime qué prefieres y lo implemento a continuación.
│   ├── test_estudia_tools.py  # Tests de herramientas
│   └── test_simple.py
├── legacy/                     # Código antiguo de FiscAI (no usar)
│   ├── main_fiscal_backup.py
│   └── ...
├── server.py                   # Entry point para deployment
├── run_server.py              # Script para ejecutar MCP
├── requirements.txt
├── .env.example
└── README.md
```

## 🔒 Seguridad

- ⚠️ **NUNCA** subas tu `.env` al repositorio
- Usa `SUPABASE_SERVICE_ROLE_KEY` solo en el backend
- Implementa Row Level Security (RLS) en Supabase para producción
- Valida permisos de usuarios antes de acceder a documentos

## 📝 Notas importantes

Este proyecto fue adaptado de un sistema fiscal (FiscAI). Si encuentras referencias a "FiscAI", "Juan Pablo", "SAT" o "bancos", son código legacy que debe ser removido.

Archivos legacy (NO USAR):
- `src/main_fiscal_backup.py` - Código antiguo de FiscAI
- `src/places.py` - Búsqueda de ubicaciones (no relevante para EstudIA)
- `src/http_server.py` - API REST antigua
- `src/gemini.py` - Contiene prompts fiscales que deben limpiarse

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

MIT License

## 🙏 Créditos

- Inspirado en [Google NotebookLM](https://notebooklm.google.com/)
- Construido con [FastMCP](https://github.com/jlowin/fastmcp)
- Powered by [Google Gemini](https://deepmind.google/technologies/gemini/)
- Base de datos con [Supabase](https://supabase.com/)

---

**EstudIA** - Aprende más inteligente, no más difícil 🚀
