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
    
    # 🆕 CAMPOS DE PERSONALIZACIÓN AVANZADA (FASE 2)
    # Buyer persona information
    buyer_persona_match: str = "unknown"  # lucia_copypro, marcos_multitask, sofia_visionaria, ricardo_rh_agil, daniel_data_innovador
    professional_level: str = "unknown"  # junior, mid-level, senior, executive
    company_size: str = "unknown"  # startup, small, medium, large, enterprise
    industry_sector: str = "unknown"  # marketing, operations, tech, consulting, healthcare, etc.
    technical_level: str = "unknown"  # beginner, intermediate, advanced
    decision_making_power: str = "unknown"  # influencer, decision_maker, budget_holder
    
    # Advanced insights
    budget_indicators: Optional[List[str]] = None  # low, medium, high, premium signals
    urgency_signals: Optional[List[str]] = None  # urgency indicators from conversation
    conversation_history: Optional[List[Dict]] = None  # detailed conversation log
    insights_confidence: float = 0.0  # confidence in extracted insights (0.0-1.0)
    last_insights_update: Optional[str] = None  # last time insights were updated
    
    # Personalization context
    response_style_preference: str = "business"  # business, technical, casual, executive
    communication_frequency: str = "standard"  # low, standard, high
    preferred_examples: Optional[List[str]] = None  # types of examples that resonate
    
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
    
    # 🆕 MÉTODOS DE PERSONALIZACIÓN AVANZADA (FASE 2)
    
    def get_buyer_persona_info(self) -> Dict[str, Any]:
        """Obtiene información completa del buyer persona detectado."""
        return {
            'persona': self.buyer_persona_match,
            'professional_level': self.professional_level,
            'company_size': self.company_size,
            'industry_sector': self.industry_sector,
            'technical_level': self.technical_level,
            'decision_making_power': self.decision_making_power,
            'confidence': self.insights_confidence
        }
    
    def get_personalization_context(self) -> Dict[str, Any]:
        """Obtiene contexto completo para personalización de respuestas."""
        return {
            'user_profile': {
                'name': self.name,
                'role': self.role,
                'buyer_persona': self.buyer_persona_match,
                'professional_level': self.professional_level,
                'company_size': self.company_size,
                'industry_sector': self.industry_sector,
                'technical_level': self.technical_level,
                'decision_making_power': self.decision_making_power
            },
            'interests_and_needs': {
                'interests': self.interests or [],
                'pain_points': self.pain_points or [],
                'automation_needs': self.automation_needs or {},
                'buying_signals': self.buying_signals or []
            },
            'communication_context': {
                'interaction_count': self.interaction_count,
                'stage': self.stage,
                'interest_level': self.interest_level,
                'lead_score': self.lead_score,
                'response_style_preference': self.response_style_preference,
                'urgency_signals': self.urgency_signals or []
            },
            'metadata': {
                'insights_confidence': self.insights_confidence,
                'last_insights_update': self.last_insights_update,
                'privacy_accepted': self.privacy_accepted
            }
        }
    
    def is_high_value_lead(self) -> bool:
        """Determina si es un lead de alto valor basado en características."""
        high_value_indicators = 0
        
        # Buyer persona de alto valor
        if self.buyer_persona_match in ['sofia_visionaria', 'daniel_data_innovador']:
            high_value_indicators += 2
        
        # Nivel profesional senior
        if self.professional_level in ['senior', 'executive']:
            high_value_indicators += 2
        
        # Poder de decisión
        if self.decision_making_power in ['decision_maker', 'budget_holder']:
            high_value_indicators += 2
        
        # Empresa mediana/grande
        if self.company_size in ['medium', 'large', 'enterprise']:
            high_value_indicators += 1
        
        # Señales de urgencia
        if self.urgency_signals and len(self.urgency_signals) > 0:
            high_value_indicators += 1
        
        # Lead score alto
        if self.lead_score >= 75:
            high_value_indicators += 1
        
        return high_value_indicators >= 4
    
    def get_recommended_approach(self) -> str:
        """Recomienda approach de comunicación basado en perfil."""
        if self.buyer_persona_match == 'lucia_copypro':
            return 'creative_roi_focused'
        elif self.buyer_persona_match == 'marcos_multitask':
            return 'efficiency_operational'
        elif self.buyer_persona_match == 'sofia_visionaria':
            return 'strategic_executive'
        elif self.buyer_persona_match == 'ricardo_rh_agil':
            return 'people_development'
        elif self.buyer_persona_match == 'daniel_data_innovador':
            return 'technical_analytical'
        else:
            return 'general_business'
    
    def should_use_technical_language(self) -> bool:
        """Determina si usar lenguaje técnico basado en perfil."""
        technical_personas = ['daniel_data_innovador']
        technical_levels = ['intermediate', 'advanced']
        
        return (self.buyer_persona_match in technical_personas or 
                self.technical_level in technical_levels)
    
    def get_conversation_priority_score(self) -> int:
        """Calcula puntuación de prioridad para esta conversación."""
        priority_score = 0
        
        # Base score from lead score
        priority_score += self.lead_score
        
        # High-value persona bonus
        if self.is_high_value_lead():
            priority_score += 20
        
        # Urgency signals
        if self.urgency_signals:
            priority_score += len(self.urgency_signals) * 5
        
        # Stage bonus (closer to conversion = higher priority)
        stage_bonuses = {
            'first_contact': 0,
            'privacy_flow': 5,
            'course_selection': 15,
            'sales_agent': 25,
            'converted': 30
        }
        priority_score += stage_bonuses.get(self.stage, 0)
        
        return min(priority_score, 100)  # Cap at 100

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
    
    def clear_user_memory(self, user_id: str) -> bool:
        """
        Limpia completamente la memoria de un usuario específico.
        
        Args:
            user_id: ID del usuario cuya memoria se va a limpiar
            
        Returns:
            bool: True si se limpió exitosamente, False en caso contrario
        """
        try:
            # Remover del cache
            if user_id in self.leads_cache:
                del self.leads_cache[user_id]
            
            # Eliminar archivo de memoria
            filename = f"memory_{user_id}.json"
            filepath = os.path.join(self.memory_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logging.info(f"✅ Memoria eliminada para usuario {user_id}")
            
            return True
        except Exception as e:
            logging.error(f"❌ Error clearing memory for {user_id}: {e}")
            return False
    
    def reset_user_memory(self, user_id: str) -> bool:
        """
        Resetea la memoria de un usuario a estado inicial (nueva conversación).
        
        Args:
            user_id: ID del usuario cuya memoria se va a resetear
            
        Returns:
            bool: True si se reseteó exitosamente, False en caso contrario
        """
        try:
            # Crear nueva memoria limpia
            now = datetime.now()
            new_memory = LeadMemory(
                user_id=user_id,
                created_at=now,
                updated_at=now
            )
            
            # Guardar nueva memoria
            success = self.save_lead_memory(user_id, new_memory)
            
            if success:
                logging.info(f"✅ Memoria reseteada para usuario {user_id}")
                return True
            else:
                logging.error(f"❌ Error saving reset memory for {user_id}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error resetting memory for {user_id}: {e}")
            return False
    
    def clear_all_memories(self) -> bool:
        """
        Limpia todas las memorias de usuarios (para testing).
        
        Returns:
            bool: True si se limpiaron exitosamente, False en caso contrario
        """
        try:
            # Limpiar cache
            self.leads_cache.clear()
            
            # Eliminar todos los archivos de memoria
            if os.path.exists(self.memory_dir):
                for filename in os.listdir(self.memory_dir):
                    if filename.startswith("memory_") and filename.endswith(".json"):
                        filepath = os.path.join(self.memory_dir, filename)
                        os.remove(filepath)
            
            logging.info(f"✅ Todas las memorias limpiadas")
            return True
        except Exception as e:
            logging.error(f"❌ Error clearing all memories: {e}")
            return False 