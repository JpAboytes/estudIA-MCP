# estudIA-MCP
RAG + FastMCP - Servidor MCP con Supabase y Gemini

## 🚀 Descripción

Servidor MCP (Model Context Protocol) que integra:
- **Google Gemini** para generación de embeddings
- **Supabase** para almacenamiento vectorial
- **FastMCP** para exponer herramientas via MCP

## 📋 Requisitos

- Python >= 3.10
- Cuenta de Google Cloud con API de Gemini habilitada
- Proyecto de Supabase configurado

## 🔧 Instalación

1. **Clonar el repositorio**
```bash
git clone <tu-repo>
cd estudIA-MCP
```

2. **Crear entorno virtual**
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -e .
```

4. **Configurar variables de entorno**

**⚠️ IMPORTANTE**: Hay dos formas diferentes de configurar las variables según cómo ejecutes el servidor:

### 🏠 Para desarrollo local (Python directo):
```bash
# Copiar el archivo de ejemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edita `.env` con tus credenciales:
```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key_aqui
GEMINI_API_KEY=tu_gemini_api_key
```

### 🚀 Para FastMCP / Claude Desktop / MCP Clients:
Las variables deben estar en el sistema operativo o en la configuración MCP.

**Ver [ENV_CONFIG.md](./ENV_CONFIG.md) para instrucciones detalladas por plataforma.**

5. **Configurar Supabase**

Ve al SQL Editor en tu proyecto de Supabase y ejecuta el contenido de `supabase_setup.sql`

## 🎯 Herramientas Disponibles

### 1. `generate_embedding`
Genera un vector embedding a partir de texto usando Gemini.

**Parámetros:**
- `text` (string): Texto para convertir en embedding

**Ejemplo:**
```python
{
  "text": "Este es un texto de ejemplo para generar embedding"
}
```

### 2. `store_embedding`
Genera un embedding y lo almacena en Supabase.

**Parámetros:**
- `text` (string): Texto para convertir y almacenar
- `table_name` (string, opcional): Nombre de la tabla (default: "embeddings")
- `metadata` (dict, opcional): Metadata adicional

**Ejemplo:**
```python
{
  "text": "Contenido del documento",
  "metadata": {"source": "documento.pdf", "page": 1}
}
```

### 3. `search_similar`
Busca documentos similares usando búsqueda vectorial.

**Parámetros:**
- `query_text` (string): Texto de búsqueda
- `table_name` (string, opcional): Nombre de la tabla
- `limit` (int, opcional): Número de resultados (default: 5)
- `threshold` (float, opcional): Umbral de similitud 0-1 (default: 0.7)

**Ejemplo:**
```python
{
  "query_text": "¿Qué es la inteligencia artificial?",
  "limit": 3,
  "threshold": 0.75
}
```

## 🏃 Ejecutar

```bash
python main.py
```

## 🔗 Integración con Claude Desktop

Agrega esto a tu configuración de Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "estudIA": {
      "command": "python",
      "args": ["c:/Users/Hp/Desktop/estudIA-MCP/main.py"],
      "env": {
        "SUPABASE_URL": "tu_url",
        "SUPABASE_KEY": "tu_key",
        "GEMINI_API_KEY": "tu_key"
      }
    }
  }
}
```

## 📚 Recursos

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Supabase Vector](https://supabase.com/docs/guides/ai/vector-columns)
- [Google Gemini API](https://ai.google.dev/docs)

## 📝 Notas

- Los embeddings de Gemini tienen 768 dimensiones
- Asegúrate de tener habilitada la extensión `pgvector` en Supabase
- La función `match_documents` debe estar creada en tu base de datos

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor abre un issue primero para discutir los cambios.

## 📄 Licencia

MIT

