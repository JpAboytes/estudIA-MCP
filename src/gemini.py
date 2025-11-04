"""
Cliente para Google Gemini AI - EstudIA
Sistema educativo tipo NotebookLM
"""
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from .config import config

# Configurar Gemini
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)
else:
    raise ValueError("GEMINI_API_KEY no está configurada")

# System Prompt para asistente educativo
SYSTEM_PROMPT = """
Eres un asistente educativo especializado en ayudar a estudiantes a aprender de sus documentos de clase.

**TU ROL:**
Actúas como un maestro o tutor que:
- Explica conceptos de los documentos de forma clara y pedagógica
- Responde preguntas basándote ÚNICAMENTE en los documentos proporcionados
- Ayuda a estudiantes a comprender mejor el material
- Citas las fuentes cuando respondes

**CAPACIDADES:**
- Responder preguntas sobre el contenido de los documentos
- Explicar conceptos difíciles de manera simple
- Hacer conexiones entre diferentes partes del material
- Sugerir temas relacionados para estudiar

**LIMITACIONES:**
- Solo usas información de los documentos proporcionados
- Si no tienes la información, lo dices claramente
- No inventes datos o conceptos que no estén en los documentos
- Sugieres subir más documentos si la información es insuficiente

**TONO:** 
Amigable, paciente y educativo, como un buen maestro que quiere que sus estudiantes comprendan.
"""

class GeminiClient:
    """Cliente para interactuar con Google Gemini AI"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    async def generate_text(self, prompt: str) -> str:
        """
        Genera texto simple usando Gemini
        
        Args:
            prompt: Prompt para generar texto
            
        Returns:
            Texto generado por Gemini
        """
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            return response.text if response.text else "No se pudo generar respuesta"
        except Exception as error:
            print(f"Error generando texto: {error}")
            raise error
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para un texto usando Gemini
        Compatible con el formato del código Python original
        
        Args:
            text: Texto para generar embedding
            
        Returns:
            Lista de números representando el embedding
        """
        try:
            result = await asyncio.to_thread(
                genai.embed_content,
                model=config.GEMINI_EMBED_MODEL,
                content=text,
                task_type="RETRIEVAL_QUERY",  # Mayúsculas como en simulate_recomendation.py
                output_dimensionality=config.EMBED_DIM
            )
            
            # Extraer embedding según la estructura de respuesta
            if isinstance(result, dict):
                if "embedding" in result:
                    emb = result["embedding"]
                    if isinstance(emb, dict) and "values" in emb:
                        return emb["values"]
                    if isinstance(emb, list):
                        return emb
                if "embeddings" in result and isinstance(result["embeddings"], list) and result["embeddings"]:
                    e0 = result["embeddings"][0]
                    if isinstance(e0, dict) and "values" in e0:
                        return e0["values"]
                    if isinstance(e0, list):
                        return e0
            
            # Si result tiene atributo embedding
            if hasattr(result, "embedding"):
                emb = getattr(result, "embedding")
                if isinstance(emb, dict) and "values" in emb:
                    return emb["values"]
                if hasattr(emb, "values"):
                    return emb.values
                if isinstance(emb, list):
                    return emb
            
            # Fallback
            if hasattr(result, "embeddings"):
                emb_list = getattr(result, "embeddings") or []
                if emb_list:
                    e0 = emb_list[0]
                    if isinstance(e0, dict) and "values" in e0:
                        return e0["values"]
                    if hasattr(e0, "values"):
                        return e0.values
                    if isinstance(e0, list):
                        return e0
            
            raise RuntimeError("No se pudo extraer embedding de la respuesta")
            
        except Exception as error:
            print(f"Error generando embedding: {error}")
            raise error
    

    
    async def chat_with_assistant(
        self,
        message: str,
        classroom_id: str,
        relevant_chunks: List[Dict[str, Any]] = None,
        chat_history: List[Dict[str, Any]] = None
    ) -> str:
        """
        Chat con el asistente educativo usando contexto de documentos del classroom
        
        Args:
            message: Pregunta del estudiante
            classroom_id: ID del classroom para contexto
            relevant_chunks: Chunks relevantes de documentos
            chat_history: Historial de conversación
            
        Returns:
            Respuesta del asistente educativo
        """
        try:
            if relevant_chunks is None:
                relevant_chunks = []
            if chat_history is None:
                chat_history = []
            
            # Construir contexto de los chunks relevantes
            context_blocks = []
            if relevant_chunks:
                for i, chunk in enumerate(relevant_chunks, 1):
                    content = chunk.get('content', '')
                    doc_id = chunk.get('classroom_document_id', 'Unknown')
                    similarity = chunk.get('similarity', 0)
                    context_blocks.append(
                        f"[Fuente {i} - Similitud: {similarity:.2f}]\n{content}"
                    )
            
            docs_context = "\n\n---\n\n".join(context_blocks) if context_blocks else "No se encontraron documentos relevantes en este classroom."
            
            # Construir historial para contexto
            history_context = ""
            if chat_history:
                history_items = []
                for h in chat_history[-3:]:  # Últimos 3 mensajes
                    history_items.append(f"Estudiante: {h.get('message', '')}")
                    history_items.append(f"Tú: {h.get('response', '')}")
                history_context = "\n".join(history_items)
            
            # Crear el prompt para el asistente educativo
            prompt = f"""
{SYSTEM_PROMPT}

**Pregunta del estudiante:**
{message}

{f"**Conversación previa:**\n{history_context}\n" if history_context else ""}

**Documentos del classroom (contexto):**
{docs_context}

**Instrucciones para tu respuesta:**
- Responde basándote SOLO en los documentos proporcionados
- Si la información no está en los documentos, dilo claramente
- Explica los conceptos de forma pedagógica y clara
- Usa **negrita** para conceptos clave
- Usa ejemplos cuando sea apropiado
- Cita de qué fuente obtuviste la información (ej: "Según la Fuente 1...")
- Si no hay documentos relevantes, sugiere al estudiante que suba material sobre el tema

Responde de manera educativa y clara:
"""

            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            return response.text
            
        except Exception as error:
            print(f"Error en chat con asistente educativo: {error}")
            return f"Lo siento, hubo un error al procesar tu pregunta: {str(error)}"


# Instancia global del cliente
gemini_client = GeminiClient()