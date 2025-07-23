from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional, Any
import os, json, shutil, logging

@dataclass
class LeadMemory:
    """
    Estructura de memoria persistente para cada usuario/lead.
    """
    user_id: str = ""
    name: str = ""
    selected_course: str = ""
    stage: str = "initial"
    privacy_accepted: bool = False
    lead_score: int = 50
    interaction_count: int = 0
    message_history: Optional[List[Dict]] = None
    pain_points: Optional[List[str]] = None
    buying_signals: Optional[List[str]] = None
    automation_needs: Optional[Dict[str, Any]] = None
    role: Optional[str] = None
    interests: Optional[List[str]] = None
    interest_level: str = "unknown"
    last_interaction: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    brenda_introduced: bool = False

class MemoryManager:
    """
    Gestor de memoria persistente con auto-corrección.
    """
    def __init__(self, memory_dir: str = "memorias"):
        self.memory_dir = memory_dir
        self.leads_cache = {}
        os.makedirs(memory_dir, exist_ok=True)
    # TODO: Implementar métodos get_lead_memory, save_lead_memory, load_lead_memory adaptados 