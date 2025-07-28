"""
Caso de uso para gestión de memoria de usuario.
Sigue los principios de Clean Architecture.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.domain.entities.user import User
from app.domain.entities.message import IncomingMessage
from memory.lead_memory import MemoryManager, LeadMemory


class ManageUserMemoryUseCase:
    """
    Caso de uso para gestionar la memoria persistente de usuarios.
    
    Responsabilidades:
    - Obtener y actualizar memoria de usuario
    - Integrar información de mensajes en la memoria
    - Mantener contexto conversacional
    - Actualizar métricas de interacción
    """
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(__name__)
    
    def get_user_memory(self, user_id: str) -> LeadMemory:
        """
        Obtiene la memoria de un usuario específico.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            LeadMemory: Objeto con toda la información del usuario
        """
        try:
            memory = self.memory_manager.get_lead_memory(user_id)
            self.logger.info(f"✅ Memoria obtenida para usuario {user_id}")
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo memoria para {user_id}: {e}")
            raise
    
    def update_user_memory(
        self,
        user_id: str,
        message: IncomingMessage,
        extracted_info: Optional[Dict[str, Any]] = None
    ) -> LeadMemory:
        """
        Actualiza la memoria de usuario con nueva información del mensaje.
        
        Args:
            user_id: Identificador único del usuario
            message: Mensaje entrante con información
            extracted_info: Información extraída del análisis del mensaje
            
        Returns:
            LeadMemory: Memoria actualizada
        """
        try:
            # Obtener memoria actual
            memory = self.get_user_memory(user_id)
            
            # Actualizar información básica
            memory.last_interaction = datetime.now()
            memory.interaction_count += 1
            
            # Agregar mensaje al historial
            if memory.message_history is None:
                memory.message_history = []
            
            message_entry = {
                "timestamp": datetime.now().isoformat(),
                "content": message.body,
                "phone": message.from_number
            }
            memory.message_history.append(message_entry)
            
            # Mantener solo los últimos 20 mensajes para eficiencia
            if len(memory.message_history) > 20:
                memory.message_history = memory.message_history[-20:]
            
            # Procesar información extraída si está disponible
            if extracted_info:
                self._process_extracted_info(memory, extracted_info)
            
            # Guardar memoria actualizada
            success = self.memory_manager.save_lead_memory(user_id, memory)
            if success:
                self.logger.info(f"✅ Memoria actualizada para usuario {user_id}")
                return memory
            else:
                raise Exception("Error guardando memoria")
                
        except Exception as e:
            self.logger.error(f"❌ Error actualizando memoria para {user_id}: {e}")
            raise
    
    def update_user_name(self, user_id: str, name: str) -> LeadMemory:
        """
        Actualiza el nombre del usuario en la memoria.
        
        Args:
            user_id: Identificador único del usuario
            name: Nombre del usuario
            
        Returns:
            LeadMemory: Memoria actualizada
        """
        try:
            memory = self.get_user_memory(user_id)
            memory.name = name.strip()
            memory.updated_at = datetime.now()
            
            self.memory_manager.save_lead_memory(user_id, memory)
            self.logger.info(f"✅ Nombre actualizado para usuario {user_id}: {name}")
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error actualizando nombre para {user_id}: {e}")
            raise
    
    def update_user_stage(self, user_id: str, stage: str) -> LeadMemory:
        """
        Actualiza la etapa del usuario en el proceso de ventas.
        
        Args:
            user_id: Identificador único del usuario
            stage: Nueva etapa (initial, engaged, interested, ready, etc.)
            
        Returns:
            LeadMemory: Memoria actualizada
        """
        try:
            memory = self.get_user_memory(user_id)
            old_stage = memory.stage
            memory.stage = stage
            memory.updated_at = datetime.now()
            
            self.memory_manager.save_lead_memory(user_id, memory)
            self.logger.info(f"✅ Etapa actualizada para usuario {user_id}: {old_stage} → {stage}")
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error actualizando etapa para {user_id}: {e}")
            raise
    
    def add_user_interest(self, user_id: str, interest: str) -> LeadMemory:
        """
        Agrega un nuevo interés a la memoria del usuario.
        
        Args:
            user_id: Identificador único del usuario
            interest: Interés detectado
            
        Returns:
            LeadMemory: Memoria actualizada
        """
        try:
            memory = self.get_user_memory(user_id)
            
            if memory.interests is None:
                memory.interests = []
            
            # Evitar duplicados
            if interest not in memory.interests:
                memory.interests.append(interest)
                memory.updated_at = datetime.now()
                
                self.memory_manager.save_lead_memory(user_id, memory)
                self.logger.info(f"✅ Interés agregado para usuario {user_id}: {interest}")
            
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error agregando interés para {user_id}: {e}")
            raise
    
    def update_lead_score(self, user_id: str, score_delta: int, reason: str = "") -> LeadMemory:
        """
        Actualiza el puntaje de lead del usuario.
        
        Args:
            user_id: Identificador único del usuario
            score_delta: Cambio en el puntaje (positivo o negativo)
            reason: Razón del cambio de puntaje
            
        Returns:
            LeadMemory: Memoria actualizada
        """
        try:
            memory = self.get_user_memory(user_id)
            old_score = memory.lead_score
            memory.lead_score = max(0, min(100, memory.lead_score + score_delta))
            memory.updated_at = datetime.now()
            
            self.memory_manager.save_lead_memory(user_id, memory)
            self.logger.info(
                f"✅ Score actualizado para usuario {user_id}: {old_score} → {memory.lead_score} "
                f"(Δ{score_delta:+d}) - {reason}"
            )
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error actualizando score para {user_id}: {e}")
            raise
    
    def _process_extracted_info(self, memory: LeadMemory, extracted_info: Dict[str, Any]) -> None:
        """
        Procesa información extraída del análisis de mensajes y actualiza la memoria.
        
        Args:
            memory: Objeto de memoria a actualizar
            extracted_info: Información extraída del mensaje
        """
        # Procesar puntos de dolor detectados
        if "pain_points" in extracted_info:
            if memory.pain_points is None:
                memory.pain_points = []
            
            for pain_point in extracted_info["pain_points"]:
                if pain_point not in memory.pain_points:
                    memory.pain_points.append(pain_point)
        
        # Procesar señales de compra detectadas
        if "buying_signals" in extracted_info:
            if memory.buying_signals is None:
                memory.buying_signals = []
            
            for signal in extracted_info["buying_signals"]:
                if signal not in memory.buying_signals:
                    memory.buying_signals.append(signal)
        
        # Actualizar rol si se detectó
        if "role" in extracted_info and extracted_info["role"]:
            memory.role = extracted_info["role"]
        
        # Actualizar nivel de interés si se detectó
        if "interest_level" in extracted_info and extracted_info["interest_level"]:
            memory.interest_level = extracted_info["interest_level"]
        
        # Procesar necesidades de automatización
        if "automation_needs" in extracted_info:
            if memory.automation_needs is None:
                memory.automation_needs = {}
            memory.automation_needs.update(extracted_info["automation_needs"])
    
    def start_privacy_flow(self, user_id: str) -> LeadMemory:
        """
        Inicia el flujo de privacidad para un usuario.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            LeadMemory: Memoria actualizada con flujo de privacidad iniciado
        """
        try:
            memory = self.get_user_memory(user_id)
            memory.stage = "privacy_flow"
            memory.current_flow = "privacy"
            memory.flow_step = 1
            memory.privacy_requested = True
            memory.waiting_for_response = "privacy_acceptance"
            memory.updated_at = datetime.now()
            
            self.memory_manager.save_lead_memory(user_id, memory)
            self.logger.info(f"✅ Flujo de privacidad iniciado para usuario {user_id}")
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error iniciando flujo de privacidad para {user_id}: {e}")
            raise
    
    def accept_privacy(self, user_id: str) -> LeadMemory:
        """
        Marca la privacidad como aceptada y avanza al siguiente flujo.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            LeadMemory: Memoria actualizada
        """
        try:
            memory = self.get_user_memory(user_id)
            memory.privacy_accepted = True
            memory.stage = "course_selection"
            memory.current_flow = "course_selection"
            memory.flow_step = 1
            memory.waiting_for_response = "course_interest"
            memory.updated_at = datetime.now()
            
            self.memory_manager.save_lead_memory(user_id, memory)
            self.logger.info(f"✅ Privacidad aceptada para usuario {user_id}")
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error aceptando privacidad para {user_id}: {e}")
            raise
    
    def start_sales_agent_flow(self, user_id: str) -> LeadMemory:
        """
        Inicia el flujo del agente de ventas inteligente.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            LeadMemory: Memoria actualizada
        """
        try:
            memory = self.get_user_memory(user_id)
            memory.stage = "sales_agent"
            memory.current_flow = "sales_conversation"
            memory.flow_step = 1
            memory.waiting_for_response = ""  # El agente inteligente maneja las respuestas
            memory.updated_at = datetime.now()
            
            self.memory_manager.save_lead_memory(user_id, memory)
            self.logger.info(f"✅ Agente de ventas iniciado para usuario {user_id}")
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error iniciando agente de ventas para {user_id}: {e}")
            raise
    
    def update_user_role(self, user_id: str, role: str) -> LeadMemory:
        """
        Actualiza el rol/profesión del usuario.
        
        Args:
            user_id: Identificador único del usuario
            role: Rol o profesión del usuario
            
        Returns:
            LeadMemory: Memoria actualizada
        """
        try:
            memory = self.get_user_memory(user_id)
            memory.role = role.strip()
            memory.updated_at = datetime.now()
            
            self.memory_manager.save_lead_memory(user_id, memory)
            self.logger.info(f"✅ Rol actualizado para usuario {user_id}: {role}")
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error actualizando rol para {user_id}: {e}")
            raise
    
    def set_waiting_for_response(self, user_id: str, response_type: str) -> LeadMemory:
        """
        Establece qué tipo de respuesta se está esperando del usuario.
        
        Args:
            user_id: Identificador único del usuario
            response_type: Tipo de respuesta esperada (name, privacy_acceptance, course_choice, etc.)
            
        Returns:
            LeadMemory: Memoria actualizada
        """
        try:
            memory = self.get_user_memory(user_id)
            memory.waiting_for_response = response_type
            memory.updated_at = datetime.now()
            
            self.memory_manager.save_lead_memory(user_id, memory)
            self.logger.info(f"✅ Esperando respuesta '{response_type}' de usuario {user_id}")
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error estableciendo tipo de respuesta para {user_id}: {e}")
            raise
    
    def advance_flow_step(self, user_id: str) -> LeadMemory:
        """
        Avanza al siguiente paso del flujo actual.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            LeadMemory: Memoria actualizada
        """
        try:
            memory = self.get_user_memory(user_id)
            memory.flow_step += 1
            memory.updated_at = datetime.now()
            
            self.memory_manager.save_lead_memory(user_id, memory)
            self.logger.info(f"✅ Flujo avanzado para usuario {user_id} - Paso: {memory.flow_step}")
            return memory
        except Exception as e:
            self.logger.error(f"❌ Error avanzando flujo para {user_id}: {e}")
            raise