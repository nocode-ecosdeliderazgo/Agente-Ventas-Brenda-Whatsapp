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
    stage: str = "first_contact"  # first_contact, privacy_flow, course_selection, sales_agent, converted
    privacy_accepted: bool = False
    privacy_requested: bool = False  # Nueva: si ya se le pidió aceptar privacidad
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
    
    # Nuevos campos para flujos personalizados
    current_flow: str = "none"  # none, privacy, course_selection, sales_conversation
    flow_step: int = 0  # paso actual dentro del flujo
    waiting_for_response: str = ""  # qué tipo de respuesta espera (name, privacy_acceptance, course_choice, etc.)
    
    def is_first_interaction(self) -> bool:
        """Verifica si es la primera interacción del usuario."""
        return self.interaction_count <= 1 and self.stage == "first_contact"
    
    def needs_privacy_flow(self) -> bool:
        """Verifica si necesita pasar por el flujo de privacidad."""
        return not self.privacy_accepted and not self.privacy_requested
    
    def is_ready_for_sales_agent(self) -> bool:
        """Verifica si está listo para el agente de ventas inteligente."""
        return (self.privacy_accepted and 
                self.interaction_count > 1 and 
                self.stage not in ["first_contact", "privacy_flow"])
    
    def get_conversation_context(self) -> str:
        """Obtiene contexto resumido para el agente."""
        context = f"Usuario: {self.name or 'Anónimo'}"
        if self.role:
            context += f", {self.role}"
        if self.interests:
            context += f", Intereses: {', '.join(self.interests)}"
        if self.pain_points:
            context += f", Necesidades: {', '.join(self.pain_points[:3])}"
        return context

class MemoryManager:
    """
    Gestor de memoria persistente con auto-corrección.
    """
    def __init__(self, memory_dir: str = "memorias"):
        self.memory_dir = memory_dir
        self.leads_cache = {}
        os.makedirs(memory_dir, exist_ok=True)
    
    def get_lead_memory(self, user_id: str) -> LeadMemory:
        """
        Obtiene la memoria de un lead específico con auto-corrección.
        
        Funcionalidad:
        - Carga memoria desde cache o archivo
        - Aplica corrección automática si es necesario
        - Crea nueva memoria si no existe
        """
        if user_id not in self.leads_cache:
            loaded_lead = self.load_lead_memory(user_id)
            if loaded_lead:
                self.leads_cache[user_id] = loaded_lead
            else:
                # Crear nueva memoria con timestamp
                now = datetime.now()
                self.leads_cache[user_id] = LeadMemory(
                    user_id=user_id,
                    created_at=now,
                    updated_at=now
                )
        
        return self.leads_cache[user_id]
    
    def save_lead_memory(self, user_id: str, lead_memory: LeadMemory) -> bool:
        """
        Guarda la memoria de un lead específico con backup automático.
        
        Funcionalidad:
        - Crea backup antes de guardar
        - Actualiza timestamp de modificación
        - Maneja errores de escritura
        """
        try:
            lead_memory.updated_at = datetime.now()
            self.leads_cache[user_id] = lead_memory
            
            # Asegurar que el directorio existe
            os.makedirs(self.memory_dir, exist_ok=True)
            
            filename = f"memory_{user_id}.json"
            filepath = os.path.join(self.memory_dir, filename)
            
            # Backup antes de guardar
            if os.path.exists(filepath):
                backup_path = f"{filepath}.backup"
                shutil.copy2(filepath, backup_path)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(lead_memory), f, ensure_ascii=False, indent=2)
            
            logging.info(f"✅ Memoria guardada para usuario {user_id}")
            return True
        except Exception as e:
            logging.error(f"❌ Error saving lead memory for {user_id}: {e}")
            return False
    
    def load_lead_memory(self, user_id: str) -> Optional[LeadMemory]:
        """
        Carga la memoria desde archivo con validación.
        
        Funcionalidad:
        - Carga desde archivo JSON
        - Valida estructura de datos
        - Convierte tipos de datos apropiadamente
        """
        try:
            filename = f"memory_{user_id}.json"
            filepath = os.path.join(self.memory_dir, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                logging.info(f"✅ Memoria cargada para usuario {user_id}")
                return self.from_dict(data)
        except Exception as e:
            logging.error(f"❌ Error loading lead memory for {user_id}: {e}")
        return None
    
    def to_dict(self, lead_memory: LeadMemory) -> dict:
        """Convierte LeadMemory a diccionario para JSON."""
        data = asdict(lead_memory)
        # Convertir datetime a string para JSON
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() if value else None
        return data
    
    def from_dict(self, data: dict) -> LeadMemory:
        """Convierte diccionario desde JSON a LeadMemory."""
        # Convertir strings de datetime de vuelta a datetime
        for key in ['last_interaction', 'created_at', 'updated_at']:
            if data.get(key):
                data[key] = datetime.fromisoformat(data[key])
        
        # Inicializar listas vacías si son None
        if data.get('message_history') is None:
            data['message_history'] = []
        if data.get('pain_points') is None:
            data['pain_points'] = []
        if data.get('buying_signals') is None:
            data['buying_signals'] = []
        if data.get('interests') is None:
            data['interests'] = []
        
        # Valores por defecto para nuevos campos (compatibilidad hacia atrás)
        if 'privacy_requested' not in data:
            data['privacy_requested'] = False
        if 'current_flow' not in data:
            data['current_flow'] = "none"
        if 'flow_step' not in data:
            data['flow_step'] = 0
        if 'waiting_for_response' not in data:
            data['waiting_for_response'] = ""
        
        # Migrar stage antiguo a nuevo sistema
        if data.get('stage') == 'initial':
            data['stage'] = 'first_contact'
        
        return LeadMemory(**data) 