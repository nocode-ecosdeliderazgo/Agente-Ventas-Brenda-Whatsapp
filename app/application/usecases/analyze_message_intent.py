"""
Caso de uso para análisis de intención de mensajes.
Integra OpenAI con el sistema de memoria para análisis inteligente.
"""
import logging
import re
from typing import Dict, Any, Optional

from app.infrastructure.openai.client import OpenAIClient
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.domain.entities.message import IncomingMessage

logger = logging.getLogger(__name__)

# Constante para regex de afirmaciones cortas (expandido)
AFFIRMATIVE_SHORT_REGEX = r"^\s*(s[ií]|sip|ok|okay|claro|vale|hecho|👍|✅)\s*$"

def debug_print(message: str, function_name: str = "", file_name: str = "analyze_message_intent.py"):
    """Print de debug visual para consola"""
    print(f"🧠 [{file_name}::{function_name}] {message}")


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
    
    def _bot_already_sent_bank_data(self, user_memory) -> bool:
        """
        Verifica si el bot ya envió datos bancarios revisando el historial de mensajes.
        
        Args:
            user_memory: Memoria del usuario
            
        Returns:
            True si se detecta que ya se enviaron datos bancarios, False si no
        """
        try:
            if not user_memory or not user_memory.message_history:
                return False
            
            # Revisar los últimos mensajes del historial (expandido a 5 mensajes)
            for message in reversed(user_memory.message_history[-5:]):  # Últimos 5 mensajes
                # Verificar si hay acción de purchase_bonus_sent
                if message.get('action') == 'purchase_bonus_sent':
                    return True
                
                # Verificar si la descripción contiene palabras clave de datos bancarios
                description = message.get('description', '')
                bank_keywords = ['Cuenta CLABE', 'datos bancarios', 'bono workbook enviados', 'banking_data_sent', 'BBVA', 'transferencia']
                if any(keyword in description for keyword in bank_keywords):
                    return True
                
                # Verificar si el contenido del mensaje contiene datos bancarios
                content = message.get('content', '')
                if any(keyword in content for keyword in bank_keywords):
                    return True
                
                # Verificar si hay banking_data_sent en el mensaje
                if message.get('banking_data_sent'):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando datos bancarios enviados: {e}")
            return False
    
    def _check_fast_payment_confirmation(
        self,
        message: str,
        user_memory
    ) -> Optional[Dict[str, Any]]:
        """
        Verifica si el mensaje cumple las condiciones para detección rápida de PAYMENT_CONFIRMATION.
        
        Args:
            message: Mensaje del usuario
            user_memory: Memoria del usuario
            
        Returns:
            Dict con análisis de intención si cumple condiciones, None si no
        """
        try:
            # Verificar si el mensaje anterior contenía datos bancarios (flag directo O fallback)
            purchase_bonus_sent = hasattr(user_memory, 'purchase_bonus_sent') and user_memory.purchase_bonus_sent
            bank_data_sent = self._bot_already_sent_bank_data(user_memory)
            
            # Si no hay flag directo pero sí hay datos bancarios en historial, log WARNING
            if not purchase_bonus_sent and bank_data_sent:
                self.logger.warning(f"⚠️ FALLBACK ACTIVADO: purchase_bonus_sent=False pero se encontró CLABE en historial para usuario")
            
            if not (purchase_bonus_sent or bank_data_sent):
                return None
            
            # Verificar longitud del mensaje (<= 5 palabras)
            word_count = len(message.strip().split())
            if word_count > 5:
                return None
            
            # Verificar si coincide con regex de afirmación corta
            if not re.match(AFFIRMATIVE_SHORT_REGEX, message.strip(), re.IGNORECASE):
                return None
            
            debug_print(f"⚡ DETECCIÓN RÁPIDA PAYMENT_CONFIRMATION - Mensaje: '{message}'", "_check_fast_payment_confirmation", "analyze_message_intent.py")
            debug_print(f"🔍 Condiciones: purchase_bonus_sent={purchase_bonus_sent}, bank_data_sent={bank_data_sent}", "_check_fast_payment_confirmation", "analyze_message_intent.py")
            
            return {
                'category': 'PAYMENT_CONFIRMATION',
                'confidence': 0.9,
                'detection_method': 'fast_rule',
                'message_length': word_count,
                'matched_pattern': message.strip(),
                'purchase_bonus_sent': purchase_bonus_sent,
                'bank_data_sent': bank_data_sent
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error en detección rápida PAYMENT_CONFIRMATION: {e}")
            return None
    
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
            debug_print(f"🔍 INICIANDO ANÁLISIS DE INTENCIÓN\n👤 Usuario: {user_id}\n💬 Mensaje: '{message.body}'", "execute", "analyze_message_intent.py")
            
            # 1. Obtener memoria del usuario
            debug_print("📚 Obteniendo memoria del usuario...", "execute", "analyze_message_intent.py")
            user_memory = self.memory_use_case.get_user_memory(user_id)
            debug_print(f"✅ Memoria obtenida - Nombre: {user_memory.name}, Interacciones: {user_memory.interaction_count}", "execute", "analyze_message_intent.py")
            
            # 1.1. Verificar detección rápida de PAYMENT_CONFIRMATION
            debug_print("⚡ Verificando detección rápida de PAYMENT_CONFIRMATION...", "execute", "analyze_message_intent.py")
            fast_detection = self._check_fast_payment_confirmation(message.body, user_memory)
            
            if fast_detection:
                debug_print(f"🎯 DETECCIÓN RÁPIDA ACTIVADA: {fast_detection['category']} (confianza: {fast_detection['confidence']})", "execute", "analyze_message_intent.py")
                
                # Retornar resultado de detección rápida sin pasar por OpenAI
                result = {
                    'success': True,
                    'intent_analysis': fast_detection,
                    'extracted_info': {},
                    'generated_response': '',
                    'updated_memory': user_memory,
                    'recommended_actions': ['continue_conversation'],
                    'should_use_ai_response': False
                }
                
                self.logger.info(
                    f"✅ Detección rápida completada para usuario {user_id}. "
                    f"Categoría: {fast_detection.get('category', 'UNKNOWN')}"
                )
                
                return result
            
            debug_print("➡️ No se activó detección rápida, continuando con análisis principal...", "execute", "analyze_message_intent.py")
            
            # 2. Preparar contexto de mensajes recientes
            debug_print("📋 Preparando contexto de mensajes recientes...", "execute", "analyze_message_intent.py")
            recent_messages = self._get_recent_messages_context(user_memory)
            message_count = len(recent_messages) if recent_messages else 0
            debug_print(f"✅ Contexto preparado - {message_count} mensajes recientes", "execute", "analyze_message_intent.py")
            
            # 3. Analizar intención y extraer información usando OpenAI
            debug_print("🤖 ENVIANDO MENSAJE A OPENAI para análisis...", "execute", "analyze_message_intent.py")
            ai_result = await self.openai_client.analyze_and_respond(
                user_message=message.body,
                user_memory=user_memory,
                recent_messages=recent_messages,
                context_info=context_info
            )
            debug_print(f"✅ RESPUESTA DE OPENAI RECIBIDA: {ai_result}", "execute", "analyze_message_intent.py")
            
            # 4. Procesar información extraída y actualizar memoria
            extracted_info = ai_result.get('extracted_info', {})
            debug_print(f"📊 Información extraída: {extracted_info}", "execute", "analyze_message_intent.py")
            
            if extracted_info:
                debug_print("🔄 Actualizando memoria con información extraída...", "execute", "analyze_message_intent.py")
                updated_memory = await self._update_memory_with_extracted_info(
                    user_id, user_memory, extracted_info
                )
                debug_print("✅ Memoria actualizada exitosamente", "execute", "analyze_message_intent.py")
            else:
                debug_print("➡️ No hay información nueva para actualizar", "execute", "analyze_message_intent.py")
                updated_memory = user_memory
            
            # 5. Determinar acciones recomendadas
            intent_analysis = ai_result.get('intent_analysis', {})
            debug_print(f"🎯 Intención detectada: {intent_analysis.get('category', 'N/A')} (confianza: {intent_analysis.get('confidence', 0)})", "execute", "analyze_message_intent.py")
            
            debug_print("🎬 Determinando acciones recomendadas...", "execute", "analyze_message_intent.py")
            recommended_actions = self._determine_recommended_actions(
                intent_analysis,
                updated_memory
            )
            debug_print(f"📋 Acciones recomendadas: {recommended_actions}", "execute", "analyze_message_intent.py")
            
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
            
            # Actualizar rol si se detectó y es válido
            if extracted_info.get('role') and extracted_info['role'] != current_memory.role:
                new_role = extracted_info['role']
                
                # Validar que el rol sea un cargo profesional válido (no saludos o mensajes)
                if self._is_valid_professional_role(new_role):
                    current_memory.role = new_role
                    self.logger.info(f"💼 Rol actualizado: {new_role}")
                else:
                    self.logger.warning(f"⚠️ Rol inválido rechazado: '{new_role}' - manteniendo rol actual: '{current_memory.role}'")
            
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
    
    def _is_valid_professional_role(self, role: str) -> bool:
        """
        Valida si un rol es un cargo profesional válido.
        
        Args:
            role: Rol/cargo a validar
            
        Returns:
            True si es un rol profesional válido, False si no
        """
        if not role or len(role.strip()) < 3:
            return False
            
        role_lower = role.lower().strip()
        
        # Rechazar saludos y palabras comunes que no son roles
        invalid_roles = {
            'hola', 'hello', 'hi', 'buenas', 'buenos dias', 'buenas tardes', 'buenas noches',
            'si', 'no', 'ok', 'perfecto', 'gracias', 'muchas gracias',
            'de que trata', 'temario', '¿de que trata?', 'info', 'información',
            'curso', 'cursos', 'precio', 'costo', 'cuanto cuesta',
            'no mencionado', 'por identificar', 'unknown', 'n/a', 'na'
        }
        
        if role_lower in invalid_roles:
            return False
        
        # Validar que contenga palabras típicas de cargos profesionales
        valid_role_keywords = {
            'director', 'gerente', 'manager', 'ceo', 'cto', 'cfo', 'coo',
            'fundador', 'founder', 'coordinador', 'supervisor', 'jefe',
            'analista', 'especialista', 'consultor', 'asesor', 'ejecutivo',
            'líder', 'lider', 'responsable', 'encargado', 'administrador',
            # Marketing y términos relacionados
            'marketing', 'marketing digital', 'publicidad', 'comunicación', 'branding',
            'campañas', 'content', 'social media', 'sem', 'seo', 'growth marketing',
            
            # Ventas y términos relacionados
            'ventas', 'sales', 'comercial', 'compras', 'procurement', 'adquisiciones',
            'business development', 'account manager', 'negociación', 'b2b', 'b2c',
            
            # Operaciones y términos relacionados
            'operaciones', 'operations', 'producción', 'manufactura', 'logística',
            'supply chain', 'procesos', 'calidad', 'lean', 'six sigma', 'industrial',
            
            # Recursos Humanos y términos relacionados
            'recursos humanos', 'rh', 'hr', 'human resources', 'people operations',
            'reclutamiento', 'talent', 'capacitación', 'training', 'nómina', 'payroll',
            
            # Innovación y tecnología
            'innovación', 'innovation', 'transformación digital', 'digital transformation',
            'tecnología', 'it', 'sistemas', 'digital', 'tech', 'startup', 'cto', 'desarrollo',
            
            # Análisis de datos y términos relacionados
            'análisis de datos', 'data analysis', 'analytics', 'bi', 'business intelligence',
            'data science', 'reporting', 'insights', 'métricas', 'kpi', 'dashboard'
        }
        
        # Verificar si contiene al menos una palabra clave de rol profesional
        has_professional_keyword = any(keyword in role_lower for keyword in valid_role_keywords)
        
        return has_professional_keyword