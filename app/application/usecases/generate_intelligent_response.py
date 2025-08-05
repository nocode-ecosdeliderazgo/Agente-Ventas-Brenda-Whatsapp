"""
Caso de uso para generar respuestas inteligentes.
Combina análisis de intención, plantillas de mensajes y respuestas de IA con sistema anti-inventos.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.application.usecases.validate_response_use_case import ValidateResponseUseCase
from app.application.usecases.anti_hallucination_use_case import AntiHallucinationUseCase
from app.application.usecases.extract_user_info_use_case import ExtractUserInfoUseCase
from app.application.usecases.personalize_response_use_case import PersonalizeResponseUseCase
from app.application.usecases.dynamic_course_info_provider import DynamicCourseInfoProvider
from app.application.usecases.bonus_activation_use_case import BonusActivationUseCase
from app.application.usecases.purchase_bonus_use_case import PurchaseBonusUseCase
from app.infrastructure.faq.faq_knowledge_provider import FAQKnowledgeProvider
from app.infrastructure.faq.faq_knowledge_provider import FAQKnowledgeProvider
from uuid import UUID
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.database.client import DatabaseClient
from app.infrastructure.database.repositories.course_repository import CourseRepository
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
        db_client: DatabaseClient,
        course_repository: CourseRepository,
        course_query_use_case: Optional[QueryCourseInformationUseCase] = None
    ):
        """
        Inicializa el caso de uso con sistema anti-inventos.
        
        Args:
            intent_analyzer: Analizador de intención de mensajes
            twilio_client: Cliente Twilio para envío de mensajes
            openai_client: Cliente OpenAI para generación y validación
            db_client: Cliente de base de datos
            course_repository: Repositorio de cursos
            course_query_use_case: Caso de uso para consultar información de cursos
        """
        self.intent_analyzer = intent_analyzer
        self.twilio_client = twilio_client
        self.openai_client = openai_client
        self.course_query_use_case = course_query_use_case
        self.course_system_available = course_query_use_case is not None
        
        # Inicializar sistema anti-inventos
        self.validate_response_use_case = ValidateResponseUseCase(db_client, course_repository)
        self.anti_hallucination_use_case = AntiHallucinationUseCase(
            openai_client, course_repository, self.validate_response_use_case
        )
        
        # Guard contra bucles de respuesta y tracking de flujo progresivo
        self._processed_messages = set()  # Prevenir bucles por mensaje similar
        self._content_flow_state = {}  # Tracking del estado de flujo de contenido por usuario
        
        # Inicializar sistema de personalización avanzada (FASE 2)
        self.extract_user_info_use_case = ExtractUserInfoUseCase(openai_client)
        self.personalize_response_use_case = PersonalizeResponseUseCase(
            openai_client, self.extract_user_info_use_case
        )
        
        # Inicializar proveedor dinámico de información de cursos (MEJORA BD)
        self.dynamic_course_provider = DynamicCourseInfoProvider(course_repository)
        
        # Inicializar sistema de bonos por intención de compra (NUEVO)
        self.purchase_bonus_use_case = PurchaseBonusUseCase(
            course_query_use_case, None, twilio_client  # memory_use_case se pasará en execute
        )
        
        # Inicializar proveedor de conocimiento FAQ para respuestas inteligentes (NUEVO)
        self.faq_knowledge_provider = FAQKnowledgeProvider()
        
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
            
            # Guard contra bucles - verificar si ya procesamos este mensaje
            loop_guard_key = f"{user_id}:{incoming_message.body[:50]}"
            if loop_guard_key in self._processed_messages:
                self.logger.warning(f"⚠️ Loop detectado para mensaje: {incoming_message.body[:30]}...")
                return self._create_loop_break_response()
            
            # Marcar mensaje como procesado
            self._processed_messages.add(loop_guard_key)
            
            # Limpiar guard periódicamente para evitar memory leak
            if len(self._processed_messages) > 100:
                oldest_messages = list(self._processed_messages)[:50]
                for msg in oldest_messages:
                    self._processed_messages.discard(msg)
            
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
        Genera respuesta contextual con sistema anti-inventos y activación inteligente de bonos.
        """
        try:
            intent_analysis = analysis_result.get('intent_analysis', {})
            category = intent_analysis.get('category', 'general')
            user_memory = analysis_result.get('updated_memory')
            
            debug_print(f"🎯 Generando respuesta para categoría: {category}", "_generate_contextual_response")
            
            # 🆕 PRIORIDAD MÁXIMA: Verificar si es una FAQ para respuesta inteligente
            user_context = {
                'user_role': getattr(user_memory, 'role', '') if user_memory else '',
                'company_size': getattr(user_memory, 'company_size', '') if user_memory else '',
                'industry': getattr(user_memory, 'industry', '') if user_memory else '',
                'name': getattr(user_memory, 'name', 'Usuario') if user_memory else 'Usuario'
            }
            
            faq_context = await self.faq_knowledge_provider.get_faq_context_for_intelligence(
                incoming_message.body, user_context
            )
            
            if faq_context['is_faq']:
                debug_print(f"❓ FAQ detectada: {faq_context['category']} - Generando respuesta inteligente", "_generate_contextual_response")
                
                # Generar respuesta FAQ inteligente usando OpenAI con contexto
                faq_response = await self._generate_intelligent_faq_response(
                    incoming_message.body, faq_context, user_context, intent_analysis
                )
                
                debug_print("✅ Respuesta FAQ inteligente generada", "_generate_contextual_response")
                return faq_response
            
            # 🎁 PRIORIDAD 2: Verificar intención de compra para activar bonos workbook
            if self.purchase_bonus_use_case.should_activate_purchase_bonus(intent_analysis):
                debug_print("🎁 Intención de compra detectada - Activando bonos workbook", "_generate_contextual_response")
                
                # Configurar memory_use_case temporalmente
                from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
                from memory.lead_memory import MemoryManager
                memory_manager = MemoryManager()
                memory_use_case = ManageUserMemoryUseCase(memory_manager)
                self.purchase_bonus_use_case.memory_use_case = memory_use_case
                
                # Generar mensaje de bono
                purchase_bonus_message = await self.purchase_bonus_use_case.generate_purchase_bonus_message(
                    user_memory, intent_analysis, course_info=None
                )
                
                # Actualizar memoria con intención de compra
                await self.purchase_bonus_use_case.update_user_memory_with_purchase_intent(
                    user_id, intent_analysis
                )
                
                debug_print("✅ Bono de compra activado y mensaje generado", "_generate_contextual_response")
                return purchase_bonus_message
            
            # 🆕 PRIORIDAD ESPECIAL: Consultas específicas (precio, sesiones, duración, etc.)
            specific_inquiry_categories = ['PRICE_INQUIRY', 'SESSION_INQUIRY', 'DURATION_INQUIRY', 'CONTENT_INQUIRY', 'MODALITY_INQUIRY']
            
            if category in specific_inquiry_categories or self._should_use_concise_response(category, incoming_message.body):
                user_name = user_memory.name if user_memory and user_memory.name != "Usuario" else ""
                user_role = user_memory.role if user_memory and user_memory.role != "No disponible" else ""
                
                # Determinar tipo de consulta específica
                if category in specific_inquiry_categories:
                    # Mapear categoría a tipo de consulta
                    category_to_type = {
                        'PRICE_INQUIRY': 'price',
                        'SESSION_INQUIRY': 'sessions', 
                        'DURATION_INQUIRY': 'duration',
                        'CONTENT_INQUIRY': 'content',
                        'MODALITY_INQUIRY': 'modality'
                    }
                    inquiry_type = category_to_type[category]
                else:
                    # Detectar por keywords para otras categorías
                    inquiry_type = self._detect_specific_inquiry_type(incoming_message.body)
                
                if inquiry_type:
                    debug_print(f"🎯 Usando respuesta concisa para consulta específica: {inquiry_type} (categoría: {category})", "_generate_contextual_response")
                    return await self._get_concise_specific_response(inquiry_type, user_name, user_role, user_memory)
            
            # 🆕 MANEJO ESPECIAL: Escalación gradual para mensajes fuera de contexto
            off_topic_categories = ['OFF_TOPIC_CASUAL', 'OFF_TOPIC_PERSONAL', 'OFF_TOPIC_UNRELATED']
            if category in off_topic_categories:
                user_name = user_memory.name if user_memory and user_memory.name != "Usuario" else ""
                
                # Verificar historial de intentos fuera de contexto
                escalation_level = self._determine_off_topic_escalation_level(user_memory)
                
                if escalation_level >= 3:
                    # Usar respuesta predeterminada para intentos repetidos
                    debug_print(f"🚫 Escalación nivel {escalation_level}: usando respuesta predeterminada", "_generate_contextual_response")
                    return self._get_off_topic_repeated_response(user_name)
                elif escalation_level == 2:
                    # Respuesta más firme pero aún con algo de humor
                    debug_print(f"⚠️ Escalación nivel {escalation_level}: respuesta firme con redirección", "_generate_contextual_response")
                    return self._get_off_topic_firm_redirect(user_name)
                else:
                    # Primera vez o pocas veces: humor ligero
                    debug_print(f"😊 Escalación nivel {escalation_level}: respuesta con humor", "_generate_contextual_response")
                    return self._get_off_topic_casual_response(user_name, incoming_message.body, user_memory)
            
            # Fallback para PRICE_INQUIRY que no sea específica
            if category == 'PRICE_INQUIRY':
                user_name = user_memory.name if user_memory and user_memory.name != "Usuario" else ""
                user_role = user_memory.role if user_memory and user_memory.role != "No disponible" else ""
                debug_print("💰 Usando método directo completo para pregunta de precio", "_generate_contextual_response")
                return await self._get_direct_price_response(user_name, user_role, user_memory)
            
            # 1. Verificar si OpenAI ya generó una respuesta de buena calidad
            openai_response = analysis_result.get('generated_response', '')
            if (openai_response and len(openai_response.strip()) > 50 and 
                self._should_use_ai_generation(category, incoming_message.body)):
                debug_print("🎯 Usando respuesta inteligente ya generada por OpenAI", "_generate_contextual_response")
                
                # ⚠️ PROBLEMA: Esta respuesta no tiene información específica del curso
                # TODO: En el futuro, mejorar el análisis de intención para incluir info de curso
                debug_print("⚠️ NOTA: Respuesta OpenAI previa puede no tener nombre específico del curso", "_generate_contextual_response")
                
                # Limpiar la respuesta de OpenAI para evitar saludos duplicados y ofertas de consulta
                cleaned_response = self._clean_openai_response(openai_response, user_memory)
                return cleaned_response
            
            # 2. Obtener información de curso si es relevante
            course_info = None
            if category in ['EXPLORATION', 'BUYING_SIGNALS', 'TEAM_TRAINING']:
                course_info = await self._get_course_info_for_validation(user_memory)
                debug_print(f"📚 Información de curso obtenida: {bool(course_info)}", "_generate_contextual_response")
            
            # 3. Determinar si usar personalización avanzada
            should_use_personalization = self._should_use_advanced_personalization(category, user_memory, incoming_message.body)
            
            if should_use_personalization:
                debug_print("🎯 Usando personalización avanzada (FASE 2)", "_generate_contextual_response")
                personalization_result = await self.personalize_response_use_case.generate_personalized_response(
                    incoming_message.body, user_memory, category
                )
                response_text = personalization_result.personalized_response
                
                # Log información de personalización
                debug_print(f"✅ Personalización aplicada - Persona: {personalization_result.buyer_persona_detected}, Confianza: {personalization_result.personalization_confidence:.2f}", "_generate_contextual_response")
                debug_print(f"📊 Personalizaciones: {', '.join(personalization_result.applied_personalizations)}", "_generate_contextual_response")
                
            elif self._should_use_ai_generation(category, incoming_message.body):
                debug_print("🤖 Usando generación IA con anti-inventos", "_generate_contextual_response")
                
                # Obtener información detallada del curso para OpenAI
                course_detailed_info = await self._get_course_detailed_info()
                debug_print(f"📚 Información de curso para OpenAI: {course_detailed_info.get('name', 'No disponible') if course_detailed_info else 'No disponible'}", "_generate_contextual_response")
                
                safe_response_result = await self.anti_hallucination_use_case.generate_safe_response(
                    incoming_message.body, user_memory, intent_analysis, course_info, course_detailed_info
                )
                response_text = safe_response_result['message']
                
                # Log información de validación
                if safe_response_result.get('anti_hallucination_applied'):
                    validation_info = safe_response_result.get('validation_result', {})
                    debug_print(f"✅ Anti-inventos aplicado - Confianza: {validation_info.get('confidence_score', 0):.2f}", "_generate_contextual_response")
            else:
                debug_print("📝 Usando templates seguros", "_generate_contextual_response")
                # 3. Activar sistema de bonos inteligente
                bonus_activation_result = await self._activate_intelligent_bonuses(
                    category, user_memory, incoming_message, user_id
                )
                
                # 4. Generar respuesta con templates validados
                response_text = await self._generate_response_with_bonuses(
                    category, user_memory, incoming_message, user_id, bonus_activation_result
                )
                
                # 5. Validar respuesta de template si menciona información específica
                if course_info and self._mentions_specific_course_info(response_text):
                    debug_print("🔍 Validando respuesta de template", "_generate_contextual_response")
                    validation_result = await self.validate_response_use_case.validate_response(
                        response_text, course_info, incoming_message.body
                    )
                    
                    if not validation_result.is_valid and validation_result.corrected_response:
                        debug_print("⚠️ Template corregido por validación", "_generate_contextual_response")
                        response_text = validation_result.corrected_response
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"❌ Error en generación contextual: {e}")
            return WhatsAppMessageTemplates.business_error_fallback()
    
    def _clean_openai_response(self, response_text: str, user_memory) -> str:
        """
        Limpia la respuesta de OpenAI para evitar saludos duplicados y ofertas de consulta.
        
        Args:
            response_text: Respuesta original de OpenAI
            user_memory: Memoria del usuario
            
        Returns:
            Respuesta limpia
        """
        try:
            # Obtener el nombre del usuario
            user_name = user_memory.name if user_memory and user_memory.name else ""
            
            # Patrones de saludo a eliminar - Expandido
            greeting_patterns = [
                f"¡Hola, {user_name}!",
                f"Hola {user_name},",
                f"¡Hola {user_name}!",
                f"Hola, {user_name},",
                f"¡Hola {user_name},",
                f"Hola {user_name}!",
                f"¡Hola {user_name}! 😊",
                f"¡Hola, {user_name}! 😊",
                f"Hola {user_name}! 😊",
                f"Hola, {user_name}! 😊",
                "¡Hola!",
                "Hola,",
                "Hola!",
                "¡Hola! 😊",
                "Hola! 😊",
                "¡Hola 😊",
                "Hola 😊"
            ]
            
            # Patrones de oferta de consulta a eliminar
            consultation_patterns = [
                "Si te parece bien, podríamos explorar cómo empezar a implementar estas soluciones en tu empresa.",
                "¿Te gustaría programar una consulta para discutir más sobre esto?",
                "¿Te gustaría programar una consulta para discutir más sobre esto y ver qué pasos podríamos tomar juntos?",
                "Te invito a agendar una consulta para explorar cómo podemos implementar esta tecnología en tu empresa.",
                "¿Te gustaría tener una consulta donde podamos identificar oportunidades específicas para tu equipo?",
                "Te invito a explorar cómo podemos aplicar estas soluciones en tu empresa.",
                "¿Te gustaría programar una consulta?",
                "¿Te gustaría agendar una consulta?",
                "¿Te gustaría tener una consulta?",
                "Te invito a que exploremos juntos cómo podrías empezar a implementar IA en tu estrategia.",
                "¿Te gustaría agendar una consulta para analizar tus necesidades específicas?",
                "¿Te gustaría agendar una consulta para analizar tus necesidades específicas y ver cómo podemos avanzar en esto?",
                "Te invito a explorar juntos cómo podrías empezar a implementar IA en tu estrategia.",
                "¿Te gustaría agendar una consulta para analizar tus necesidades?",
                "¿Te gustaría agendar una consulta para analizar tus necesidades específicas?",
                "¿Te gustaría agendar una consulta para analizar tus necesidades específicas y ver cómo podemos avanzar?",
                "Te invito a que exploremos juntos",
                "¿Te gustaría agendar una consulta",
                "¿Te gustaría programar una consulta",
                "¿Te gustaría tener una consulta",
                "Te invito a agendar",
                "Te invito a programar",
                "Te invito a explorar",
                "¿Te gustaría explorar",
                "¿Te gustaría analizar",
                "¿Te gustaría discutir"
            ]
            
            cleaned_response = response_text
            
            # Eliminar saludos duplicados
            for pattern in greeting_patterns:
                if pattern in cleaned_response:
                    debug_print(f"🧹 Eliminando saludo: {pattern}", "_clean_openai_response")
                    cleaned_response = cleaned_response.replace(pattern, "").strip()
            
            # Eliminar ofertas de consulta
            for pattern in consultation_patterns:
                if pattern in cleaned_response:
                    debug_print(f"🧹 Eliminando oferta de consulta: {pattern}", "_clean_openai_response")
                    cleaned_response = cleaned_response.replace(pattern, "").strip()
            
            # Limpiar espacios extra y saltos de línea
            cleaned_response = "\n".join([line.strip() for line in cleaned_response.split("\n") if line.strip()])
            
            # Mejorar el formato del mensaje
            cleaned_response = self._format_message_beautifully(cleaned_response)
            
            debug_print(f"✅ Respuesta limpia generada ({len(cleaned_response)} caracteres)", "_clean_openai_response")
            return cleaned_response
            
        except Exception as e:
            debug_print(f"❌ Error limpiando respuesta OpenAI: {e}", "_clean_openai_response")
            return response_text
    
    def _format_message_beautifully(self, message_text: str) -> str:
        """
        Formatea el mensaje para que se vea más bonito y legible.
        
        Args:
            message_text: Mensaje original
            
        Returns:
            Mensaje formateado
        """
        try:
            # Dividir el mensaje en oraciones
            sentences = message_text.split('. ')
            
            # Formatear cada oración
            formatted_sentences = []
            for i, sentence in enumerate(sentences):
                sentence = sentence.strip()
                if sentence:
                    # Agregar punto si no lo tiene
                    if not sentence.endswith('.') and not sentence.endswith('!') and not sentence.endswith('?'):
                        sentence += '.'
                    
                    # Agregar espacios entre oraciones
                    if i > 0:
                        formatted_sentences.append(f"\n\n{sentence}")
                    else:
                        formatted_sentences.append(sentence)
            
            # Unir las oraciones
            formatted_message = ''.join(formatted_sentences)
            
            # Limpiar espacios extra
            formatted_message = '\n'.join([line.strip() for line in formatted_message.split('\n') if line.strip()])
            
            debug_print(f"🎨 Mensaje formateado con {len(formatted_sentences)} oraciones", "_format_message_beautifully")
            return formatted_message
            
        except Exception as e:
            debug_print(f"❌ Error formateando mensaje: {e}", "_format_message_beautifully")
            return message_text

    def _should_use_ai_generation(self, category: str, message_text: str) -> bool:
        """
        Determina si debe usar generación IA con anti-inventos o templates seguros.
        """
        # 🆕 EXCLUSIONES: Categorías que tienen métodos específicos dedicados
        if category == 'PRICE_INQUIRY':
            return False  # PRICE_INQUIRY usa método directo específico
        
        # Usar IA para preguntas específicas que requieren información detallada
        ai_generation_categories = [
            'EXPLORATION_SECTOR', 'EXPLORATION_ROI', 'EXPLORATION_COMPETITORS',
            'EXPLORATION_COURSE_DETAILS', 'EXPLORATION_PRICING', 'EXPLORATION_SCHEDULE',
            'OBJECTION_COMPLEX', 'TECHNICAL_QUESTIONS', 'AUTOMATION_REPORTS',
            'AUTOMATION_CONTENT', 'TEAM_TRAINING', 'STRATEGIC_CONSULTATION'
        ]
        
        # Keywords expandidos que indican necesidad de información específica
        specific_keywords = [
            # Precios y costos
            'cuánto cuesta', 'cuanto cuesta', 'precio exacto', 'precio', 'costo', 'valor',
            'tarifa', 'inversión', 'pagar', 'presupuesto', 'financiamiento',
            
            # Duración y tiempo
            'duración específica', 'duración', 'tiempo', 'dura', 'largo', 'cronograma',
            'calendario', 'horarios', 'fechas', 'schedule', 'timing',
            
            # Contenido y curriculum
            'contenido detallado', 'contenido', 'temario', 'programa', 'curriculum',
            'módulos incluye', 'módulos', 'capítulos', 'lecciones', 'sesiones',
            'de que trata', 'que trata', 'trata sobre', 'abarca', 'cubre',
            'qué aprendo', 'que aprendo', 'enseña', 'aprenderé', 'incluye',
            
            # Certificación y acreditación
            'certificado', 'diploma', 'acreditación', 'título', 'reconocimiento',
            'validez', 'respaldo', 'avalado',
            
            # Inicio y disponibilidad
            'cuando empieza', 'cuando inicia', 'cuando comienza', 'fecha inicio',
            'próxima fecha', 'disponible', 'disponibilidad', 'cupos',
            
            # Requisitos
            'requisitos técnicos', 'requisitos', 'prerrequisitos', 'necesito',
            'conocimientos previos', 'experiencia previa', 'condiciones',
            
            # Modalidad y formato
            'nivel', 'modalidad', 'formato', 'metodología', 'presencial',
            'online', 'virtual', 'híbrido', 'sincrónico', 'asincrónico',
            
            # Instructores y personal
            'instructor', 'profesor', 'docente', 'maestro', 'tutor',
            'quién enseña', 'quien enseña', 'experiencia instructor',
            'perfil instructor', 'biografía', 'currículum instructor',
            
            # Características del curso
            'curso', 'programa', 'capacitación', 'entrenamiento', 'formación',
            'workshop', 'seminario', 'bootcamp', 'masterclass',
            
            # Soporte y recursos
            'material', 'recursos', 'herramientas', 'plataforma', 'acceso',
            'soporte', 'ayuda', 'asistencia', 'acompañamiento',
            
            # Resultados y beneficios
            'resultados', 'beneficios', 'ventajas', 'logros', 'objetivos',
            'metas', 'competencias', 'habilidades', 'skills'
        ]
        
        message_lower = message_text.lower()
        has_specific_keywords = any(keyword in message_lower for keyword in specific_keywords)
        
        return category in ai_generation_categories or has_specific_keywords

    async def _get_course_info_for_validation(self, user_memory) -> Optional[Dict]:
        """
        Obtiene información de curso para validación desde la base de datos.
        """
        try:
            if not self.course_query_use_case:
                return None
                
            # Si el usuario tiene un curso seleccionado, obtener su información
            if user_memory and hasattr(user_memory, 'selected_course') and user_memory.selected_course:
                course_info = await self.course_query_use_case.get_course_details(user_memory.selected_course)
                if course_info:
                    return course_info
            
            # Si no, obtener información general del catálogo
            catalog_summary = await self.course_query_use_case.get_course_catalog_summary()
            if catalog_summary and catalog_summary.get('sample_course'):
                return catalog_summary['sample_course']
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información de curso para validación: {e}")
            return None

    def _mentions_specific_course_info(self, response_text: str) -> bool:
        """
        Verifica si la respuesta menciona información específica de cursos que requiere validación.
        """
        response_lower = response_text.lower()
        
        specific_mentions = [
            'precio', 'cuesta', '$', 'pesos', 'dólares',
            'duración', 'horas', 'minutos', 'sesiones',
            'módulos', 'certificado', 'nivel', 'requisitos'
        ]
        
        return any(mention in response_lower for mention in specific_mentions)

    def _should_use_advanced_personalization(self, category: str, user_memory, message_text: str) -> bool:
        """
        Determina si debe usar personalización avanzada basada en contexto del usuario.
        """
        # Usar personalización si tenemos información suficiente del usuario
        has_buyer_persona = (hasattr(user_memory, 'buyer_persona_match') and 
                            user_memory.buyer_persona_match != 'unknown')
        
        has_sufficient_info = (
            user_memory.name and user_memory.role and 
            user_memory.interaction_count > 1
        )
        
        # Categorías que se benefician más de personalización
        personalization_categories = [
            'EXPLORATION', 'BUYING_SIGNALS', 'OBJECTION_PRICE', 'OBJECTION_VALUE',
            'AUTOMATION_NEED', 'TEAM_TRAINING', 'CONTACT_ADVISOR_EXECUTIVE'
        ]
        
        # Keywords que indican necesidad de personalización
        personalization_keywords = [
            'mi empresa', 'nuestro negocio', 'mi equipo', 'mi sector', 'mi industria',
            'como director', 'como gerente', 'en mi rol', 'mi experiencia'
        ]
        
        message_lower = message_text.lower()
        has_personalization_keywords = any(keyword in message_lower for keyword in personalization_keywords)
        
        # Usar personalización si:
        # 1. Tenemos buyer persona detectado, O
        # 2. Tenemos información suficiente Y la categoría se beneficia, O
        # 3. El usuario usa lenguaje personal/empresarial
        return (
            has_buyer_persona or
            (has_sufficient_info and category in personalization_categories) or
            has_personalization_keywords
        )

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
            if not hasattr(self, 'bonus_activation_use_case'):
                self.bonus_activation_use_case = BonusActivationUseCase()
            
            debug_print(f"🎁 Activando bonos para categoría: {category}", "_activate_intelligent_bonuses")
            
            # Obtener información del usuario
            user_name = user_memory.name if user_memory else "Usuario"
            user_role = user_memory.role if user_memory else "Profesional"
            message_text = incoming_message.body.lower()
            
            # Determinar contexto de conversación
            conversation_context = self._determine_conversation_context(category, message_text)
            urgency_level = self._determine_urgency_level(category, user_memory)
            
            # 🆕 Obtener bonos contextuales usando el sistema inteligente
            contextual_bonuses = []
            
            try:
                # Usar el sistema inteligente de bonos 
                if hasattr(self, 'dynamic_course_provider') and self.dynamic_course_provider:
                    # Obtener ID del curso principal
                    course_data = await self.dynamic_course_provider.get_primary_course_info()
                    course_id = course_data.get('id')  # La clave correcta es 'id', no 'id_course'
                    
                    if course_id:
                        # Usar el sistema de bonos inteligente
                        debug_print(f"🎯 Obteniendo bonos contextuales para curso {course_id}", "_activate_intelligent_bonuses")
                        # Convertir string a UUID si es necesario
                        course_uuid = UUID(course_id) if isinstance(course_id, str) else course_id
                        raw_bonuses = await self.bonus_activation_use_case.get_contextual_bonuses(
                            course_id=course_uuid,
                            user_memory=user_memory,
                            conversation_context=conversation_context,
                            limit=3
                        )
                        
                        # Convertir formato para compatibilidad
                        contextual_bonuses = []
                        for bonus in raw_bonuses:
                            contextual_bonuses.append({
                                "name": bonus.get('content', 'Bono disponible'),
                                "description": bonus.get('content', 'Descripción del bono'),
                                "priority_reason": bonus.get('priority_reason', 'Ideal para tu perfil'),
                                "sales_angle": bonus.get('sales_angle', 'Valor agregado')
                            })
                        
                        debug_print(f"✅ {len(contextual_bonuses)} bonos contextuales obtenidos", "_activate_intelligent_bonuses")
                    else:
                        debug_print("⚠️ No se pudo obtener ID del curso", "_activate_intelligent_bonuses")
                        
            except Exception as e:
                self.logger.error(f"Error obteniendo bonos contextuales inteligentes: {e}")
                debug_print(f"❌ Error en bonos inteligentes: {e}", "_activate_intelligent_bonuses")
            
            # Fallback si no se obtuvieron bonos inteligentes
            if not contextual_bonuses:
                debug_print("🔄 Usando fallback de bonos básicos", "_activate_intelligent_bonuses")
                contextual_bonuses = [
                    {
                        "name": "Recursos Adicionales Especializados",
                        "description": "Material complementario adaptado a tu sector",
                        "priority_reason": "Ideal para tu perfil empresarial",
                        "sales_angle": "Valor agregado inmediato"
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
        
        debug_print(f"🔍 DEBUG TEMPLATE SELECTION - Categoría: {category}, Nombre: '{user_name}', Rol: '{user_role}'", "_get_template_response")
        
        # Mapeo de categorías a templates - EXPANDIDO con más categorías PyME
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
            'GENERAL_QUESTION': lambda: self._get_general_response(user_name, user_role),
            # Nuevas categorías PyME específicas
            'EXPLORATION_SECTOR': lambda: asyncio.create_task(self._get_exploration_response(user_name, user_role)),
            'EXPLORATION_ROI': lambda: asyncio.create_task(self._get_roi_exploration_response(user_name, user_role)),
            'PRICE_INQUIRY': lambda: asyncio.create_task(self._get_direct_price_response(user_name, user_role, user_memory)),
            'OBJECTION_BUDGET_PYME': lambda: asyncio.create_task(self._get_dynamic_price_objection_response(user_name, user_role, user_memory)),
            'OBJECTION_TECHNICAL_TEAM': lambda: self._get_technical_objection_response(user_name, user_role),
            'AUTOMATION_REPORTS': lambda: self._get_automation_response(user_name, user_role),
            'AUTOMATION_CONTENT': lambda: self._get_content_automation_response(user_name, user_role),
            'BUYING_SIGNALS_EXECUTIVE': lambda: self._get_buying_signals_response(user_name),
            'PILOT_REQUEST': lambda: self._get_pilot_request_response(user_name, user_role),
            'TEAM_TRAINING': lambda: asyncio.create_task(self._get_team_training_response(user_name, user_role)),
            'STRATEGIC_CONSULTATION': lambda: self._get_strategic_consultation_response(user_name, user_role),
            # Nuevas categorías para mensajes fuera de contexto
            'OFF_TOPIC_CASUAL': lambda: self._get_off_topic_casual_response(user_name, incoming_message.body, user_memory),
            'OFF_TOPIC_PERSONAL': lambda: self._get_off_topic_casual_response(user_name, incoming_message.body, user_memory),
            'OFF_TOPIC_UNRELATED': lambda: self._get_off_topic_casual_response(user_name, incoming_message.body, user_memory),
            'OFF_TOPIC_REPEATED': lambda: self._get_off_topic_repeated_response(user_name),
            'OFFENSIVE_MESSAGE': lambda: self._get_offensive_message_response(user_name)
        }
        
        # Manejar casos especiales según estado del usuario
        if not user_name and category != 'CONTACT_REQUEST':
            debug_print(f"❌ CASO ESPECIAL 1 - Sin nombre detectado", "_get_template_response")
            # Si no tenemos nombre, pedirlo primero
            if user_memory and user_memory.interaction_count == 1:
                return WhatsAppMessageTemplates.welcome_new_business_user()
            else:
                return WhatsAppMessageTemplates.executive_name_request()
        
        if user_name and not user_role and category not in ['CONTACT_REQUEST', 'FREE_RESOURCES']:
            debug_print(f"❌ CASO ESPECIAL 2 - Tiene nombre '{user_name}' pero no rol '{user_role}', categoría: {category}", "_get_template_response")
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
        result = template_func()
        
        # Manejar funciones asíncronas
        if hasattr(result, '__await__'):
            return await result
        return result
    
    async def _get_exploration_response(self, user_name: str, user_role: str) -> str:
        """Respuesta para usuarios explorando opciones usando información de la BD."""
        name_part = f"{user_name}, " if user_name else ""
        role_context = f"Como {user_role}, " if user_role else ""
        
        try:
            if self.course_query_use_case:
                # Obtener información de cursos disponibles
                catalog_summary = await self.course_query_use_case.get_course_catalog_summary()
                if catalog_summary and catalog_summary.get('statistics', {}).get('total_courses', 0) > 0:
                    total_courses = catalog_summary['statistics']['total_courses']
                    featured_courses = catalog_summary.get('featured_courses', [])
                    
                    # Generar información de cursos contextual
                    course_info_text = self._generate_course_info_text(total_courses, featured_courses, 'EXPLORATION')
                    
                    return f"""¡Excelente que estés explorando{', ' + name_part if name_part else ''}! 🎯

{role_context}estoy segura de que la IA puede transformar completamente tu forma de trabajar.

**📚 Te puedo mostrar:**
• Temario completo de {self._get_course_name_text(total_courses, featured_courses)}
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
    
    async def _get_general_response(self, user_name: str, user_role: str) -> str:
        """Respuesta general personalizada con información de base de datos."""
        name_part = f"{user_name}, " if user_name else ""
        role_context = f"Como {user_role}, " if user_role else ""
        
        try:
            # Intentar obtener información de cursos de la base de datos
            if self.course_query_use_case:
                catalog_summary = await self.course_query_use_case.get_course_catalog_summary()
                if catalog_summary and catalog_summary.get('statistics', {}).get('total_courses', 0) > 0:
                    total_courses = catalog_summary['statistics']['total_courses']
                    available_levels = catalog_summary.get('available_options', {}).get('levels', [])
                    featured_courses = catalog_summary.get('featured_courses', [])
                    
                    levels_text = ", ".join(available_levels) if available_levels else "todos los niveles"
                    course_name_text = self._get_course_name_text(total_courses, featured_courses)
                    
                    courses_text = f"**📚 Tenemos {course_name_text}** para {levels_text}, diseñados específicamente para profesionales como tú." if total_courses == 1 else f"**📚 Tenemos {total_courses} cursos disponibles** para {levels_text}, diseñados específicamente para profesionales como tú."
                    
                    return f"""{role_context}Estoy aquí para ayudarte a descubrir cómo la IA puede transformar tu trabajo.

{courses_text}

**🎯 Puedo ayudarte con:**
• Información detallada sobre nuestros cursos
• Recursos gratuitos para empezar hoy mismo
• Consultas específicas sobre automatización
• Conexión con nuestro equipo de asesores especializados

¿En qué puedo asistirte específicamente?"""
        except Exception as e:
            self.logger.error(f"Error obteniendo información de cursos para respuesta general: {e}")
        
        # Fallback sin información de BD
        return f"""{role_context}Estoy aquí para ayudarte a descubrir cómo la IA puede transformar tu trabajo.

**🎯 Puedo ayudarte con:**
• Información sobre nuestros cursos especializados
• Recursos gratuitos para empezar
• Consultas específicas sobre automatización
• Conexión con nuestro equipo de asesores

¿En qué puedo asistirte específicamente?"""
    
    async def _get_roi_exploration_response(self, user_name: str, user_role: str) -> str:
        """
        Respuesta para exploración de ROI específica por rol.
        Usa datos dinámicos de la base de datos para cálculos de ROI.
        """
        try:
            # Obtener información dinámica del curso desde BD
            course_data = await self.dynamic_course_provider.get_primary_course_info()
            
            name_part = f"{user_name}, " if user_name else ""
            role_context = f"Como {user_role}, " if user_role else ""
            course_price = course_data['price']
            currency = course_data['currency']
            currency_symbol = "$" if currency in ["USD", "MXN"] else currency + " "
            
            # ROI específico por buyer persona usando datos reales de BD
            roi_data = course_data.get('roi_examples', {})
            
            # Generar ROI basado en rol y precio real del curso
            if any(keyword in user_role.lower() for keyword in ['marketing', 'digital', 'comercial']):
                marketing_roi = roi_data.get('marketing_manager', {})
                monthly_savings = marketing_roi.get('monthly_savings', 1200)
                break_even = marketing_roi.get('roi_months_to_break_even', max(1, round(course_price / monthly_savings, 1)))
                roi_text = f"• 80% menos tiempo creando contenido\n• {currency_symbol}{monthly_savings:,}/mes ahorro → Recuperas inversión en {break_even} {'mes' if break_even == 1 else 'meses'}"
            
            elif any(keyword in user_role.lower() for keyword in ['operaciones', 'operations', 'gerente', 'director']):
                operations_roi = roi_data.get('operations_manager', {})
                monthly_savings = operations_roi.get('monthly_savings', 2000)
                break_even = operations_roi.get('roi_months_to_break_even', max(1, round(course_price / monthly_savings, 1)))
                roi_text = f"• 30% reducción en procesos manuales\n• {currency_symbol}{monthly_savings:,}/mes ahorro → Recuperas inversión en {break_even} {'mes' if break_even == 1 else 'meses'}"
            
            elif any(keyword in user_role.lower() for keyword in ['ceo', 'founder', 'fundador', 'director general']):
                ceo_roi = roi_data.get('ceo_founder', {})
                yearly_savings = ceo_roi.get('yearly_savings', 27600)
                roi_percentage = round((yearly_savings / course_price) * 100) if course_price > 0 else 500
                roi_text = f"• 40% más productividad del equipo\n• {currency_symbol}{yearly_savings:,} ahorro anual vs contratar analista → ROI del {roi_percentage}% anual"
            
            elif any(keyword in user_role.lower() for keyword in ['rh', 'recursos humanos', 'hr', 'talent']):
                monthly_savings = 1500
                break_even = max(1, round(course_price / monthly_savings, 1))
                roi_text = f"• 70% más eficiencia en capacitaciones\n• {currency_symbol}{monthly_savings:,} ahorro mensual → ROI del 300% primer trimestre"
            
            else:
                # ROI general basado en precio del curso
                estimated_monthly_savings = max(1000, course_price // 3)
                break_even = max(1, round(course_price / estimated_monthly_savings, 1))
                roi_percentage = round((estimated_monthly_savings * 3 / course_price) * 100) if course_price > 0 else 250
                roi_text = f"• 50% más eficiencia en procesos\n• {currency_symbol}{estimated_monthly_savings:,} ahorro mensual → ROI del {roi_percentage}% primeros 3 meses"
            
            return f"""¡Excelente pregunta sobre ROI{', ' + name_part if name_part else ''}! 📊

{role_context}resultados reales de profesionales como tú:

**💰 RESULTADOS COMPROBADOS:**
{roi_text}

**⚡ Beneficios inmediatos:**
• Automatización tareas desde día 1
• ↑ Calidad y consistencia
• Más tiempo actividades estratégicas

¿Te gustaría casos específicos de tu sector?"""
        except Exception as e:
            debug_print(f"Error al obtener info de curso para ROI: {e}", "_get_roi_response")
            course_price = 5000  # Precio base si falla la consulta
            course_currency = 'MXN'
            
        # ... resto del código ...

    def _get_technical_objection_response(self, user_name: str, user_role: str) -> str:
        """Respuesta para objeciones técnicas (falta de equipo técnico)."""
        name_part = f"{user_name}, " if user_name else ""
        
        return f"""Entiendo tu preocupación{', ' + name_part if name_part else ''}! 🔧

**🎯 Diseñado para PyMEs SIN equipo técnico:**

• **Sin programación**: Interfaz visual
• **Sin infraestructura**: Todo en la nube
• **Sin mantenimiento**: Automatizado
• **Soporte incluido**: Acompañamiento completo

**📊 90% estudiantes SIN background técnico** obtienen resultados desde semana 1.

¿Te gustaría ejemplos específicos de tu área?"""
    
    def _get_content_automation_response(self, user_name: str, user_role: str) -> str:
        """Respuesta específica para automatización de contenido."""
        name_part = f"{user_name}, " if user_name else ""
        
        return f"""¡Perfecto{', ' + name_part if name_part else ''}! 📝

La automatización de contenido es donde vemos el **mayor impacto inmediato**:

**🚀 AUTOMATIZACIONES PRÁCTICAS:**
• Emails marketing personalizados (5 min vs 2 horas)
• Posts para redes sociales (calendario completo en 30 min)
• Propuestas comerciales (plantillas inteligentes)
• Reportes ejecutivos (datos → insights automáticamente)

**💡 CASO REAL:**
Una agencia redujo 80% el tiempo de creación de contenido, pasando de 8 horas/día a 1.5 horas/día.

¿En qué tipo de contenido inviertes más tiempo actualmente?"""
    
    def _get_pilot_request_response(self, user_name: str, user_role: str) -> str:
        """Respuesta para solicitudes de proyecto piloto."""
        name_part = f"{user_name}, " if user_name else ""
        
        return f"""¡Excelente enfoque{', ' + name_part if name_part else ''}! 🎯

**🚀 PILOTO PERFECTO PARA TI:**

• **Duración**: 30 días de implementación práctica
• **Enfoque**: Un proceso específico de tu área
• **Entregables**: Automatización funcionando + ROI medible
• **Soporte**: Acompañamiento personalizado

**📊 Resultados típicos del piloto:**
• 40-60% reducción de tiempo en proceso elegido
• ROI visible desde la primera semana
• Team buy-in del 95% (equipo convencido de beneficios)

¿Qué proceso te gustaría automatizar primero en el piloto?"""
    
    async def _get_team_training_response(self, user_name: str, user_role: str) -> str:
        """Respuesta para capacitación de equipos con información de BD."""
        name_part = f"{user_name}, " if user_name else ""
        
        try:
            if self.course_query_use_case:
                catalog_summary = await self.course_query_use_case.get_course_catalog_summary()
                training_programs = catalog_summary.get('available_options', {}).get('modalities', [])
                
                modalities_text = ", ".join(training_programs[:3]) if training_programs else "presencial, online e híbrida"
                
                return f"""¡Perfecto{', ' + name_part if name_part else ''}! 👥

**🎓 CAPACITACIÓN EMPRESARIAL PERSONALIZADA:**

• **Modalidades**: {modalities_text}  
• **Grupos**: 5-20 personas por cohorte
• **Duración**: Flexible según necesidades del equipo
• **Aplicación**: Casos reales de tu empresa

**💼 BENEFICIOS CORPORATIVOS:**
• Descuentos por volumen (15-30% según tamaño grupo)
• Certificación oficial para todo el equipo
• Implementación inmediata en proyectos reales
• Mentoring post-capacitación incluido

¿Cuántas personas de tu equipo participarían?"""
            else:
                return f"""¡Perfecto{', ' + name_part if name_part else ''}! 👥

**🎓 CAPACITACIÓN EMPRESARIAL PERSONALIZADA:**

• **Modalidades**: Presencial, online e híbrida
• **Grupos**: 5-20 personas por cohorte
• **Duración**: Flexible según necesidades del equipo
• **Aplicación**: Casos reales de tu empresa

**💼 BENEFICIOS CORPORATIVOS:**
• Descuentos por volumen (15-30% según tamaño grupo)
• Certificación oficial para todo el equipo
• Implementación inmediata en proyectos reales
• Mentoring post-capacitación incluido

¿Cuántas personas de tu equipo participarían?"""
                
        except Exception as e:
            self.logger.error(f"Error obteniendo información de capacitación: {e}")
            return f"""¡Perfecto{', ' + name_part if name_part else ''}! 👥

**🎓 CAPACITACIÓN EMPRESARIAL PERSONALIZADA:**

• **Modalidades**: Presencial, online e híbrida
• **Grupos**: 5-20 personas por cohorte
• **Duración**: Flexible según necesidades del equipo
• **Aplicación**: Casos reales de tu empresa

¿Cuántas personas de tu equipo participarían?"""
    
    def _get_strategic_consultation_response(self, user_name: str, user_role: str) -> str:
        """Respuesta para consultoría estratégica."""
        name_part = f"{user_name}, " if user_name else ""
        
        return f"""¡Excelente visión estratégica{', ' + name_part if name_part else ''}! 🎯

**🏢 CONSULTORÍA ESTRATÉGICA EN IA:**

**📋 PROCESO DE CONSULTORÍA:**
• **Diagnóstico**: Análisis actual de procesos (2 semanas)
• **Roadmap**: Plan de implementación IA personalizado
• **Priorización**: ROI máximo con recursos disponibles
• **Implementación**: Acompañamiento en ejecución

**💼 IDEAL PARA:**
• Directores que definen estrategia tecnológica
• Empresas 50+ empleados evaluando transformación digital
• Organizaciones que buscan ventaja competitiva sostenible

**⏰ INVERSIÓN:** 2-4 semanas → Plan estratégico completo

¿Cuál es tu principal desafío estratégico con IA actualmente?"""
    
    async def _send_response(self, to_number: str, response_text: str) -> Dict[str, Any]:
        """
        Envía respuesta al usuario con typing simulation inteligente.
        
        Args:
            to_number: Número de WhatsApp del usuario
            response_text: Texto de respuesta a enviar
            
        Returns:
            Resultado del envío
        """
        try:
            # Determinar tipo de respuesta para typing apropiado
            response_type = self._classify_response_type(response_text)
            
            if response_type == "quick":
                # Respuestas rápidas (confirmaciones, saludos cortos)
                return await self.twilio_client.send_quick_response(to_number, response_text)
            elif response_type == "thoughtful":
                # Respuestas elaboradas (análisis, explicaciones técnicas)
                return await self.twilio_client.send_thoughtful_response(to_number, response_text)
            else:
                # Respuestas normales con typing automático
                return await self.twilio_client.send_text_with_typing(to_number, response_text)
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando respuesta: {e}")
            return {'success': False, 'error': str(e)}
    
    def _classify_response_type(self, response_text: str) -> str:
        """
        Clasifica el tipo de respuesta para determinar el timing de typing apropiado.
        
        Args:
            response_text: Texto de la respuesta
            
        Returns:
            Tipo de respuesta: "quick", "thoughtful", "normal"
        """
        text_lower = response_text.lower()
        text_length = len(response_text)
        
        # Respuestas rápidas (confirmaciones, saludos)
        quick_indicators = [
            "perfecto", "entendido", "claro", "ok", "correcto", "¡excelente!",
            "gracias", "te ayudo", "por supuesto", "¡hola", "bienvenido"
        ]
        
        # Respuestas elaboradas (análisis, explicaciones técnicas)
        thoughtful_indicators = [
            "analicemos", "específicamente", "detalladamente", "implementación",
            "estrategia", "proceso completo", "paso a paso", "considerando",
            "evaluación", "diagnóstico", "recomendaciones"
        ]
        
        # Clasificar por contenido
        if any(indicator in text_lower for indicator in quick_indicators) and text_length < 100:
            return "quick"
        elif any(indicator in text_lower for indicator in thoughtful_indicators) or text_length > 400:
            return "thoughtful"
        else:
            return "normal"
    
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
                
                if catalog_summary and catalog_summary.get('statistics', {}).get('total_courses', 0) > 0:
                    statistics = catalog_summary.get('statistics', {})
                    total_courses = statistics.get('total_courses', 0)
                    available_options = catalog_summary.get('available_options', {})
                    available_modalities = available_options.get('modalities', [])
                    course_categories = available_options.get('levels', [])
                    featured_courses = catalog_summary.get('featured_courses', [])
                    
                    # Generar información de cursos contextual
                    course_info_text = self._generate_course_info_text(total_courses, featured_courses, category)
                    
                    if category == 'EXPLORATION':
                        return f"""¡Excelente que estés explorando{', ' + name_part if name_part else ''}! 🎯

{course_info_text}
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
                        course_name_text = self._get_course_name_text(total_courses, featured_courses)
                        return f"""**📚 Te ayudo con información sobre:**
• {course_name_text}
• Programas de automatización empresarial
• Capacitación personalizada según tu sector
• Recursos gratuitos para empezar

¿En qué área te gustaría especializarte?"""
            
            # Fallback si no hay base de datos
            return f"""**📚 Te ayudo con información sobre nuestros cursos de IA aplicada.**

¿En qué área te gustaría especializarte?"""
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información de cursos: {e}")
            return f"""**📚 Te ayudo con información sobre nuestros cursos de IA aplicada.**

¿En qué área te gustaría especializarte?"""
    
    def _generate_course_info_text(self, total_courses: int, featured_courses: list, category: str) -> str:
        """
        Genera texto informativo sobre cursos según el contexto.
        
        Args:
            total_courses: Número total de cursos disponibles
            featured_courses: Lista de cursos destacados con información
            category: Categoría de la consulta
            
        Returns:
            Texto formateado con información de cursos
        """
        if total_courses == 1 and featured_courses:
            # Caso actual: Solo 1 curso - mostrar nombre específico
            course_name = featured_courses[0].get('name', 'nuestro curso de IA')
            level = featured_courses[0].get('level', '')
            modality = featured_courses[0].get('modality', '')
            
            level_text = f" (Nivel: {level})" if level else ""
            modality_text = f" - Modalidad: {modality}" if modality else ""
            
            return f"""**📚 Tenemos el curso: "{course_name}"{level_text}**{modality_text}

Este curso te enseña:"""
            
        elif total_courses > 1:
            # Caso futuro: Múltiples cursos - mostrar los más relevantes
            if category in ['EXPLORATION_SECTOR', 'AUTOMATION_CONTENT', 'AUTOMATION_REPORTS']:
                # Para categorías específicas, filtrar cursos relevantes
                relevant_courses = [course for course in featured_courses[:3]]  # Top 3 más relevantes
                
                if relevant_courses:
                    course_list = []
                    for course in relevant_courses:
                        name = course.get('name', 'Curso de IA')
                        level = course.get('level', '')
                        level_text = f" ({level})" if level else ""
                        course_list.append(f"• **{name}**{level_text}")
                    
                    return f"""**📚 Cursos disponibles relacionados con tu consulta:**

{chr(10).join(course_list)}

Cada curso te enseña:"""
                
            # Caso general: mostrar resumen de cursos
            return f"**📚 Tenemos {total_courses} cursos de IA especializados que te enseñan:**"
            
        else:
            # Fallback genérico
            return f"**📚 Tenemos {total_courses} cursos de IA que te enseñan:**"
    
    def _get_course_name_text(self, total_courses: int, featured_courses: list) -> str:
        """
        Obtiene texto simple del nombre del curso para uso en listas.
        
        Args:
            total_courses: Número total de cursos
            featured_courses: Lista de cursos destacados
            
        Returns:
            Texto simple con nombre(s) de curso(s)
        """
        if total_courses == 1 and featured_courses:
            course_name = featured_courses[0].get('name', 'nuestro curso de IA')
            return f'"{course_name}"'
        elif total_courses > 1:
            return f"nuestros {total_courses} cursos de IA"
        else:
            return f"nuestros {total_courses} cursos de IA"
    
    async def _get_course_detailed_info(self) -> dict:
        """
        Obtiene información detallada del curso dinámicamente desde BD.
        Reemplaza datos hardcodeados con información real de la base de datos.
        
        Returns:
            Dict con información completa del curso para OpenAI
        """
        try:
            # Usar el nuevo proveedor dinámico de información
            course_data = await self.dynamic_course_provider.get_primary_course_info()
            
            # Estructurar información para OpenAI con datos reales de BD
            course_info = {
                'name': course_data['name'],
                'short_description': course_data['short_description'],
                'long_description': course_data['long_description'],
                'level': course_data['level'],
                'modality': course_data['modality'],
                'price': course_data['price'],
                'price_formatted': course_data['price_formatted'],
                'currency': course_data['currency'],
                'session_count': course_data['session_count'],
                'total_duration_hours': course_data['total_duration_hours'],
                'total_duration_formatted': course_data['total_duration_formatted'],
                'bonds': course_data['bonds'][:5],  # Top 5 bonos para OpenAI
                'bonds_count': course_data['bonds_count'],
                'roi_examples': course_data['roi_examples'],
                'id': course_data['id'],
                'has_real_data': course_data['price'] > 0,  # Flag para OpenAI
                'data_source': 'database' if course_data['price'] > 0 else 'fallback'
            }
            
            self.logger.info(f"📚 Información dinámica de curso obtenida para OpenAI: {course_info['name']} (${course_info['price']})")
            return course_info
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información detallada del curso: {e}")
            return {
                'name': 'Curso de IA Profesional',
                'short_description': 'Información por confirmar',
                'level': 'Profesional',
                'modality': 'Online',
                'price': 0,
                'price_formatted': 'Consultar precio',
                'currency': 'USD',
                'session_count': 0,
                'total_duration_hours': 0,
                'bonds': [],
                'bonds_count': 0,
                'roi_examples': {},
                'has_real_data': False,
                'data_source': 'error_fallback'
            }
    
    async def _get_dynamic_price_objection_response(self, user_name: str, user_role: str, user_memory) -> str:
        """
        Respuesta a objeciones de precio con información dinámica desde BD.
        Reemplaza valores hardcodeados con datos reales del curso.
        """
        try:
            # Obtener información dinámica del curso desde BD
            course_data = await self.dynamic_course_provider.get_primary_course_info()
            
            name_part = f"{user_name}, " if user_name else ""
            course_name = course_data['name']
            price_formatted = course_data['price_formatted']
            currency = course_data['currency']
            price_numeric = course_data['price']
            
            # Calcular ROI dinámico basado en precio real
            roi_example = self._calculate_dynamic_roi_for_role(price_numeric, user_role, currency)
            
            response = f"""Entiendo la preocupación por el presupuesto{', ' + name_part if name_part else ''} - es típico de líderes PyME responsables. 💰

**🏢 PERSPECTIVA EMPRESARIAL:**
• {course_name}: {price_formatted} (inversión única, resultados permanentes)
• Contratar especialista IA: $3,000-5,000/mes (+ prestaciones)
• Consultoría externa: $200/hora × 40 horas = $8,000 USD
• Seguir perdiendo eficiencia: **Costo de oportunidad ilimitado**

**📊 VALOR ESPECÍFICO PARA PYMES:**
• Framework IMPULSO: aplicable a cualquier proceso desde día 1
• Sin dependencia técnica: tu equipo actual puede implementarlo
• Actualizaciones incluidas: siempre al día con nueva tecnología
• Casos reales PyME: ejemplos de tu mismo tamaño de empresa{roi_example}

**🎯 LA PREGUNTA ESTRATÉGICA:**
¿Puedes permitirte que tu competencia implemente IA antes que tú?

¿Te gustaría que revisemos un plan de implementación por fases para optimizar tu inversión?"""
            
            self.logger.info(f"✅ Respuesta de precio generada con datos dinámicos: {price_formatted}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error generando respuesta dinámica de precio: {e}")
            # Fallback sin datos específicos
            return f"""Entiendo tu preocupación por el presupuesto{', ' + user_name + ', ' if user_name else ''} - es típico de líderes responsables. 💰

**🏢 PERSPECTIVA EMPRESARIAL:**
• Nuestro curso: Inversión única con resultados permanentes
• Contratar especialista: $3,000-5,000/mes + prestaciones
• Consultoría externa: $8,000+ USD por proyecto

**📊 VALOR PARA PYMES:**
• Sin dependencia técnica: tu equipo puede implementarlo
• ROI personalizado según tu empresa específica

¿Te gustaría que revisemos las opciones de inversión disponibles?"""
    
    def _calculate_dynamic_roi_for_role(self, price_numeric: int, user_role: str, currency: str = "MXN") -> str:
        """
        Calcula ROI dinámico basado en precio real del curso y rol del usuario.
        """
        if price_numeric <= 0:
            return "\n• ROI personalizado según tu empresa y necesidades específicas"
        
        currency_symbol = "$" if currency in ["USD", "MXN"] else currency + " "
        
        # ROI específico por buyer persona con precio real
        if "marketing" in user_role.lower() or "content" in user_role.lower():
            monthly_savings = 4800 if currency == "MXN" else 300  # Ajuste por moneda
            monthly_savings_formatted = f"{currency_symbol}{monthly_savings:,}"
            months_to_break_even = max(1, round(price_numeric / (monthly_savings * 4), 1))  # 4 campañas/mes
            return f"""

**💡 ROI para Marketing (casos documentados):**
• Antes: 8 horas/campaña = {monthly_savings_formatted}/mes en 4 campañas
• Después: 2 horas con IA = reducción del 75%
• **Ahorro mensual: {monthly_savings_formatted}** → Break-even en {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}"""
        
        elif "operaciones" in user_role.lower() or "manufactura" in user_role.lower():
            monthly_savings = 8000 if currency == "MXN" else 500  # Ajuste por moneda
            monthly_savings_formatted = f"{currency_symbol}{monthly_savings:,}"
            months_to_break_even = max(1, round(price_numeric / monthly_savings, 1))
            return f"""

**💡 ROI para Operaciones (casos reales):**
• Antes: 12 horas/semana reportes = {currency_symbol}{monthly_savings * 3:,}/mes
• Después: 2 horas automatizadas = {currency_symbol}{monthly_savings // 4:,}/mes
• **Ahorro mensual: {monthly_savings_formatted}** → Break-even en {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}"""
        
        elif "ceo" in user_role.lower() or "fundador" in user_role.lower():
            monthly_cost_analyst = 12000 if currency == "MXN" else 750  # Costo analista
            course_monthly_equivalent = max(200, round(price_numeric / 12, 0))
            monthly_savings = monthly_cost_analyst - course_monthly_equivalent
            monthly_savings_formatted = f"{currency_symbol}{monthly_savings:,}"
            months_to_break_even = max(1, round(price_numeric / monthly_savings, 1))
            return f"""

**💡 ROI Ejecutivo (análisis de costos):**
• Costo analista junior: {currency_symbol}{monthly_cost_analyst:,}/mes
• Costo curso amortizado: {currency_symbol}{course_monthly_equivalent:,}/mes
• **Ahorro mensual: {monthly_savings_formatted}** → Break-even en {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}"""
        
        else:
            # ROI genérico calculado dinámicamente
            estimated_monthly_savings = max(2000 if currency == "MXN" else 125, price_numeric // 4)
            months_to_break_even = max(1, round(price_numeric / estimated_monthly_savings, 1))
            return f"""

**💡 ROI Personalizado para tu área:**
• Ahorro estimado: {currency_symbol}{estimated_monthly_savings:,}/mes en procesos optimizados
• **Break-even: {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}**
• ROI anual proyectado: {round((estimated_monthly_savings * 12 / price_numeric) * 100)}%"""
    
    async def _get_direct_price_response(self, user_name: str, user_role: str, user_memory) -> str:
        """
        Respuesta directa a preguntas específicas de precio.
        Proporciona información clara y luego agrega valor/beneficios.
        """
        try:
            # Obtener información dinámica del curso desde BD
            course_data = await self.dynamic_course_provider.get_primary_course_info()
            
            name_part = f"{user_name}, " if user_name else ""
            course_name = course_data['name']
            price_formatted = course_data['price_formatted']
            currency = course_data['currency']
            price_numeric = course_data['price']
            session_count = course_data['session_count']
            duration_formatted = course_data['total_duration_formatted']
            
            # ROI específico pero más breve para respuesta directa
            roi_brief = self._get_brief_roi_for_role(price_numeric, user_role, currency)
            
            response = f"""¡Hola{', ' + name_part if name_part else ''}! 💰

**🎓 {course_name}**
💰 **Precio**: {price_formatted}
⏱️ **Duración**: {duration_formatted} ({session_count} sesiones)
📊 **Modalidad**: Online

{roi_brief}

**🎁 INCLUYE:**
• Acceso 100% online a grabaciones
• Workbook interactivo en Coda.io  
• Soporte en Telegram
• Comunidad privada vitalicia

**💡 Lo mejor:** Puedes aplicar lo que aprendes desde la primera sesión, recuperando tu inversión rápidamente con la automatización de procesos.

¿Te gustaría conocer más detalles sobre el contenido del curso o tienes alguna otra pregunta?"""
            
            self.logger.info(f"✅ Respuesta directa de precio enviada: {price_formatted}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error generando respuesta directa de precio: {e}")
            # Fallback directo
            return f"""¡Hola{', ' + user_name + ', ' if user_name else ''}! 💰

Te comparto la información que solicitas:

**🎓 Curso de IA para Profesionales**  
💰 **Precio**: Déjame consultar el precio actual para darte la información más exacta.

Mientras tanto, te comento que es una inversión única que incluye:
• Acceso completo online
• Materiales interactivos  
• Soporte especializado
• Actualizaciones de por vida

¿Te gustaría que te contacte con más detalles específicos?"""
    
    def _get_brief_roi_for_role(self, price_numeric: int, user_role: str, currency: str = "MXN") -> str:
        """
        Genera ROI breve para respuestas directas de precio.
        """
        if price_numeric <= 0:
            return "**💡 Inversión que se recupera rápidamente** con la automatización de procesos."
        
        currency_symbol = "$" if currency in ["USD", "MXN"] else currency + " "
        
        # ROI breve por rol
        if "operaciones" in user_role.lower():
            monthly_savings = 8000 if currency == "MXN" else 500
            months_to_break_even = max(1, round(price_numeric / monthly_savings, 1))
            return f"**💡 Para {user_role}:** Ahorro típico de {currency_symbol}{monthly_savings:,}/mes → Recuperas inversión en {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}"
        
        elif "marketing" in user_role.lower():
            monthly_savings = 4800 if currency == "MXN" else 300
            months_to_break_even = max(1, round(price_numeric / (monthly_savings * 4), 1))
            return f"**💡 Para {user_role}:** Ahorro típico de {currency_symbol}{monthly_savings:,}/mes → Recuperas inversión en {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}"
        
        elif "ceo" in user_role.lower() or "fundador" in user_role.lower():
            monthly_savings = 8000 if currency == "MXN" else 500
            months_to_break_even = max(1, round(price_numeric / monthly_savings, 1))
            return f"**💡 Para {user_role}:** Ahorro vs contratar especialista → Recuperas inversión en {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}"
        
        else:
            estimated_monthly_savings = max(3000 if currency == "MXN" else 200, price_numeric // 3)
            months_to_break_even = max(1, round(price_numeric / estimated_monthly_savings, 1))
            return f"**💡 Inversión inteligente:** Recuperas el costo en {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'} con automatización de procesos"
    
    async def _get_concise_specific_response(self, inquiry_type: str, user_name: str, user_role: str, user_memory) -> str:
        """
        Genera respuestas concisas para consultas específicas (precio, sesiones, duración, etc.).
        Solo muestra: título del curso + información específica + pregunta final.
        """
        try:
            # Obtener información dinámica del curso desde BD
            course_data = await self.dynamic_course_provider.get_primary_course_info()
            course_name = course_data['name']
            
            if inquiry_type == 'price':
                price_formatted = course_data['price_formatted']
                return f"""🎓 **{course_name}**
💰 **Precio**: {price_formatted}

¿Te gustaría conocer más detalles del curso?"""
            
            elif inquiry_type == 'sessions':
                session_count = course_data['session_count']
                duration_formatted = course_data['total_duration_formatted']
                return f"""🎓 **{course_name}**
📅 **Sesiones**: {session_count} sesiones ({duration_formatted})

¿Te gustaría conocer el contenido de las sesiones?"""
            
            elif inquiry_type == 'duration':
                duration_formatted = course_data['total_duration_formatted']
                session_count = course_data['session_count']
                return f"""🎓 **{course_name}**
⏱️ **Duración**: {duration_formatted} ({session_count} sesiones)

¿Te gustaría saber más sobre el programa?"""
            
            elif inquiry_type == 'content':
                # Implementar flujo progresivo de contenido
                return await self._handle_progressive_content_flow(course_data, course_name, user_memory)
            
            elif inquiry_type == 'detailed_content':
                # Para temario detallado, obtener información completa de sesiones
                try:
                    from app.infrastructure.database.repositories.course_repository import CourseRepository
                    from app.application.usecases.query_course_information import QueryCourseInformationUseCase
                    
                    course_repo = CourseRepository()
                    course_query = QueryCourseInformationUseCase(course_repo)
                    
                    # Buscar el curso por nombre similar
                    courses = await course_query.search_courses_by_keyword("IA", 3)
                    if courses:
                        target_course = courses[0]  # Usar el primero encontrado
                        detailed_content = await course_query.get_course_detailed_content(target_course.id_course)
                        
                        if detailed_content and detailed_content.get('sessions'):
                            # Construir respuesta con estructura de sesiones
                            sessions_text = ""
                            for i, session_data in enumerate(detailed_content['sessions'][:3], 1):  # Limitar a 3 sesiones
                                session = session_data['session']
                                title = session.get('title', f'Sesión {i}')
                                description = session.get('description', 'Contenido práctico de IA')
                                sessions_text += f"\n📚 **{title}**\n   {description}\n"
                            
                            return f"""🎓 **{course_name}**
📋 **Temario Detallado** ({detailed_content.get('total_sessions', 4)} sesiones):
{sessions_text}
¿Te interesa profundizar en algún módulo específico?"""
                        
                except Exception as e:
                    self.logger.error(f"Error obteniendo contenido detallado: {e}")
                
                # Fallback si no se puede obtener información detallada
                session_count = course_data['session_count']
                return f"""🎓 **{course_name}**

📚 **CONTENIDO DEL CURSO:**

**📋 Estructura:**
• {session_count} sesiones prácticas (70% práctica, 30% teoría)
• Casos reales de empresas

**🛠️ Herramientas:**
• ChatGPT, Claude, Gemini
• Zapier/Make para automatización
• Integración Slack, Teams, CRM
• Dashboards en Coda.io

**👨‍🏫 Instructor:**
• +5 años en IA empresarial
• +200 empresas implementadas
• Certificaciones OpenAI y Google AI

**📊 Metodología:**
• Ejercicios hands-on
• Plantillas reutilizables
• Proyectos aplicados a tu sector

**🎁 Incluye:**
• Workbooks por módulo
• +500 prompts especializados
• Comunidad exclusiva
• Soporte 3 meses

¿Quieres detalles de algún módulo específico?"""
            
            elif inquiry_type == 'modality':
                modality = course_data['modality']
                return f"""🎓 **{course_name}**
📊 **Modalidad**: {modality}

¿Te gustaría conocer más detalles del formato del curso?"""
            
            elif inquiry_type == 'affirmative_detailed':
                # Respuesta afirmativa - manejar como contenido para flujo progresivo
                return await self._handle_progressive_content_flow(course_data, course_name, user_memory)
            
            else:
                # Fallback genérico
                return f"""🎓 **{course_name}**

¿Te gustaría conocer más información específica del curso?"""
                
        except Exception as e:
            self.logger.error(f"Error generando respuesta concisa específica: {e}")
            return """🎓 **Curso de IA para Profesionales**

¿Te gustaría conocer más información del curso?"""
    
    def _detect_specific_inquiry_type(self, message_body: str) -> str:
        """
        Detecta el tipo específico de consulta para usar respuesta concisa.
        
        Returns:
            Tipo de consulta: 'price', 'sessions', 'duration', 'content', 'modality' o None
        """
        message_lower = message_body.lower()
        
        # Detectar consultas de precio
        price_keywords = ['precio', 'costo', 'cuánto cuesta', 'cuanto cuesta', 'valor', 'inversión']
        if any(keyword in message_lower for keyword in price_keywords):
            return 'price'
        
        # Detectar consultas de sesiones
        sessions_keywords = ['sesiones', 'sesión', 'clases', 'clase', 'cuántas sesiones', 'cuantas sesiones']
        if any(keyword in message_lower for keyword in sessions_keywords):
            return 'sessions'
        
        # Detectar consultas de duración
        duration_keywords = ['duración', 'duracion', 'tiempo', 'horas', 'cuánto dura', 'cuanto dura']
        if any(keyword in message_lower for keyword in duration_keywords):
            return 'duration'
        
        # Detectar consultas de contenido - Expandido con más keywords
        content_keywords = [
            'contenido', 'temario', 'programa', 'qué aprendo', 'que aprendo', 'temas',
            'módulos', 'modulos', 'organizan', 'estructura', 'requisitos', 'previos',
            'instructores', 'profesor', 'metodología', 'metodologia', 'enseñanza',
            'ejercicio', 'ejercicios', 'práctico', 'practico', 'herramientas', 'plataformas',
            'sectores', 'industrias', 'casos de éxito', 'casos de exito', 'aplicado',
            'soporte', 'mentoria', 'mentoría', 'grupos', 'slack', 'telegram', 'recursos extra',
            'bonos', 'materiales adicionales', 'acceso', 'evaluación', 'evaluacion', 
            'feedback', 'progreso', 'criterios', 'quizzes', 'retos', 'código', 'codigo',
            'proyectos finales', 'personaliza', 'ejemplos', 'perfil', 'empresa',
            'integraciones', 'teams', 'zapier', 'n8n', 'configurar', 'plantillas',
            'prompts', 'scripts', 'reutilizar', 'comunidad', 'alumnos', 'egresados',
            'consultar', 'actualizaciones', 'evoluciona', 'certificado', 'badge digital',
            'completar', 'pruebas', 'testimonios', 'anteriores participantes', 'adaptar',
            'proyecto real', 'marcha', 'objetivos de aprendizaje', 'sesión', 'sesion'
        ]
        if any(keyword in message_lower for keyword in content_keywords):
            return 'content'
        
        
        # Detectar consultas de modalidad
        modality_keywords = ['modalidad', 'formato', 'presencial', 'online', 'virtual', 'cómo es', 'como es']
        if any(keyword in message_lower for keyword in modality_keywords):
            return 'modality'
        
        # Detectar respuestas afirmativas (para flujo progresivo)
        affirmative_keywords = ['sí', 'si', 'claro', 'perfecto', 'ok', 'dale', 'por favor', 'me interesa', 'quiero saber']
        if any(keyword in message_lower for keyword in affirmative_keywords):
            return 'affirmative_detailed'
        
        return None
    
    def _should_use_concise_response(self, category: str, message_body: str) -> bool:
        """
        Determina si debe usar respuesta concisa basado en la categoría y contenido del mensaje.
        """
        # Lista de categorías que siempre usan respuesta concisa
        specific_inquiry_categories = [
            'PRICE_INQUIRY', 
            'SESSION_INQUIRY', 
            'DURATION_INQUIRY', 
            'CONTENT_INQUIRY', 
            'MODALITY_INQUIRY'
        ]
        
        # Usar respuesta concisa para categorías específicas
        if category in specific_inquiry_categories:
            return True
        
        # Para otras categorías, detectar si es consulta específica por keywords
        inquiry_type = self._detect_specific_inquiry_type(message_body)
        return inquiry_type is not None
    
    async def _generate_intelligent_faq_response(
        self,
        user_message: str,
        faq_context: Dict[str, Any],
        user_context: Dict[str, Any],
        intent_analysis: Dict[str, Any]
    ) -> str:
        """
        Genera respuesta inteligente y natural para FAQs usando OpenAI con contexto.
        
        Args:
            user_message: Mensaje original del usuario
            faq_context: Contexto de la FAQ detectada
            user_context: Contexto del usuario (rol, empresa, etc.)
            intent_analysis: Análisis de intención del mensaje
            
        Returns:
            Respuesta inteligente y personalizada
        """
        try:
            debug_print(f"🤖 Generando respuesta FAQ inteligente para: {faq_context['category']}", "_generate_intelligent_faq_response")
            
            # Construir prompt para respuesta FAQ inteligente
            system_prompt = f"""Eres Brenda, asistente de "Aprenda y Aplique IA".

Responde natural y personalizada usando SOLO la información proporcionada.

USUARIO:
- Nombre: {user_context.get('name', 'Usuario')}
- Rol: {user_context.get('user_role', 'No especificado')}
- Empresa: {user_context.get('company_size', 'No especificada')}

{faq_context['context_for_ai']}

REGLAS:
1. Usa SOLO información proporcionada
2. Personaliza según rol del usuario  
3. Tono profesional pero amigable
4. Máximo 1200 caracteres
5. Emojis moderados

Responde natural y conversacional."""

            user_prompt = f"""Pregunta: "{user_message}"

Respuesta personalizada y útil usando contexto."""

            # Generar respuesta con OpenAI
            if hasattr(self.openai_client, 'generate_completion'):
                response = await self.openai_client.generate_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
            else:
                # Fallback al método chat_completion genérico
                response_dict = await self.openai_client.chat_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                response = response_dict.get('content') if isinstance(response_dict, dict) else response_dict
            
            if response and response.strip():
                debug_print("✅ Respuesta FAQ inteligente generada exitosamente", "_generate_intelligent_faq_response")
                return response.strip()
            else:
                debug_print("⚠️ OpenAI no generó respuesta, usando respuesta base", "_generate_intelligent_faq_response")
                # Fallback a respuesta base personalizada
                return self._generate_fallback_faq_response(faq_context, user_context)
                
        except Exception as e:
            debug_print(f"❌ Error generando respuesta FAQ inteligente: {e}", "_generate_intelligent_faq_response")
            # Fallback a respuesta base
            return self._generate_fallback_faq_response(faq_context, user_context)
    
    def _generate_fallback_faq_response(
        self,
        faq_context: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> str:
        """
        Genera respuesta FAQ de fallback cuando OpenAI no está disponible.
        
        Args:
            faq_context: Contexto de la FAQ
            user_context: Contexto del usuario
            
        Returns:
            Respuesta FAQ personalizada básica
        """
        name = user_context.get('name', 'Usuario')
        user_role = user_context.get('user_role', '')
        base_answer = faq_context['base_answer']
        category = faq_context['category']
        escalation_needed = faq_context.get('escalation_needed', False)
        
        # Personalización básica - saludo breve
        greeting = f"Hola {name}!" if name != 'Usuario' else "Hola!"
        
        if user_role and 'CEO' in user_role:
            role_context = "Como líder de tu organización, "
        elif user_role and ('Manager' in user_role or 'Gerente' in user_role):
            role_context = "Como gerente, "
        else:
            role_context = ""
        
        # Construir respuesta personalizada
        response = f"{greeting}\n\n{role_context}{base_answer}"
        
        # Agregar información de escalación si es necesaria
        if escalation_needed:
            response += "\n\n👨‍💼 Para darte información más detallada y personalizada, te conectaré con un especialista que se pondrá en contacto contigo muy pronto."
        
        # Agregar contexto adicional según categoría
        if category == 'precio':
            response += "\n\n💡 ¿Te gustaría que calcule el ROI específico para tu empresa?"
        elif category == 'implementación':
            response += "\n\n🚀 ¿Te interesaría ver casos de éxito similares a tu industria?"
        
        return response
    
    async def _handle_off_topic_message(
        self,
        category: str,
        user_memory,
        user_id: str,
        intent_analysis: Dict[str, Any]
    ) -> str:
        """
        Maneja mensajes fuera de contexto y ofensivos según la severidad.
        
        Args:
            category: Categoría del mensaje off-topic
            user_memory: Memoria del usuario
            user_id: ID del usuario
            intent_analysis: Análisis de intención completo
            
        Returns:
            Respuesta apropiada según el tipo de mensaje off-topic
        """
        try:
            debug_print(f"🚨 Manejando mensaje fuera de contexto: {category}", "_handle_off_topic_message")
            
            user_name = getattr(user_memory, 'name', '') if user_memory else ''
            
            # Importar templates
            from prompts.agent_prompts import WhatsAppBusinessTemplates
            
            # Obtener información sobre intentos previos de off-topic
            off_topic_attempts = self._get_off_topic_attempts_count(user_memory)
            redirection_style = intent_analysis.get('redirection_style', 'humor')
            
            if category == 'OFFENSIVE_MESSAGE':
                debug_print("🚨 Mensaje ofensivo detectado - Respuesta firme", "_handle_off_topic_message")
                # Actualizar memoria con comportamiento inapropiado
                await self._update_user_memory_with_offensive_behavior(user_id, user_memory)
                return WhatsAppBusinessTemplates.offensive_message_firm_response(user_name)
            
            elif category == 'OFF_TOPIC_REPEATED' or off_topic_attempts >= 2:
                debug_print(f"🚨 Intentos repetidos detectados ({off_topic_attempts}) - Mensaje predeterminado", "_handle_off_topic_message")
                # Actualizar contador de intentos
                await self._update_user_memory_with_off_topic_attempt(user_id, user_memory)
                return WhatsAppBusinessTemplates.off_topic_repeated_predefined(user_name)
            
            else:
                debug_print(f"😊 Primer intento off-topic - Redirección con humor/sarcasmo", "_handle_off_topic_message")
                # Actualizar contador de intentos
                await self._update_user_memory_with_off_topic_attempt(user_id, user_memory)
                
                topic_mentioned = intent_analysis.get('key_topics', [''])[0] if intent_analysis.get('key_topics') else ''
                return WhatsAppBusinessTemplates.off_topic_casual_redirect(user_name, topic_mentioned)
            
        except Exception as e:
            debug_print(f"❌ Error manejando mensaje off-topic: {e}", "_handle_off_topic_message")
            # Fallback seguro
            return WhatsAppBusinessTemplates.off_topic_casual_redirect(user_name)
    
    def _get_off_topic_attempts_count(self, user_memory) -> int:
        """
        Obtiene el número de intentos previos de mensajes off-topic.
        
        Args:
            user_memory: Memoria del usuario
            
        Returns:
            Número de intentos off-topic previos
        """
        if not user_memory:
            return 0
        
        # Si la memoria tiene el atributo off_topic_attempts, usarlo
        if hasattr(user_memory, 'off_topic_attempts'):
            return getattr(user_memory, 'off_topic_attempts', 0)
        
        # Si no, buscar en pain_points por registros de off-topic
        pain_points = getattr(user_memory, 'pain_points', [])
        off_topic_count = len([p for p in pain_points if 'off_topic_attempt' in str(p).lower()])
        
        return off_topic_count

    async def _update_user_memory_with_off_topic_attempt(self, user_id: str, user_memory):
        """
        Actualiza la memoria del usuario con un nuevo intento off-topic.
        
        Args:
            user_id: ID del usuario
            user_memory: Memoria actual del usuario
        """
        try:
            from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
            from memory.lead_memory import MemoryManager
            
            memory_manager = MemoryManager()
            memory_use_case = ManageUserMemoryUseCase(memory_manager)
            
            if user_memory:
                # Incrementar contador de intentos off-topic
                current_attempts = self._get_off_topic_attempts_count(user_memory)
                user_memory.off_topic_attempts = current_attempts + 1
                
                # Agregar a pain_points para tracking
                if not hasattr(user_memory, 'pain_points'):
                    user_memory.pain_points = []
                
                user_memory.pain_points.append(f"off_topic_attempt_{current_attempts + 1}")
                
                # Reducir ligeramente el lead_score por comportamiento off-topic
                if hasattr(user_memory, 'lead_score'):
                    user_memory.lead_score = max(0, user_memory.lead_score - 2)
                
                memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
                
            debug_print(f"✅ Memoria actualizada con intento off-topic para usuario {user_id}", "_update_user_memory_with_off_topic_attempt")
            
        except Exception as e:
            debug_print(f"❌ Error actualizando memoria con off-topic: {e}", "_update_user_memory_with_off_topic_attempt")

    async def _update_user_memory_with_offensive_behavior(self, user_id: str, user_memory):
        """
        Actualiza la memoria del usuario con comportamiento ofensivo.
        
        Args:
            user_id: ID del usuario
            user_memory: Memoria actual del usuario
        """
        try:
            from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
            from memory.lead_memory import MemoryManager
            
            memory_manager = MemoryManager()
            memory_use_case = ManageUserMemoryUseCase(memory_manager)
            
            if user_memory:
                # Marcar comportamiento ofensivo
                if not hasattr(user_memory, 'pain_points'):
                    user_memory.pain_points = []
                
                user_memory.pain_points.append("offensive_behavior_detected")
                
                # Reducir significativamente el lead_score
                if hasattr(user_memory, 'lead_score'):
                    user_memory.lead_score = max(0, user_memory.lead_score - 10)
                
                # Marcar como lead problemático
                user_memory.stage = 'problematic_lead'
                
                memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
                
            debug_print(f"✅ Memoria actualizada con comportamiento ofensivo para usuario {user_id}", "_update_user_memory_with_offensive_behavior")
            
        except Exception as e:
            debug_print(f"❌ Error actualizando memoria con comportamiento ofensivo: {e}", "_update_user_memory_with_offensive_behavior")
    
    def _get_off_topic_casual_response(self, user_name: str, message_body: str, user_memory) -> str:
        """
        Maneja mensajes casuales fuera de contexto con redirección amable y humor.
        
        Args:
            user_name: Nombre del usuario
            message_body: Contenido del mensaje fuera de contexto
            user_memory: Memoria del usuario para tracking
            
        Returns:
            Respuesta con humor sutil redirigiendo al tema principal
        """
        try:
            # Importar templates después de asegurar que están disponibles
            from prompts.agent_prompts import BusinessPromptTemplates
            
            # Trackear mensaje fuera de contexto en memoria
            if user_memory:
                self._track_off_topic_attempt(user_memory, 'casual')
            
            # Usar template con humor para redirección
            response = BusinessPromptTemplates.off_topic_casual_redirect(
                name=user_name,
                topic_mentioned=message_body[:50] + "..." if len(message_body) > 50 else message_body
            )
            
            self.logger.info(f"✅ Respuesta casual fuera de contexto enviada para: {user_name}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error generando respuesta casual fuera de contexto: {e}")
            # Fallback directo
            name_greeting = f"{user_name}, " if user_name else ""
            return f"""{name_greeting}😊 Mi especialidad es la IA empresarial, no esas consultas generales.

¿Te gustaría que exploremos cómo la IA puede ayudar específicamente a tu empresa? Puedo contarte sobre nuestros cursos especializados para líderes PyME. 🚀"""
    
    def _get_off_topic_repeated_response(self, user_name: str) -> str:
        """
        Maneja intentos repetidos de desviar la conversación con mensaje predeterminado.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Respuesta predeterminada firme pero cortés
        """
        try:
            # Importar templates después de asegurar que están disponibles
            from prompts.agent_prompts import BusinessPromptTemplates
            
            # Usar template predeterminado para intentos repetidos
            response = BusinessPromptTemplates.off_topic_repeated_predefined(name=user_name)
            
            self.logger.info(f"✅ Respuesta predeterminada para intentos repetidos enviada para: {user_name}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error generando respuesta para intentos repetidos: {e}")
            # Fallback directo
            name_greeting = f"{user_name}, " if user_name else ""
            return f"""{name_greeting}Noto que estás preguntando sobre temas fuera de mi área de especialidad. 

Mi función principal no es responder ese tipo de preguntas, pero estaré encantada de continuar ofreciendo información sobre nuestros cursos de IA para empresas.

🎓 **¿Te interesa conocer cómo podemos ayudarte a:**
• Automatizar procesos empresariales
• Optimizar toma de decisiones con IA  
• Capacitar a tu equipo en herramientas de IA
• Implementar soluciones prácticas sin equipo técnico

¿Por cuál empezamos? 🚀"""
    
    def _get_offensive_message_response(self, user_name: str) -> str:
        """
        Maneja mensajes ofensivos con respuesta firme pero profesional.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Respuesta firme estableciendo límites profesionales
        """
        try:
            # Importar templates después de asegurar que están disponibles
            from prompts.agent_prompts import BusinessPromptTemplates
            
            # Usar template firme para mensajes ofensivos
            response = BusinessPromptTemplates.offensive_message_firm_response(name=user_name)
            
            self.logger.info(f"✅ Respuesta firme para mensaje ofensivo enviada para: {user_name}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error generando respuesta para mensaje ofensivo: {e}")
            # Fallback directo
            name_greeting = f"{user_name}, " if user_name else ""
            return f"""{name_greeting}Ese tipo de comportamiento no es adecuado en nuestra conversación profesional.

Mantengo un ambiente de respeto mutuo y mi función es únicamente proveer información relevante sobre nuestros cursos de IA empresarial.

Si estás interesado en conocer nuestras soluciones de IA para PyMEs, estaré disponible para ayudarte de manera profesional. 

¿Te gustaría que continuemos con información sobre los cursos? 🎓"""
    
    def _track_off_topic_attempt(self, user_memory, attempt_type: str) -> None:
        """
        Rastrea intentos de mensajes fuera de contexto en la memoria del usuario.
        
        Args:
            user_memory: Memoria del usuario
            attempt_type: Tipo de intento (casual, personal, unrelated)
        """
        try:
            if not hasattr(user_memory, 'off_topic_attempts'):
                user_memory.off_topic_attempts = []
            
            user_memory.off_topic_attempts.append({
                'type': attempt_type,
                'timestamp': datetime.now().isoformat(),
                'count': len(user_memory.off_topic_attempts) + 1
            })
            
            # Si hay demasiados intentos, marcar para escalación
            if len(user_memory.off_topic_attempts) >= 3:
                if not hasattr(user_memory, 'pain_points'):
                    user_memory.pain_points = []
                user_memory.pain_points.append("repeated_off_topic_attempts")
            
            debug_print(f"✅ Intento fuera de contexto trackeado: {attempt_type}", "_track_off_topic_attempt")
            
        except Exception as e:
            debug_print(f"❌ Error trackeando intento fuera de contexto: {e}", "_track_off_topic_attempt")
    
    def _determine_off_topic_escalation_level(self, user_memory) -> int:
        """
        Determina el nivel de escalación basado en el historial de intentos fuera de contexto.
        
        Args:
            user_memory: Memoria del usuario
            
        Returns:
            Nivel de escalación (0: primera vez, 1: pocas veces, 2: firme, 3+: predeterminado)
        """
        try:
            if not user_memory or not hasattr(user_memory, 'off_topic_attempts'):
                return 0
            
            attempts_count = len(user_memory.off_topic_attempts)
            
            # Determinar nivel basado en número de intentos
            if attempts_count == 0:
                return 0  # Primera vez
            elif attempts_count == 1:
                return 1  # Segunda vez - humor ligero
            elif attempts_count == 2:
                return 2  # Tercera vez - más firme
            else:
                return 3  # Cuarta vez o más - predeterminado
                
        except Exception as e:
            debug_print(f"❌ Error determinando nivel de escalación: {e}", "_determine_off_topic_escalation_level")
            return 0  # Default: primera vez
    
    def _get_off_topic_firm_redirect(self, user_name: str) -> str:
        """
        Respuesta más firme para el segundo nivel de escalación.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Respuesta firme pero aún amable redirigiendo al tema
        """
        name_greeting = f"{user_name}, " if user_name else ""
        
        return f"""{name_greeting}🎯 Noto que sigues preguntando sobre temas que no están relacionados con nuestros cursos de IA empresarial.

Mi especialidad es ayudar a líderes PyME como tú a implementar IA en sus empresas de manera práctica y efectiva.

**¿Te gustaría que enfoquemos la conversación en:**
• Cómo la IA puede resolver problemas específicos de tu empresa
• Qué curso se adapta mejor a tu situación actual
• Casos de éxito en tu industria
• ROI y beneficios concretos para tu PyME

¿Por dónde empezamos? 🚀"""
    
    def _create_loop_break_response(self) -> Dict[str, Any]:
        """Respuesta específica para romper bucles detectados."""
        return {
            'response_sent': True,
            'response_text': "🤖 Te conectaré con un asesor para ayudarte mejor.\n\n👨‍💼 Enviaré tu consulta a nuestro equipo especializado.",
            'processing_type': 'loop_break',
            'escalate_to_advisor': True,
            'should_stop_processing': True
        }
    
    async def _handle_progressive_content_flow(self, course_data: Dict[str, Any], course_name: str, user_memory) -> str:
        """
        Maneja el flujo progresivo de contenido del curso:
        1ra vez: Contenido básico + pregunta si quiere detalle
        2da vez: Temario detallado
        3ra vez: Recursos adicionales
        """
        try:
            # Obtener user_id desde user_memory o usar un ID temporal
            user_id = getattr(user_memory, 'user_id', 'unknown_user') if user_memory else 'unknown_user'
            
            # Verificar estado del flujo de contenido para este usuario
            if user_id not in self._content_flow_state:
                self._content_flow_state[user_id] = {
                    'syllabus_basic_provided': False,
                    'syllabus_detailed_provided': False
                }
            
            state = self._content_flow_state[user_id]
            syllabus_basic_provided = state['syllabus_basic_provided']
            syllabus_detailed_provided = state['syllabus_detailed_provided']
            
            session_count = course_data['session_count']
            
            if not syllabus_basic_provided:
                # Primera vez: contenido básico
                long_description = course_data.get('long_description', '').strip()
                
                if long_description:
                    # Limitar a ~300 caracteres para no exceder límite WhatsApp
                    if len(long_description) > 300:
                        long_description = long_description[:300] + "..."
                    
                    response = f"""🎓 **{course_name}**
📚 **Contenido** ({session_count} sesiones):

{long_description}

¿Te gustaría conocer el temario detallado de cada sesión?"""
                else:
                    # Fallback si no hay descripción larga
                    response = f"""🎓 **{course_name}**
📚 **Contenido**: {session_count} sesiones prácticas de IA aplicada

¿Te gustaría conocer el temario detallado?"""
                
                # Marcar como proporcionado en el estado interno
                self._content_flow_state[user_id]['syllabus_basic_provided'] = True
                
                return response
                
            elif not syllabus_detailed_provided:
                # Segunda vez: temario detallado
                detailed_response = f"""🎓 **{course_name}**
📋 **Temario Detallado** ({session_count} sesiones):

📚 **Sesión 1: Fundamentos de Prompting Profesional**
   • Técnicas avanzadas de prompting
   • Optimización de instrucciones para resultados precisos
   • Casos de uso empresariales específicos

📚 **Sesión 2: ChatGPT Avanzado para Productividad**
   • Automatización de tareas repetitivas
   • Integración con workflows existentes
   • Análisis y síntesis de información compleja

📚 **Sesión 3: Gemini y Herramientas de Google**
   • Capacidades multimodales (texto, imagen, código)
   • Integración con Google Workspace
   • Análisis avanzado de datos y documentos

📚 **Sesión 4: Implementación y Casos Reales**
   • Desarrollo de agentes GPT personalizados
   • Medición de ROI y resultados
   • Estrategias de adopción empresarial

¿Te interesa alguna sesión en particular o quieres información sobre inscripciones?"""
                
                # Marcar como proporcionado en el estado interno
                self._content_flow_state[user_id]['syllabus_detailed_provided'] = True
                
                return detailed_response
                
            else:
                # Tercera vez: recursos adicionales
                return """📋 Ya te compartí el temario completo del curso.

🎯 **¿Te interesa alguna de estas opciones?**

• 📄 Descargar PDF con información completa
• 📞 Hablar con un asesor especializado  
• 💰 Conocer opciones de inscripción y precios
• 🎁 Ver bonos y materiales incluidos

¿Cuál te interesa más?"""
                
        except Exception as e:
            self.logger.error(f"Error en flujo progresivo de contenido: {e}")
            # Fallback básico
            session_count = course_data.get('session_count', 4)
            return f"""🎓 **{course_name}**
📚 **Contenido**: {session_count} sesiones prácticas de IA aplicada

¿Te gustaría conocer el temario detallado?"""