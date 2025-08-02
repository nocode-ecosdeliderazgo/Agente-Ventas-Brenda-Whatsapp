"""
Entidad de hashtag para el flujo de anuncios.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class HashtagType(Enum):
    """Tipos de hashtags"""
    COURSE = "course"
    CAMPAIGN = "campaign"
    UNKNOWN = "unknown"


@dataclass
class Hashtag:
    """Entidad que representa un hashtag"""
    
    text: str
    hashtag_type: HashtagType
    mapped_value: Optional[str] = None  # ID del curso o nombre de campaña
    confidence: float = 1.0  # Confianza en la detección (0.0 a 1.0)
    
    def __post_init__(self):
        # Normalizar el texto del hashtag
        self.text = self.text.strip()
        if not self.text.startswith('#'):
            self.text = f"#{self.text}"
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            'text': self.text,
            'hashtag_type': self.hashtag_type.value,
            'mapped_value': self.mapped_value,
            'confidence': self.confidence
        }
    
    def is_course_hashtag(self) -> bool:
        """Verifica si es un hashtag de curso"""
        return self.hashtag_type == HashtagType.COURSE
    
    def is_campaign_hashtag(self) -> bool:
        """Verifica si es un hashtag de campaña"""
        return self.hashtag_type == HashtagType.CAMPAIGN 