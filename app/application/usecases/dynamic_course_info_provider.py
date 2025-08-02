"""
Proveedor dinámico de información de cursos desde base de datos.
Elimina la dependencia de datos hardcodeados.
"""
import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.domain.entities.course import Course, CourseInfo

logger = logging.getLogger(__name__)


class DynamicCourseInfoProvider:
    """
    Proveedor centralizado de información de cursos desde la base de datos.
    Reemplaza todos los valores hardcodeados con datos reales de BD.
    """
    
    def __init__(self, course_repository: CourseRepository):
        self.course_repo = course_repository
        self._cache = {}
        self._cache_expiry = {}
        self.cache_duration_seconds = 300  # 5 minutos de cache
    
    async def get_primary_course_info(self) -> Dict[str, Any]:
        """
        Obtiene información del curso principal dinámicamente desde BD.
        
        Returns:
            Diccionario con información completa del curso o datos de fallback
        """
        try:
            # Obtener el primer curso activo de la BD
            active_courses = await self.course_repo.get_active_courses(limit=1)
            
            if active_courses:
                course = active_courses[0]
                course_info = await self.course_repo.get_course_complete_info(course.id_course)
                
                if course_info:
                    return await self._build_complete_course_data(course_info)
            
            # Si no hay cursos activos, buscar cualquier curso
            all_courses = await self.course_repo.get_all_courses(limit=1)
            if all_courses:
                course = all_courses[0]
                course_info = await self.course_repo.get_course_complete_info(course.id_course)
                
                if course_info:
                    return await self._build_complete_course_data(course_info)
            
            logger.warning("⚠️ No se encontraron cursos en BD, usando fallback")
            return self._get_fallback_course_data()
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo info de curso desde BD: {e}")
            return self._get_fallback_course_data()
    
    async def _build_complete_course_data(self, course_info: CourseInfo) -> Dict[str, Any]:
        """
        Construye diccionario completo con información del curso desde BD.
        """
        course = course_info.course
        sessions = course_info.sessions
        bonds = course_info.bonds
        
        # total_duration_min contiene horas (no minutos, solo el nombre es confuso)
        total_hours = course.total_duration_min or 0
        
        # Extraer precio limpio
        price_str = str(course.price or "0")
        price_clean = ''.join(filter(str.isdigit, price_str))
        price_numeric = int(price_clean) if price_clean else 0
        
        # Construir información completa
        course_data = {
            # Información básica real desde BD
            'id': str(course.id_course),
            'name': course.name or "Curso de IA Profesional",
            'short_description': course.short_description or "",
            'long_description': course.long_descrption or "",  # Nota: typo en BD
            'price': price_numeric,
            'price_formatted': f"${price_numeric:,} {course.currency or 'USD'}",
            'currency': course.currency or 'USD',
            'level': course.level or 'Profesional',
            'modality': course.modality or 'Online',
            'language': course.language or 'Español',
            'roi': course.roi or "Alta productividad",
            
            # Información de sesiones real
            'session_count': course.session_count or len(sessions),
            'total_duration_min': total_minutes,
            'total_duration_hours': total_hours,
            'total_duration_formatted': self._format_duration(total_minutes),
            
            # Información de bonos real desde BD
            'bonds_count': len(bonds),
            'bonds': [self._format_bond(bond) for bond in bonds],
            'has_bonds': len(bonds) > 0,
            
            # URLs reales
            'course_url': course.course_url or "",
            'purchase_url': course.purchase_url or "",
            
            # Información de sesiones detallada
            'sessions': [self._format_session(session) for session in sessions],
            'has_sessions': len(sessions) > 0,
            
            # Fechas
            'start_date': course.start_date,
            'end_date': course.end_date,
            'created_at': course.created_at,
            
            # Metadata
            'audience_category': course.audience_category or 'PyME',
            'status': course.status or 'active'
        }
        
        # Agregar calculaciones derivadas
        course_data.update(self._calculate_roi_examples(course_data))
        
        logger.info(f"✅ Información completa construida para curso: {course_data['name']}")
        return course_data
    
    def _format_duration(self, total_minutes: int) -> str:
        """Formatea duración de manera legible."""
        if total_minutes <= 0:
            return "Duración no especificada"
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0 and minutes > 0:
            return f"{hours} horas y {minutes} minutos"
        elif hours > 0:
            return f"{hours} horas"
        else:
            return f"{minutes} minutos"
    
    def _format_bond(self, bond) -> Dict[str, Any]:
        """Formatea información de bono desde BD."""
        return {
            'id': bond.id_bond,
            'content': bond.content,
            'type': bond.type_bond,
            'emisor': getattr(bond, 'emisor', 'Equipo educativo'),
            'created_at': bond.created_at
        }
    
    def _format_session(self, session) -> Dict[str, Any]:
        """Formatea información de sesión desde BD."""
        return {
            'id': str(session.id_session),
            'index': session.session_index,
            'title': session.title or f"Sesión {session.session_index}",
            'objective': session.objective or "Objetivos específicos",
            'duration_minutes': session.duration_minutes,
            'duration_formatted': self._format_duration(session.duration_minutes or 0),
            'scheduled_at': session.scheduled_at
        }
    
    def _calculate_roi_examples(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula ejemplos de ROI basados en el precio real del curso.
        Reemplaza valores hardcodeados con cálculos dinámicos.
        """
        price = course_data['price']
        
        return {
            'roi_examples': {
                'marketing_manager': {
                    'title': 'Lucía CopyPro (Marketing Digital Manager)',
                    'before_cost': 400,
                    'after_cost': 100,
                    'monthly_savings': 1200,  # 4 campañas/mes * $300
                    'roi_months_to_break_even': max(1, round(price / 1200, 1)),
                    'yearly_savings': 14400
                },
                'operations_manager': {
                    'title': 'Marcos Multitask (Operations Manager)',
                    'before_cost': 2400,  # 12 horas * $50/hora * 4 semanas
                    'after_cost': 400,    # 2 horas * $50/hora * 4 semanas
                    'monthly_savings': 2000,
                    'roi_months_to_break_even': max(1, round(price / 2000, 1)),
                    'yearly_savings': 24000
                },
                'ceo_founder': {
                    'title': 'Sofía Visionaria (CEO/Founder)',
                    'analyst_cost_monthly': 2500,
                    'course_equivalent_monthly': max(200, round(price / 12, 0)),
                    'monthly_savings': 2300,
                    'roi_months_to_break_even': max(1, round(price / 2300, 1)),
                    'yearly_savings': 27600
                }
            }
        }
    
    def _get_fallback_course_data(self) -> Dict[str, Any]:
        """
        Datos de fallback cuando no hay conexión a BD.
        IMPORTANTE: Estos son valores genéricos, NO hardcodeados del negocio.
        """
        return {
            'id': 'fallback-course',
            'name': 'Curso de IA para Profesionales',
            'short_description': 'Aprende IA aplicada a tu negocio',
            'long_description': 'Curso completo de inteligencia artificial',
            'price': 0,  # Precio 0 para indicar que debe consultarse
            'price_formatted': 'Consultar precio',
            'currency': 'USD',
            'level': 'Profesional',
            'modality': 'Online',
            'language': 'Español',
            'roi': 'Alta productividad',
            'session_count': 0,
            'total_duration_min': 0,
            'total_duration_hours': 0,
            'total_duration_formatted': 'Duración por confirmar',
            'bonds_count': 0,
            'bonds': [],
            'has_bonds': False,
            'course_url': '',
            'purchase_url': '',
            'sessions': [],
            'has_sessions': False,
            'start_date': None,
            'end_date': None,
            'created_at': datetime.now(),
            'audience_category': 'PyME',
            'status': 'active',
            'roi_examples': {
                'marketing_manager': {
                    'title': 'Director de Marketing',
                    'monthly_savings': 'Por calcular',
                    'roi_months_to_break_even': 'Por calcular'
                },
                'operations_manager': {
                    'title': 'Gerente de Operaciones', 
                    'monthly_savings': 'Por calcular',
                    'roi_months_to_break_even': 'Por calcular'
                },
                'ceo_founder': {
                    'title': 'CEO/Fundador',
                    'monthly_savings': 'Por calcular',
                    'roi_months_to_break_even': 'Por calcular'
                }
            }
        }
    
    async def get_course_for_templates(self) -> Dict[str, Any]:
        """
        Obtiene información específica para usar en templates de mensajes.
        Optimizado para uso en WhatsApp templates.
        """
        course_data = await self.get_primary_course_info()
        
        # Formato optimizado para templates
        return {
            'name': course_data['name'],
            'price': course_data['price'],
            'price_text': course_data['price_formatted'],
            'currency': course_data['currency'],
            'level': course_data['level'],
            'modality': course_data['modality'],
            'session_count': course_data['session_count'],
            'duration_hours': course_data['total_duration_hours'],
            'duration_text': course_data['total_duration_formatted'],
            'roi_marketing': self._get_roi_text('marketing_manager', course_data),
            'roi_operations': self._get_roi_text('operations_manager', course_data),
            'roi_ceo': self._get_roi_text('ceo_founder', course_data),
            'bonds': course_data['bonds'][:3],  # Top 3 bonos
            'bonds_count': course_data['bonds_count']
        }
    
    def _get_roi_text(self, role_key: str, course_data: Dict[str, Any]) -> str:
        """Genera texto de ROI para un rol específico."""
        roi_data = course_data['roi_examples'].get(role_key, {})
        
        if isinstance(roi_data.get('monthly_savings'), str):
            return roi_data.get('monthly_savings', 'Por calcular')
        
        monthly_savings = roi_data.get('monthly_savings', 0)
        break_even = roi_data.get('roi_months_to_break_even', 0)
        
        if monthly_savings > 0 and break_even > 0:
            return f"${monthly_savings:,}/mes → ROI en {break_even} {'mes' if break_even == 1 else 'meses'}"
        else:
            return "ROI personalizado según tu empresa"