"""
Cliente PostgreSQL para la base de datos de cursos.
"""
import logging
from typing import Optional, List, Dict, Any
import asyncpg
from asyncpg import Pool, Connection
from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseClient:
    """Cliente para conexiones a PostgreSQL."""
    
    def __init__(self):
        self.pool: Optional[Pool] = None
        self._connection_url = settings.database_url
        
    async def connect(self) -> bool:
        """Establece conexión con la base de datos."""
        try:
            self.pool = await asyncpg.create_pool(
                self._connection_url,
                min_size=1,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'jit': 'off'  # Mejora performance para queries simples
                }
            )
            
            # Probar conexión
            async with self.pool.acquire() as conn:
                await conn.execute('SELECT 1')
                
            logger.info("✅ Conexión a PostgreSQL establecida")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            return False
    
    async def disconnect(self):
        """Cierra las conexiones a la base de datos."""
        if self.pool:
            await self.pool.close()
            logger.info("🔌 Conexión a PostgreSQL cerrada")
    
    async def execute_query(
        self, 
        query: str, 
        *args,
        fetch_mode: str = "all"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Ejecuta una query SELECT y retorna los resultados.
        
        Args:
            query: Query SQL a ejecutar
            *args: Parámetros para la query
            fetch_mode: 'all', 'one' o 'none'
        
        Returns:
            Lista de registros como diccionarios o None si hay error
        """
        if not self.pool:
            logger.error("❌ No hay conexión a la base de datos")
            return None
            
        try:
            async with self.pool.acquire() as conn:
                if fetch_mode == "all":
                    records = await conn.fetch(query, *args)
                elif fetch_mode == "one":
                    record = await conn.fetchrow(query, *args)
                    records = [record] if record else []
                else:  # none
                    await conn.execute(query, *args)
                    return []
                
                # Convertir records a diccionarios
                return [dict(record) for record in records] if records else []
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Args: {args}")
            return None
    
    async def execute_transaction(
        self, 
        operations: List[tuple]
    ) -> bool:
        """
        Ejecuta múltiples operaciones en una transacción.
        
        Args:
            operations: Lista de tuplas (query, *args)
        
        Returns:
            True si la transacción fue exitosa
        """
        if not self.pool:
            logger.error("❌ No hay conexión a la base de datos")
            return False
            
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    for query, *args in operations:
                        await conn.execute(query, *args)
                        
            logger.info(f"✅ Transacción completada: {len(operations)} operaciones")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en transacción: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Verifica que la conexión esté funcionando."""
        try:
            result = await self.execute_query("SELECT 1 as health", fetch_mode="one")
            return result is not None and len(result) > 0
        except Exception:
            return False


# Instancia global del cliente
database_client = DatabaseClient()