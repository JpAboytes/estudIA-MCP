# 🔄 Migración de FiscAI a EstudIA

Este documento explica la transformación del proyecto de **FiscAI** (asesoría fiscal) a **EstudIA** (sistema educativo tipo NotebookLM).

## 📊 Resumen de cambios

### ✅ Archivos actualizados

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `README.md` | ✅ Actualizado | Ahora describe EstudIA (NotebookLM educativo) |
| `src/main.py` | ✅ OK | Ya implementa EstudIA correctamente |
| `src/config.py` | ✅ Actualizado | Comentarios actualizados a EstudIA |
| `server.py` | ✅ Actualizado | Mensajes actualizados a EstudIA |
| `supabase_setup.sql` | ✅ Creado | Setup completo de la base de datos |
| `.env.example` | ✅ Creado | Plantilla de variables de entorno |

### ⚠️ Archivos legacy (NO USAR)

Estos archivos contienen código antiguo de FiscAI y deben ser ignorados o eliminados:

| Archivo | Tipo | Contenido Legacy | Acción Recomendada |
|---------|------|------------------|-------------------|
| `src/main_fiscal_backup.py` | Legacy | Herramientas fiscales completas | 🗑️ Eliminar o mover a `/legacy` |
| `src/gemini.py` | Mixto | Prompts de "Juan Pablo" fiscal | 🔧 Necesita limpieza |
| `src/supabase_client.py` | Mixto | Búsquedas en tabla `documents` | 🔧 Necesita actualización |
| `src/places.py` | Legacy | Búsqueda de bancos/SAT | 🗑️ Eliminar o mover a `/legacy` |
| `src/http_server.py` | Legacy | API REST de FiscAI | 🗑️ Eliminar o mover a `/legacy` |
| `check_*.py` | Scripts | Scripts de verificación mixtos | ✅ OK, útiles para debugging |

## 🎯 Estructura actual vs Ideal

### 📂 Estructura ACTUAL

```
estudIA-MCP/
├── src/
│   ├── main.py ✅              # EstudIA (CORRECTO)
│   ├── config.py ✅            # Actualizado
│   ├── gemini.py ⚠️            # Contiene código fiscal legacy
│   ├── supabase_client.py ⚠️  # Busca en tabla 'documents' legacy
│   ├── places.py ❌            # FiscAI (NO RELEVANTE)
│   ├── http_server.py ❌       # FiscAI (NO RELEVANTE)
│   └── main_fiscal_backup.py ❌ # FiscAI (NO RELEVANTE)
├── test_estudia_tools.py ✅
├── README.md ✅
└── server.py ✅
```

### 📂 Estructura IDEAL

```
estudIA-MCP/
├── src/
│   ├── main.py ✅              # EstudIA MCP Server
│   ├── config.py ✅
│   ├── gemini.py ✅            # Limpio (solo embeddings + chat educativo)
│   └── supabase_client.py ✅   # Solo classroom_document_chunks
├── legacy/                      # Código antiguo de FiscAI
│   ├── main_fiscal_backup.py
│   ├── gemini_fiscal.py
│   ├── places.py
│   └── http_server.py
├── tests/
│   ├── test_estudia_tools.py
│   └── test_simple.py
├── supabase_setup.sql ✅
├── .env.example ✅
├── README.md ✅
└── server.py ✅
```

## 🔧 Tareas pendientes de limpieza

### 1. Limpiar `src/gemini.py` 🔴 PRIORITARIO

**Problemas actuales:**
- Contiene `SYSTEM_PROMPT` de "Juan Pablo" (asistente fiscal)
- Función `detect_user_intent()` busca bancos y SAT
- Referencias a `open_map_location` (no existe en EstudIA)

**Solución:**
```python
# REMOVER:
SYSTEM_PROMPT = """
Eres Juan Pablo, un asistente fiscal experto en México...
"""

def detect_user_intent(message: str) -> Dict[str, Any]:
    # Todo este código de ubicaciones/bancos/SAT

# MANTENER SOLO:
- generate_embedding() ✅
- generate_text() ✅
- Configuración de genai ✅
```

### 2. Actualizar `src/supabase_client.py` 🟡 IMPORTANTE

