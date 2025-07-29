"""
Caso de uso para generar respuestas inteligentes.
Combina análisis de intención, plantillas de mensajes y respuestas de IA.
"""
import logging
from typing import Dict, Any, Optional

from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
# from app.application.usecases.bonus_activation_use_case import BonusActivationUseCase  # Comentado temporalmente
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.infrastructure.openai.client import OpenAIClient
from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from prompts.agent_prompts import WhatsAppMessageTemplates, get_response_generation_prompt

logger = logging.getLogger(__name__)

def debug_print(message: str, function_name: str = "", file_name: str = "generate_intelligent_response.py"):
    """Print de debug visual para consola"""
    print(f"💬 [{file_name}::{function_name}] {message}")


class GenerateIntelligentResponseUseCase:
    """
    Caso de uso para generar respuestas inteligentes basadas en intención.
    
    Responsabilidades:
    - Analizar intención del mensaje
    - Seleccionar tipo de respuesta (IA vs template)
    - Generar respuesta personalizada
    - Manejar acciones especiales (recursos, contacto, etc.)
    """
    
    def __init__(
        self,
        intent_analyzer: AnalyzeMessageIntentUseCase,
        twilio_client: TwilioWhatsAppClient,
        openai_client: OpenAIClient,
        course_query_use_case: Optional[QueryCourseInformationUseCase] = None
    ):
        """
        Inicializa el caso de uso.
        
        Args:
            intent_analyzer: Analizador de intención de mensajes
            twilio_client: Cliente Twilio para envío de mensajes
            openai_client: Cliente OpenAI para validación
            course_query_use_case: Caso de uso para consultar información de cursos
        """
        self.intent_analyzer = intent_analyzer
        self.twilio_client = twilio_client
        self.openai_client = openai_client
        self.course_query_use_case = course_query_use_case
        self.course_system_available = course_query_use_case is not None
        self.logger = logging.getLogger(__name__)
    
    async def execute(
        self,
        user_id: str,
        incoming_message: IncomingMessage,
        context_info: str = ""
    ) -> Dict[str, Any]:
        """
        Ejecuta la generación de respuesta inteligente completa.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje entrante a procesar
            context_info: Información adicional de contexto
            
        Returns:
            Dict con resultado del procesamiento y respuesta enviada
        """
        try:
            debug_print(f"💬 GENERANDO RESPUESTA INTELIGENTE\n👤 Usuario: {user_id}\n📨 Mensaje: '{incoming_message.body}'", "execute", "generate_intelligent_response.py")
            
            # 1. Analizar intención del mensaje
            debug_print("🧠 Ejecutando análisis de intención...", "execute", "generate_intelligent_response.py")
            analysis_result = await self.intent_analyzer.execute(
                user_id, incoming_message, context_info
            )
            
            if not analysis_result['success']:
                debug_print(f"❌ FALLO ANÁLISIS DE INTENCIÓN: {analysis_result.get('error')}", "execute", "generate_intelligent_response.py")
                response_text = WhatsAppMessageTemplates.business_error_fallback()
                debug_print(f"🔄 Usando respuesta de FALLBACK: {response_text}", "execute", "generate_intelligent_response.py")
            else:
                debug_print(f"✅ Análisis completado - Intención: {analysis_result.get('intent_analysis', {}).get('category', 'N/A')}", "execute", "generate_intelligent_response.py")
                
                # 2. Generar respuesta basada en análisis
                debug_print("📝 Generando respuesta contextual...", "execute", "generate_intelligent_response.py")
                response_text = await self._generate_contextual_response(
                    analysis_result, incoming_message, user_id
                )
                debug_print(f"✅ Respuesta generada: {response_text[:100]}{'...' if len(response_text) > 100 else ''}", "execute", "generate_intelligent_response.py")
            
            # 3. Enviar respuesta principal
            debug_print(f"📤 Enviando respuesta a WhatsApp: {incoming_message.from_number}", "execute", "generate_intelligent_response.py")
            send_result = await self._send_response(
                incoming_message.from_number, response_text
            )
            
            if send_result['success']:
                debug_print(f"✅ MENSAJE ENVIADO EXITOSAMENTE!\n🔗 SID: {send_result.get('message_sid', 'N/A')}", "execute", "generate_intelligent_response.py")
            else:
                debug_print(f"❌ ERROR ENVIANDO MENSAJE: {send_result.get('error', 'Error desconocido')}", "execute", "generate_intelligent_response.py")
            
            # 4. Ejecutar acciones adicionales si es necesario
            recommended_actions = analysis_result.get('recommended_actions', [])
            debug_print(f"🎬 Ejecutando acciones adicionales: {recommended_actions}", "execute", "generate_intelligent_response.py")
            additional_actions = await self._execute_additional_actions(
                recommended_actions,
                user_id,
                incoming_message.from_number,
                analysis_result.get('updated_memory')
            )
            
            result = {
                'success': send_result['success'],
                'intent_analysis': analysis_result.get('intent_analysis', {}),
                'response_text': response_text,
                'response_sent': send_result['success'],
                'response_sid': send_result.get('message_sid'),
                'additional_actions': additional_actions,
                'user_memory_updated': analysis_result['success'],
                'extracted_info': analysis_result.get('extracted_info', {})
            }
            
            if result['success']:
                self.logger.info(f"✅ Respuesta inteligente enviada a {user_id}")
            else:
                self.logger.error(f"❌ Error enviando respuesta: {send_result.get('error')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"💥 Error generando respuesta inteligente: {e}")
            
            # Enviar respuesta de fallback
            fallback_response = WhatsAppMessageTemplates.business_error_fallback()
            fallback_result = await self._send_response(
                incoming_message.from_number, fallback_response
            )
            
            return {
                'success': fallback_result['success'],
                'error': str(e),
                'response_text': fallback_response,
                'response_sent': fallback_result['success'],
                'response_sid': fallback_result.get('message_sid'),
                'additional_actions': [],
                'user_memory_updated': False,
                'extracted_info': {}
            }
    
    async def _generate_contextual_response(
        self,
        analysis_result: Dict[str, Any],
        incoming_message: IncomingMessage,
        user_id: str
    ) -> str:
        """
        Genera respuesta contextual con activación inteligente de bonos.
        """
        try:
            intent_analysis = analysis_result.get('intent_analysis', {})
            category = intent_analysis.get('category', 'general')
            user_memory = analysis_result.get('updated_memory')  # Cambiar de 'user_memory' a 'updated_memory'
            
            debug_print(f"🎯 Generando respuesta para categoría: {category}", "_generate_contextual_response")
            
            # 1. Activar sistema de bonos inteligente
            bonus_activation_result = await self._activate_intelligent_bonuses(
                category, user_memory, incoming_message, user_id
            )
            
            # 2. Generar respuesta con bonos contextuales
            response_text = await self._generate_response_with_bonuses(
                category, user_memory, incoming_message, user_id, bonus_activation_result
            )
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"❌ Error en generación contextual: {e}")
            return WhatsAppMessageTemplates.business_error_fallback()

    async def _activate_intelligent_bonuses(
        self,
        category: str,
        user_memory,
        incoming_message: IncomingMessage,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Activa sistema de bonos inteligente basado en contexto del usuario.
        """
        try:
            # Inicializar caso de uso de bonos si no existe
            # if not hasattr(self, 'bonus_activation_use_case'):
            #     self.bonus_activation_use_case = BonusActivationUseCase()
            
            debug_print(f"🎁 Activando bonos para categoría: {category}", "_activate_intelligent_bonuses")
            
            # Obtener información del usuario
            user_name = user_memory.name if user_memory else "Usuario"
            user_role = user_memory.role if user_memory else "Profesional"
            message_text = incoming_message.body.lower()
            
            # Determinar contexto de conversación
            conversation_context = self._determine_conversation_context(category, message_text)
            urgency_level = self._determine_urgency_level(category, user_memory)
            
            # Obtener bonos contextuales desde la base de datos
            contextual_bonuses = []
            
            if self.course_query_use_case:
                try:
                    # Buscar bonos disponibles para esta categoría
                    available_bonuses = await self.course_query_use_case.get_available_options()
                    bonus_options = available_bonuses.get('bonuses', [])
                    
                    # Filtrar bonos relevantes para la categoría
                    relevant_bonuses = []
                    for bonus in bonus_options[:2]:  # Máximo 2 bonos
                        if isinstance(bonus, dict):
                            relevant_bonuses.append({
                                "name": bonus.get('name', 'Bono disponible'),
                                "description": bonus.get('description', 'Descripción del bono'),
                                "priority_reason": bonus.get('priority_reason', 'Ideal para tu perfil'),
                                "sales_angle": bonus.get('sales_angle', 'Valor agregado')
                            })
                    
                    contextual_bonuses = relevant_bonuses
                    
                except Exception as e:
                    self.logger.error(f"Error obteniendo bonos de la base de datos: {e}")
                    # Fallback a bonos básicos si no hay BD
                    contextual_bonuses = [
                        {
                            "name": "Recursos Adicionales",
                            "description": "Material complementario incluido",
                            "priority_reason": "Ideal para tu perfil",
                            "sales_angle": "Valor agregado"
                        }
                    ]
            else:
                # Fallback si no hay sistema de cursos
                contextual_bonuses = [
                    {
                        "name": "Recursos Adicionales",
                        "description": "Material complementario incluido",
                        "priority_reason": "Ideal para tu perfil",
                        "sales_angle": "Valor agregado"
                    }
                ]
            
            bonus_result = {
                'should_activate': True,
                'contextual_bonuses': contextual_bonuses
            }
            
            debug_print(f"✅ Bonos activados: {len(bonus_result.get('contextual_bonuses', []))} bonos priorizados", "_activate_intelligent_bonuses")
            
            return {
                'should_activate_bonuses': bonus_result.get('should_activate', False),
                'conversation_context': conversation_context,
                'urgency_level': urgency_level,
                'contextual_bonuses': bonus_result.get('contextual_bonuses', []),
                'bonus_activation_info': bonus_result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error activando bonos: {e}")
            return {
                'should_activate_bonuses': False,
                'conversation_context': 'general',
                'urgency_level': 'low',
                'contextual_bonuses': [],
                'bonus_activation_info': {}
            }

    def _determine_conversation_context(self, category: str, message_text: str) -> str:
        """
        Determina el contexto de conversación para activación de bonos.
        """
        if any(word in message_text for word in ['precio', 'costo', 'caro', 'inversión']):
            return 'price_objection'
        elif any(word in message_text for word in ['valor', 'beneficio', 'roi', 'resultado']):
            return 'value_objection'
        elif any(word in message_text for word in ['comprar', 'adquirir', 'inscribir', 'empezar']):
            return 'buying_signals'
        elif any(word in message_text for word in ['difícil', 'complejo', 'técnico', 'miedo']):
            return 'technical_fear'
        elif any(word in message_text for word in ['crecer', 'desarrollar', 'progresar', 'carrera']):
            return 'career_growth'
        else:
            return 'general'

    def _determine_urgency_level(self, category: str, user_memory) -> str:
        """
        Determina el nivel de urgencia para activación de bonos.
        """
        if category in ['buying_signals', 'price_objection', 'value_objection']:
            return 'high'
        elif category in ['automation_needs', 'career_growth']:
            return 'medium'
        else:
            return 'low'

    async def _generate_response_with_bonuses(
        self,
        category: str,
        user_memory,
        incoming_message: IncomingMessage,
        user_id: str,
        bonus_activation_result: Dict[str, Any]
    ) -> str:
        """
        Genera respuesta integrando bonos contextuales.
        """
        try:
            # Por ahora, usar template básico con información de bonos
            user_name = user_memory.name if user_memory else "Usuario"
            user_role = user_memory.role if user_memory else "Profesional"
            
            # Generar respuesta básica
            base_response = await self._get_template_response(category, user_memory, incoming_message)
            
            # Solo agregar bonos para categorías específicas (no para respuestas generales)
            categories_with_bonuses = ['BUYING_SIGNALS', 'EXPLORATION', 'AUTOMATION_NEED', 'OBJECTION_PRICE']
            if (category in categories_with_bonuses and 
                bonus_activation_result.get('should_activate_bonuses', False)):
                bonus_info = self._format_bonus_information(bonus_activation_result)
                if bonus_info:
                    base_response += f"\n\n{bonus_info}"
            
            return base_response
                
        except Exception as e:
            self.logger.error(f"❌ Error generando respuesta con bonos: {e}")
            return await self._get_template_response(category, user_memory, incoming_message)

    def _format_bonus_information(self, bonus_activation_result: Dict[str, Any]) -> str:
        """
        Formatea información de bonos para incluir en la respuesta.
        """
        try:
            contextual_bonuses = bonus_activation_result.get('contextual_bonuses', [])
            if not contextual_bonuses:
                return ""
            
            bonus_text = "\n🎁 **BONOS INCLUIDOS:**\n"
            for i, bonus in enumerate(contextual_bonuses[:3], 1):
                bonus_name = bonus.get('name', 'Bono disponible')
                bonus_description = bonus.get('description', '')
                if bonus_description:
                    bonus_text += f"• {bonus_name}: {bonus_description}\n"
                else:
                    bonus_text += f"• {bonus_name}\n"
            
            # Calcular valor total dinámicamente
            total_value = len(contextual_bonuses) * 500  # Valor estimado por bono
            bonus_text += f"\n💡 **Valor total:** Más de ${total_value} USD en bonos adicionales incluidos GRATIS."
            return bonus_text
            
        except Exception as e:
            self.logger.error(f"❌ Error formateando información de bonos: {e}")
            return ""
    
    async def _get_template_response(
        self,
        category: str,
        user_memory,
        incoming_message: IncomingMessage
    ) -> str:
        """
        Obtiene respuesta basada en templates según categoría.
        
        Args:
            category: Categoría de intención detectada
            user_memory: Memoria del usuario
            incoming_message: Mensaje entrante
            
        Returns:
            Respuesta basada en template
        """
        user_name = user_memory.name if user_memory and user_memory.name else ""
        user_role = user_memory.role if user_memory and user_memory.role else ""
        
        # Mapeo de categorías a templates
        template_map = {
            'FREE_RESOURCES': lambda: WhatsAppMessageTemplates.business_resources_offer(user_name, user_role),
            'CONTACT_REQUEST': lambda: WhatsAppMessageTemplates.executive_advisor_transition(user_name, user_role),
            'OBJECTION_PRICE': lambda: WhatsAppMessageTemplates.business_price_objection_response(role=user_role),
            'AUTOMATION_NEED': lambda: self._get_automation_response(user_name, user_role),
            'BUYING_SIGNALS': lambda: self._get_buying_signals_response(user_name),
            'PROFESSION_CHANGE': lambda: self._get_profession_change_response(user_name),
            'OBJECTION_TIME': lambda: self._get_time_objection_response(user_name),
            'OBJECTION_VALUE': lambda: self._get_value_objection_response(user_name),
            'OBJECTION_TRUST': lambda: self._get_trust_objection_response(user_name),
            'GENERAL_QUESTION': lambda: self._get_general_response(user_name, user_role)
        }
        
        # Manejar casos especiales según estado del usuario
        if not user_name and category != 'CONTACT_REQUEST':
            # Si no tenemos nombre, pedirlo primero
            if user_memory and user_memory.interaction_count == 1:
                return WhatsAppMessageTemplates.welcome_new_business_user()
            else:
                return WhatsAppMessageTemplates.executive_name_request()
        
        if user_name and not user_role and category not in ['CONTACT_REQUEST', 'FREE_RESOURCES']:
            # Si tenemos nombre pero no profesión
            return WhatsAppMessageTemplates.business_role_inquiry(user_name)
        
        # Usar template correspondiente o respuesta general
        if category == 'EXPLORATION':
            return await self._get_exploration_response(user_name, user_role)
        
        # Para categorías relacionadas con cursos, usar información de la base de datos
        course_related_categories = ['TEAM_TRAINING', 'CONTACT_ADVISOR_EXECUTIVE', 'BUYING_SIGNALS']
        if category in course_related_categories:
            return await self._generate_course_enhanced_response(
                category, user_name, [], incoming_message.body
            )
        
        template_func = template_map.get(category, template_map['GENERAL_QUESTION'])
        return template_func()
    
    async def _get_exploration_response(self, user_name: str, user_role: str) -> str:
        """Respuesta para usuarios explorando opciones usando información de la BD."""
        name_part = f"{user_name}, " if user_name else ""
        role_context = f"Como {user_role}, " if user_role else ""
        
        try:
            if self.course_query_use_case:
                # Obtener información de cursos disponibles
                catalog_summary = await self.course_query_use_case.get_course_catalog_summary()
                total_courses = catalog_summary.get('total_courses', 0) if catalog_summary else 0
                
                return f"""¡Excelente que estés explorando{', ' + name_part if name_part else ''}! 🎯

{role_context}estoy segura de que la IA puede transformar completamente tu forma de trabajar.

**📚 Te puedo mostrar:**
• Temario completo de nuestros {total_courses} cursos
• Recursos gratuitos para empezar hoy
• Casos de éxito de personas como tú

¿Qué te gustaría ver primero?"""
            else:
                return f"""¡Excelente que estés explorando{', ' + name_part if name_part else ''}! 🎯

{role_context}estoy segura de que la IA puede transformar completamente tu forma de trabajar.

**📚 Te puedo mostrar:**
• Temario completo de nuestros cursos
• Recursos gratuitos para empezar hoy
• Casos de éxito de personas como tú

¿Qué te gustaría ver primero?"""
                
        except Exception as e:
            self.logger.error(f"Error obteniendo información de exploración: {e}")
            return f"""¡Excelente que estés explorando{', ' + name_part if name_part else ''}! 🎯

{role_context}estoy segura de que la IA puede transformar completamente tu forma de trabajar.

**📚 Te puedo mostrar:**
• Temario completo de nuestros cursos
• Recursos gratuitos para empezar hoy
• Casos de éxito de personas como tú

¿Qué te gustaría ver primero?"""
    
    def _get_automation_response(self, user_name: str, user_role: str) -> str:
        """Respuesta para necesidades específicas de automatización."""
        name_part = f"{user_name}, " if user_name else ""
        
        return f"""¡Perfecto{', ' + name_part if name_part else ''}! 🤖

La automatización es exactamente donde la IA más impacto tiene.

**💡 En nuestro curso aprenderás a automatizar:**
• Reportes y análisis de datos
• Creación de contenido
• Procesos repetitivos
• Comunicación con clientes

¿Te gustaría que te muestre ejemplos específicos para tu área?"""
    
    def _get_buying_signals_response(self, user_name: str) -> str:
        """Respuesta para señales de compra."""
        name_part = f"{user_name}, " if user_name else ""
        
        return f"""Me da mucho gusto tu interés{', ' + name_part if name_part else ''}! 🚀

**🎯 Para facilitar tu decisión:**
• Puedo mostrarte el temario completo
• Conectarte con un asesor especializado
• Explicarte nuestras opciones de pago

¿Qué prefieres hacer primero?"""
    
    def _get_profession_change_response(self, user_name: str) -> str:
        """Respuesta para cambio profesional."""
        name_part = f"{user_name}, " if user_name else ""
        
        return f"""¡Qué emocionante{', ' + name_part if name_part else ''}! 💼

Los cambios profesionales son el momento perfecto para dominar nuevas tecnologías.

**🌟 La IA te va a ayudar a:**
• Diferenciarte en tu nueva área
• Automatizar desde el inicio
• Ser más eficiente que la competencia

¿En qué área te gustaría enfocarte?"""
    
    def _get_time_objection_response(self, user_name: str) -> str:
        """Respuesta para objeciones de tiempo."""
        name_part = f"{user_name}, " if user_name else ""
        
        return f"""Entiendo perfectamente tu preocupación por el tiempo{', ' + name_part if name_part else ''}. ⏰

**⚡ Lo bueno del curso:**
• Solo 2-3 horas por semana
• Aplicación inmediata en tu trabajo
• El tiempo que inviertas lo recuperas automatizando

**💡 Dato real:** El 85% de estudiantes reporta ahorro de tiempo desde la primera semana.

¿Te gustaría ver cómo otros han organizado su tiempo de estudio?"""
    
    def _get_value_objection_response(self, user_name: str) -> str:
        """Respuesta para objeciones de valor."""
        name_part = f"{user_name}, " if user_name else ""
        
        return f"""Excelente pregunta{', ' + name_part if name_part else ''}! 📊

**🔍 El valor real está en:**
• Ahorro de tiempo (10-20 horas/semana)
• Mejora en calidad de trabajo
• Nuevas oportunidades profesionales
• Automatización de tareas repetitivas

**✅ Garantía:** Si no ves resultados concretos en 30 días, te devolvemos tu inversión.

¿Te gustaría ver casos específicos de resultados obtenidos?"""
    
    def _get_trust_objection_response(self, user_name: str) -> str:
        """Respuesta para objeciones de confianza."""
        name_part = f"{user_name}, " if user_name else ""
        
        return f"""Comprendo perfectamente{', ' + name_part if name_part else ''}. 🛡️

**🏆 Nuestra transparencia:**
• +1,200 estudiantes satisfechos
• Garantía de 30 días sin preguntas
• Instructor con certificaciones verificables
• Comunidad activa de profesionales

**📋 Puedes verificar:**
• Testimonios reales en LinkedIn
• Casos de estudio documentados
• Referencias de empleadores

¿Te gustaría que te conecte con algunos graduados para que te cuenten su experiencia?"""
    
    def _get_general_response(self, user_name: str, user_role: str) -> str:
        """Respuesta general personalizada."""
        name_part = f"{user_name}, " if user_name else ""
        role_context = f"Como {user_role}, " if user_role else ""
        
        return f"""¡Hola{', ' + name_part if name_part else ''}! 😊

{role_context}estoy aquí para ayudarte a descubrir cómo la IA puede transformar tu trabajo.

**🎯 Puedo ayudarte con:**
• Información sobre nuestros cursos
• Recursos gratuitos para empezar
• Consultas específicas sobre automatización
• Conexión con nuestro equipo de asesores

¿En qué puedo asistirte específicamente?"""
    
    async def _send_response(self, to_number: str, response_text: str) -> Dict[str, Any]:
        """
        Envía respuesta al usuario.
        
        Args:
            to_number: Número de WhatsApp del usuario
            response_text: Texto de respuesta a enviar
            
        Returns:
            Resultado del envío
        """
        try:
            response_message = OutgoingMessage(
                to_number=to_number,
                body=response_text,
                message_type=MessageType.TEXT
            )
            
            return await self.twilio_client.send_message(response_message)
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando respuesta: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_additional_actions(
        self,
        recommended_actions: list,
        user_id: str,
        user_number: str,
        user_memory
    ) -> list:
        """
        Ejecuta acciones adicionales recomendadas.
        
        Args:
            recommended_actions: Lista de acciones recomendadas
            user_id: ID del usuario
            user_number: Número de WhatsApp del usuario
            user_memory: Memoria del usuario
            
        Returns:
            Lista de acciones ejecutadas
        """
        executed_actions = []
        
        try:
            # Por ahora solo loggeamos las acciones recomendadas
            # En el futuro aquí se pueden implementar:
            # - Envío de recursos gratuitos
            # - Activación de herramientas específicas
            # - Inicialización de flujos de contacto
            # - Triggers de seguimiento
            
            for action in recommended_actions:
                self.logger.info(f"📋 Acción recomendada para {user_id}: {action}")
                
                # Ejemplo de acciones que se pueden implementar:
                if action == 'send_free_resources':
                    # TODO: Implementar envío de recursos
                    self.logger.info("📚 Acción: Enviar recursos gratuitos")
                    executed_actions.append('free_resources_noted')
                
                elif action == 'initiate_advisor_contact':
                    # TODO: Implementar flujo de contacto con asesor
                    self.logger.info("👥 Acción: Iniciar contacto con asesor")
                    executed_actions.append('advisor_contact_initiated')
                
                elif action == 'provide_course_overview':
                    # TODO: Implementar envío de overview del curso
                    self.logger.info("📖 Acción: Proveer overview del curso")
                    executed_actions.append('course_overview_noted')
                
                else:
                    executed_actions.append(f'{action}_logged')
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando acciones adicionales: {e}")
        
        return executed_actions
    
    async def _enhance_response_with_course_info(
        self,
        category: str,
        user_memory,
        incoming_message: IncomingMessage,
        user_id: str
    ) -> Optional[str]:
        """
        Mejora la respuesta con información específica de cursos cuando es relevante.
        
        Args:
            category: Categoría de intención detectada
            user_memory: Memoria del usuario
            incoming_message: Mensaje entrante
            user_id: ID del usuario
            
        Returns:
            Respuesta mejorada con información de cursos o None si no aplica
        """
        if not self.course_system_available:
            return None
        
        try:
            message_text = incoming_message.body.lower()
            user_name = user_memory.name if user_memory and user_memory.name else ""
            user_interests = user_memory.interests if user_memory and user_memory.interests else []
            
            # Categorías que se benefician de información de cursos
            course_relevant_categories = [
                'EXPLORATION', 'BUYING_SIGNALS', 'GENERAL_QUESTION', 
                'AUTOMATION_NEED', 'PROFESSION_CHANGE'
            ]
            
            if category not in course_relevant_categories:
                return None
            
            # Detectar si está buscando cursos específicos
            course_keywords = [
                'curso', 'cursos', 'temario', 'programa', 'contenido',
                'qué aprendo', 'que aprendo', 'nivel', 'modalidad'
            ]
            
            searching_courses = any(keyword in message_text for keyword in course_keywords)
            
            if searching_courses or category in ['EXPLORATION', 'BUYING_SIGNALS']:
                return await self._generate_course_enhanced_response(
                    category, user_name, user_interests, message_text
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error mejorando respuesta con información de cursos: {e}")
            return None
    
    async def _generate_course_enhanced_response(
        self,
        category: str,
        user_name: str,
        user_interests: list,
        message_text: str
    ) -> str:
        """
        Genera respuesta mejorada con información específica de cursos.
        
        Args:
            category: Categoría de intención
            user_name: Nombre del usuario
            user_interests: Intereses del usuario
            message_text: Texto del mensaje para búsqueda
            
        Returns:
            Respuesta con información de cursos
        """
        name_part = f"{user_name}, " if user_name else ""
        
        try:
            # Intentar obtener información real de la base de datos
            if self.course_query_use_case:
                # Buscar cursos relevantes basados en el mensaje
                relevant_courses = await self.course_query_use_case.search_courses_by_keyword(
                    message_text, limit=3
                )
                
                if relevant_courses:
                    # Formatear información de cursos para chat
                    course_info = await self.course_query_use_case.format_course_list_for_chat(relevant_courses)
                    return f"""¡Perfecto{', ' + name_part if name_part else ''}! 📚

He encontrado estos cursos que podrían interesarte:

{course_info}

¿Te gustaría que te dé más detalles sobre alguno de estos cursos?"""
                
                # Si no encuentra cursos específicos, buscar recomendados
                recommended_courses = await self.course_query_use_case.get_recommended_courses(
                    user_interests=user_interests, limit=3
                )
                
                if recommended_courses:
                    course_info = await self.course_query_use_case.format_course_list_for_chat(recommended_courses)
                    return f"""¡Excelente{', ' + name_part if name_part else ''}! 🎯

Basándome en tus intereses, te recomiendo estos cursos:

{course_info}

¿Te gustaría conocer más detalles sobre alguno de ellos?"""
            
            # Fallback a respuesta estándar si no hay base de datos
            return await self._get_standard_course_response(category, user_name)
        
        except Exception as e:
            self.logger.error(f"Error generando respuesta con cursos: {e}")
            return await self._get_standard_course_response(category, user_name)
    
    async def _get_standard_course_response(self, category: str, user_name: str) -> str:
        """Respuesta estándar usando información de la base de datos."""
        name_part = f"{user_name}, " if user_name else ""
        
        try:
            if self.course_query_use_case:
                # Obtener catálogo de cursos desde la base de datos
                catalog_summary = await self.course_query_use_case.get_course_catalog_summary()
                
                if catalog_summary:
                    statistics = catalog_summary.get('statistics', {})
                    total_courses = statistics.get('total_courses', 0)
                    available_options = catalog_summary.get('available_options', {})
                    available_modalities = available_options.get('modalities', [])
                    course_categories = available_options.get('levels', [])
                    
                    if category == 'EXPLORATION':
                        return f"""¡Excelente que estés explorando{', ' + name_part if name_part else ''}! 🎯

**📚 Tenemos {total_courses} cursos de IA que te enseñan:**
• Automatización de procesos empresariales
• Análisis inteligente de datos
• Creación de contenido con IA
• Optimización de flujos de trabajo

**💡 Modalidades disponibles:**
{chr(10).join([f"• {modality}" for modality in available_modalities[:3]])}

¿Te gustaría conocer el temario completo de algún curso específico?"""
                    
                    elif category == 'BUYING_SIGNALS':
                        return f"""Me da mucho gusto tu interés{', ' + name_part if name_part else ''}! 🚀

**🎯 Para facilitar tu decisión:**
• Puedo mostrarte el programa completo de cualquier curso
• Conectarte con un asesor especializado
• Explicarte nuestras opciones de pago flexibles
• Compartir testimonios de profesionales exitosos

¿Qué prefieres hacer primero?"""
                    
                    else:
                        return f"""¡Hola{', ' + name_part if name_part else ''}! 😊

**📚 Te ayudo con información sobre:**
• {total_courses} cursos de IA aplicada
• Programas de automatización empresarial
• Capacitación personalizada según tu sector
• Recursos gratuitos para empezar

¿En qué área te gustaría especializarte?"""
            
            # Fallback si no hay base de datos
            return f"""¡Hola{', ' + name_part if name_part else ''}! 😊

**📚 Te ayudo con información sobre nuestros cursos de IA aplicada.**

¿En qué área te gustaría especializarte?"""
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información de cursos: {e}")
            return f"""¡Hola{', ' + name_part if name_part else ''}! 😊

**📚 Te ayudo con información sobre nuestros cursos de IA aplicada.**

¿En qué área te gustaría especializarte?"""