"""
Cliente de Twilio para envío de mensajes de WhatsApp.
Capa de infraestructura que maneja la comunicación con la API de Twilio.
"""
import logging
import asyncio
import time
import random
from typing import Dict, Any, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from app.config import settings
from app.domain.entities.message import OutgoingMessage, MessageType

logger = logging.getLogger(__name__)

def debug_print(message: str, function_name: str = "", file_name: str = "twilio_client.py"):
    """Print de debug visual para consola"""
    print(f"📱 [{file_name}::{function_name}] {message}")


class TwilioWhatsAppClient:
    """Cliente especializado para WhatsApp via Twilio."""
    
    def __init__(self):
        """Inicializa el cliente de Twilio."""
        self.client = Client(
            settings.twilio_account_sid, 
            settings.twilio_auth_token
        )
        self.from_number = f"whatsapp:{settings.twilio_phone_number}"
        
    async def send_message_with_typing(
        self, 
        message: OutgoingMessage, 
        typing_duration: Optional[float] = None,
        simulate_human_delay: bool = True
    ) -> Dict[str, Any]:
        """
        Envía un mensaje con simulación de typing indicator para más naturalidad.
        
        Args:
            message: Mensaje a enviar
            typing_duration: Duración personalizada del typing (opcional)
            simulate_human_delay: Si simular delays humanos realistas
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            if simulate_human_delay:
                # Calcular delay basado en longitud del mensaje (simula escritura humana)
                typing_delay = self._calculate_realistic_typing_delay(message.body, typing_duration)
                
                debug_print(f"⌨️ SIMULANDO TYPING por {typing_delay:.1f} segundos...", "send_message_with_typing")
                
                # Simular typing indicator (delay realista)
                await asyncio.sleep(typing_delay)
            
            # Enviar el mensaje
            return await self.send_message(message)
            
        except Exception as e:
            debug_print(f"💥 ERROR EN TYPING SIMULATION: {e}", "send_message_with_typing")
            # Fallback: enviar mensaje sin typing
            return await self.send_message(message)
    
    def _calculate_realistic_typing_delay(self, message_body: str, custom_duration: Optional[float] = None) -> float:
        """
        Calcula un delay realista basado en la longitud del mensaje.
        Simula velocidad de escritura humana.
        
        Args:
            message_body: Contenido del mensaje
            custom_duration: Duración personalizada (opcional)
            
        Returns:
            Delay en segundos
        """
        if custom_duration is not None:
            return max(0.5, min(custom_duration, 8.0))  # Entre 0.5 y 8 segundos max
        
        # Calcular delay basado en longitud
        message_length = len(message_body)
        
        # Velocidad de escritura humana: ~40-60 caracteres por minuto = 0.7-1.0 char/segundo
        base_typing_speed = 0.85  # caracteres por segundo (velocidad promedio)
        
        # Calcular tiempo base
        base_delay = message_length / base_typing_speed
        
        # Agregar variabilidad humana (±20%)
        variation = random.uniform(-0.2, 0.2)
        realistic_delay = base_delay * (1 + variation)
        
        # Límites realistas
        min_delay = 0.8  # Mínimo medio segundo
        max_delay = 6.0  # Máximo 6 segundos para mensajes largos
        
        # Escalado por longitud
        if message_length <= 50:
            # Mensajes cortos: 0.8-2 segundos
            final_delay = max(min_delay, min(realistic_delay, 2.0))
        elif message_length <= 150:
            # Mensajes medianos: 1-3.5 segundos
            final_delay = max(1.0, min(realistic_delay, 3.5))
        elif message_length <= 300:
            # Mensajes largos: 1.5-5 segundos
            final_delay = max(1.5, min(realistic_delay, 5.0))
        else:
            # Mensajes muy largos: 2-6 segundos
            final_delay = max(2.0, min(realistic_delay, max_delay))
        
        return final_delay

    async def send_message(self, message: OutgoingMessage) -> Dict[str, Any]:
        """
        Envía un mensaje de WhatsApp.
        
        Args:
            message: Mensaje a enviar
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            debug_print(f"📤 ENVIANDO MENSAJE WHATSAPP\n👤 A: {message.to_number}\n💬 Texto: '{message.body[:100]}{'...' if len(message.body) > 100 else ''}'", "send_message", "twilio_client.py")
            
            # Preparar datos para Twilio
            # Verificar si el número ya tiene el prefijo whatsapp:
            to_number = message.to_number
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            twilio_data = {
                'body': message.body,
                'from_': self.from_number,
                'to': to_number
            }
            debug_print(f"⚙️ Datos preparados para Twilio:\n📞 From: {self.from_number}\n📞 To: {to_number}", "send_message", "twilio_client.py")
            
            # Agregar multimedia si existe
            if message.media_url:
                twilio_data['media_url'] = [message.media_url]
                debug_print(f"🖼️ Multimedia incluida: {message.media_url}", "send_message", "twilio_client.py")
            
            # Enviar mensaje
            debug_print("🚀 Llamando API de Twilio...", "send_message", "twilio_client.py")
            twilio_message = self.client.messages.create(**twilio_data)
            debug_print(f"✅ MENSAJE ENVIADO EXITOSAMENTE!\n🔗 SID: {twilio_message.sid}\n📊 Status: {twilio_message.status}", "send_message", "twilio_client.py")
            
            logger.info(f"Mensaje enviado exitosamente. SID: {twilio_message.sid}")
            
            return {
                'success': True,
                'message_sid': twilio_message.sid,
                'status': twilio_message.status,
                'to': message.to_number,
                'error': None
            }
            
        except TwilioException as e:
            debug_print(f"❌ ERROR DE TWILIO: {e}", "send_message", "twilio_client.py")
            return {
                'success': False,
                'message_sid': None,
                'status': 'failed',
                'to': message.to_number,
                'error': str(e)
            }
        except Exception as e:
            debug_print(f"💥 ERROR INESPERADO: {e}", "send_message", "twilio_client.py")
            return {
                'success': False,
                'message_sid': None,
                'status': 'failed', 
                'to': message.to_number,
                'error': str(e)
            }
    
    async def send_text(self, to_number: str, text: str) -> Dict[str, Any]:
        """
        Envía un mensaje de texto simple.
        
        Args:
            to_number: Número de teléfono destino
            text: Texto del mensaje
            
        Returns:
            Dict con el resultado del envío
        """
        message = OutgoingMessage(
            to_number=to_number,
            body=text,
            message_type=MessageType.TEXT
        )
        return await self.send_message(message)
    
    async def send_text_with_typing(
        self, 
        to_number: str, 
        text: str, 
        typing_duration: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de texto con simulación de typing.
        
        Args:
            to_number: Número de teléfono destino
            text: Texto del mensaje
            typing_duration: Duración personalizada del typing
            
        Returns:
            Dict con el resultado del envío
        """
        message = OutgoingMessage(
            to_number=to_number,
            body=text,
            message_type=MessageType.TEXT
        )
        return await self.send_message_with_typing(message, typing_duration)
    
    async def send_quick_response(self, to_number: str, text: str) -> Dict[str, Any]:
        """
        Envía respuesta rápida (mensajes cortos, confirmaciones).
        Typing reducido para simular respuestas automáticas rápidas.
        
        Args:
            to_number: Número de teléfono destino
            text: Texto del mensaje
            
        Returns:
            Dict con el resultado del envío
        """
        message = OutgoingMessage(
            to_number=to_number,
            body=text,
            message_type=MessageType.TEXT
        )
        # Typing corto para respuestas rápidas (0.5-1 segundo)
        return await self.send_message_with_typing(message, typing_duration=random.uniform(0.5, 1.0))
    
    async def send_thoughtful_response(self, to_number: str, text: str) -> Dict[str, Any]:
        """
        Envía respuesta elaborada (análisis, explicaciones detalladas).
        Typing más largo para simular pensamiento/análisis.
        
        Args:
            to_number: Número de teléfono destino
            text: Texto del mensaje
            
        Returns:
            Dict con el resultado del envío
        """
        message = OutgoingMessage(
            to_number=to_number,
            body=text,
            message_type=MessageType.TEXT
        )
        # Typing largo para respuestas elaboradas (2-4 segundos)
        return await self.send_message_with_typing(message, typing_duration=random.uniform(2.0, 4.0))
    
    async def send_multiple_messages_with_spacing(
        self, 
        to_number: str, 
        messages: list, 
        spacing_seconds: float = 1.5
    ) -> list:
        """
        Envía múltiples mensajes con espaciado temporal para simular conversación natural.
        
        Args:
            to_number: Número de teléfono destino
            messages: Lista de mensajes a enviar
            spacing_seconds: Segundos entre mensajes
            
        Returns:
            Lista de resultados de envío
        """
        results = []
        
        for i, message_text in enumerate(messages):
            if i > 0:  # No esperar antes del primer mensaje
                debug_print(f"⏸️ Esperando {spacing_seconds}s antes del siguiente mensaje...")
                await asyncio.sleep(spacing_seconds)
            
            # Determinar tipo de mensaje para timing apropiado
            if len(message_text) < 50:
                result = await self.send_quick_response(to_number, message_text)
            elif len(message_text) > 300:
                result = await self.send_thoughtful_response(to_number, message_text)
            else:
                result = await self.send_text_with_typing(to_number, message_text)
            
            results.append(result)
            
            # Si hay error, detener el envío de mensajes adicionales
            if not result.get('success', False):
                debug_print(f"❌ Error enviando mensaje {i+1}, deteniendo secuencia")
                break
        
        return results
    
    async def send_media(self, to_number: str, text: str, media_url: str) -> Dict[str, Any]:
        """
        Envía un mensaje con multimedia.
        
        Args:
            to_number: Número de teléfono destino
            text: Texto del mensaje
            media_url: URL del archivo multimedia
            
        Returns:
            Dict con el resultado del envío
        """
        message = OutgoingMessage(
            to_number=to_number,
            body=text,
            message_type=MessageType.IMAGE,  # Por ahora asumimos imagen
            media_url=media_url
        )
        return await self.send_message(message)
    
    def verify_webhook_signature(self, signature: str, url: str, params: Dict[str, Any]) -> bool:
        """
        Verifica la firma del webhook de Twilio para seguridad.
        
        Args:
            signature: Firma del webhook
            url: URL del webhook
            params: Parámetros del webhook
            
        Returns:
            True si la firma es válida
        """
        if not settings.webhook_verify_signature:
            return True
            
        try:
            from twilio.request_validator import RequestValidator
            validator = RequestValidator(settings.twilio_auth_token)
            return validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Error verificando firma del webhook: {e}")
            return False