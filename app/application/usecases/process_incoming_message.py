"""
Caso de uso para procesar mensajes entrantes de WhatsApp.
"""
import logging
from typing import Dict, Any

from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.application.usecases.tool_activation_use_case import ToolActivationUseCase
from app.application.usecases.course_announcement_use_case import CourseAnnouncementUseCase
from app.application.usecases.detect_ad_hashtags_use_case import DetectAdHashtagsUseCase
from app.application.usecases.process_ad_flow_use_case import ProcessAdFlowUseCase
from app.application.usecases.welcome_flow_use_case import WelcomeFlowUseCase

logger = logging.getLogger(__name__)


class ProcessIncomingMessageUseCase:
    """Caso de uso para procesar mensajes entrantes y generar respuestas."""
    
    def __init__(
        self, 
        twilio_client: TwilioWhatsAppClient, 
        memory_use_case: ManageUserMemoryUseCase,
        intelligent_response_use_case: GenerateIntelligentResponseUseCase = None,
        privacy_flow_use_case: PrivacyFlowUseCase = None,
        tool_activation_use_case: ToolActivationUseCase = None,
        course_announcement_use_case: CourseAnnouncementUseCase = None,
        detect_ad_hashtags_use_case: DetectAdHashtagsUseCase = None,
        process_ad_flow_use_case: ProcessAdFlowUseCase = None,
        welcome_flow_use_case: WelcomeFlowUseCase = None
    ):
        """
        Inicializa el caso de uso.
        
        Args:
            twilio_client: Cliente de Twilio para envío de respuestas
            memory_use_case: Caso de uso para gestión de memoria
            intelligent_response_use_case: Caso de uso para respuestas inteligentes (opcional)
            privacy_flow_use_case: Caso de uso para flujo de privacidad (opcional)
            tool_activation_use_case: Caso de uso para activación de herramientas (opcional)
            course_announcement_use_case: Caso de uso para anuncios de cursos (opcional)
        """
        self.twilio_client = twilio_client
        self.memory_use_case = memory_use_case
        self.intelligent_response_use_case = intelligent_response_use_case
        self.privacy_flow_use_case = privacy_flow_use_case
        self.tool_activation_use_case = tool_activation_use_case
        self.course_announcement_use_case = course_announcement_use_case
        self.detect_ad_hashtags_use_case = detect_ad_hashtags_use_case
        self.process_ad_flow_use_case = process_ad_flow_use_case
        self.welcome_flow_use_case = welcome_flow_use_case
    
    async def execute(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un mensaje entrante y envía una respuesta automática.
        
        Args:
            webhook_data: Datos del webhook de Twilio
            
        Returns:
            Dict con el resultado del procesamiento
        """
        try:
            # Crear entidad de mensaje entrante
            incoming_message = IncomingMessage.from_twilio_webhook(webhook_data)
            
            # Extraer user_id del número de teléfono (sin el prefijo whatsapp:)
            user_id = incoming_message.from_number.replace("+", "")
            
            logger.info(
                f"📨 Mensaje recibido de {incoming_message.from_number} (user_id: {user_id}): "
                f"'{incoming_message.body}'"
            )
            
            # Solo procesar mensajes de WhatsApp (ignorar SMS por ahora)
            if not incoming_message.is_whatsapp():
                logger.info("📱 Mensaje no es de WhatsApp, ignorando...")
                return {
                    'success': True,
                    'processed': False,
                    'reason': 'not_whatsapp'
                }
            
            # PRIORIDAD 1: Verificar si el usuario necesita flujo de privacidad
            if self.privacy_flow_use_case:
                try:
                    # Obtener memoria del usuario para verificar su estado
                    user_memory = self.memory_use_case.get_user_memory(user_id)
                    
                    # Verificar si debe manejar el flujo de privacidad
                    if self.privacy_flow_use_case.should_handle_privacy_flow(user_memory):
                        logger.info(f"🔐 Iniciando flujo de privacidad para usuario {user_id}")
                        
                        privacy_result = await self.privacy_flow_use_case.handle_privacy_flow(
                            user_id, incoming_message
                        )
                        
                        if privacy_result['success'] and privacy_result['in_privacy_flow']:
                            logger.info(f"✅ Flujo de privacidad procesado para {user_id}")
                            return {
                                'success': True,
                                'processed': True,
                                'incoming_message': {
                                    'from': incoming_message.from_number,
                                    'body': incoming_message.body,
                                    'message_sid': incoming_message.message_sid
                                },
                                'response_sent': privacy_result.get('message_sent', False),
                                'response_sid': None,  # Privacy flow doesn't return SID
                                'response_text': "Privacy flow handled",
                                'processing_type': 'privacy_flow',
                                'privacy_stage': privacy_result.get('stage', 'unknown'),
                                'privacy_flow_completed': privacy_result.get('flow_completed', False)
                            }
                        elif not privacy_result['in_privacy_flow'] and privacy_result.get('should_continue_normal_flow'):
                            logger.info(f"🔄 Usuario {user_id} no está en flujo privacidad, continuando procesamiento normal")
                            # Verificar si el flujo de privacidad activó automáticamente el flujo de anuncios
                            if privacy_result.get('ad_flow_activated') and privacy_result.get('ad_flow_result'):
                                logger.info(f"🎯 Flujo de anuncios ya activado automáticamente por flujo de privacidad")
                                ad_result = privacy_result['ad_flow_result']
                                return {
                                    'success': True,
                                    'processed': True,
                                    'incoming_message': {
                                        'from': incoming_message.from_number,
                                        'body': incoming_message.body,
                                        'message_sid': incoming_message.message_sid
                                    },
                                    'response_sent': True,
                                    'response_sid': None,
                                    'response_text': ad_result.get('response_text', ''),
                                    'processing_type': 'privacy_flow_to_ad_flow',
                                    'course_id': ad_result.get('course_id'),
                                    'campaign_name': ad_result.get('campaign_name'),
                                    'ad_flow_completed': True,
                                    'privacy_flow_completed': True
                                }
                            # Continuar con procesamiento normal
                        else:
                            logger.error(f"❌ Error en flujo de privacidad para {user_id}: {privacy_result}")
                            # Continuar con procesamiento normal como fallback
                            
                except Exception as e:
                    logger.error(f"❌ Error procesando flujo de privacidad: {e}")
                    # Continuar con procesamiento normal como fallback
            
            # PRIORIDAD 1.5: Verificar si es un anuncio con hashtags específicos
            # O si el usuario ya completó privacidad y tiene hashtags de anuncio
            if self.detect_ad_hashtags_use_case and self.process_ad_flow_use_case:
                try:
                    # Detectar hashtags de anuncios
                    hashtags_info = await self.detect_ad_hashtags_use_case.execute(incoming_message.body)
                    
                    # Verificar si es un anuncio directo O si el usuario ya completó privacidad y tiene hashtags
                    user_memory = self.memory_use_case.get_user_memory(user_id)
                    is_ad = hashtags_info.get('is_ad')
                    has_completed_privacy = (user_memory and 
                                          getattr(user_memory, 'privacy_accepted', False) and 
                                          getattr(user_memory, 'name', None))  # Usar 'name' en lugar de 'user_name'
                    
                    # Activar flujo de anuncios si:
                    # 1. Es un anuncio directo (usuario nuevo con hashtags)
                    # 2. Usuario existente con privacidad completa envía hashtags
                    if is_ad or (has_completed_privacy and hashtags_info.get('has_course_hashtag')):
                        logger.info(f"📢 Detectado anuncio con hashtags para {user_id}: {hashtags_info}")
                        logger.info(f"📊 Estado usuario - Privacidad: {has_completed_privacy}, Hashtags: {is_ad}")
                        
                        # Procesar flujo de anuncios
                        ad_flow_result = await self.process_ad_flow_use_case.execute(
                            webhook_data, 
                            {'id': user_id, 'first_name': getattr(user_memory, 'name', 'Usuario') if user_memory else 'Usuario'}, 
                            hashtags_info
                        )
                        
                        if ad_flow_result['success'] and ad_flow_result['ad_flow_completed']:
                            logger.info(f"✅ Flujo de anuncios procesado para {user_id}")
                            return {
                                'success': True,
                                'processed': True,
                                'incoming_message': {
                                    'from': incoming_message.from_number,
                                    'body': incoming_message.body,
                                    'message_sid': incoming_message.message_sid
                                },
                                'response_sent': True,
                                'response_sid': None,
                                'response_text': ad_flow_result.get('response_text', ''),
                                'processing_type': 'ad_flow',
                                'course_id': ad_flow_result.get('course_id'),
                                'campaign_name': hashtags_info.get('campaign_name'),
                                'ad_flow_completed': True
                            }
                        else:
                            logger.warning(f"⚠️ Error en flujo de anuncios: {ad_flow_result}")
                            # Continuar con procesamiento normal si falla el anuncio
                            
                except Exception as e:
                    logger.error(f"❌ Error procesando flujo de anuncios: {e}")
                    # Continuar con procesamiento normal como fallback
            
            # PRIORIDAD 1.6: Verificar si es un anuncio de curso específico
            if self.course_announcement_use_case:
                try:
                    if self.course_announcement_use_case.should_handle_course_announcement(incoming_message):
                        logger.info(f"📚 Detectado código de curso en mensaje de {user_id}")
                        
                        course_announcement_result = await self.course_announcement_use_case.handle_course_announcement(
                            user_id, incoming_message
                        )
                        
                        if course_announcement_result['success']:
                            logger.info(f"✅ Flujo de anuncio de curso procesado para {user_id}")
                            return {
                                'success': True,
                                'processed': True,
                                'incoming_message': {
                                    'from': incoming_message.from_number,
                                    'body': incoming_message.body,
                                    'message_sid': incoming_message.message_sid
                                },
                                'response_sent': course_announcement_result.get('response_sent', False),
                                'response_sid': course_announcement_result.get('response_sid'),
                                'response_text': course_announcement_result.get('response_text', ''),
                                'processing_type': 'course_announcement',
                                'course_code': course_announcement_result.get('course_code'),
                                'course_name': course_announcement_result.get('course_name'),
                                'additional_resources_sent': course_announcement_result.get('additional_resources_sent', {})
                            }
                        else:
                            logger.warning(f"⚠️ Error en flujo de anuncio: {course_announcement_result}")
                            # Continuar con procesamiento normal si falla el anuncio
                            
                except Exception as e:
                    logger.error(f"❌ Error procesando anuncio de curso: {e}")
                    # Continuar con procesamiento normal como fallback
            
            # PRIORIDAD 1.7: Verificar si es un mensaje genérico que debe activar el flujo de bienvenida
            if self.welcome_flow_use_case:
                try:
                    # Obtener memoria del usuario
                    user_memory = self.memory_use_case.get_user_memory(user_id)
                    
                    # Verificar si debe manejar el flujo de bienvenida
                    if self.welcome_flow_use_case.should_handle_welcome_flow(incoming_message, user_memory):
                        logger.info(f"🎯 Iniciando flujo de bienvenida genérico para usuario {user_id}")
                        
                        welcome_result = await self.welcome_flow_use_case.handle_welcome_flow(
                            user_id, incoming_message
                        )
                        
                        if welcome_result.get('success'):
                            logger.info(f"✅ Flujo de bienvenida procesado para {user_id}")
                            return {
                                'success': True,
                                'processed': True,
                                'incoming_message': {
                                    'from': incoming_message.from_number,
                                    'body': incoming_message.body,
                                    'message_sid': incoming_message.message_sid
                                },
                                'response_sent': True,
                                'response_sid': welcome_result.get('response_sid'),
                                'response_text': welcome_result.get('response_text', ''),
                                'processing_type': 'welcome_flow',
                                'welcome_flow_completed': welcome_result.get('welcome_flow_completed', False),
                                'course_selected': welcome_result.get('course_selected', False),
                                'ready_for_intelligent_agent': welcome_result.get('ready_for_intelligent_agent', False)
                            }
                        else:
                            logger.error(f"❌ Error en flujo de bienvenida: {welcome_result}")
                            # Continuar con procesamiento normal
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando flujo de bienvenida: {e}")
                    # Continuar con procesamiento normal
            
            # PRIORIDAD 2: Usar respuesta inteligente si está disponible
            if self.intelligent_response_use_case:
                # Procesamiento inteligente con OpenAI
                try:
                    intelligent_result = await self.intelligent_response_use_case.execute(
                        user_id, incoming_message
                    )
                    
                    response_text = intelligent_result.get('response_text', '')
                    response_sent = intelligent_result.get('response_sent', False)
                    response_sid = intelligent_result.get('response_sid')
                    intent_analysis = intelligent_result.get('intent_analysis', {})
                    
                    # PRIORIDAD 2.1: Activar herramientas de conversión si está disponible
                    tool_results = []
                    if self.tool_activation_use_case and intent_analysis:
                        try:
                            user_memory = self.memory_use_case.get_user_memory(user_id)
                            
                            # Verificar si se deben activar herramientas
                            if self.tool_activation_use_case.should_activate_tools(intent_analysis):
                                logger.info(f"🛠️ Activando herramientas de conversión para {user_id}")
                                
                                tool_results = await self.tool_activation_use_case.activate_tools_by_intent(
                                    intent_analysis=intent_analysis,
                                    user_id=user_id,
                                    incoming_message=incoming_message,
                                    user_memory=user_memory
                                )
                                
                                logger.info(f"✅ {len(tool_results)} herramientas activadas")
                        except Exception as e:
                            logger.error(f"❌ Error activando herramientas: {e}")
                            # Continuar con respuesta normal si fallan las herramientas
                    
                    logger.info(f"🤖 Respuesta inteligente generada para {user_id}")
                    
                    return {
                        'success': True,
                        'processed': True,
                        'incoming_message': {
                            'from': incoming_message.from_number,
                            'body': incoming_message.body,
                            'message_sid': incoming_message.message_sid
                        },
                        'response_sent': response_sent,
                        'response_sid': response_sid,
                        'response_text': response_text,
                        'processing_type': 'intelligent',
                        'intent_analysis': intent_analysis,
                        'extracted_info': intelligent_result.get('extracted_info', {}),
                        'tool_results': tool_results,
                        'tools_activated': len(tool_results) > 0
                    }
                    
                except Exception as e:
                    logger.error(f"❌ Error en respuesta inteligente, usando fallback: {e}")
                    # Continuar con respuesta básica si falla la inteligente
            
            # Fallback: Procesamiento básico con memoria
            try:
                user_memory = self.memory_use_case.update_user_memory(
                    user_id=user_id,
                    message=incoming_message
                )
                logger.info(f"🧠 Memoria actualizada para usuario {user_id}")
            except Exception as e:
                logger.error(f"❌ Error actualizando memoria: {e}")
                # Continuar procesamiento aunque falle la memoria
                user_memory = None
            
            # Generar respuesta básica (con contexto de memoria)
            response_text = self._generate_auto_response(incoming_message, user_memory)
            
            # Crear mensaje de respuesta
            response_message = OutgoingMessage(
                to_number=incoming_message.from_number,
                body=response_text,
                message_type=MessageType.TEXT
            )
            
            # Enviar respuesta
            send_result = await self.twilio_client.send_message(response_message)
            
            if send_result['success']:
                logger.info(
                    f"✅ Respuesta enviada a {incoming_message.from_number}. "
                    f"SID: {send_result['message_sid']}"
                )
            else:
                logger.error(
                    f"❌ Error enviando respuesta: {send_result['error']}"
                )
            
            return {
                'success': True,
                'processed': True,
                'incoming_message': {
                    'from': incoming_message.from_number,
                    'body': incoming_message.body,
                    'message_sid': incoming_message.message_sid
                },
                'response_sent': send_result['success'],
                'response_sid': send_result.get('message_sid'),
                'response_text': response_text,
                'processing_type': 'basic'
            }
            
        except Exception as e:
            logger.error(f"💥 Error procesando mensaje entrante: {e}")
            return {
                'success': False,
                'processed': False,
                'error': str(e)
            }
    
    def _generate_auto_response(self, incoming_message: IncomingMessage, user_memory=None) -> str:
        """
        Genera una respuesta automática para cualquier mensaje.
        
        Args:
            incoming_message: Mensaje entrante
            user_memory: Memoria del usuario (opcional)
            
        Returns:
            Texto de respuesta
        """
        # Respuesta básica con contexto de memoria si está disponible
        if user_memory and user_memory.name:
            # Si conocemos el nombre del usuario, personalizar saludo
            if user_memory.interaction_count <= 2:
                return f"¡Hola {user_memory.name}! 👋 Gracias por escribirnos a Aprenda y Aplique IA. ¿En qué puedo ayudarte hoy?"
            else:
                return f"Hola de nuevo {user_memory.name} 😊 ¿Cómo puedo asistirte?"
        elif user_memory and user_memory.interaction_count == 1:
            # Primera interacción, solicitar nombre
            return "¡Hola! 👋 Bienvenido/a a Aprenda y Aplique IA. Para brindarte una mejor atención, ¿me podrías decir tu nombre?"
        else:
            # Respuesta genérica para usuarios sin memoria o nombre
            return "¡Hola! 👋 Gracias por contactar a Aprenda y Aplique IA. ¿En qué puedo ayudarte?"
        
        # En el futuro aquí podemos agregar lógica más sofisticada:
        # - Análisis de intención con OpenAI
        # - Respuestas contextuales basadas en el historial
        # - Integración con las 35+ herramientas del legacy
        # - Sistema de activación inteligente de herramientas