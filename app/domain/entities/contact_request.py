#!/usr/bin/env python3
"""
Entidad para representar solicitudes de contacto con asesores.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ContactRequest(BaseModel):
    """
    Entidad que representa una solicitud de contacto con un asesor.
    """
    
    # Identificadores
    user_id: str = Field(..., description="ID único del usuario")
    request_id: Optional[str] = Field(None, description="ID único de la solicitud")
    
    # Información del usuario
    user_name: str = Field(..., description="Nombre del usuario")
    user_phone: str = Field(..., description="Teléfono del usuario")
    user_role: Optional[str] = Field(None, description="Rol del usuario en la empresa")
    company_size: Optional[str] = Field(None, description="Tamaño de la empresa")
    industry: Optional[str] = Field(None, description="Industria del usuario")
    
    # Detalles de la solicitud
    contact_reason: str = Field(..., description="Motivo del contacto")
    contact_timestamp: Optional[float] = Field(None, description="Timestamp de la solicitud")
    
    # Estado de la solicitud
    status: str = Field(default="pending", description="Estado de la solicitud")
    priority: str = Field(default="normal", description="Prioridad de la solicitud")
    
    # Información del asesor
    assigned_advisor: Optional[str] = Field(None, description="ID del asesor asignado")
    advisor_name: Optional[str] = Field(None, description="Nombre del asesor")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    assigned_at: Optional[datetime] = Field(None, description="Fecha de asignación")
    completed_at: Optional[datetime] = Field(None, description="Fecha de completado")
    
    # Notas y comentarios
    notes: Optional[str] = Field(None, description="Notas adicionales")
    advisor_notes: Optional[str] = Field(None, description="Notas del asesor")
    
    # Métricas
    response_time: Optional[int] = Field(None, description="Tiempo de respuesta en minutos")
    satisfaction_score: Optional[int] = Field(None, description="Puntuación de satisfacción (1-5)")
    
    class Config:
        """Configuración de Pydantic."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def __init__(self, **data):
        """Inicializa la solicitud de contacto."""
        super().__init__(**data)
        
        # Generar ID único si no existe
        if not self.request_id:
            import uuid
            self.request_id = f"REQ_{uuid.uuid4().hex[:8].upper()}"
        
        # Establecer timestamp de creación si no existe
        if not self.created_at:
            self.created_at = datetime.now()
    
    def assign_advisor(self, advisor_id: str, advisor_name: str) -> None:
        """
        Asigna un asesor a la solicitud.
        
        Args:
            advisor_id: ID del asesor
            advisor_name: Nombre del asesor
        """
        self.assigned_advisor = advisor_id
        self.advisor_name = advisor_name
        self.assigned_at = datetime.now()
        self.status = "assigned"
        self.updated_at = datetime.now()
    
    def mark_as_completed(self, satisfaction_score: Optional[int] = None) -> None:
        """
        Marca la solicitud como completada.
        
        Args:
            satisfaction_score: Puntuación de satisfacción opcional
        """
        self.status = "completed"
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
        
        if satisfaction_score is not None:
            self.satisfaction_score = satisfaction_score
    
    def update_status(self, new_status: str, notes: Optional[str] = None) -> None:
        """
        Actualiza el estado de la solicitud.
        
        Args:
            new_status: Nuevo estado
            notes: Notas opcionales
        """
        self.status = new_status
        self.updated_at = datetime.now()
        
        if notes:
            if self.notes:
                self.notes += f"\n{notes}"
            else:
                self.notes = notes
    
    def calculate_response_time(self) -> Optional[int]:
        """
        Calcula el tiempo de respuesta en minutos.
        
        Returns:
            Tiempo de respuesta en minutos o None si no hay datos
        """
        if self.assigned_at and self.created_at:
            delta = self.assigned_at - self.created_at
            return int(delta.total_seconds() / 60)
        return None
    
    def is_urgent(self) -> bool:
        """
        Determina si la solicitud es urgente.
        
        Returns:
            True si es urgente
        """
        urgent_keywords = [
            'urgente', 'inmediato', 'crítico', 'emergencia',
            'necesito ya', 'lo antes posible', 'hoy mismo'
        ]
        
        return any(keyword in self.contact_reason.lower() for keyword in urgent_keywords)
    
    def get_priority_score(self) -> int:
        """
        Calcula un score de prioridad basado en varios factores.
        
        Returns:
            Score de prioridad (1-10)
        """
        score = 5  # Prioridad base
        
        # Factor de urgencia
        if self.is_urgent():
            score += 3
        
        # Factor de tamaño de empresa (empresas grandes = mayor prioridad)
        if self.company_size:
            if 'grande' in self.company_size.lower() or 'enterprise' in self.company_size.lower():
                score += 2
            elif 'mediana' in self.company_size.lower() or 'medium' in self.company_size.lower():
                score += 1
        
        # Factor de industria (algunas industrias tienen mayor prioridad)
        high_priority_industries = ['tecnología', 'finanzas', 'salud', 'educación']
        if self.industry and any(ind in self.industry.lower() for ind in high_priority_industries):
            score += 1
        
        # Factor de tiempo de espera
        if self.created_at:
            hours_since_creation = (datetime.now() - self.created_at).total_seconds() / 3600
            if hours_since_creation > 24:
                score += 2
            elif hours_since_creation > 4:
                score += 1
        
        return min(score, 10)  # Máximo 10
    
    def to_dict(self) -> dict:
        """
        Convierte la entidad a diccionario.
        
        Returns:
            Diccionario con los datos de la solicitud
        """
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_phone': self.user_phone,
            'user_role': self.user_role,
            'company_size': self.company_size,
            'industry': self.industry,
            'contact_reason': self.contact_reason,
            'status': self.status,
            'priority': self.priority,
            'assigned_advisor': self.assigned_advisor,
            'advisor_name': self.advisor_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'advisor_notes': self.advisor_notes,
            'response_time': self.response_time,
            'satisfaction_score': self.satisfaction_score,
            'priority_score': self.get_priority_score()
        }
    
    def __str__(self) -> str:
        """Representación en string de la solicitud."""
        return f"ContactRequest(id={self.request_id}, user={self.user_name}, status={self.status})"
    
    def __repr__(self) -> str:
        """Representación detallada de la solicitud."""
        return f"ContactRequest(request_id='{self.request_id}', user_id='{self.user_id}', status='{self.status}')" 