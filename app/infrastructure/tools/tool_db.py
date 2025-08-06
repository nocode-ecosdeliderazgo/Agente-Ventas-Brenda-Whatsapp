"""
Minimal Database Wrapper Tool for AI Agent
==========================================
Provides simple async query interface for the AI agent to access database information
when specific data is needed. Uses existing DatabaseClient infrastructure.

DESIGN PRINCIPLES:
- Minimal interface: tool_db.query(table, filters, limit)  
- Read-only queries only
- Safe parameter binding
- Graceful fallback if database unavailable
- Zero disruption to existing legacy repositories
"""

import logging
from typing import Dict, List, Any, Optional
from app.infrastructure.database.client import DatabaseClient

logger = logging.getLogger(__name__)

class ToolDB:
    """Minimal database wrapper tool for AI agent queries."""
    
    def __init__(self, db_client: Optional[DatabaseClient] = None):
        self.db_client = db_client or DatabaseClient()
        self._connection_ready = False
        
        # Allowed tables for safety (read-only access)
        self.allowed_tables = {
            'ai_courses': {
                'columns': ['id_course', 'name', 'short_description', 'session_count', 
                           'total_duration_min', 'price', 'currency', 'modality', 'roi'],
                'safe_filters': ['name', 'modality', 'status', 'audience_category']
            },
            'ai_course_session': {
                'columns': ['id_session', 'session_index', 'title', 'objective', 
                           'duration_minutes', 'id_course_fk'],
                'safe_filters': ['title', 'id_course_fk']
            },
            'bond': {
                'columns': ['id_bond', 'content', 'type_bond', 'emisor', 'bond_url', 'active'],
                'safe_filters': ['type_bond', 'active', 'id_courses_fk']
            },
            'elements_url': {
                'columns': ['id_element', 'item_type', 'url_test', 'description_url'],
                'safe_filters': ['item_type', 'id_session_fk']
            },
            'ai_tema_activity': {
                'columns': ['id_activity', 'item_type', 'title_item', 'item_session'],
                'safe_filters': ['item_type', 'id_course_fk', 'id_session_fk']
            }
        }
    
    async def ensure_connection(self) -> bool:
        """Ensure database connection is ready."""
        try:
            if not self._connection_ready:
                success = await self.db_client.connect()
                self._connection_ready = success
                return success
            return True
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            return False
    
    async def query(
        self, 
        table: str, 
        filters: Optional[Dict[str, Any]] = None, 
        limit: int = 5,
        columns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Simple database query interface for AI agent.
        
        Args:
            table: Table name (must be in allowed_tables)
            filters: WHERE conditions as dict (optional)
            limit: Max results to return (default: 5, max: 20)
            columns: Specific columns to select (optional, uses defaults)
            
        Returns:
            List of dictionaries with query results
            
        Examples:
            # Get course info
            courses = await tool_db.query('ai_courses', {'modality': 'online'}, limit=3)
            
            # Get course sessions
            sessions = await tool_db.query('ai_course_session', {'id_course_fk': course_id})
            
            # Get bonuses for a course
            bonuses = await tool_db.query('bond', {'active': True, 'id_courses_fk': course_id})
        """
        try:
            # Validate inputs
            if table not in self.allowed_tables:
                logger.warning(f"Table '{table}' not allowed for tool queries")
                return []
            
            if not await self.ensure_connection():
                logger.warning("Database not available for tool query")
                return []
            
            # Sanitize filters
            filters = filters or {}
            safe_filters = self.allowed_tables[table]['safe_filters']
            sanitized_filters = {k: v for k, v in filters.items() if k in safe_filters}
            
            # Limit protection
            limit = min(max(1, limit), 20)
            
            # Select columns
            if columns:
                allowed_columns = self.allowed_tables[table]['columns']
                columns = [col for col in columns if col in allowed_columns]
            else:
                columns = self.allowed_tables[table]['columns']
                
            columns_str = ', '.join(columns)
            
            # Build query
            query = f"SELECT {columns_str} FROM {table}"
            params = []
            
            if sanitized_filters:
                where_conditions = []
                param_index = 1
                
                for column, value in sanitized_filters.items():
                    where_conditions.append(f"{column} = ${param_index}")
                    params.append(value)
                    param_index += 1
                
                query += f" WHERE {' AND '.join(where_conditions)}"
            
            query += f" LIMIT ${len(params) + 1}"
            params.append(limit)
            
            # Execute query
            if self.db_client and hasattr(self.db_client, 'pool'):
                async with self.db_client.pool.acquire() as conn:
                    rows = await conn.fetch(query, *params)
                    
                # Convert to dict list
                results = [dict(row) for row in rows]
                
                logger.info(f"🔍 tool_db.query({table}) returned {len(results)} results")
                return results
            else:
                logger.warning("Database client not properly initialized")
                return []
            
        except Exception as e:
            logger.error(f"Error in tool_db.query({table}): {e}")
            return []
    
    async def get_course_by_name(self, course_name: str) -> Optional[Dict[str, Any]]:
        """Helper: Get course by name or partial match."""
        try:
            # First try exact match
            results = await self.query('ai_courses', {'name': course_name}, limit=1)
            if results:
                return results[0]
            
            # Try partial match (requires raw SQL for ILIKE)
            if await self.ensure_connection() and self.db_client and hasattr(self.db_client, 'pool'):
                query = """
                    SELECT id_course, name, short_description, session_count, 
                           total_duration_min, price, currency, modality, roi 
                    FROM ai_courses 
                    WHERE name ILIKE $1 
                    LIMIT 1
                """
                async with self.db_client.pool.acquire() as conn:
                    rows = await conn.fetch(query, f"%{course_name}%")
                    
                if rows:
                    return dict(rows[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error in get_course_by_name({course_name}): {e}")
            return None
    
    async def get_course_sessions(self, course_id: str) -> List[Dict[str, Any]]:
        """Helper: Get all sessions for a course."""
        return await self.query('ai_course_session', {'id_course_fk': course_id}, limit=20)
    
    async def get_active_bonuses(self, course_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Helper: Get active bonuses, optionally filtered by course."""
        filters = {'active': True}
        if course_id:
            filters['id_courses_fk'] = course_id
        return await self.query('bond', filters, limit=10)


# Global instance for easy access
_tool_db_instance = None

async def get_tool_db() -> ToolDB:
    """Get or create global ToolDB instance.
    
    Returns:
        ToolDB: Configured ToolDB instance ready for database queries.
        
    Note:
        Uses singleton pattern to ensure single database connection pool.
    """
    global _tool_db_instance
    if _tool_db_instance is None:
        _tool_db_instance = ToolDB()
    return _tool_db_instance

# Convenience function for direct access
async def query(table: str, filters: Optional[Dict[str, Any]] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Direct query function - main interface for AI agent.
    
    Args:
        table: Name of the database table to query (must be whitelisted).
        filters: Optional dictionary of column-value pairs for WHERE conditions.
        limit: Maximum number of results to return (default: 5, max: 20).
        
    Returns:
        List[Dict[str, Any]]: Query results as list of dictionaries.
        
    Example:
        >>> courses = await query('ai_courses', {'modality': 'online'}, limit=3)
        >>> sessions = await query('ai_course_session', {'id_course_fk': course_id})
    """
    tool_db = await get_tool_db()
    return await tool_db.query(table, filters, limit)

# Example usage for documentation:
"""
USAGE EXAMPLES:

# Get course information
courses = await tool_db.query('ai_courses', {'modality': 'online'}, limit=3)

# Get sessions for a specific course  
sessions = await tool_db.query('ai_course_session', {'id_course_fk': course_uuid})

# Get active bonuses
bonuses = await tool_db.query('bond', {'active': True})

# Get multimedia elements
elements = await tool_db.query('elements_url', {'item_type': 'video'})

# Get course activities  
activities = await tool_db.query('ai_tema_activity', {'item_type': 'practica'})
"""