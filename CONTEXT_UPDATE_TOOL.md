# 🎯 Herramienta: Análisis y Actualización de Contexto de Usuario

## Descripción

La herramienta `analyze_and_update_user_context` es una función MCP que analiza toda la conversación de una sesión de cubículo (classroom) y determina automáticamente si el contexto del usuario debe actualizarse con información relevante para personalizar su experiencia de aprendizaje.

## ¿Qué hace?

1. **Lee el contexto actual del usuario** desde la tabla `users` (campo `user_context`)
2. **Obtiene todos los mensajes** de la sesión especificada desde `cubicle_messages`
3. **Analiza con Gemini** la conversación completa para extraer información relevante
4. **Decide automáticamente** si el contexto debe actualizarse
5. **Actualiza la base de datos** si encuentra información nueva y valiosa

## Información que analiza

La herramienta busca y extrae:

- 📚 **Nivel educativo**: Grado escolar, carrera, área de estudio
- 🎨 **Estilo de aprendizaje**: Visual, auditivo, kinestésico, preferencias de explicación
- 🌟 **Intereses académicos**: Temas favoritos, áreas de especialización
- 💪 **Fortalezas académicas**: Materias en las que destaca
- 🆘 **Áreas de mejora**: Materias que necesitan refuerzo
- 🎯 **Objetivos educativos**: Metas de aprendizaje, proyectos, exámenes próximos
- 💬 **Preferencias de comunicación**: Cómo prefiere que le expliquen conceptos
- ⏰ **Hábitos de estudio**: Horarios, frecuencia, metodología
- 👤 **Contexto personal**: Cualquier información relevante para personalizar el aprendizaje

## Uso

### Como herramienta MCP

```python
from src.main import analyze_and_update_user_context

result = await analyze_and_update_user_context(
    user_id="uuid-del-usuario",
    session_id="uuid-de-la-sesion"
)
```

### Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `user_id` | `str` (UUID) | ID del usuario cuyo contexto se analizará |
| `session_id` | `str` (UUID) | ID de la sesión del cubículo con la conversación |

### Respuesta

```json
{
  "success": true,
  "context_updated": true,
  "previous_context": "Contexto anterior del usuario...",
  "new_context": "Contexto actualizado con nueva información...",
  "reasons": [
    "Se identificó el nivel educativo: Universidad, Ingeniería",
    "Se detectaron preferencias de aprendizaje visual",
    "Se encontraron objetivos: preparación para examen final"
  ],
  "key_findings": {
    "nivel_educativo": "Universidad - Ingeniería de Software",
    "estilo_aprendizaje": "Visual, prefiere diagramas y ejemplos prácticos",
    "intereses": ["algoritmos", "desarrollo web", "bases de datos"],
    "fortalezas": ["programación", "lógica"],
    "debilidades": ["matemáticas discretas"],
    "objetivos": "Aprobar examen final de estructuras de datos",
    "preferencias": "Explicaciones con código y ejemplos reales",
    "otros": "Estudia mejor por las noches"
  },
  "messages_analyzed": 15,
  "user_id": "uuid-del-usuario",
  "user_name": "Juan Pérez",
  "session_id": "uuid-de-la-sesion",
  "message": "Contexto actualizado"
}
```

## Ejemplo de uso

### Escenario: Primera sesión de estudio

**Conversación en el cubículo:**

```
Usuario: Hola, necesito ayuda con algoritmos de ordenamiento
Asistente: ¡Claro! ¿Qué algoritmo te gustaría repasar?
Usuario: QuickSort, tengo examen la próxima semana
Asistente: Perfecto, ¿en qué nivel estás? ¿Universidad?
Usuario: Sí, tercer semestre de Ingeniería en Software
Asistente: Genial, ¿prefieres que te lo explique con código o con diagramas?
Usuario: Me gusta más ver el código y debuggearlo paso a paso
```

**Resultado del análisis:**

