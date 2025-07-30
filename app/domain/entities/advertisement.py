"""
Entidad de anuncio para el flujo de anuncios.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Advertisement:
    """Entidad que representa un anuncio"""
    
    id: str
    campaign_id: str
    course_id: str
    user_id: str
    message_content: str
    hashtags_detected: list[str]
    interaction_type: str = "ad_click"  # ad_click, privacy_accepted, course_presented
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'message_content': self.message_content,
            'hashtags_detected': self.hashtags_detected,
            'interaction_type': self.interaction_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 