"""
Entidad de campaña para el flujo de anuncios.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Campaign:
    """Entidad que representa una campaña publicitaria"""
    
    id: str
    name: str
    description: Optional[str] = None
    hashtag: Optional[str] = None
    platform: Optional[str] = None  # facebook, instagram, etc.
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
            'name': self.name,
            'description': self.description,
            'hashtag': self.hashtag,
            'platform': self.platform,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 