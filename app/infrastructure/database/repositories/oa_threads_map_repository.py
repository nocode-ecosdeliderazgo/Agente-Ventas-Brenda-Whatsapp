"""
Repositorio para gestión de mapeo de OpenAI Threads en PostgreSQL.
Mapea números de WhatsApp con Thread IDs de OpenAI Assistants API.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.infrastructure.database.client import database_client

logger = logging.getLogger(__name__)


class OAThreadsMapRepository:
    """Repositorio para operaciones de mapeo de OpenAI Threads."""
    
    def __init__(self):
        self.db = database_client
    
    async def ensure_table_exists(self):
        """Crea la tabla de mapeo de threads si no existe."""
        create_table_query = """
            CREATE TABLE IF NOT EXISTS oa_threads_map (
                user_phone text PRIMARY KEY,
                thread_id text NOT NULL,
                created_at timestamp with time zone NOT NULL DEFAULT now(),
                updated_at timestamp with time zone DEFAULT now()
            );
            
            CREATE INDEX IF NOT EXISTS idx_oa_threads_map_thread_id 
            ON oa_threads_map(thread_id);
        """
        
        try:
            await self.db.execute_query(create_table_query, fetch_mode="none")
            logger.info("✅ Tabla oa_threads_map verificada/creada")
        except Exception as e:
            logger.error(f"Error creando tabla oa_threads_map: {e}")
    
    async def get_thread_id(self, user_phone: str) -> Optional[str]:
        """
        Obtiene el thread_id asociado a un número de WhatsApp.
        
        Args:
            user_phone: Número de WhatsApp en formato Twilio (ej: "whatsapp:+1234567890")
        
        Returns:
            Thread ID de OpenAI o None si no existe
        """
        query = """
            SELECT thread_id 
            FROM oa_threads_map 
            WHERE user_phone = $1
        """
        
        try:
            records = await self.db.execute_query(query, user_phone, fetch_mode="one")
            
            if records and len(records) > 0:
                thread_id = records[0].get('thread_id')
                logger.info(f"✅ Thread ID encontrado para {user_phone}: {thread_id}")
                return thread_id
            
            logger.info(f"ℹ️ No existe thread_id para {user_phone}")
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo thread_id para {user_phone}: {e}")
            return None
    
    async def save_thread_id(self, user_phone: str, thread_id: str) -> bool:
        """
        Guarda o actualiza el mapeo entre número de WhatsApp y thread_id.
        
        Args:
            user_phone: Número de WhatsApp en formato Twilio
            thread_id: Thread ID de OpenAI Assistants API
        
        Returns:
            True si se guardó exitosamente
        """
        query = """
            INSERT INTO oa_threads_map (user_phone, thread_id, updated_at)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_phone) DO UPDATE SET
                thread_id = EXCLUDED.thread_id,
                updated_at = EXCLUDED.updated_at
        """
        
        try:
            await self.db.execute_query(
                query,
                user_phone,
                thread_id,
                datetime.now(),
                fetch_mode="none"
            )
            
            logger.info(f"✅ Thread ID guardado: {user_phone} -> {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando thread_id para {user_phone}: {e}")
            return False
    
    async def get_user_phone_by_thread_id(self, thread_id: str) -> Optional[str]:
        """
        Obtiene el número de WhatsApp asociado a un thread_id (búsqueda reversa).
        
        Args:
            thread_id: Thread ID de OpenAI
        
        Returns:
            Número de WhatsApp o None si no existe
        """
        query = """
            SELECT user_phone 
            FROM oa_threads_map 
            WHERE thread_id = $1
        """
        
        try:
            records = await self.db.execute_query(query, thread_id, fetch_mode="one")
            
            if records and len(records) > 0:
                user_phone = records[0].get('user_phone')
                logger.info(f"✅ Número encontrado para thread {thread_id}: {user_phone}")
                return user_phone
            
            logger.info(f"ℹ️ No existe user_phone para thread_id {thread_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo user_phone para thread_id {thread_id}: {e}")
            return None
    
    async def delete_mapping(self, user_phone: str) -> bool:
        """
        Elimina el mapeo de un usuario.
        
        Args:
            user_phone: Número de WhatsApp
        
        Returns:
            True si se eliminó exitosamente
        """
        query = "DELETE FROM oa_threads_map WHERE user_phone = $1"
        
        try:
            await self.db.execute_query(query, user_phone, fetch_mode="none")
            logger.info(f"✅ Mapeo eliminado para {user_phone}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando mapeo para {user_phone}: {e}")
            return False
    
    async def get_all_mappings(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene todos los mapeos existentes.
        
        Args:
            limit: Número máximo de mapeos a retornar
        
        Returns:
            Lista de mapeos con información básica
        """
        query = """
            SELECT user_phone, thread_id, created_at, updated_at
            FROM oa_threads_map
            ORDER BY updated_at DESC
            LIMIT $1
        """
        
        try:
            records = await self.db.execute_query(query, limit)
            if records:
                logger.info(f"✅ Obtenidos {len(records)} mapeos de threads")
                return [dict(record) for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo mapeos de threads: {e}")
            return []
    
    async def get_mapping_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de mapeos."""
        query = """
            SELECT 
                COUNT(*) as total_mappings,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as created_last_24h,
                COUNT(CASE WHEN updated_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as updated_last_24h,
                MIN(created_at) as first_mapping_created,
                MAX(updated_at) as last_mapping_updated
            FROM oa_threads_map
        """
        
        try:
            records = await self.db.execute_query(query, fetch_mode="one")
            if records and len(records) > 0:
                stats = records[0]
                return {
                    "total_mappings": stats.get('total_mappings', 0),
                    "created_last_24h": stats.get('created_last_24h', 0),
                    "updated_last_24h": stats.get('updated_last_24h', 0),
                    "first_mapping_created": stats.get('first_mapping_created'),
                    "last_mapping_updated": stats.get('last_mapping_updated')
                }
            return {}
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de mapeos: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Verifica que la tabla y conexión funcionen correctamente."""
        try:
            await self.ensure_table_exists()
            
            # Probar una consulta simple
            query = "SELECT COUNT(*) as count FROM oa_threads_map LIMIT 1"
            result = await self.db.execute_query(query, fetch_mode="one")
            
            if result and len(result) > 0:
                logger.info(f"✅ Health check OK - {result[0]['count']} mapeos existentes")
                return True
            return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False