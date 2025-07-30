"""
Caso de uso para consultar información de cursos.
"""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.infrastructure.database.client import database_client
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.domain.entities.course import Course, CourseInfo, CourseSearchFilters

logger = logging.getLogger(__name__)


class QueryCourseInformationUseCase:
    """Caso de uso para consultar información de cursos."""
    
    def __init__(self):
        self.course_repo = CourseRepository()
        self.db = database_client
    
    async def initialize(self) -> bool:
        """Inicializa la conexión a la base de datos."""
        try:
            if not await self.db.connect():
                logger.warning("⚠️ No se pudo conectar a PostgreSQL")
                return False
            
            # Verificar que las tablas existen
            health_ok = await self.db.health_check()
            if not health_ok:
                logger.warning("⚠️ Health check de PostgreSQL falló")
                return False
            
            logger.info("✅ Sistema de consulta de cursos inicializado")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando sistema de cursos: {e}")
            return False
    
    async def search_courses_by_keyword(
        self, 
        keyword: str, 
        limit: int = 5
    ) -> List[Course]:
        """
        Busca cursos por palabra clave.
        
        Args:
            keyword: Palabra clave a buscar
            limit: Número máximo de resultados
        
        Returns:
            Lista de cursos que coinciden con la búsqueda
        """
        try:
            courses = await self.course_repo.search_courses_by_text(keyword, limit)
            logger.info(f"🔍 Búsqueda '{keyword}': {len(courses)} cursos encontrados")
            return courses
        except Exception as e:
            logger.error(f"Error buscando cursos por keyword '{keyword}': {e}")
            return []
    
    async def get_course_details(self, course_id: UUID) -> Optional[CourseInfo]:
        """
        Obtiene información detallada de un curso.
        
        Args:
            course_id: ID del curso
        
        Returns:
            Información completa del curso o None si no existe
        """
        try:
            course_info = await self.course_repo.get_course_complete_info(course_id)
            if course_info:
                logger.info(f"📚 Información completa obtenida para curso {course_id}")
            else:
                logger.warning(f"❌ Curso {course_id} no encontrado")
            return course_info
        except Exception as e:
            logger.error(f"Error obteniendo detalles del curso {course_id}: {e}")
            return None
    
    async def get_course_detailed_content(self, course_id: UUID) -> Dict[str, Any]:
        """
        Obtiene contenido detallado completo de un curso para usar en prompts.
        Incluye toda la información estructural: sesiones, actividades, bonos, recursos.
        
        Args:
            course_id: ID del curso
        
        Returns:
            Diccionario con información detallada para prompts o {} si no existe
        """
        try:
            detailed_content = await self.course_repo.get_course_detailed_content(course_id)
            if detailed_content:
                logger.info(f"📚 Contenido detallado obtenido para curso {course_id}")
                logger.info(f"   - {detailed_content.get('total_sessions', 0)} sesiones")
                logger.info(f"   - {detailed_content.get('total_bonds', 0)} bonos")
            else:
                logger.warning(f"❌ Contenido detallado del curso {course_id} no encontrado")
            return detailed_content
        except Exception as e:
            logger.error(f"Error obteniendo contenido detallado del curso {course_id}: {e}")
            return {}
    
    async def get_all_courses(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los cursos disponibles de la base de datos.
        
        Returns:
            Lista de diccionarios con información de cursos disponibles
        """
        try:
            # Obtener todos los cursos desde el repositorio
            courses = await self.course_repo.get_all_courses()
            
            if courses:
                logger.info(f"📚 Obtenidos {len(courses)} cursos de la base de datos")
                
                # Convertir a formato de diccionario para el welcome flow
                courses_data = []
                for course in courses:
                    course_data = {
                        'code': str(course.id_course),
                        'name': course.name,
                        'title': course.name,
                        'description': course.short_description or 'Descripción no disponible',
                        'price': course.price or 'Precio no disponible',
                        'cost': course.price or 'Precio no disponible',
                        'level': course.level or 'Nivel no disponible',
                        'difficulty': course.level or 'Nivel no disponible',
                        'sessions': course.session_count or 'Duración no disponible',
                        'duration_weeks': course.session_count or 'Duración no disponible',
                        'duration_hours': course.total_duration_min or 'Horas no disponibles',
                        'total_hours': course.total_duration_min or 'Horas no disponibles'
                    }
                    courses_data.append(course_data)
                
                return courses_data
            else:
                logger.warning("⚠️ No se encontraron cursos en la base de datos")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo todos los cursos: {e}")
            return []
    
    async def get_courses_by_level(self, level: str, limit: int = 5) -> List[Course]:
        """
        Obtiene cursos filtrados por nivel.
        
        Args:
            level: Nivel del curso (ej. "principiante", "intermedio", "avanzado")
            limit: Número máximo de resultados
        
        Returns:
            Lista de cursos del nivel especificado
        """
        try:
            courses = await self.course_repo.get_courses_by_level(level, limit)
            logger.info(f"📊 Cursos nivel '{level}': {len(courses)} encontrados")
            return courses
        except Exception as e:
            logger.error(f"Error obteniendo cursos por nivel '{level}': {e}")
            return []
    
    async def get_courses_by_modality(self, modality: str, limit: int = 5) -> List[Course]:
        """
        Obtiene cursos filtrados por modalidad.
        
        Args:
            modality: Modalidad del curso (ej. "online", "presencial", "híbrido")
            limit: Número máximo de resultados
        
        Returns:
            Lista de cursos de la modalidad especificada
        """
        try:
            courses = await self.course_repo.get_courses_by_modality(modality, limit)
            logger.info(f"💻 Cursos modalidad '{modality}': {len(courses)} encontrados")
            return courses
        except Exception as e:
            logger.error(f"Error obteniendo cursos por modalidad '{modality}': {e}")
            return []
    
    async def get_recommended_courses(
        self, 
        user_interests: List[str] = None,
        user_level: str = None,
        limit: int = 3
    ) -> List[Course]:
        """
        Obtiene cursos recomendados basados en intereses y nivel del usuario.
        
        Args:
            user_interests: Lista de intereses del usuario
            user_level: Nivel del usuario
            limit: Número máximo de cursos recomendados
        
        Returns:
            Lista de cursos recomendados
        """
        try:
            # Si hay nivel específico, filtrar por nivel
            if user_level:
                level_courses = await self.get_courses_by_level(user_level, limit * 2)
                if level_courses:
                    return level_courses[:limit]
            
            # Si hay intereses, buscar por palabras clave
            if user_interests:
                all_recommendations = []
                for interest in user_interests[:3]:  # Máximo 3 intereses
                    interest_courses = await self.search_courses_by_keyword(interest, 2)
                    all_recommendations.extend(interest_courses)
                
                # Eliminar duplicados manteniendo orden
                seen_ids = set()
                unique_courses = []
                for course in all_recommendations:
                    if course.id_course not in seen_ids:
                        seen_ids.add(course.id_course)
                        unique_courses.append(course)
                
                return unique_courses[:limit]
            
            # Si no hay filtros específicos, obtener cursos más populares
            filters = CourseSearchFilters(status="active")
            courses = await self.course_repo.get_all_courses(filters, limit)
            
            logger.info(f"💡 {len(courses)} cursos recomendados generados")
            return courses
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}")
            return []
    
    async def get_available_options(self) -> Dict[str, List[str]]:
        """
        Obtiene las opciones disponibles para filtros.
        
        Returns:
            Diccionario con niveles y modalidades disponibles
        """
        try:
            levels = await self.course_repo.get_available_levels()
            modalities = await self.course_repo.get_available_modalities()
            
            return {
                "levels": levels,
                "modalities": modalities
            }
        except Exception as e:
            logger.error(f"Error obteniendo opciones disponibles: {e}")
            return {"levels": [], "modalities": []}
    
    async def get_course_catalog_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del catálogo de cursos.
        
        Returns:
            Resumen con estadísticas y cursos destacados
        """
        try:
            # Obtener estadísticas
            stats = await self.course_repo.get_course_statistics()
            
            # Obtener opciones disponibles
            options = await self.get_available_options()
            
            # Obtener algunos cursos destacados
            featured_courses = await self.course_repo.get_active_courses(limit=3)
            
            summary = {
                "statistics": stats,
                "available_options": options,
                "featured_courses": [
                    {
                        "id": str(course.id_course),
                        "name": course.name,
                        "short_description": course.short_description,
                        "level": course.level,
                        "modality": course.modality
                    }
                    for course in featured_courses
                ],
                # Agregar sample_course para validación anti-inventos
                "sample_course": featured_courses[0].__dict__ if featured_courses else None
            }
            
            logger.info("📊 Resumen del catálogo generado")
            return summary
            
        except Exception as e:
            logger.error(f"Error generando resumen del catálogo: {e}")
            return {}
    
    async def format_course_for_chat(self, course: Course) -> str:
        """
        Formatea un curso para mostrar en el chat.
        
        Args:
            course: Objeto Course
        
        Returns:
            Texto formateado para WhatsApp
        """
        try:
            parts = []
            
            if course.name:
                parts.append(f"📚 **{course.name}**")
            
            if course.short_description:
                parts.append(f"📝 {course.short_description}")
            
            details = []
            if course.level:
                details.append(f"📊 Nivel: {course.level}")
            if course.modality:
                details.append(f"💻 Modalidad: {course.modality}")
            if course.session_count:
                details.append(f"🗓️ Sesiones: {course.session_count}")
            
            if details:
                parts.append(" | ".join(details))
            
            if course.price and course.currency:
                parts.append(f"💰 Precio: {course.price} {course.currency}")
            
            return "\n".join(parts)
            
        except Exception as e:
            logger.error(f"Error formateando curso para chat: {e}")
            return f"Curso: {course.name or 'Sin nombre'}"
    
    async def format_course_list_for_chat(self, courses: List[Course]) -> str:
        """
        Formatea una lista de cursos para mostrar en el chat.
        
        Args:
            courses: Lista de cursos
        
        Returns:
            Texto formateado para WhatsApp
        """
        if not courses:
            return "No se encontraron cursos que coincidan con tu búsqueda."
        
        formatted_courses = []
        for i, course in enumerate(courses, 1):
            course_text = await self.format_course_for_chat(course)
            formatted_courses.append(f"{i}. {course_text}")
        
        return "\n\n".join(formatted_courses)
    
    async def format_detailed_course_for_chat(self, detailed_content: Dict[str, Any]) -> str:
        """
        Formatea información detallada de un curso para mostrar en el chat.
        
        Args:
            detailed_content: Diccionario con información detallada del curso
        
        Returns:
            Texto formateado para WhatsApp con información completa
        """
        if not detailed_content:
            return "No se pudo obtener información detallada del curso."
        
        try:
            course_data = detailed_content.get('course', {})
            sessions_data = detailed_content.get('sessions', [])
            bonds_data = detailed_content.get('bonds', [])
            
            parts = []
            
            # Información básica del curso
            if course_data.get('name'):
                parts.append(f"📚 **{course_data['name']}**")
            
            if course_data.get('short_description'):
                parts.append(f"📝 {course_data['short_description']}")
            
            # Detalles del curso
            details = []
            if course_data.get('price') and course_data.get('currency'):
                details.append(f"💰 {course_data['price']} {course_data['currency']}")
            if course_data.get('session_count'):
                duration_hours = round(course_data.get('total_duration_min', 0) / 60, 1)
                details.append(f"🗓️ {course_data['session_count']} sesiones ({duration_hours}h)")
            if course_data.get('level'):
                details.append(f"📊 {course_data['level']}")
            if course_data.get('modality'):
                details.append(f"💻 {course_data['modality']}")
            
            if details:
                parts.append(" | ".join(details))
            
            # Estructura del curso (primeras 3 sesiones para no saturar)
            if sessions_data:
                parts.append("\n**📋 ESTRUCTURA DEL CURSO:**")
                for i, session_data in enumerate(sessions_data[:3], 1):
                    session = session_data.get('session', {})
                    session_title = session.get('title', f'Sesión {i}')
                    session_duration = session.get('duration_minutes', 0)
                    activities_count = len(session_data.get('activities', []))
                    
                    parts.append(f"**Sesión {i}: {session_title}** ({session_duration} min)")
                    if activities_count > 0:
                        parts.append(f"   • {activities_count} actividades prácticas")
                
                if len(sessions_data) > 3:
                    parts.append(f"   ... y {len(sessions_data) - 3} sesiones más")
            
            # Bonos (primeros 5 para no saturar)
            if bonds_data:
                parts.append(f"\n**🎁 BONOS INCLUIDOS ({len(bonds_data)} total):**")
                for i, bond in enumerate(bonds_data[:5], 1):
                    bond_content = bond.get('content', 'Bono disponible')
                    # Truncar si es muy largo
                    if len(bond_content) > 60:
                        bond_content = bond_content[:60] + "..."
                    parts.append(f"{i}. {bond_content}")
                
                if len(bonds_data) > 5:
                    parts.append(f"   ... y {len(bonds_data) - 5} bonos más")
            
            return "\n".join(parts)
            
        except Exception as e:
            logger.error(f"Error formateando curso detallado para chat: {e}")
            return "Error al formatear la información del curso."