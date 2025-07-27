"""
Caso de uso para análisis de intención de mensajes.
Integra OpenAI con el sistema de memoria para análisis inteligente.
"""
import logging
from typing import Dict, Any, Optional

from app.infrastructure.openai.client import OpenAIClient
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.domain.entities.message import IncomingMessage

logger = logging.getLogger(__name__)


class AnalyzeMessageIntentUseCase:
    """
    Caso de uso para analizar la intención de mensajes entrantes.
    
    Responsabilidades:
    - Análisis de intención usando OpenAI
    - Extracción de información del usuario
    - Actualización de memoria con información extraída
    - Clasificación de mensajes para activación de herramientas
    """
    
    def __init__(
        self, 
        openai_client: OpenAIClient,
        memory_use_case: ManageUserMemoryUseCase
    ):
        """
        Inicializa el caso de uso.
        
        Args:
            openai_client: Cliente OpenAI para análisis
            memory_use_case: Caso de uso de memoria de usuario
        """
        self.openai_client = openai_client
        self.memory_use_case = memory_use_case
        self.logger = logging.getLogger(__name__)
    
    async def execute(
        self,
        user_id: str,
        message: IncomingMessage,
        context_info: str = ""
    ) -> Dict[str, Any]:
        """
        Ejecuta el análisis completo de intención del mensaje.
        
        Args:
            user_id: ID del usuario
            message: Mensaje entrante a analizar
            context_info: Información adicional de contexto
            
        Returns:
            Dict con análisis completo e información extraída
        """
        try:
            self.logger.info(f"🔍 Iniciando análisis de intención para usuario {user_id}")
            
            # 1. Obtener memoria del usuario
            user_memory = self.memory_use_case.get_user_memory(user_id)
            
            # 2. Preparar contexto de mensajes recientes
            recent_messages = self._get_recent_messages_context(user_memory)
            
            # 3. Analizar intención y extraer información usando OpenAI
            ai_result = await self.openai_client.analyze_and_respond(
                user_message=message.body,
                user_memory=user_memory,
                recent_messages=recent_messages,
                context_info=context_info
            )
            
            # 4. Procesar información extraída y actualizar memoria
            extracted_info = ai_result.get('extracted_info', {})
            if extracted_info:
                updated_memory = await self._update_memory_with_extracted_info(
                    user_id, user_memory, extracted_info
                )
            else:
                updated_memory = user_memory
            
            # 5. Determinar acciones recomendadas
            recommended_actions = self._determine_recommended_actions(
                ai_result.get('intent_analysis', {}),
                updated_memory
            )
            
            result = {
                'success': ai_result.get('success', True),
                'intent_analysis': ai_result.get('intent_analysis', {}),
                'extracted_info': extracted_info,
                'generated_response': ai_result.get('response', ''),
                'updated_memory': updated_memory,
                'recommended_actions': recommended_actions,
                'should_use_ai_response': self._should_use_ai_response(
                    ai_result.get('intent_analysis', {})
                )
            }
            
            self.logger.info(
                f"✅ Análisis completado para usuario {user_id}. "
                f"Categoría: {result['intent_analysis'].get('category', 'UNKNOWN')}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"💥 Error en análisis de intención para usuario {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'intent_analysis': {'category': 'GENERAL_QUESTION'},
                'extracted_info': {},
                'generated_response': 'Disculpa, tuve un problema procesando tu mensaje. ¿Podrías repetirlo?',
                'updated_memory': self.memory_use_case.get_user_memory(user_id),
                'recommended_actions': ['continue_conversation'],
                'should_use_ai_response': False
            }
    
    def _get_recent_messages_context(self, user_memory) -> Optional[list]:
        """
        Extrae contexto de mensajes recientes de la memoria.
        
        Args:
            user_memory: Memoria del usuario
            
        Returns:
            Lista de mensajes recientes para contexto
        """
        if not user_memory or not user_memory.message_history:
            return None
        
        # Obtener últimos 3 mensajes para contexto
        recent = user_memory.message_history[-3:] if len(user_memory.message_history) >= 3 else user_memory.message_history
        return [msg.get('content', '') for msg in recent]
    
    async def _update_memory_with_extracted_info(
        self,
        user_id: str,
        current_memory,
        extracted_info: Dict[str, Any]
    ):
        """
        Actualiza la memoria del usuario con información extraída.
        
        Args:
            user_id: ID del usuario
            current_memory: Memoria actual del usuario
            extracted_info: Información extraída del mensaje
            
        Returns:
            Memoria actualizada
        """
        try:
            # Actualizar nombre si se detectó
            if extracted_info.get('name') and not current_memory.name:
                current_memory = self.memory_use_case.update_user_name(
                    user_id, extracted_info['name']
                )
                self.logger.info(f"👤 Nombre actualizado: {extracted_info['name']}")
            
            # Actualizar rol si se detectó
            if extracted_info.get('role') and extracted_info['role'] != current_memory.role:
                current_memory.role = extracted_info['role']
                self.logger.info(f"💼 Rol actualizado: {extracted_info['role']}")
            
            # Agregar nuevos intereses
            if extracted_info.get('interests'):
                for interest in extracted_info['interests']:
                    if interest and interest not in (current_memory.interests or []):
                        current_memory = self.memory_use_case.add_user_interest(user_id, interest)
            
            # Agregar nuevos pain points
            if extracted_info.get('pain_points'):
                if not current_memory.pain_points:
                    current_memory.pain_points = []
                for pain_point in extracted_info['pain_points']:
                    if pain_point and pain_point not in current_memory.pain_points:
                        current_memory.pain_points.append(pain_point)
            
            # Actualizar necesidades de automatización
            if extracted_info.get('automation_needs'):
                if not current_memory.automation_needs:
                    current_memory.automation_needs = {}
                current_memory.automation_needs.update(extracted_info['automation_needs'])
            
            # Actualizar nivel de interés
            if extracted_info.get('interest_level'):
                current_memory.interest_level = extracted_info['interest_level']
            
            # Guardar cambios
            self.memory_use_case.memory_manager.save_lead_memory(user_id, current_memory)
            
            return current_memory
            
        except Exception as e:
            self.logger.error(f"❌ Error actualizando memoria con info extraída: {e}")
            return current_memory
    
    def _determine_recommended_actions(
        self,
        intent_analysis: Dict[str, Any],
        user_memory
    ) -> list:
        """
        Determina acciones recomendadas basadas en intención y memoria.
        
        Args:
            intent_analysis: Resultado del análisis de intención
            user_memory: Memoria del usuario
            
        Returns:
            Lista de acciones recomendadas
        """
        category = intent_analysis.get('category', 'GENERAL_QUESTION')
        recommended_action = intent_analysis.get('recommended_action', 'continue_conversation')
        
        actions = []
        
        # Acciones basadas en categoría de intención
        if category == 'FREE_RESOURCES':
            actions.extend(['send_free_resources', 'offer_course_info'])
        elif category == 'EXPLORATION':
            actions.extend(['provide_course_overview', 'ask_specific_needs'])
        elif category == 'CONTACT_REQUEST':
            actions.extend(['initiate_advisor_contact', 'collect_contact_info'])
        elif category in ['OBJECTION_PRICE', 'OBJECTION_VALUE', 'OBJECTION_TIME', 'OBJECTION_TRUST']:
            actions.extend(['address_objection', 'provide_social_proof'])
        elif category == 'BUYING_SIGNALS':
            actions.extend(['facilitate_next_step', 'offer_demo'])
        elif category == 'AUTOMATION_NEED':
            actions.extend(['show_automation_examples', 'connect_to_course'])
        
        # Acciones basadas en estado del usuario
        if not user_memory.name:
            actions.append('request_name')
        elif not user_memory.role:
            actions.append('ask_profession')
        
        # Acción recomendada por IA
        if recommended_action and recommended_action not in actions:
            actions.append(recommended_action)
        
        # Asegurar que siempre hay al menos una acción
        if not actions:
            actions.append('continue_conversation')
        
        return actions
    
    def _should_use_ai_response(self, intent_analysis: Dict[str, Any]) -> bool:
        """
        Determina si se debe usar la respuesta generada por IA.
        
        Args:
            intent_analysis: Análisis de intención
            
        Returns:
            True si se debe usar la respuesta de IA, False para usar templates
        """
        category = intent_analysis.get('category', 'GENERAL_QUESTION')
        confidence = intent_analysis.get('confidence', 0.5)
        
        # Usar IA para respuestas complejas y con alta confianza
        high_confidence_categories = [
            'EXPLORATION', 'AUTOMATION_NEED', 'PROFESSION_CHANGE', 
            'GENERAL_QUESTION', 'OBJECTION_VALUE', 'OBJECTION_TRUST'
        ]
        
        return category in high_confidence_categories and confidence >= 0.7