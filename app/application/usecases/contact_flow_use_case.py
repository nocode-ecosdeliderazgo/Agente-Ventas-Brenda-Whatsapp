#!/usr/bin/env python3
"""
Caso de uso para el flujo de contacto con asesores.
Permite a los usuarios conectarse con asesores humanos.
"""

import asyncio
from typing import Dict, Any, Optional
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.templates.contact_flow_templates import ContactFlowTemplates
from app.domain.entities.contact_request import ContactRequest


class ContactFlowUseCase:
    """
    Caso de uso para manejar el flujo de contacto con asesores.
    """
    
    def __init__(
        self,
        memory_use_case: ManageUserMemoryUseCase,
        privacy_flow_use_case: PrivacyFlowUseCase,
        twilio_client: TwilioWhatsAppClient
    ):
        self.memory_use_case = memory_use_case
        self.privacy_flow_use_case = privacy_flow_use_case
        self.twilio_client = twilio_client
        self.templates = ContactFlowTemplates()
    
    def _update_memory_data(self, user_id: str, data: Dict[str, Any]) -> None:
        """
        Actualiza datos específicos en la memoria del usuario.
        
        Args:
            user_id: ID del usuario
            data: Datos a actualizar
        """
        try:
            memory = self.memory_use_case.get_user_memory(user_id)
            
            # Actualizar atributos dinámicamente
            for key, value in data.items():
                setattr(memory, key, value)
            
            # Guardar memoria actualizada
            self.memory_use_case.memory_manager.save_lead_memory(user_id, memory)
            
        except Exception as e:
            print(f"❌ Error actualizando memoria para {user_id}: {e}")
    
    async def execute(
        self, 
        webhook_data: Dict[str, Any], 
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta el flujo de contacto completo.
        
        Args:
            webhook_data: Datos del webhook de Twilio
            user_data: Datos del usuario
            
        Returns:
            Dict con el resultado del flujo
        """
        try:
            print("📞 INICIANDO FLUJO DE CONTACTO")
            print(f"   Usuario: {user_data.get('id', 'unknown')}")
            print(f"   Mensaje: {webhook_data.get('Body', '')}")
            
            # Obtener memoria del usuario
            user_memory = self.memory_use_case.get_user_memory(user_data['id'])
            
            # Verificar si el usuario ya completó el flujo de privacidad
            if not getattr(user_memory, 'privacy_consent_given', False):
                print("⚠️ Usuario no ha dado consentimiento de privacidad")
                return await self._handle_privacy_required(webhook_data, user_data)
            
            # Verificar estado actual del flujo de contacto
            contact_state = getattr(user_memory, 'contact_flow_state', 'initial')
            
            if contact_state == 'initial':
                return await self._handle_initial_contact(webhook_data, user_data, user_memory)
            elif contact_state == 'collecting_info':
                return await self._handle_info_collection(webhook_data, user_data, user_memory)
            elif contact_state == 'confirming':
                return await self._handle_confirmation(webhook_data, user_data, user_memory)
            elif contact_state == 'completed':
                return await self._handle_already_contacted(webhook_data, user_data, user_memory)
            else:
                return await self._handle_initial_contact(webhook_data, user_data, user_memory)
                
        except Exception as e:
            print(f"❌ Error en flujo de contacto: {e}")
            return {
                'success': False,
                'error': str(e),
                'response_text': 'Lo siento, hubo un error procesando tu solicitud de contacto. Por favor, intenta de nuevo.'
            }
    
    async def _handle_privacy_required(
        self, 
        webhook_data: Dict[str, Any], 
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Maneja el caso cuando se requiere consentimiento de privacidad."""
        print("🔒 Redirigiendo a flujo de privacidad")
        
        # Ejecutar flujo de privacidad
        privacy_result = await self.privacy_flow_use_case.execute(webhook_data, user_data)
        
        return {
            'success': True,
            'privacy_required': True,
            'response_text': privacy_result.get('response_text', ''),
            'contact_flow_pending': True
        }
    
    async def _handle_initial_contact(
        self, 
        webhook_data: Dict[str, Any], 
        user_data: Dict[str, Any],
        user_memory: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Maneja la solicitud inicial de contacto."""
        print("📞 Procesando solicitud inicial de contacto")
        
        # Actualizar estado en memoria
        self._update_memory_data(
            user_data['id'],
            {'contact_flow_state': 'collecting_info'}
        )
        
        # Enviar mensaje de bienvenida y solicitar información
        response_text = self.templates.get_contact_welcome_message(
            user_data.get('first_name', 'Usuario')
        )
        
        await self.twilio_client.send_message(response_text)
        
        return {
            'success': True,
            'contact_flow_started': True,
            'response_text': response_text,
            'next_state': 'collecting_info'
        }
    
    async def _handle_info_collection(
        self, 
        webhook_data: Dict[str, Any], 
        user_data: Dict[str, Any],
        user_memory: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recopila información adicional del usuario."""
        print("📝 Recopilando información adicional")
        
        user_message = webhook_data.get('Body', '').strip()
        
        # Guardar información en memoria
        contact_info = {
            'contact_reason': user_message,
            'contact_timestamp': asyncio.get_event_loop().time(),
            'user_phone': user_data.get('phone', ''),
            'user_name': user_data.get('first_name', ''),
            'user_role': getattr(user_memory, 'user_role', ''),
            'company_size': getattr(user_memory, 'company_size', ''),
            'industry': getattr(user_memory, 'industry', '')
        }
        
        self._update_memory_data(
            user_data['id'],
            {
                'contact_info': contact_info,
                'contact_flow_state': 'confirming'
            }
        )
        
        # Enviar confirmación y solicitar confirmación
        response_text = self.templates.get_contact_confirmation_message(
            user_data.get('first_name', 'Usuario'),
            contact_info
        )
        
        await self.twilio_client.send_message(response_text)
        
        return {
            'success': True,
            'info_collected': True,
            'response_text': response_text,
            'next_state': 'confirming'
        }
    
    async def _handle_confirmation(
        self, 
        webhook_data: Dict[str, Any], 
        user_data: Dict[str, Any],
        user_memory: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Maneja la confirmación del contacto."""
        print("✅ Procesando confirmación de contacto")
        
        user_message = webhook_data.get('Body', '').strip().lower()
        
        if any(word in user_message for word in ['si', 'sí', 'yes', 'confirmo', 'confirmar', 'ok', 'okay']):
            # Usuario confirma el contacto
            contact_info = getattr(user_memory, 'contact_info', {})
            
            # Crear solicitud de contacto
            contact_request = ContactRequest(
                user_id=user_data['id'],
                user_name=contact_info.get('user_name', ''),
                user_phone=contact_info.get('user_phone', ''),
                user_role=contact_info.get('user_role', ''),
                company_size=contact_info.get('company_size', ''),
                industry=contact_info.get('industry', ''),
                contact_reason=contact_info.get('contact_reason', ''),
                status='pending'
            )
            
            # Aquí se enviaría la solicitud al sistema de asesores
            # Por ahora, simulamos el envío
            print(f"📤 Enviando solicitud de contacto: {contact_request}")
            
            # Actualizar estado en memoria
            self._update_memory_data(
                user_data['id'],
                {
                    'contact_flow_state': 'completed',
                    'contact_request_id': f"REQ_{user_data['id']}_{int(asyncio.get_event_loop().time())}",
                    'contact_status': 'pending'
                }
            )
            
            # Enviar confirmación final
            response_text = self.templates.get_contact_success_message(
                user_data.get('first_name', 'Usuario')
            )
            
            await self.twilio_client.send_message(response_text)
            
            return {
                'success': True,
                'contact_confirmed': True,
                'response_text': response_text,
                'contact_request': contact_request.dict()
            }
        else:
            # Usuario no confirma, volver a solicitar información
            self._update_memory_data(
                user_data['id'],
                {'contact_flow_state': 'collecting_info'}
            )
            
            response_text = self.templates.get_contact_retry_message(
                user_data.get('first_name', 'Usuario')
            )
            
            await self.twilio_client.send_message(response_text)
            
            return {
                'success': True,
                'contact_retry': True,
                'response_text': response_text,
                'next_state': 'collecting_info'
            }
    
    async def _handle_already_contacted(
        self, 
        webhook_data: Dict[str, Any], 
        user_data: Dict[str, Any],
        user_memory: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Maneja el caso cuando el usuario ya solicitó contacto."""
        print("📞 Usuario ya solicitó contacto anteriormente")
        
        contact_status = getattr(user_memory, 'contact_status', 'pending')
        
        if contact_status == 'pending':
            response_text = self.templates.get_contact_pending_message(
                user_data.get('first_name', 'Usuario')
            )
        else:
            response_text = self.templates.get_contact_already_processed_message(
                user_data.get('first_name', 'Usuario')
            )
        
        await self.twilio_client.send_message(response_text)
        
        return {
            'success': True,
            'already_contacted': True,
            'response_text': response_text,
            'contact_status': contact_status
        }
    
    async def detect_contact_intent(self, message: str) -> bool:
        """
        Detecta si el mensaje indica intención de contacto.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            True si hay intención de contacto
        """
        contact_keywords = [
            'hablar con asesor', 'contactar asesor', 'asesor humano',
            'hablar con alguien', 'contacto humano', 'asesoría',
            'ayuda personalizada', 'atención personal', 'asesor',
            'representante', 'vendedor', 'consultor', 'especialista',
            'contacto directo', 'llamada', 'conversación directa'
        ]
        
        message_lower = message.lower()
        
        # Verificar palabras clave
        for keyword in contact_keywords:
            if keyword in message_lower:
                return True
        
        # Verificar patrones específicos
        contact_patterns = [
            'quiero hablar',
            'necesito hablar',
            'puedo hablar',
            'me gustaría hablar',
            'busco asesor',
            'necesito asesor',
            'quiero asesor',
            'contacto directo',
            'atención personal'
        ]
        
        for pattern in contact_patterns:
            if pattern in message_lower:
                return True
        
        return False 