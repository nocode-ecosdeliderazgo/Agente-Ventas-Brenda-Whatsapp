"""
Caso de uso para procesar mensajes entrantes de WhatsApp.
"""
import logging
from typing import Dict, Any

from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase

logger = logging.getLogger(__name__)


class ProcessIncomingMessageUseCase:
    """Caso de uso para procesar mensajes entrantes y generar respuestas."""
    
    def __init__(
        self, 
        twilio_client: TwilioWhatsAppClient, 
        memory_use_case: ManageUserMemoryUseCase,
        intelligent_response_use_case: GenerateIntelligentResponseUseCase = None
    ):
        """
        Inicializa el caso de uso.
        
        Args:
            twilio_client: Cliente de Twilio para envío de respuestas
            memory_use_case: Caso de uso para gestión de memoria
            intelligent_response_use_case: Caso de uso para respuestas inteligentes (opcional)
        """
        self.twilio_client = twilio_client
        self.memory_use_case = memory_use_case
        self.intelligent_response_use_case = intelligent_response_use_case
    
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
            user_id = incoming_message.from_phone.replace("+", "")
            
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
            
            # Usar respuesta inteligente si está disponible, sino usar respuesta básica
            if self.intelligent_response_use_case:
                # Procesamiento inteligente con OpenAI
                try:
                    intelligent_result = await self.intelligent_response_use_case.execute(
                        user_id, incoming_message
                    )
                    
                    response_text = intelligent_result.get('response_text', '')
                    response_sent = intelligent_result.get('response_sent', False)
                    response_sid = intelligent_result.get('response_sid')
                    
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
                        'intent_analysis': intelligent_result.get('intent_analysis', {}),
                        'extracted_info': intelligent_result.get('extracted_info', {})
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