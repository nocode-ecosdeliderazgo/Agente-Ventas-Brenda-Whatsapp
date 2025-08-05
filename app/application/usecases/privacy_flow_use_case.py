"""
Caso de uso para gestionar el flujo completo de consentimiento de privacidad.
Incluye extracción de nombre de WhatsApp y personalización del nombre del usuario.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from app.application.usecases.course_announcement_use_case import CourseAnnouncementUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.templates.privacy_flow_templates import PrivacyFlowTemplates
from app.config.campaign_config import (
    COURSE_HASHTAG_MAPPING, 
    get_course_id_from_hashtag, 
    is_course_hashtag
)
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
        twilio_client: TwilioWhatsAppClient,
        course_announcement_use_case: Optional[CourseAnnouncementUseCase] = None
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
        self.course_announcement_use_case = course_announcement_use_case
    
    async def handle_privacy_flow(
        self,
        user_id: str,
        incoming_message: IncomingMessage
    ) -> Dict[str, Any]:
        """
        Maneja el flujo de privacidad para un usuario.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje entrante del usuario
            
        Returns:
            Resultado del procesamiento del flujo de privacidad
        """
        debug_print(f"🔐 INICIANDO FLUJO DE PRIVACIDAD\n👤 Usuario: {user_id}\n💬 Mensaje: '{incoming_message.body}'")
        
        try:
            # Obtener memoria del usuario
            user_memory = self.memory_use_case.get_user_memory(user_id)
            
            debug_print(f"📋 Estado usuario - Stage: {user_memory.stage}, Privacidad: {user_memory.privacy_accepted}, Esperando: {user_memory.waiting_for_response}")
            
            # Si es la primera interacción, iniciar flujo de privacidad
            if user_memory.stage == "first_contact":
                debug_print("🆕 Primera interacción detectada - Iniciando flujo de privacidad")
                return await self._initiate_privacy_flow(user_id, incoming_message, user_memory)
            
            # Si está esperando respuesta de consentimiento de privacidad
            elif user_memory.waiting_for_response == "privacy_acceptance":
                debug_print("⏳ Esperando respuesta de consentimiento - IGNORANDO (hardcodeado)")
                # 🆕 IGNORAR RESPUESTA DE PRIVACIDAD - YA ESTÁ ACEPTADA AUTOMÁTICAMENTE
                # Simplemente continuar con el flujo normal
                return {
                    'success': True,
                    'in_privacy_flow': False,
                    'should_continue_normal_flow': True,
                    'stage': 'privacy_flow_completed'
                }
            
            # Si está esperando nombre del usuario
            elif user_memory.waiting_for_response == "user_name":
                debug_print("⏳ Esperando nombre personalizado del usuario")
                return await self._handle_name_response(user_id, incoming_message, user_memory)
            
            # Si está esperando rol/cargo del usuario
            elif user_memory.waiting_for_response == "user_role":
                debug_print("⏳ Esperando rol/cargo del usuario")
                return await self._handle_role_response(user_id, incoming_message, user_memory)
            
            # Si ya completó el flujo de privacidad
            elif user_memory.stage == "privacy_flow_completed":
                debug_print("✅ Usuario ya completó flujo de privacidad")
                return {
                    'success': True,
                    'in_privacy_flow': False,
                    'should_continue_normal_flow': True,
                    'stage': 'privacy_flow_completed'
                }
            
            # Caso por defecto - no está en flujo de privacidad
            else:
                debug_print("ℹ️ Usuario no está en flujo de privacidad")
                return {
                    'success': True,
                    'in_privacy_flow': False,
                    'should_continue_normal_flow': True,
                    'stage': user_memory.stage
                }
                
        except Exception as e:
            debug_print(f"💥 ERROR EN FLUJO DE PRIVACIDAD: {e}")
            raise
    
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
        debug_print("🚀 Iniciando flujo de consentimiento de privacidad", "_initiate_privacy_flow")
        
        try:
            # Extraer nombre de WhatsApp si está disponible
            whatsapp_name = incoming_message.from_number.replace("+", "").replace("whatsapp:", "")
            debug_print(f"👤 Nombre extraído de WhatsApp: {whatsapp_name}", "_initiate_privacy_flow")
            
            # Almacenar mensaje original en memoria para verificar hashtags después
            user_memory.original_message_body = incoming_message.body
            user_memory.original_message_sid = incoming_message.message_sid
            
            # 🆕 EXTRAER Y MAPEAR HASHTAGS INMEDIATAMENTE desde el primer mensaje
            hashtags_detected = self._extract_and_map_hashtags(incoming_message.body, user_memory)
            if hashtags_detected:
                debug_print(f"📋 Hashtags detectados y mapeados: {hashtags_detected}", "_initiate_privacy_flow")
            
            self.memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
            
            # 🆕 HARDCODEAR ACEPTACIÓN DE PRIVACIDAD - NO ESPERAR RESPUESTA
            debug_print("🔐 ACEPTACIÓN AUTOMÁTICA DE PRIVACIDAD - Hardcodeada", "_initiate_privacy_flow")
            
            # Marcar privacidad como aceptada automáticamente
            updated_memory = self.memory_use_case.accept_privacy(user_id)
            updated_memory.stage = "privacy_flow"
            
            # Establecer que esperamos el nombre del usuario
            self.memory_use_case.set_waiting_for_response(user_id, "user_name")
            debug_print("⏳ Establecido esperando nombre del usuario", "_initiate_privacy_flow")
            
            # Enviar mensaje de consentimiento
            consent_message = self.templates.privacy_consent_request(whatsapp_name)
            send_result = await self._send_message(incoming_message.from_number, consent_message)
            
            if send_result:
                debug_print("✅ Mensaje de consentimiento enviado exitosamente", "_initiate_privacy_flow")
                
                # 🆕 ENVIAR INMEDIATAMENTE EL MENSAJE PIDIENDO EL NOMBRE
                name_request_message = self.templates.privacy_accepted_name_request()
                name_send_result = await self._send_message(incoming_message.from_number, name_request_message)
                
                if name_send_result:
                    debug_print("✅ Mensaje de solicitud de nombre enviado automáticamente", "_initiate_privacy_flow")
                    return {
                        'success': True,
                        'in_privacy_flow': True,
                        'stage': 'name_requested',
                        'privacy_accepted': True,
                        'message_sent': True,
                        'waiting_for': 'user_name'
                    }
                else:
                    debug_print("❌ Error enviando solicitud de nombre", "_initiate_privacy_flow")
                    return {
                        'success': False,
                        'in_privacy_flow': True,
                        'error': 'Failed to send name request message'
                    }
            else:
                debug_print("❌ Error enviando mensaje de consentimiento", "_initiate_privacy_flow")
                return {
                    'success': False,
                    'in_privacy_flow': True,
                    'error': 'Failed to send consent message'
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
                
                # 🆕 PASO 1: Actualizar el nombre en la memoria
                self.memory_use_case.update_user_name(user_id, user_name)
                debug_print(f"💾 Nombre '{user_name}' guardado en memoria", "_handle_name_response")

                # 🆕 PASO 2: Activar el anuncio del curso automáticamente
                debug_print("🚀 Activando flujo de anuncio de curso...", "_handle_name_response")
                
                if self.course_announcement_use_case:
                    # Crear un "mensaje falso" para activar el anuncio por defecto
                    fake_message_for_announcement = IncomingMessage(
                        from_number=incoming_message.from_number,
                        body="#Experto_IA_GPT_Gemini",  # Hashtag por defecto
                        message_sid=incoming_message.message_sid,
                        to_number=incoming_message.to_number,
                        timestamp=datetime.now(),
                        raw_data={}
                    )
                    
                    announcement_result = await self.course_announcement_use_case.handle_course_announcement(
                        user_id, fake_message_for_announcement
                    )
                    
                    if announcement_result.get('success'):
                        debug_print("✅ Anuncio de curso enviado exitosamente", "_handle_name_response")
                        # Ahora, después del anuncio, pedimos el rol
                        return await self._request_user_role_after_announcement(user_id, incoming_message.from_number, user_name)
                    else:
                        debug_print("⚠️ Falló el envío del anuncio, pidiendo rol de todas formas", "_handle_name_response")
                        return await self._request_user_role_after_announcement(user_id, incoming_message.from_number, user_name)
                else:
                    debug_print("❌ CourseAnnouncementUseCase no disponible, saltando al siguiente paso.", "_handle_name_response")
                    return await self._request_user_role_after_announcement(user_id, incoming_message.from_number, user_name)
            else:
                debug_print("❌ Nombre no válido - pidiendo nombre nuevamente", "_handle_name_response")
                return await self._request_name_again(user_id, incoming_message.from_number)
        
        except Exception as e:
            debug_print(f"💥 ERROR PROCESANDO NOMBRE: {e}", "_handle_name_response")
            raise
    
    
    async def _request_user_role_after_announcement(
        self,
        user_id: str,
        user_number: str,
        user_name: str
    ) -> Dict[str, Any]:
        """
        Después de enviar el anuncio, solicita el rol del usuario.
        """
        debug_print(f"👋 Solicitando rol para {user_name} después del anuncio.", "_request_user_role_after_announcement")
        
        # Configurar para esperar respuesta del rol
        self.memory_use_case.set_waiting_for_response(user_id, "user_role")
        debug_print("⏳ Configurado para esperar rol del usuario", "_request_user_role_after_announcement")
        
        # Enviar mensaje de confirmación y solicitud de rol
        confirmation_message = self.templates.name_confirmed(user_name)
        send_result = await self._send_message(user_number, confirmation_message)
        
        if send_result:
            debug_print("✅ Mensaje de solicitud de rol enviado", "_request_user_role_after_announcement")
            return {
                'success': True,
                'in_privacy_flow': True,
                'stage': 'waiting_for_role',
                'user_name': user_name,
                'privacy_accepted': True,
                'waiting_for_response': 'user_role',
                'message_sent': True
            }
        else:
            debug_print("❌ Error enviando solicitud de rol", "_request_user_role_after_announcement")
            return {
                'success': False,
                'in_privacy_flow': True,
                'error': 'Failed to send role request message'
            }

    async def _handle_role_response(
        self,
        user_id: str,
        incoming_message: IncomingMessage,
        user_memory: LeadMemory
    ) -> Dict[str, Any]:
        """
        Maneja la respuesta del usuario con su rol/cargo.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje con el rol
            user_memory: Memoria actual del usuario
            
        Returns:
            Resultado del procesamiento
        """
        try:
            debug_print(f"👔 Procesando rol del usuario: '{incoming_message.body}'", "_handle_role_response")
            
            # Actualizar memoria con el mensaje
            self.memory_use_case.update_user_memory(user_id, incoming_message)
            
            # Extraer y validar el rol
            user_role = self._extract_user_role(incoming_message.body)
            debug_print(f"🔍 Rol extraído: {user_role or 'No válido'}", "_handle_role_response")
            
            if user_role:
                debug_print(f"✅ Rol válido recibido: {user_role}", "_handle_role_response")
                
                # Guardar el rol en memoria
                self.memory_use_case.update_user_role(user_id, user_role)
                debug_print(f"💾 Rol '{user_role}' guardado en memoria", "_handle_role_response")

                # --- ¡CORRECCIÓN CLAVE! ---
                # Finaliza el flujo de privacidad aquí y delega al procesador principal
                debug_print("✅ Rol guardado. Finalizando flujo de privacidad y activando agente.", "_handle_role_response")
                self.memory_use_case.complete_privacy_flow(user_id) # Usar el método centralizado
                
                return {
                    'success': True,
                    'in_privacy_flow': False,
                    'should_continue_normal_flow': True, # Indica al procesador que continúe
                    'stage': 'privacy_flow_completed',
                    'message_sent': False # No enviamos mensaje aquí
                }
                # --- FIN DE LA CORRECIÓN ---
            else:
                debug_print("❌ Rol no válido - pidiendo rol nuevamente", "_handle_role_response")
                return await self._request_role_again(user_id, incoming_message.from_number)
        
        except Exception as e:
            debug_print(f"💥 ERROR PROCESANDO ROL: {e}", "_handle_role_response")
            raise
    
    async def _complete_privacy_flow(
        self,
        user_id: str,
        user_number: str,
        user_name: str
    ) -> Dict[str, Any]:
        """
        Completa el flujo de privacidad con el nombre del usuario y solicita el rol.
        
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
        
        # Configurar para esperar respuesta del rol
        self.memory_use_case.set_waiting_for_response(user_id, "user_role")
        debug_print("⏳ Configurado para esperar rol del usuario", "_complete_privacy_flow")
        
        # Enviar mensaje de confirmación y solicitud de rol
        confirmation_message = self.templates.name_confirmed(user_name)
        send_result = await self._send_message(user_number, confirmation_message)
        
        if send_result:
            debug_print("✅ Mensaje de confirmación enviado, esperando rol", "_complete_privacy_flow")
            return {
                'success': True,
                'in_privacy_flow': True,  # Aún en flujo esperando rol
                'stage': 'waiting_for_role',
                'user_name': user_name,
                'privacy_accepted': True,
                'waiting_for_response': 'user_role',
                'message_sent': True
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
    
    def _extract_user_role(self, message_text: str) -> Optional[str]:
        """
        Extrae el rol/cargo del usuario del mensaje con detección inteligente de roles relacionados.
        
        Args:
            message_text: Texto del mensaje del usuario
            
        Returns:
            Rol extraído o None si no es válido
        """
        try:
            # Limpiar y normalizar el texto
            text = message_text.strip().lower()
            
            # Mapeo inteligente de roles con sinónimos y términos relacionados
            role_mapping = {
                # Marketing Digital y términos relacionados
                'Marketing Digital': [
                    'marketing', 'marketing digital', 'mercadotecnia', 'publicidad', 'comunicación',
                    'community manager', 'social media', 'content manager', 'brand manager',
                    'digital marketing', 'growth marketing', 'performance marketing', 'sem', 'seo',
                    'creative director', 'diseño gráfico', 'copywriter', 'content creator',
                    'agencia', 'medios digitales', 'campañas', 'branding'
                ],
                
                # Ventas y términos relacionados
                'Ventas': [
                    'ventas', 'vendedor', 'vendedora', 'sales', 'comercial', 'business development',
                    'account manager', 'key account', 'inside sales', 'field sales', 'compras',
                    'procurement', 'adquisiciones', 'buyer', 'purchasing', 'negociación',
                    'b2b', 'b2c', 'consultoría comercial', 'representante comercial'
                ],
                
                # Operaciones y términos relacionados
                'Operaciones': [
                    'operaciones', 'operations', 'producción', 'manufactura', 'plant manager',
                    'supervisor', 'jefe de planta', 'logística', 'supply chain', 'cadena suministro',
                    'almacén', 'inventarios', 'quality manager', 'calidad', 'procesos',
                    'industrial', 'fábrica', 'facility manager', 'lean', 'six sigma'
                ],
                
                # Recursos Humanos y términos relacionados  
                'Recursos Humanos': [
                    'recursos humanos', 'rh', 'hr', 'human resources', 'people operations',
                    'talent acquisition', 'reclutamiento', 'selección', 'capacitación',
                    'training', 'desarrollo organizacional', 'culture', 'nómina', 'payroll',
                    'compensaciones', 'beneficios', 'employee experience', 'people analytics'
                ],
                
                # CEO/Founder y términos relacionados
                'CEO/Founder': [
                    'ceo', 'chief executive', 'director general', 'gerente general', 'founder',
                    'fundador', 'cofundador', 'co-founder', 'presidente', 'dueño', 'propietario',
                    'empresario', 'emprendedor', 'managing director', 'executive director',
                    'country manager', 'regional director'
                ],
                
                # Innovación/Transformación Digital y términos relacionados
                'Innovación/Transformación Digital': [
                    'innovación', 'innovation', 'transformación digital', 'digital transformation',
                    'cto', 'chief technology', 'it manager', 'sistemas', 'tecnología',
                    'digital', 'tech lead', 'product manager', 'project manager',
                    'scrum master', 'agile coach', 'digital strategy', 'startup'
                ],
                
                # Análisis de Datos y términos relacionados
                'Análisis de Datos': [
                    'análisis de datos', 'data analysis', 'data analytics', 'data scientist',
                    'data analyst', 'business intelligence', 'bi', 'analytics', 'reporting',
                    'insights', 'métricas', 'kpi', 'dashboard', 'tableau', 'power bi',
                    'sql', 'python', 'estadística', 'machine learning', 'data mining'
                ]
            }
            
            # Buscar coincidencias inteligentes
            for target_role, keywords in role_mapping.items():
                for keyword in keywords:
                    if keyword in text:
                        debug_print(f"✅ Rol detectado: '{target_role}' por keyword: '{keyword}'", "_extract_user_role")
                        return target_role
            
            # Si no hay coincidencia exacta, devolver el texto original capitalizado si es válido
            if len(text) > 2:  # Al menos 3 caracteres
                capitalized_role = message_text.strip().title()
                debug_print(f"🔄 Rol genérico detectado: '{capitalized_role}'", "_extract_user_role")
                return capitalized_role
            
            return None
            
        except Exception as e:
            debug_print(f"💥 ERROR EXTRAYENDO ROL: {e}", "_extract_user_role")
            return None
    
    async def _complete_role_collection(
        self,
        user_id: str,
        user_number: str,
        user_role: str,
        original_message: Optional[IncomingMessage] = None
    ) -> Dict[str, Any]:
        """
        Completa la recolección del rol y inicia el flujo de ventas.
        
        Args:
            user_id: ID del usuario
            user_number: Número de WhatsApp del usuario
            user_role: Rol validado del usuario
            original_message: Mensaje original que inició el flujo (opcional)
            
        Returns:
            Resultado del procesamiento
        """
        debug_print(f"🎉 Completando recolección de rol: {user_role}", "_complete_role_collection")
        
        # Actualizar rol en memoria
        updated_memory = self.memory_use_case.update_user_role(user_id, user_role)
        
        # Completar flujo de privacidad
        updated_memory = self.memory_use_case.complete_privacy_flow(user_id)
        debug_print("✅ Flujo de privacidad completado", "_complete_role_collection")
        
        # Iniciar flujo del agente de ventas
        self.memory_use_case.start_sales_agent_flow(user_id)
        debug_print("🤖 Flujo de agente de ventas iniciado", "_complete_role_collection")
        
        # Verificar si el mensaje original tenía códigos de curso específicos
        course_announcement_activated = False
        if original_message:
            try:
                from app.application.usecases.course_announcement_use_case import CourseAnnouncementUseCase
                from app.application.usecases.query_course_information import QueryCourseInformationUseCase
                
                # Crear instancia temporal para verificar códigos de curso
                course_query_use_case = QueryCourseInformationUseCase()
                course_announcement = CourseAnnouncementUseCase(
                    course_query_use_case=course_query_use_case,
                    memory_use_case=self.memory_use_case,
                    twilio_client=self.twilio_client
                )
                
                # Verificar si el mensaje original contiene códigos de curso
                if course_announcement.should_handle_course_announcement(original_message):
                    debug_print(f"🎯 Detectado código de curso en mensaje original: {original_message.body}", "_complete_role_collection")
                    
                    # Procesar flujo de anuncio de curso automáticamente
                    course_announcement_result = await course_announcement.handle_course_announcement(
                        user_id, original_message
                    )
                    
                    if course_announcement_result['success']:
                        debug_print("✅ Flujo de anuncio de curso activado automáticamente después de privacidad", "_complete_role_collection")
                        course_announcement_activated = True
                        return {
                            'success': True,
                            'in_privacy_flow': False,
                            'stage': 'privacy_flow_completed',
                            'user_role': user_role,
                            'privacy_accepted': True,
                            'ready_for_sales_agent': True,
                            'message_sent': True,
                            'flow_completed': True,
                            'course_announcement_activated': True,
                            'course_announcement_result': course_announcement_result,
                            'should_continue_normal_flow': False  # NO continuar con procesamiento normal
                        }
                    else:
                        debug_print(f"⚠️ Error activando flujo de anuncio de curso: {course_announcement_result}", "_complete_role_collection")
                        
            except Exception as e:
                debug_print(f"❌ Error verificando códigos de curso: {e}", "_complete_role_collection")
        
        # Si no se activó el flujo de anuncio de curso, activar automáticamente el flujo de bienvenida
        if not course_announcement_activated:
            debug_print("✅ Flujo de privacidad completado, activando automáticamente flujo de bienvenida", "_complete_role_collection")
            return {
                'success': True,
                'in_privacy_flow': False,  # Flujo completado
                'stage': 'privacy_flow_completed',
                'user_role': user_role,
                'privacy_accepted': True,
                'ready_for_sales_agent': True,
                'message_sent': False,  # NO enviar mensaje aquí
                'flow_completed': True,
                'should_continue_normal_flow': True,  # Continuar con procesamiento normal
                'trigger_welcome_flow': True  # TRIGGER para activar flujo de bienvenida automáticamente
            }
        
        # Return por defecto (no debería llegar aquí)
        return {
            'success': True,
            'in_privacy_flow': False,
            'stage': 'privacy_flow_completed',
            'user_role': user_role,
            'privacy_accepted': True,
            'ready_for_sales_agent': True,
            'message_sent': False,
            'flow_completed': True
        }
    
    async def _request_role_again(
        self,
        user_id: str,
        user_number: str
    ) -> Dict[str, Any]:
        """
        Solicita el rol nuevamente cuando no es válido.
        
        Args:
            user_id: ID del usuario
            user_number: Número de WhatsApp del usuario
            
        Returns:
            Resultado del procesamiento
        """
        try:
            debug_print("🔄 Solicitando rol nuevamente", "_request_role_again")
            
            # Enviar mensaje de recordatorio
            reminder_message = """Por favor, ¿podrías decirme en qué área de tu empresa te desempeñas?

Esto me ayudará a recomendarte las mejores estrategias de IA para tu sector específico. 😊"""
            
            send_result = await self._send_message(user_number, reminder_message)
            
            if send_result:
                return {
                    'success': True,
                    'in_privacy_flow': True,
                    'waiting_for_response': 'user_role',
                    'message_sent': True
                }
            else:
                return {
                    'success': False,
                    'in_privacy_flow': True,
                    'error': 'Failed to send role reminder'
                }
        
        except Exception as e:
            debug_print(f"💥 ERROR SOLICITANDO ROL: {e}", "_request_role_again")
            raise
    
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
            
            # Determinar tipo de mensaje para privacy flow
            if len(message_text) < 100:
                # Mensajes cortos del privacy flow
                result = await self.twilio_client.send_quick_response(to_number, message_text)
            else:
                # Mensajes largos (explicaciones de privacidad)
                result = await self.twilio_client.send_text_with_typing(to_number, message_text)
            
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
        # Si ya completó el flujo de privacidad, no debe manejarlo
        if user_memory.privacy_accepted and user_memory.name and user_memory.role:
            return False
            
        return (
            user_memory.is_first_interaction() and user_memory.needs_privacy_flow()
        ) or user_memory.waiting_for_response in ["privacy_acceptance", "user_name", "user_role"]
    
    def _extract_and_map_hashtags(self, message_body: str, user_memory: LeadMemory) -> Dict[str, Any]:
        """
        Extrae hashtags del mensaje y los mapea a course_ids usando el sistema centralizado.
        Guarda la información en la memoria del usuario inmediatamente.
        
        Args:
            message_body: Cuerpo del mensaje a analizar
            user_memory: Memoria del usuario para actualizar
            
        Returns:
            Dict con información de hashtags detectados y mapeados
        """
        try:
            debug_print(f"🔍 Analizando mensaje para hashtags: '{message_body}'", "_extract_and_map_hashtags")
            
            # Inicializar listas en memoria si no existen
            if user_memory.interests is None:
                user_memory.interests = []
            if user_memory.buying_signals is None:
                user_memory.buying_signals = []
            
            hashtags_found = []
            course_ids_mapped = []
            message_lower = message_body.lower()
            
            # Buscar en el mapeo centralizado de cursos
            for hashtag in COURSE_HASHTAG_MAPPING.keys():
                # Buscar tanto con # como sin #
                for pattern in [f"#{hashtag}", hashtag]:
                    if pattern.lower() in message_lower:
                        debug_print(f"📋 Hashtag detectado: {hashtag}", "_extract_and_map_hashtags")
                        
                        # Evitar duplicados
                        if hashtag not in hashtags_found:
                            hashtags_found.append(hashtag)
                        
                        # Mapear a course_id
                        course_id = get_course_id_from_hashtag(hashtag)
                        if course_id and course_id not in course_ids_mapped:
                            course_ids_mapped.append(course_id)
                        
                        # 🎯 GUARDAR COURSE_ID EN EL CAMPO CORRECTO: selected_course
                        if course_id and not user_memory.selected_course:
                            user_memory.selected_course = course_id
                            debug_print(f"🎯 Course ID guardado en selected_course: {course_id}", "_extract_and_map_hashtags")
                        
                        # Guardar en memoria del usuario (intereses adicionales)
                        hashtag_interest = f"hashtag:{hashtag}"
                        if hashtag_interest not in user_memory.interests:
                            user_memory.interests.append(hashtag_interest)
                            debug_print(f"💾 Guardado en intereses: {hashtag_interest}", "_extract_and_map_hashtags")
                        
                        if course_id:
                            course_id_interest = f"course_id:{course_id}"
                            if course_id_interest not in user_memory.interests:
                                user_memory.interests.append(course_id_interest)
                                debug_print(f"💾 Guardado course_id en intereses: {course_id_interest}", "_extract_and_map_hashtags")
                        
                        # Agregar señal de compra temprana
                        buying_signal = f"Mensaje inicial con hashtag: {hashtag}"
                        if buying_signal not in user_memory.buying_signals:
                            user_memory.buying_signals.append(buying_signal)
                        
                        # Solo procesar el primer hashtag encontrado (para evitar sobrecargar)
                        break
                
                # Solo procesar el primer hashtag de curso válido
                if hashtags_found:
                    break
            
            # Incrementar lead score si se encontraron hashtags
            if hashtags_found:
                user_memory.lead_score += 10
                debug_print(f"📈 Lead score incrementado a {user_memory.lead_score}", "_extract_and_map_hashtags")
            
            result = {
                'hashtags_found': hashtags_found,
                'course_ids_mapped': course_ids_mapped,
                'interests_updated': len(hashtags_found) > 0,
                'buying_signals_added': len(hashtags_found) > 0
            }
            
            debug_print(f"✅ Resultado extracción: {result}", "_extract_and_map_hashtags")
            return result
            
        except Exception as e:
            debug_print(f"💥 Error extrayendo hashtags: {e}", "_extract_and_map_hashtags")
            return {
                'hashtags_found': [],
                'course_ids_mapped': [],
                'interests_updated': False,
                'buying_signals_added': False,
                'error': str(e)
            }