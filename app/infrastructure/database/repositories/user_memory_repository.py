"""
Repositorio para gestión de memoria de usuarios en PostgreSQL.
"""
import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.infrastructure.database.client import database_client
from memory.lead_memory import LeadMemory

logger = logging.getLogger(__name__)


class UserMemoryRepository:
    """Repositorio para operaciones de memoria de usuario en PostgreSQL."""
    
    def __init__(self):
        self.db = database_client
    
    async def ensure_table_exists(self):
        """Crea la tabla de memoria de usuarios si no existe."""
        create_table_query = """
            CREATE TABLE IF NOT EXISTS user_memory (
                user_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                role VARCHAR(255),
                interests TEXT[],
                pain_points TEXT[],
                lead_score INTEGER DEFAULT 0,
                interaction_count INTEGER DEFAULT 0,
                first_interaction_at TIMESTAMP WITH TIME ZONE,
                last_interaction_at TIMESTAMP WITH TIME ZONE,
                message_history JSONB DEFAULT '[]'::jsonb,
                additional_data JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            );
            
            CREATE INDEX IF NOT EXISTS idx_user_memory_lead_score ON user_memory(lead_score);
            CREATE INDEX IF NOT EXISTS idx_user_memory_last_interaction ON user_memory(last_interaction_at);
        """
        
        try:
            await self.db.execute_query(create_table_query, fetch_mode="none")
            logger.info("✅ Tabla user_memory verificada/creada")
        except Exception as e:
            logger.error(f"Error creando tabla user_memory: {e}")
    
    async def save_user_memory(self, user_memory: LeadMemory) -> bool:
        """
        Guarda o actualiza la memoria de un usuario.
        
        Args:
            user_memory: Objeto LeadMemory con la información del usuario
        
        Returns:
            True si se guardó exitosamente
        """
        query = """
            INSERT INTO user_memory (
                user_id, name, role, interests, pain_points, lead_score,
                interaction_count, first_interaction_at, last_interaction_at,
                message_history, additional_data, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            ON CONFLICT (user_id) DO UPDATE SET
                name = EXCLUDED.name,
                role = EXCLUDED.role,
                interests = EXCLUDED.interests,
                pain_points = EXCLUDED.pain_points,
                lead_score = EXCLUDED.lead_score,
                interaction_count = EXCLUDED.interaction_count,
                last_interaction_at = EXCLUDED.last_interaction_at,
                message_history = EXCLUDED.message_history,
                additional_data = EXCLUDED.additional_data,
                updated_at = EXCLUDED.updated_at
        """
        
        try:
            # Convertir message_history a JSON
            message_history_json = json.dumps([
                {
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", datetime.now()).isoformat() if isinstance(msg.get("timestamp"), datetime) else msg.get("timestamp", ""),
                    "type": msg.get("type", "user")
                }
                for msg in user_memory.message_history
            ])
            
            # Convertir datos adicionales a JSON
            additional_data_json = json.dumps(user_memory.additional_data)
            
            await self.db.execute_query(
                query,
                user_memory.user_id,
                user_memory.name,
                user_memory.role,
                user_memory.interests,
                user_memory.pain_points,
                user_memory.lead_score,
                user_memory.interaction_count,
                user_memory.first_interaction_at,
                user_memory.last_interaction_at,
                message_history_json,
                additional_data_json,
                datetime.now(),
                fetch_mode="none"
            )
            
            logger.info(f"✅ Memoria guardada para usuario {user_memory.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando memoria del usuario {user_memory.user_id}: {e}")
            return False
    
    async def load_user_memory(self, user_id: str) -> Optional[LeadMemory]:
        """
        Carga la memoria de un usuario desde PostgreSQL.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            LeadMemory object o None si no existe
        """
        query = """
            SELECT user_id, name, role, interests, pain_points, lead_score,
                   interaction_count, first_interaction_at, last_interaction_at,
                   message_history, additional_data, created_at, updated_at
            FROM user_memory
            WHERE user_id = $1
        """
        
        try:
            records = await self.db.execute_query(query, user_id, fetch_mode="one")
            
            if not records or len(records) == 0:
                return None
            
            record = records[0]
            
            # Convertir message_history de JSON
            message_history = []
            if record.get('message_history'):
                try:
                    message_history = json.loads(record['message_history'])
                    # Convertir timestamps de string a datetime
                    for msg in message_history:
                        if isinstance(msg.get('timestamp'), str):
                            try:
                                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                            except:
                                msg['timestamp'] = datetime.now()
                except json.JSONDecodeError:
                    message_history = []
            
            # Convertir additional_data de JSON
            additional_data = {}
            if record.get('additional_data'):
                try:
                    additional_data = json.loads(record['additional_data'])
                except json.JSONDecodeError:
                    additional_data = {}
            
            # Crear objeto LeadMemory
            lead_memory = LeadMemory(
                user_id=record['user_id'],
                name=record.get('name'),
                role=record.get('role'),
                interests=record.get('interests') or [],
                pain_points=record.get('pain_points') or [],
                lead_score=record.get('lead_score', 0),
                interaction_count=record.get('interaction_count', 0),
                first_interaction_at=record.get('first_interaction_at'),
                last_interaction_at=record.get('last_interaction_at'),
                message_history=message_history,
                additional_data=additional_data,
                created_at=record.get('created_at'),
                updated_at=record.get('updated_at')
            )
            
            logger.info(f"✅ Memoria cargada para usuario {user_id}")
            return lead_memory
            
        except Exception as e:
            logger.error(f"Error cargando memoria del usuario {user_id}: {e}")
            return None
    
    async def get_high_score_leads(self, min_score: int = 70, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Obtiene leads con alto puntaje.
        
        Args:
            min_score: Puntaje mínimo para considerar un lead calificado
            limit: Número máximo de leads a retornar
        
        Returns:
            Lista de leads con información básica
        """
        query = """
            SELECT user_id, name, role, lead_score, interaction_count,
                   last_interaction_at, interests, pain_points
            FROM user_memory
            WHERE lead_score >= $1
            ORDER BY lead_score DESC, last_interaction_at DESC
            LIMIT $2
        """
        
        try:
            records = await self.db.execute_query(query, min_score, limit)
            if records:
                return [dict(record) for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo leads de alto puntaje: {e}")
            return []
    
    async def get_recent_interactions(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtiene usuarios con interacciones recientes.
        
        Args:
            days: Número de días hacia atrás para considerar "reciente"
            limit: Número máximo de usuarios a retornar
        
        Returns:
            Lista de usuarios con interacciones recientes
        """
        query = """
            SELECT user_id, name, role, lead_score, interaction_count,
                   last_interaction_at, interests
            FROM user_memory
            WHERE last_interaction_at >= NOW() - INTERVAL '%s days'
            ORDER BY last_interaction_at DESC
            LIMIT $1
        """
        
        try:
            # Formatear la query con el número de días
            formatted_query = query % days
            records = await self.db.execute_query(formatted_query, limit)
            if records:
                return [dict(record) for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo interacciones recientes: {e}")
            return []
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de usuarios."""
        query = """
            SELECT 
                COUNT(*) as total_users,
                AVG(lead_score) as avg_lead_score,
                AVG(interaction_count) as avg_interactions,
                COUNT(CASE WHEN lead_score >= 70 THEN 1 END) as high_score_leads,
                COUNT(CASE WHEN last_interaction_at >= NOW() - INTERVAL '7 days' THEN 1 END) as active_last_week
            FROM user_memory
        """
        
        try:
            records = await self.db.execute_query(query, fetch_mode="one")
            if records and len(records) > 0:
                stats = records[0]
                return {
                    "total_users": stats.get('total_users', 0),
                    "avg_lead_score": round(stats.get('avg_lead_score', 0) or 0, 1),
                    "avg_interactions": round(stats.get('avg_interactions', 0) or 0, 1),
                    "high_score_leads": stats.get('high_score_leads', 0),
                    "active_last_week": stats.get('active_last_week', 0)
                }
            return {}
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de usuarios: {e}")
            return {}
    
    async def delete_user_memory(self, user_id: str) -> bool:
        """
        Elimina la memoria de un usuario.
        
        Args:
            user_id: ID del usuario a eliminar
        
        Returns:
            True si se eliminó exitosamente
        """
        query = "DELETE FROM user_memory WHERE user_id = $1"
        
        try:
            await self.db.execute_query(query, user_id, fetch_mode="none")
            logger.info(f"✅ Memoria eliminada para usuario {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando memoria del usuario {user_id}: {e}")
            return False