**Problemas actuales:**
- `search_similar_documents()` busca en tabla `documents` (legacy)
- Usa RPC `match_documents` (para FiscAI)
- Métodos como `find_similar_fiscal_cases()` no relevantes

**Solución:**
- Reemplazar búsquedas en `documents` por `classroom_document_chunks`
- Usar RPC `match_classroom_chunks` (ya existe)
- Eliminar métodos fiscales

### 3. Mover archivos legacy 🟢 OPCIONAL

```powershell
# Crear carpeta legacy
mkdir legacy

# Mover archivos de FiscAI
Move-Item src/main_fiscal_backup.py legacy/
Move-Item src/places.py legacy/
Move-Item src/http_server.py legacy/

# Opcional: crear README en legacy
```

## 🗄️ Base de datos

### Tablas que SÍ usa EstudIA ✅

```sql
classrooms                    -- Aulas/salones
classroom_documents           -- Documentos por aula
classroom_document_chunks     -- Fragmentos con embeddings
```

### Tablas legacy (NO USADAS) ⚠️

```sql
documents                     -- Tabla antigua de FiscAI (15 registros)
```

**Recomendación:** 
- Mantener por ahora (15 registros no molestan)
- En el futuro: migrar a `classroom_documents` si es necesario
- O simplemente ignorar

### Funciones RPC

**Usadas por EstudIA:**
- ✅ `match_classroom_chunks` - Búsqueda en EstudIA
- ✅ `match_document_chunks` - Búsqueda en documento específico

**Legacy (FiscAI):**
- ⚠️ `match_documents` - Busca en tabla `documents` antigua
- ⚠️ `match_documents_by_classroom` - Variante antigua

## 📋 Checklist de migración completa

- [x] README actualizado
- [x] server.py actualizado
- [x] config.py actualizado
- [x] supabase_setup.sql creado
- [x] .env.example creado
- [ ] Limpiar src/gemini.py (remover código fiscal)
- [ ] Actualizar src/supabase_client.py (usar classroom_document_chunks)
- [ ] Mover archivos legacy a carpeta /legacy
- [ ] Eliminar referencias a FiscAI en código
- [ ] Actualizar tests si es necesario

## 🚀 Próximos pasos recomendados

### Inmediato (esta semana)
1. ✅ Leer este documento completo
2. 🔄 Decidir qué hacer con archivos legacy (mover o eliminar)
3. 🔧 Limpiar `src/gemini.py`
4. 🔧 Actualizar `src/supabase_client.py`

### Corto plazo (próximas 2 semanas)
1. 🧪 Crear más tests específicos de EstudIA
2. 📝 Documentar API completa
3. 🎨 Crear ejemplos de uso
4. 🐳 Crear Dockerfile para deployment

### Largo plazo (próximo mes)
1. 🌐 Interfaz web para subir documentos
2. 📱 Integración con app móvil
3. 🔐 Implementar RLS en Supabase
4. 📊 Dashboard de estadísticas

## ❓ Preguntas frecuentes

### ¿Puedo eliminar los archivos de FiscAI?

Sí, pero mejor **muévelos a `/legacy`** primero por si acaso necesitas algo después.

### ¿La tabla `documents` me afecta?

No. EstudIA usa `classroom_documents` y `classroom_document_chunks`. La tabla `documents` es legacy y no interfiere.

### ¿Necesito actualizar la base de datos?

Si ya tienes las tablas `classroom_*`, solo ejecuta `supabase_setup.sql` para asegurar que tienes los índices y funciones RPC.

### ¿Qué hago con src/gemini.py?

Tienes dos opciones:
1. **Limpiarlo** - Remover código fiscal, mantener solo embeddings + generación
2. **Crear uno nuevo** - `src/gemini_clean.py` solo para EstudIA

### ¿El proyecto funciona ahora?

**SÍ**, `src/main.py` ya implementa EstudIA correctamente. Los archivos legacy no interfieren, solo están ahí como referencia.

## 📞 Soporte

Si tienes dudas sobre la migración, revisa:
1. Este documento (MIGRATION.md)
2. README.md actualizado
3. Código en src/main.py (referencia de cómo debe funcionar)
4. supabase_setup.sql (estructura de DB correcta)

---

**Última actualización:** 2025-11-03  
**Versión:** 1.0.0 - EstudIA MCP Server
