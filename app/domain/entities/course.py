"""
Entidades de dominio para cursos de IA.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class Course(BaseModel):
    """Entidad para representar un curso de IA."""
    
    id_course: UUID
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None  # Corregido typo del SQL
    created_at: datetime
    session_count: Optional[int] = None
    total_duration_min: Optional[int] = None
    price: Optional[str] = None
    currency: Optional[str] = None
    course_url: Optional[str] = None
    purchase_url: Optional[str] = None
    level: Optional[str] = None
    language: Optional[str] = None
    audience_category: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    roi: Optional[str] = None
    modality: str
    
    class Config:
        from_attributes = True


class CourseSession(BaseModel):
    """Entidad para representar una sesión de curso."""
    
    id_session: UUID
    created_at: datetime
    session_index: Optional[int] = None
    title: Optional[str] = None
    objective: Optional[str] = None
    duration_minutes: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    id_course_fk: UUID
    
    class Config:
        from_attributes = True


class SessionActivity(BaseModel):
    """Entidad para representar una actividad de sesión."""
    
    id_activity: UUID
    created_at: datetime
    id_course_fk: UUID
    id_session_fk: UUID
    item_session: int
    item_type: str
    title_item: str
    
    class Config:
        from_attributes = True


class Bond(BaseModel):
    """Entidad para representar un bono asociado a cursos."""
    
    id_bond: int
    created_at: datetime
    content: str
    type_bond: str
    id_courses_fk: Optional[UUID] = None
    
    class Config:
        from_attributes = True


class ElementUrl(BaseModel):
    """Entidad para representar URLs de elementos educativos."""
    
    id_element: UUID
    created_at: datetime
    id_session_fk: UUID
    id_activity_fk: Optional[UUID] = None
    item_type: str
    url_test: str
    description_url: str
    
    class Config:
        from_attributes = True


class CourseInfo(BaseModel):
    """Información completa de un curso para el bot."""
    
    course: Course
    sessions: List[CourseSession] = []
    bonds: List[Bond] = []
    total_activities: int = 0
    
    def get_basic_info(self) -> str:
        """Retorna información básica del curso para el chat."""
        info_parts = []
        
        if self.course.name:
            info_parts.append(f"📚 **{self.course.name}**")
        
        if self.course.short_description:
            info_parts.append(f"📝 {self.course.short_description}")
        
        if self.course.level:
            info_parts.append(f"📊 Nivel: {self.course.level}")
        
        if self.course.modality:
            info_parts.append(f"💻 Modalidad: {self.course.modality}")
        
        if self.course.session_count:
            info_parts.append(f"🗓️ Sesiones: {self.course.session_count}")
        
        if self.course.total_duration_min:
            hours = self.course.total_duration_min // 60
            minutes = self.course.total_duration_min % 60
            if hours > 0:
                info_parts.append(f"⏱️ Duración: {hours}h {minutes}min")
            else:
                info_parts.append(f"⏱️ Duración: {minutes}min")
        
        if self.course.price and self.course.currency:
            info_parts.append(f"💰 Precio: {self.course.price} {self.course.currency}")
        
        return "\n".join(info_parts)
    
    def get_detailed_info(self) -> str:
        """Retorna información detallada del curso."""
        info = self.get_basic_info()
        
        if self.course.long_description:
            info += f"\n\n📖 **Descripción completa:**\n{self.course.long_description}"
        
        if self.course.audience_category:
            info += f"\n\n👥 **Dirigido a:** {self.course.audience_category}"
        
        if self.course.roi:
            info += f"\n\n📈 **ROI esperado:** {self.course.roi}"
        
        if self.sessions:
            info += f"\n\n🗓️ **Sesiones programadas:**"
            for session in self.sessions[:3]:  # Mostrar máximo 3 sesiones
                if session.title:
                    info += f"\n• {session.title}"
                    if session.objective:
                        info += f" - {session.objective}"
        
        if self.bonds:
            info += f"\n\n🎁 **Bonos incluidos:**"
            for bond in self.bonds[:2]:  # Mostrar máximo 2 bonos
                info += f"\n• {bond.type_bond}: {bond.content[:100]}..."
        
        return info
    
    def get_purchase_info(self) -> Dict[str, Any]:
        """Retorna información para la compra."""
        return {
            "name": self.course.name,
            "price": self.course.price,
            "currency": self.course.currency,
            "purchase_url": self.course.purchase_url,
            "course_url": self.course.course_url,
            "modality": self.course.modality
        }


class CourseSearchFilters(BaseModel):
    """Filtros para búsqueda de cursos."""
    
    level: Optional[str] = None
    modality: Optional[str] = None
    language: Optional[str] = None
    audience_category: Optional[str] = None
    status: Optional[str] = None
    max_price: Optional[float] = None
    search_text: Optional[str] = None  # Búsqueda en nombre y descripción
    
    class Config:
        from_attributes = True