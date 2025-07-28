"""
Caso de uso para gestionar el flujo completo de consentimiento de privacidad.
Incluye extracción de nombre de WhatsApp y personalización del nombre del usuario.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.templates.privacy_flow_templates import PrivacyFlowTemplates
from memory.lead_memory import LeadMemory

logger = logging.getLogger(__name__)

def debug_print(message: str, function_name: str = "", file_name: str = "privacy_flow_use_case.py"):
    """Print de debug visual para consola"""
    print(f"🔐 [{file_name}::{function_name}] {message}")


class PrivacyFlowUseCase:
    """
    Caso de uso para manejar el flujo completo de consentimiento de privacidad.
    
    Responsabilidades:
    - Detectar si un usuario necesita el flujo de privacidad
    - Extraer nombre de WhatsApp desde metadatos
    - Gestionar aceptación/rechazo de privacidad
    - Solicitar y validar nombre personalizado del usuario
    - Transicionar entre etapas del flujo
    """
    
    def __init__(
        self,
        memory_use_case: ManageUserMemoryUseCase,
        twilio_client: TwilioWhatsAppClient
    ):
        """
        Inicializa el caso de uso de flujo de privacidad.
        
        Args:
            memory_use_case: Caso de uso para gestionar memoria de usuario
            twilio_client: Cliente Twilio para envío de mensajes
        """
        self.memory_use_case = memory_use_case
        self.twilio_client = twilio_client
        self.templates = PrivacyFlowTemplates()
        self.logger = logging.getLogger(__name__)
    
    async def handle_privacy_flow(
        self,
        user_id: str,
        incoming_message: IncomingMessage
    ) -> Dict[str, Any]:
        """
        Maneja todo el flujo de privacidad según el estado actual del usuario.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje entrante
            
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            debug_print(f"🔐 INICIANDO FLUJO DE PRIVACIDAD\\n👤 Usuario: {user_id}\\n💬 Mensaje: '{incoming_message.body}'", "handle_privacy_flow")
            
            # Obtener memoria actual del usuario
            user_memory = self.memory_use_case.get_user_memory(user_id)
            debug_print(f"📋 Estado usuario - Stage: {user_memory.stage}, Privacidad: {user_memory.privacy_accepted}, Esperando: {user_memory.waiting_for_response}", "handle_privacy_flow")
            
            # Determinar qué hacer según el estado actual
            if user_memory.is_first_interaction() and user_memory.needs_privacy_flow():
                debug_print("🆕 Primera interacción detectada - Iniciando flujo de privacidad", "handle_privacy_flow")
                return await self._initiate_privacy_flow(user_id, incoming_message, user_memory)
            
            elif user_memory.waiting_for_response == "privacy_acceptance":
                debug_print("⏳ Esperando respuesta de consentimiento", "handle_privacy_flow")
                return await self._handle_privacy_response(user_id, incoming_message, user_memory)
            
            elif user_memory.waiting_for_response == "user_name":
                debug_print("⏳ Esperando nombre personalizado del usuario", "handle_privacy_flow")
                return await self._handle_name_response(user_id, incoming_message, user_memory)
            
            else:
                debug_print("❌ Usuario no está en flujo de privacidad", "handle_privacy_flow")
                return {
                    'success': False,
                    'in_privacy_flow': False,
                    'reason': 'User not in privacy flow',
                    'should_continue_normal_flow': True
                }
        
        except Exception as e:
            debug_print(f"💥 ERROR EN FLUJO DE PRIVACIDAD: {e}", "handle_privacy_flow")
            self.logger.error(f"Error in privacy flow: {e}")
            
            # Enviar mensaje de error y continuar
            error_response = "Disculpa, hubo un problema técnico. ¿Podrías intentar de nuevo?"
            await self._send_message(incoming_message.from_number, error_response)
            
            return {
                'success': False,
                'error': str(e),
                'in_privacy_flow': True,
                'message_sent': True
            }
    
    async def _initiate_privacy_flow(
        self,
        user_id: str,
        incoming_message: IncomingMessage,
        user_memory: LeadMemory
    ) -> Dict[str, Any]:
        """
        Inicia el flujo de consentimiento de privacidad.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje entrante
            user_memory: Memoria actual del usuario
            
        Returns:
            Resultado del procesamiento
        """
        try:
            debug_print("🚀 Iniciando flujo de consentimiento de privacidad", "_initiate_privacy_flow")
            
            # Actualizar memoria con el mensaje entrante
            self.memory_use_case.update_user_memory(user_id, incoming_message)
            
            # Extraer nombre de WhatsApp si está disponible
            whatsapp_name = self.templates.get_whatsapp_display_name(incoming_message.raw_data)
            debug_print(f"👤 Nombre extraído de WhatsApp: {whatsapp_name or 'No disponible'}", "_initiate_privacy_flow")
            
            # Iniciar flujo de privacidad en memoria
            updated_memory = self.memory_use_case.start_privacy_flow(user_id)
            debug_print(f"📝 Flujo iniciado - Stage: {updated_memory.stage}, Esperando: {updated_memory.waiting_for_response}", "_initiate_privacy_flow")
            
            # Generar mensaje de consentimiento
            privacy_message = self.templates.privacy_consent_request(whatsapp_name)
            debug_print(f"💬 Enviando mensaje de consentimiento ({len(privacy_message)} caracteres)", "_initiate_privacy_flow")
            
            # Enviar mensaje
            send_result = await self._send_message(incoming_message.from_number, privacy_message)
            
            if send_result:
                debug_print("✅ Mensaje de consentimiento enviado exitosamente", "_initiate_privacy_flow")
                return {
                    'success': True,
                    'in_privacy_flow': True,
                    'stage': 'privacy_consent_requested',
                    'whatsapp_name_extracted': whatsapp_name,
                    'message_sent': True,
                    'waiting_for': 'privacy_acceptance'
                }
            else:
                debug_print("❌ Error enviando mensaje de consentimiento", "_initiate_privacy_flow")
                return {
                    'success': False,
                    'in_privacy_flow': True,
                    'error': 'Failed to send privacy consent message'
                }
        
        except Exception as e:
            debug_print(f"💥 ERROR INICIANDO FLUJO: {e}", "_initiate_privacy_flow")
            raise
    
    async def _handle_privacy_response(
        self,
        user_id: str,
        incoming_message: IncomingMessage,
        user_memory: LeadMemory
    ) -> Dict[str, Any]:
        """
        Maneja la respuesta del usuario al consentimiento de privacidad.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje con la respuesta
            user_memory: Memoria actual del usuario
            
        Returns:
            Resultado del procesamiento
        """
        try:
            debug_print(f"📝 Procesando respuesta de privacidad: '{incoming_message.body}'", "_handle_privacy_response")
            
            # Actualizar memoria con el mensaje
            self.memory_use_case.update_user_memory(user_id, incoming_message)
            
            # Extraer respuesta de consentimiento
            consent_response = self.templates.extract_consent_response(incoming_message.body)
            debug_print(f"🔍 Respuesta interpretada: {consent_response}", "_handle_privacy_response")
            
            if consent_response is True:
                debug_print("✅ Usuario aceptó el consentimiento", "_handle_privacy_response")
                return await self._handle_privacy_accepted(user_id, incoming_message.from_number)
            
            elif consent_response is False:
                debug_print("❌ Usuario rechazó el consentimiento", "_handle_privacy_response")
                return await self._handle_privacy_rejected(user_id, incoming_message.from_number)
            
            else:
                debug_print("❓ Respuesta de consentimiento no clara", "_handle_privacy_response")
                return await self._handle_unclear_privacy_response(user_id, incoming_message.from_number)
        
        except Exception as e:
            debug_print(f"💥 ERROR PROCESANDO RESPUESTA: {e}", "_handle_privacy_response")
            raise
    
    async def _handle_privacy_accepted(
        self,
        user_id: str,
        user_number: str
    ) -> Dict[str, Any]:
        """
        Maneja cuando el usuario acepta el consentimiento de privacidad.
        
        Args:
            user_id: ID del usuario
            user_number: Número de WhatsApp del usuario
            
        Returns:
            Resultado del procesamiento
        """
        debug_print("🎉 Procesando aceptación de privacidad", "_handle_privacy_accepted")
        
        # Marcar privacidad como aceptada
        updated_memory = self.memory_use_case.accept_privacy(user_id)
        
        # Establecer que esperamos el nombre del usuario
        self.memory_use_case.set_waiting_for_response(user_id, "user_name")
        debug_print("⏳ Establecido esperando nombre del usuario", "_handle_privacy_accepted")
        
        # Enviar mensaje pidiendo el nombre
        name_request_message = self.templates.privacy_accepted_name_request()
        send_result = await self._send_message(user_number, name_request_message)
        
        if send_result:
            debug_print("✅ Mensaje de solicitud de nombre enviado", "_handle_privacy_accepted")
            return {
                'success': True,
                'in_privacy_flow': True,
                'stage': 'name_requested',
                'privacy_accepted': True,
                'message_sent': True,
                'waiting_for': 'user_name'
            }
        else:
            debug_print("❌ Error enviando solicitud de nombre", "_handle_privacy_accepted")
            return {
                'success': False,
                'in_privacy_flow': True,
                'error': 'Failed to send name request message'
            }
    
    async def _handle_privacy_rejected(
        self,
        user_id: str,
        user_number: str
    ) -> Dict[str, Any]:
        """
        Maneja cuando el usuario rechaza el consentimiento de privacidad.
        
        Args:
            user_id: ID del usuario
            user_number: Número de WhatsApp del usuario
            
        Returns:
            Resultado del procesamiento
        """
        debug_print("🚫 Procesando rechazo de privacidad", "_handle_privacy_rejected")
        
        # Actualizar memoria - usuario no acepta privacidad
        memory = self.memory_use_case.get_user_memory(user_id)
        memory.stage = "privacy_rejected"
        memory.current_flow = "none"
        memory.waiting_for_response = ""
        memory.privacy_requested = True
        memory.privacy_accepted = False
        self.memory_use_case.memory_manager.save_lead_memory(user_id, memory)
        
        # Enviar mensaje de despedida profesional
        rejection_message = self.templates.privacy_rejected()
        send_result = await self._send_message(user_number, rejection_message)
        
        if send_result:
            debug_print("✅ Mensaje de rechazo enviado", "_handle_privacy_rejected")
            return {
                'success': True,
                'in_privacy_flow': False,  # Flujo terminado
                'stage': 'privacy_rejected',
                'privacy_accepted': False,
                'message_sent': True,
                'flow_completed': True
            }
        else:
            debug_print("❌ Error enviando mensaje de rechazo", "_handle_privacy_rejected")
            return {
                'success': False,
                'in_privacy_flow': True,
                'error': 'Failed to send rejection message'
            }
    
    async def _handle_unclear_privacy_response(
        self,
        user_id: str,
        user_number: str
    ) -> Dict[str, Any]:
        """
        Maneja cuando la respuesta de privacidad no es clara.
        
        Args:
            user_id: ID del usuario
            user_number: Número de WhatsApp del usuario
            
        Returns:
            Resultado del procesamiento
        """
        debug_print("❓ Respuesta de privacidad no clara - pidiendo clarificación", "_handle_unclear_privacy_response")
        
        # Enviar mensaje pidiendo clarificación
        clarification_message = self.templates.invalid_privacy_response()
        send_result = await self._send_message(user_number, clarification_message)
        
        if send_result:
            debug_print("✅ Mensaje de clarificación enviado", "_handle_unclear_privacy_response")
            return {
                'success': True,
                'in_privacy_flow': True,
                'stage': 'privacy_clarification_requested',
                'message_sent': True,
                'waiting_for': 'privacy_acceptance'
            }
        else:
            debug_print("❌ Error enviando clarificación", "_handle_unclear_privacy_response")
            return {
                'success': False,
                'in_privacy_flow': True,
                'error': 'Failed to send clarification message'
            }
    
    async def _handle_name_response(
        self,
        user_id: str,
        incoming_message: IncomingMessage,
        user_memory: LeadMemory
    ) -> Dict[str, Any]:
        """
        Maneja la respuesta del usuario con su nombre preferido.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje con el nombre
            user_memory: Memoria actual del usuario
            
        Returns:
            Resultado del procesamiento
        """
        try:
            debug_print(f"👤 Procesando nombre del usuario: '{incoming_message.body}'", "_handle_name_response")
            
            # Actualizar memoria con el mensaje
            self.memory_use_case.update_user_memory(user_id, incoming_message)
            
            # Extraer y validar el nombre
            user_name = self.templates.extract_user_name(incoming_message.body)
            debug_print(f"🔍 Nombre extraído: {user_name or 'No válido'}", "_handle_name_response")
            
            if user_name:
                debug_print(f"✅ Nombre válido recibido: {user_name}", "_handle_name_response")
                return await self._complete_privacy_flow(user_id, incoming_message.from_number, user_name)
            else:
                debug_print("❌ Nombre no válido - pidiendo nombre nuevamente", "_handle_name_response")
                return await self._request_name_again(user_id, incoming_message.from_number)
        
        except Exception as e:
            debug_print(f"💥 ERROR PROCESANDO NOMBRE: {e}", "_handle_name_response")
            raise
    
    async def _complete_privacy_flow(
        self,
        user_id: str,
        user_number: str,
        user_name: str
    ) -> Dict[str, Any]:
        """
        Completa el flujo de privacidad con el nombre del usuario.
        
        Args:
            user_id: ID del usuario
            user_number: Número de WhatsApp del usuario
            user_name: Nombre validado del usuario
            
        Returns:
            Resultado del procesamiento
        """
        debug_print(f"🎉 Completando flujo de privacidad con nombre: {user_name}", "_complete_privacy_flow")
        
        # Actualizar nombre en memoria
        updated_memory = self.memory_use_case.update_user_name(user_id, user_name)
        
        # Iniciar flujo del agente de ventas
        self.memory_use_case.start_sales_agent_flow(user_id)
        debug_print("🤖 Flujo de agente de ventas iniciado", "_complete_privacy_flow")
        
        # Enviar mensaje de confirmación y bienvenida
        confirmation_message = self.templates.name_confirmed(user_name)
        send_result = await self._send_message(user_number, confirmation_message)
        
        if send_result:
            debug_print("✅ Flujo de privacidad completado exitosamente", "_complete_privacy_flow")
            return {
                'success': True,
                'in_privacy_flow': False,  # Flujo completado
                'stage': 'privacy_flow_completed',
                'user_name': user_name,
                'privacy_accepted': True,
                'ready_for_sales_agent': True,
                'message_sent': True,
                'flow_completed': True
            }
        else:
            debug_print("❌ Error enviando confirmación", "_complete_privacy_flow")
            return {
                'success': False,
                'in_privacy_flow': True,
                'error': 'Failed to send confirmation message'
            }
    
    async def _request_name_again(
        self,
        user_id: str,
        user_number: str
    ) -> Dict[str, Any]:
        """
        Solicita el nombre nuevamente cuando no es válido.
        
        Args:
            user_id: ID del usuario
            user_number: Número de WhatsApp del usuario
            
        Returns:
            Resultado del procesamiento
        """
        debug_print("🔄 Solicitando nombre nuevamente", "_request_name_again")
        
        # Enviar recordatorio para proporcionar nombre
        reminder_message = self.templates.name_request_reminder()
        send_result = await self._send_message(user_number, reminder_message)
        
        if send_result:
            debug_print("✅ Recordatorio de nombre enviado", "_request_name_again")
            return {
                'success': True,
                'in_privacy_flow': True,
                'stage': 'name_reminder_sent',
                'message_sent': True,
                'waiting_for': 'user_name'
            }
        else:
            debug_print("❌ Error enviando recordatorio", "_request_name_again")
            return {
                'success': False,
                'in_privacy_flow': True,
                'error': 'Failed to send name reminder'
            }
    
    async def _send_message(self, to_number: str, message_text: str) -> bool:
        """
        Envía un mensaje via Twilio.
        
        Args:
            to_number: Número de destino
            message_text: Texto del mensaje
            
        Returns:
            True si se envió exitosamente
        """
        try:
            outgoing_message = OutgoingMessage(
                to_number=to_number,
                body=message_text,
                message_type=MessageType.TEXT
            )
            
            result = await self.twilio_client.send_message(outgoing_message)
            return result.get('success', False)
        
        except Exception as e:
            debug_print(f"💥 ERROR ENVIANDO MENSAJE: {e}", "_send_message")
            self.logger.error(f"Error sending message: {e}")
            return False
            
    def should_handle_privacy_flow(self, user_memory: LeadMemory) -> bool:
        """
        Determina si un usuario debe ser manejado por el flujo de privacidad.
        
        Args:
            user_memory: Memoria del usuario
            
        Returns:
            True si debe manejar el flujo de privacidad
        """
        return (
            user_memory.is_first_interaction() and user_memory.needs_privacy_flow()
        ) or user_memory.waiting_for_response in ["privacy_acceptance", "user_name"]