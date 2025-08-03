"""
Repositorio para gestión de cursos en PostgreSQL.
"""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.infrastructure.database.client import database_client
from app.domain.entities.course import (
    Course, CourseSession, SessionActivity, Bond, ElementUrl,
    CourseInfo, CourseSearchFilters
)

logger = logging.getLogger(__name__)


class CourseRepository:
    """Repositorio para operaciones de cursos en la base de datos."""
    
    def __init__(self):
        self.db = database_client
    
    async def get_all_courses(
        self, 
        filters: Optional[CourseSearchFilters] = None,
        limit: int = 10
    ) -> List[Course]:
        """
        Obtiene todos los cursos con filtros opcionales.
        
        Args:
            filters: Filtros de búsqueda
            limit: Número máximo de cursos a retornar
        
        Returns:
            Lista de cursos
        """
        query = """
            SELECT 
                id_course, name, short_description, long_descrption, created_at, session_count,
                total_duration_min, price, currency, course_url, purchase_url, level, language,
                audience_category, status, start_date, end_date, roi, modality
            FROM ai_courses
            WHERE 1=1
        """
        params = []
        param_count = 0
        
        # Aplicar filtros
        if filters:
            if filters.level:
                param_count += 1
                query += f" AND level = ${param_count}"
                params.append(filters.level)
            
            if filters.modality:
                param_count += 1
                query += f" AND modality = ${param_count}"
                params.append(filters.modality)
            
            if filters.language:
                param_count += 1
                query += f" AND language = ${param_count}"
                params.append(filters.language)
            
            if filters.audience_category:
                param_count += 1
                query += f" AND audience_category = ${param_count}"
                params.append(filters.audience_category)
            
            if filters.status:
                param_count += 1
                query += f" AND status = ${param_count}"
                params.append(filters.status)
            
            if filters.search_text:
                param_count += 1
                query += f" AND (name ILIKE ${param_count} OR short_description ILIKE ${param_count})"
                search_pattern = f"%{filters.search_text}%"
                params.extend([search_pattern, search_pattern])
                param_count += 1  # Segundo parámetro para la segunda condición
        
        query += " ORDER BY created_at DESC"
        
        if limit > 0:
            param_count += 1
            query += f" LIMIT ${param_count}"
            params.append(limit)
        
        try:
            records = await self.db.execute_query(query, *params)
            if records:
                return [Course(**record) for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo cursos: {e}")
            return []
    
    async def get_course_by_id(self, course_id: UUID) -> Optional[Course]:
        """Obtiene un curso por su ID."""
        query = """
            SELECT 
                id_course, name, short_description, long_descrption, created_at, session_count,
                total_duration_min, price, currency, course_url, purchase_url, level, language,
                audience_category, status, start_date, end_date, roi, modality
            FROM ai_courses
            WHERE id_course = $1
        """
        
        try:
            records = await self.db.execute_query(query, course_id, fetch_mode="one")
            if records and len(records) > 0:
                return Course(**records[0])
            return None
        except Exception as e:
            logger.error(f"Error obteniendo curso {course_id}: {e}")
            return None
    
    async def get_course_sessions(self, course_id: UUID) -> List[CourseSession]:
        """Obtiene las sesiones de un curso."""
        query = """
            SELECT id_session, created_at, session_index, title, objective,
                   duration_minutes, scheduled_at, id_course_fk
            FROM ai_course_session
            WHERE id_course_fk = $1
            ORDER BY session_index ASC
        """
        
        try:
            records = await self.db.execute_query(query, course_id)
            if records:
                return [CourseSession(**record) for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo sesiones del curso {course_id}: {e}")
            return []
    
    async def get_course_bonds(self, course_id: UUID) -> List[Bond]:
        """Obtiene los bonos asociados a un curso."""
        query = """
            SELECT id_bond, created_at, content, type_bond, id_courses_fk, emisor
            FROM bond
            WHERE id_courses_fk = $1
            ORDER BY created_at DESC
        """
        
        try:
            records = await self.db.execute_query(query, course_id)
            if records:
                return [Bond(**record) for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo bonos del curso {course_id}: {e}")
            return []
    
    async def get_course_bonuses(self, course_id: UUID) -> List[Bond]:
        """Alias para get_course_bonds para compatibilidad."""
        return await self.get_course_bonds(course_id)
    
    async def get_session_activities(self, session_id: UUID) -> List[SessionActivity]:
        """Obtiene las actividades de una sesión."""
        query = """
            SELECT id_activity, created_at, id_course_fk, id_session_fk,
                   item_session, item_type, title_item
            FROM ai_tema_activity
            WHERE id_session_fk = $1
            ORDER BY item_session ASC
        """
        
        try:
            records = await self.db.execute_query(query, session_id)
            if records:
                return [SessionActivity(**record) for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo actividades de la sesión {session_id}: {e}")
            return []
    
    async def get_course_complete_info(self, course_id: UUID) -> Optional[CourseInfo]:
        """
        Obtiene información completa de un curso incluyendo sesiones y bonos.
        
        Args:
            course_id: ID del curso
        
        Returns:
            Información completa del curso o None si no existe
        """
        # Obtener curso base
        course = await self.get_course_by_id(course_id)
        if not course:
            return None
        
        # Obtener datos relacionados en paralelo
        sessions = await self.get_course_sessions(course_id)
        bonds = await self.get_course_bonds(course_id)
        
        # Contar actividades totales
        total_activities = 0
        if sessions:
            for session in sessions:
                activities = await self.get_session_activities(session.id_session)
                total_activities += len(activities)
        
        return CourseInfo(
            course=course,
            sessions=sessions,
            bonds=bonds,
            total_activities=total_activities
        )
    
    async def search_courses_by_text(self, search_text: str, limit: int = 5) -> List[Course]:
        """
        Busca cursos por texto en nombre y descripción.
        
        Args:
            search_text: Texto a buscar
            limit: Número máximo de resultados
        
        Returns:
            Lista de cursos que coinciden con la búsqueda
        """
        try:
            # Consulta simple para buscar cursos
            query = """
                SELECT 
                    id_course, name, short_description, long_descrption, created_at, session_count,
                    total_duration_min, price, currency, course_url, purchase_url, level, language,
                    audience_category, status, start_date, end_date, roi, modality
                FROM ai_courses
                WHERE (name ILIKE $1 OR short_description ILIKE $1)
                ORDER BY created_at DESC 
                LIMIT $2
            """
            search_pattern = f"%{search_text}%"
            records = await self.db.execute_query(query, search_pattern, limit)
            
            if records:
                return [Course(**record) for record in records]
            return []
            
        except Exception as e:
            logger.error(f"Error buscando cursos por texto '{search_text}': {e}")
            return []
    
    async def get_courses_by_level(self, level: str, limit: int = 5) -> List[Course]:
        """Obtiene cursos filtrados por nivel."""
        filters = CourseSearchFilters(level=level)
        return await self.get_all_courses(filters, limit)
    
    async def get_courses_by_modality(self, modality: str, limit: int = 5) -> List[Course]:
        """Obtiene cursos filtrados por modalidad."""
        try:
            query = """
                SELECT 
                    id_course, Name as name, Short_description as short_description,
                    Long_descrption as long_description, created_at, session_count,
                    total_duration_min, Price as price, Currency as currency,
                    course_url, Purchase_url as purchase_url, level, language,
                    audience_category, status, start_date, end_date, roi, modality
                FROM ai_courses
                WHERE modality = $1
                ORDER BY created_at DESC 
                LIMIT $2
            """
            records = await self.db.execute_query(query, modality, limit)
            
            if records:
                return [Course(**record) for record in records]
            return []
            
        except Exception as e:
            logger.error(f"Error obteniendo cursos por modalidad '{modality}': {e}")
            return []
    
    async def get_active_courses(self, limit: int = 5) -> List[Course]:
        """Obtiene cursos activos."""
        try:
            query = """
                SELECT 
                    id_course, name, short_description, long_descrption, created_at, session_count,
                    total_duration_min, price, currency, course_url, purchase_url, level, language,
                    audience_category, status, start_date, end_date, roi, modality
                FROM ai_courses
                WHERE status = 'active'
                ORDER BY created_at DESC 
                LIMIT $1
            """
            records = await self.db.execute_query(query, limit)
            
            if records:
                return [Course(**record) for record in records]
            return []
            
        except Exception as e:
            logger.error(f"Error obteniendo cursos activos: {e}")
            return []
    
    async def get_available_levels(self) -> List[str]:
        """Obtiene todos los niveles de curso disponibles."""
        query = "SELECT DISTINCT level FROM ai_courses WHERE level IS NOT NULL ORDER BY level"
        
        try:
            records = await self.db.execute_query(query)
            if records:
                return [record['level'] for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo niveles: {e}")
            return []
    
    async def get_available_modalities(self) -> List[str]:
        """Obtiene todas las modalidades disponibles."""
        query = "SELECT DISTINCT modality FROM ai_courses WHERE modality IS NOT NULL ORDER BY modality"
        
        try:
            records = await self.db.execute_query(query)
            if records:
                return [record['modality'] for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo modalidades: {e}")
            return []
    
    async def get_session_resources(self, session_id: UUID) -> List[Dict[str, Any]]:
        """Obtiene recursos multimedia de una sesión."""
        query = """
            SELECT id_element, created_at, id_session_fk, id_activity_fk,
                   item_type, url_test, description_url
            FROM elements_url
            WHERE id_session_fk = $1
            ORDER BY created_at ASC
        """
        
        try:
            records = await self.db.execute_query(query, session_id)
            if records:
                return [dict(record) for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo recursos de la sesión {session_id}: {e}")
            return []
    
    async def get_activity_resources(self, activity_id: UUID) -> List[Dict[str, Any]]:
        """Obtiene recursos multimedia de una actividad específica."""
        query = """
            SELECT id_element, created_at, id_session_fk, id_activity_fk,
                   item_type, url_test, description_url
            FROM elements_url
            WHERE id_activity_fk = $1
            ORDER BY created_at ASC
        """
        
        try:
            records = await self.db.execute_query(query, activity_id)
            if records:
                return [dict(record) for record in records]
            return []
        except Exception as e:
            logger.error(f"Error obteniendo recursos de la actividad {activity_id}: {e}")
            return []
    
    async def get_course_detailed_content(self, course_id: UUID) -> Dict[str, Any]:
        """
        Obtiene contenido detallado completo de un curso para uso en prompts.
        Incluye curso, sesiones, actividades, bonos y recursos.
        """
        try:
            # Obtener curso base
            course = await self.get_course_by_id(course_id)
            if not course:
                return {}
            
            # Obtener sesiones
            sessions = await self.get_course_sessions(course_id)
            
            # Obtener bonos
            bonds = await self.get_course_bonds(course_id)
            
            # Para cada sesión, obtener actividades y recursos
            detailed_sessions = []
            for session in sessions:
                activities = await self.get_session_activities(session.id_session)
                resources = await self.get_session_resources(session.id_session)
                
                # Para cada actividad, obtener sus recursos
                detailed_activities = []
                for activity in activities:
                    activity_resources = await self.get_activity_resources(activity.id_activity)
                    detailed_activities.append({
                        "activity": activity.__dict__,
                        "resources": activity_resources
                    })
                
                detailed_sessions.append({
                    "session": session.__dict__,
                    "activities": detailed_activities,
                    "resources": resources
                })
            
            return {
                "course": course.__dict__,
                "sessions": detailed_sessions,
                "bonds": [bond.__dict__ for bond in bonds],
                "total_sessions": len(sessions),
                "total_bonds": len(bonds),
                "course_structure": self._build_course_structure_text(detailed_sessions, bonds)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo contenido detallado del curso {course_id}: {e}")
            return {}
    
    def _build_course_structure_text(self, detailed_sessions: List[Dict], bonds: List[Dict]) -> str:
        """Construye texto estructurado del curso para usar en prompts."""
        structure = []
        
        for i, session_data in enumerate(detailed_sessions, 1):
            session = session_data["session"]
            activities = session_data["activities"]
            
            structure.append(f"""
**Sesión {session.get('session_index', i)}: {session.get('title', 'Sin título')}** ({session.get('duration_minutes', 0)} min)
Objetivo: {session.get('objective', 'No especificado')}
Actividades:""")
            
            for j, activity_data in enumerate(activities, 1):
                activity = activity_data["activity"]
                activity_type = "📝" if activity.get('item_type') == 'actividad' else "📚"
                structure.append(f"  {activity_type} {activity.get('title_item', 'Sin título')}")
        
        # Agregar bonos
        if bonds:
            structure.append("\n**🎁 BONOS INCLUIDOS:**")
            for i, bond in enumerate(bonds, 1):
                structure.append(f"{i}. {bond.get('content', 'Bono disponible')}")
        
        return "\n".join(structure)
    
    async def get_course_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de cursos."""
        query = """
            SELECT 
                COUNT(*) as total_courses,
                COUNT(DISTINCT level) as total_levels,
                COUNT(DISTINCT modality) as total_modalities,
                AVG(session_count) as avg_sessions,
                AVG(total_duration_min) as avg_duration_min
            FROM ai_courses
        """
        
        try:
            records = await self.db.execute_query(query, fetch_mode="one")
            if records and len(records) > 0:
                stats = records[0]
                return {
                    "total_courses": stats.get('total_courses', 0),
                    "total_levels": stats.get('total_levels', 0),
                    "total_modalities": stats.get('total_modalities', 0),
                    "avg_sessions": round(stats.get('avg_sessions', 0) or 0, 1),
                    "avg_duration_hours": round((stats.get('avg_duration_min', 0) or 0) / 60, 1)
                }
            return {}
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}