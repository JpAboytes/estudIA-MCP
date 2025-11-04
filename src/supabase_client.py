"""
Cliente para Supabase - Base de datos y funciones para EstudIA
"""
import asyncio
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from .config import config

if not config.SUPABASE_URL or not config.SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Faltan variables de entorno de Supabase")

class SupabaseClient:
    """Cliente para interactuar con Supabase"""
    
    def __init__(self):
        # Cliente principal con service role key
        self.client: Client = create_client(
            config.SUPABASE_URL,
            config.SUPABASE_SERVICE_ROLE_KEY
        )
    
    async def search_classroom_chunks(
        self, 
        embedding: List[float],
        classroom_id: str,
        limit: int = 5,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Buscar chunks de documentos similares en un aula usando embeddings
        Usa la función RPC match_classroom_chunks
        
        Args:
            embedding: Vector de embedding para la búsqueda (768 dimensiones)
            classroom_id: UUID del aula para filtrar
            limit: Número máximo de chunks a retornar
            threshold: Umbral de similitud (default: 0.7)
            
        Returns:
            Lista de chunks similares con campos: id, classroom_document_id, chunk_index, 
            content, token_count, similarity, document_title, document_storage_path
        """
        try:
            if threshold is None:
                threshold = 0.7
            
            print(f"[SUPABASE] Buscando chunks similares en aula {classroom_id}...")
            print(f"[SUPABASE] - Embedding dimension: {len(embedding)}")
            print(f"[SUPABASE] - Match threshold: {threshold}")
            print(f"[SUPABASE] - Match count: {limit}")
            
            payload = {
                'query_embedding': embedding,
                'filter_classroom_id': classroom_id,
                'match_threshold': threshold,
                'match_count': limit
            }
            
            print("[SUPABASE] Llamando match_classroom_chunks RPC...")
            response = await asyncio.to_thread(
                lambda: self.client.rpc('match_classroom_chunks', payload).execute()
            )
            
            if response.data:
                print(f"[SUPABASE] ✅ Encontrados {len(response.data)} chunks")
                return response.data
            
            print("[SUPABASE] ⚠️  No se encontraron chunks")
            return []
            
        except Exception as error:
            print(f"[SUPABASE] ❌ Error buscando chunks similares: {error}")
            import traceback
            traceback.print_exc()
            return []
    
    async def get_classroom_info(self, classroom_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información del aula desde la base de datos
        
        Args:
            classroom_id: UUID del aula
            
        Returns:
            Información del aula con estadísticas de documentos o None si no se encuentra
        """
        try:
            # Obtener información del aula
            classroom_response = await asyncio.to_thread(
                self.client.table('classrooms')
                .select('*')
                .eq('id', classroom_id)
                .single()
                .execute
            )
            
            if not classroom_response.data:
                return None
            
            classroom = classroom_response.data
            
            # Contar documentos del aula
            docs_response = await asyncio.to_thread(
                self.client.table('classroom_documents')
                .select('id', count='exact')
                .eq('classroom_id', classroom_id)
                .execute
            )
            
            # Contar chunks totales del aula
            chunks_response = await asyncio.to_thread(
                self.client.table('classroom_document_chunks')
                .select('id', count='exact')
                .eq('classroom_id', classroom_id)
                .execute
            )
            
            classroom['document_count'] = docs_response.count or 0
            classroom['chunk_count'] = chunks_response.count or 0
            
            return classroom
            
        except Exception as error:
            print(f"Error obteniendo información del aula: {error}")
            return None
    
    async def save_chat_message(
        self,
        classroom_id: str,
        user_id: str,
        message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Guardar mensaje del chat en la tabla 'classroom_chat_history'
        
        Args:
            classroom_id: UUID del aula
            user_id: ID del usuario
            message: Mensaje del usuario
            response: Respuesta del asistente
            metadata: Metadatos adicionales (ej: chunks usados, similarity scores)
            
        Returns:
            Registro guardado o None si falló
        """
        try:
            import datetime
            
            data = {
                'classroom_id': classroom_id,
                'user_id': user_id,
                'message': message,
                'response': response,
                'metadata': metadata or {},
                'created_at': datetime.datetime.now().isoformat()
            }
            
            response = await asyncio.to_thread(
                self.client.table('classroom_chat_history').insert(data).execute
            )
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as error:
            print(f"Error guardando mensaje: {error}")
            return None
    
    async def get_chat_history(
        self, 
        classroom_id: str,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtener historial de chat del aula desde la tabla 'classroom_chat_history'
        
        Args:
            classroom_id: UUID del aula
            user_id: ID del usuario (opcional, para filtrar por usuario específico)
            limit: Número máximo de mensajes
            
        Returns:
            Lista de mensajes del historial ordenados por fecha
        """
        try:
            query = self.client.table('classroom_chat_history').select('*')
            query = query.eq('classroom_id', classroom_id)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            query = query.order('created_at', desc=True).limit(limit)
            
            response = await asyncio.to_thread(query.execute)
            
            if response.data:
                return response.data
            return []
            
        except Exception as error:
            print(f"Error obteniendo historial: {error}")
            return []


# Instancia global del cliente
supabase_client = SupabaseClient()