```json
{
  "context_updated": true,
  "reasons": [
    "Se identificó nivel educativo: Universidad, 3er semestre de Ingeniería en Software",
    "Se detectó objetivo inmediato: examen de algoritmos la próxima semana",
    "Se identificó preferencia de aprendizaje: código y debugging paso a paso",
    "Se identificó tema de interés: algoritmos de ordenamiento (QuickSort)"
  ],
  "new_context": "Estudiante de Ingeniería en Software, 3er semestre. Tiene examen de algoritmos de ordenamiento la próxima semana. Prefiere aprender mediante código práctico y debugging paso a paso en lugar de explicaciones teóricas. Está estudiando QuickSort actualmente."
}
```

## Estructura de tablas involucradas

### Tabla `users`

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name TEXT,
  email TEXT,
  user_context TEXT,  -- ⭐ Campo que se actualiza
  -- ... otros campos
);
```

### Tabla `cubicle_messages`

```sql
CREATE TABLE cubicle_messages (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES cubicle_sessions(id),
  user_id UUID REFERENCES users(id),  -- NULL si es del asistente
  content TEXT,
  created_at TIMESTAMPTZ
);
```

## Criterios de actualización

El sistema **SÍ actualiza** cuando:
- ✅ Encuentra información nueva no presente en el contexto actual
- ✅ Detecta cambios en nivel educativo, intereses u objetivos
- ✅ Identifica patrones claros de aprendizaje o preferencias
- ✅ Hay información contradictoria que necesita corrección

El sistema **NO actualiza** cuando:
- ❌ La conversación es muy breve o superficial
- ❌ No hay información personal o educativa relevante
- ❌ La información ya está completamente en el contexto actual
- ❌ Los mensajes son solo saludos o conversación casual

## Pruebas

Para probar la herramienta, ejecuta:

```bash
python test_user_context_update.py
```

Este script:
1. Busca usuarios y sesiones disponibles en la base de datos
2. Ejecuta el análisis automáticamente
3. Muestra los resultados detallados
4. Compara el contexto anterior vs nuevo

## Integración recomendada

### Cuándo llamar a la herramienta

1. **Al finalizar una sesión de estudio**: Analizar toda la conversación
2. **Periódicamente durante sesiones largas**: Cada 10-15 mensajes
3. **Cuando el usuario menciona cambios**: Nueva materia, examen próximo, etc.
4. **En la primera interacción**: Para crear el contexto inicial

### Ejemplo de flujo en la aplicación

```python
# En el endpoint de finalizar sesión
@app.post("/api/sessions/{session_id}/end")
async def end_session(session_id: str, user_id: str):
    # 1. Marcar sesión como finalizada
    await mark_session_ended(session_id)
    
    # 2. Analizar y actualizar contexto
    context_result = await analyze_and_update_user_context(
        user_id=user_id,
        session_id=session_id
    )
    
    # 3. Notificar al usuario si hubo actualización
    if context_result.get('context_updated'):
        return {
            "message": "Sesión finalizada. Hemos actualizado tu perfil de aprendizaje.",
            "updates": context_result['key_findings']
        }
    
    return {"message": "Sesión finalizada"}
```

## Beneficios

- 🎯 **Personalización automática**: No requiere que el usuario llene formularios
- 🧠 **Aprendizaje contextual**: El sistema aprende de las conversaciones naturales
- 📈 **Mejora continua**: El contexto se enriquece con cada sesión
- 🤖 **Inteligente**: Gemini decide qué información es relevante
- 💾 **Persistente**: El contexto se guarda en la base de datos

## Consideraciones

- **Privacy**: Solo analiza conversaciones de sesiones educativas
- **Actualizaciones incrementales**: Combina contexto anterior con nueva información
- **No destructivo**: Siempre preserva información anterior relevante
- **Opt-out**: Los usuarios pueden limpiar su contexto si lo desean

## Siguiente paso

Integra esta herramienta en tu flujo de chat para crear experiencias de aprendizaje verdaderamente personalizadas que se adaptan automáticamente a cada estudiante.
