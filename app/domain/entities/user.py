"""
Entidades de dominio para usuarios.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class UserStatus(Enum):
    """Estados del usuario."""
    ACTIVE = "active"
    NEW = "new"
    BLOCKED = "blocked"


@dataclass
class User:
    """Usuario de WhatsApp."""
    
    # Identificador único
    phone_number: str
    
    # Información personal
    name: Optional[str] = None
    preferred_name: Optional[str] = None
    
    # Estado y metadatos
    status: UserStatus = UserStatus.NEW
    created_at: datetime = None
    last_interaction: datetime = None
    
    # Contexto conversacional
    current_flow: Optional[str] = None
    memory: Dict[str, Any] = None
    
    def __post_init__(self):
        """Inicializa valores por defecto."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.memory is None:
            self.memory = {}
    
    @property
    def display_name(self) -> str:
        """Nombre para mostrar en conversaciones."""
        return self.preferred_name or self.name or "Usuario"
    
    @property
    def is_new_user(self) -> bool:
        """Verifica si es un usuario nuevo."""
        return self.status == UserStatus.NEW
    
    def update_last_interaction(self):
        """Actualiza timestamp de última interacción."""
        self.last_interaction = datetime.now()
    
    def set_memory(self, key: str, value: Any):
        """Establece un valor en la memoria del usuario."""
        self.memory[key] = value
    
    def get_memory(self, key: str, default=None):
        """Obtiene un valor de la memoria del usuario."""
        return self.memory.get(key, default)