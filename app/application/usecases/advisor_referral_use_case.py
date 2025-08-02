"""
Caso de uso para referir usuarios a asesores humanos.
Detecta solicitudes de asesoría personalizada y proporciona información de contacto.
"""

from dataclasses import dataclass
from typing import Optional
import logging

from app.domain.entities.message import IncomingMessage, OutgoingMessage
from app.templates.advisor_referral_templates import AdvisorReferralTemplates
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.config.settings import settings
from memory.lead_memory import LeadMemory

logger = logging.getLogger(__name__)


@dataclass
class AdvisorReferralResult:
    """Resultado del proceso de referencia al asesor."""
    should_refer: bool
    referral_message: str
    urgency_level: str  # 'normal', 'high', 'urgent'
    referral_type: str  # 'general', 'contextual', 'urgent'
    advisor_notified: bool = False  # Si se notificó al asesor
    notification_sid: Optional[str] = None  # ID del mensaje enviado al asesor


class AdvisorReferralUseCase:
    """Caso de uso para manejar referencias a asesores humanos."""
    
    def __init__(self, twilio_client: TwilioWhatsAppClient = None):
        self.templates = AdvisorReferralTemplates()
        self.twilio_client = twilio_client
        
    async def handle_advisor_request(
        self, 
        incoming_message: IncomingMessage, 
        user_memory: LeadMemory
    ) -> AdvisorReferralResult:
        """
        Procesa una solicitud de referencia al asesor.
        
        Args:
            incoming_message: Mensaje entrante del usuario
            user_memory: Memoria del usuario
            
        Returns:
            AdvisorReferralResult con la información de referencia
        """
        message_text = incoming_message.body.lower().strip()
        
        # Determinar si debe referir al asesor
        should_refer = self._should_refer_to_advisor(message_text)
        
        if not should_refer:
            return AdvisorReferralResult(
                should_refer=False,
                referral_message="",
                urgency_level="normal",
                referral_type="none"
            )
        
        # Determinar urgencia y tipo de referencia
        urgency_level = self._determine_urgency_level(message_text)
        referral_type = self._determine_referral_type(message_text, user_memory, urgency_level)
        
        # Generar mensaje de referencia
        referral_message = self._generate_referral_message(
            referral_type, 
            urgency_level, 
            user_memory, 
            message_text
        )
        
        # Actualizar memoria del usuario
        self._update_user_memory(user_memory, referral_type, urgency_level)
        
        # Enviar notificación al asesor
        advisor_notified = False
        notification_sid = None
        
        if self.twilio_client:
            try:
                advisor_notified, notification_sid = await self._notify_advisor(
                    incoming_message.from_number, 
                    user_memory, 
                    message_text, 
                    urgency_level
                )
            except Exception as e:
                logger.error(f"Error enviando notificación al asesor: {e}")
                # No fallar si no se puede notificar al asesor
        
        logger.info(f"Referencia al asesor generada para usuario {user_memory.user_id} - Tipo: {referral_type}, Urgencia: {urgency_level}, Asesor notificado: {advisor_notified}")
        
        return AdvisorReferralResult(
            should_refer=True,
            referral_message=referral_message,
            urgency_level=urgency_level,
            referral_type=referral_type,
            advisor_notified=advisor_notified,
            notification_sid=notification_sid
        )
    
    def _should_refer_to_advisor(self, message_text: str) -> bool:
        """
        Determina si el mensaje requiere referencia al asesor.
        
        Args:
            message_text: Texto del mensaje en minúsculas
            
        Returns:
            True si debe referir al asesor
        """
        # Palabras clave que indican solicitud de asesor
        advisor_keywords = [
            'asesor', 'asesora', 'asesoría', 'asesoria',
            'vendedor', 'vendedora', 'ventas',
            'persona', 'humano', 'humana',
            'hablar con alguien', 'hablar con una persona',
            'contactar', 'contacto', 'llamar',
            'reunión', 'reunion', 'cita',
            'representante', 'agente',
            'especialista', 'experto', 'consultor',
            'equipo comercial', 'equipo de ventas',
            'atención personalizada', 'atencion personalizada',
            'hablar contigo', 'necesito ayuda personalizada',
            'quiero hablar', 'necesito hablar',
            'consulta personalizada', 'asesoramiento'
        ]
        
        # Frases que indican necesidad de asesor
        advisor_phrases = [
            'quiero hablar con',
            'necesito hablar con',
            'me puedes conectar con',
            'hay algún asesor',
            'hay algun asesor',
            'tienen asesor',
            'puedo hablar con',
            'me gustaría hablar',
            'quisiera hablar',
            'necesito contactar',
            'como contacto',
            'como los contacto',
            'número de teléfono',
            'numero de telefono',
            'atención al cliente',
            'atencion al cliente'
        ]
        
        # Verificar palabras clave
        for keyword in advisor_keywords:
            if keyword in message_text:
                return True
                
        # Verificar frases
        for phrase in advisor_phrases:
            if phrase in message_text:
                return True
                
        return False
    
    def _determine_urgency_level(self, message_text: str) -> str:
        """
        Determina el nivel de urgencia de la solicitud.
        
        Args:
            message_text: Texto del mensaje
            
        Returns:
            Nivel de urgencia: 'normal', 'high', 'urgent'
        """
        urgent_keywords = [
            'urgente', 'urgencia', 'emergencia',
            'rápido', 'rapido', 'pronto', 'ya',
            'inmediato', 'ahora mismo', 'hoy',
            'necesito ya', 'lo antes posible'
        ]
        
        high_priority_keywords = [
            'importante', 'priority', 'prioridad',
            'mañana', 'esta semana', 'proyecto',
            'equipo esperando', 'jefe pregunta'
        ]
        
        for keyword in urgent_keywords:
            if keyword in message_text:
                return 'urgent'
                
        for keyword in high_priority_keywords:
            if keyword in message_text:
                return 'high'
                
        return 'normal'
    
    def _determine_referral_type(
        self, 
        message_text: str, 
        user_memory: LeadMemory, 
        urgency_level: str
    ) -> str:
        """
        Determina el tipo de referencia según el contexto.
        
        Args:
            message_text: Texto del mensaje
            user_memory: Memoria del usuario
            urgency_level: Nivel de urgencia
            
        Returns:
            Tipo de referencia: 'general', 'contextual', 'urgent'
        """
        if urgency_level == 'urgent':
            return 'urgent'
            
        # Si tenemos información del usuario (nombre y rol), usar referencia contextual
        if user_memory.name and user_memory.name != "Usuario" and user_memory.role:
            return 'contextual'
            
        return 'general'
    
    def _generate_referral_message(
        self, 
        referral_type: str, 
        urgency_level: str, 
        user_memory: LeadMemory, 
        message_text: str
    ) -> str:
        """
        Genera el mensaje de referencia apropiado.
        
        Args:
            referral_type: Tipo de referencia
            urgency_level: Nivel de urgencia
            user_memory: Memoria del usuario
            message_text: Texto original del mensaje
            
        Returns:
            Mensaje de referencia formateado
        """
        if referral_type == 'urgent':
            return self.templates.urgent_contact_message()
            
        elif referral_type == 'contextual':
            # Extraer interés específico del mensaje
            specific_interest = self._extract_specific_interest(message_text)
            
            return self.templates.advisor_referral_with_context(
                user_name=user_memory.name,
                user_role=user_memory.role,
                specific_interest=specific_interest
            )
            
        else:  # referral_type == 'general'
            user_name = user_memory.name if user_memory.name != "Usuario" else ""
            return self.templates.advisor_referral_message(user_name)
    
    def _extract_specific_interest(self, message_text: str) -> str:
        """
        Extrae el interés específico mencionado en el mensaje.
        
        Args:
            message_text: Texto del mensaje
            
        Returns:
            Interés específico o string vacío
        """
        # Patrones de intereses específicos
        interests_patterns = {
            'automatización': ['automatizar', 'automatización', 'automatizacion'],
            'marketing': ['marketing', 'publicidad', 'contenido', 'campañas'],
            'reportes': ['reportes', 'informes', 'análisis', 'datos'],
            'capacitación': ['capacitación', 'capacitacion', 'entrenar', 'formar'],
            'implementación': ['implementar', 'implementación', 'integrar'],
            'estrategia': ['estrategia', 'planeación', 'roadmap'],
            'presupuesto': ['precio', 'costo', 'presupuesto', 'inversión']
        }
        
        for interest, keywords in interests_patterns.items():
            for keyword in keywords:
                if keyword in message_text:
                    return interest
                    
        return ""
    
    def _update_user_memory(
        self, 
        user_memory: LeadMemory, 
        referral_type: str, 
        urgency_level: str
    ) -> None:
        """
        Actualiza la memoria del usuario con información de la referencia.
        
        Args:
            user_memory: Memoria del usuario
            referral_type: Tipo de referencia
            urgency_level: Nivel de urgencia
        """
        # Agregar señal de compra
        buying_signal = f"Solicitud de asesor - {referral_type} ({urgency_level})"
        if buying_signal not in user_memory.buying_signals:
            user_memory.buying_signals.append(buying_signal)
        
        # Actualizar stage si es apropiado
        if user_memory.stage in ["first_contact", "privacy_flow", "course_selection"]:
            user_memory.stage = "sales_agent"
            
        # Incrementar lead score por solicitud de asesor
        urgency_scores = {
            'normal': 15,
            'high': 25, 
            'urgent': 35
        }
        user_memory.lead_score += urgency_scores.get(urgency_level, 15)
        
        logger.info(f"Memoria actualizada para {user_memory.user_id} - Stage: {user_memory.stage}, Score: {user_memory.lead_score}")
    
    async def _notify_advisor(
        self, 
        user_phone: str, 
        user_memory: LeadMemory, 
        original_message: str, 
        urgency_level: str
    ) -> tuple[bool, Optional[str]]:
        """
        Envía notificación al asesor sobre el nuevo lead.
        
        Args:
            user_phone: Número del usuario
            user_memory: Memoria del usuario
            original_message: Mensaje original del usuario
            urgency_level: Nivel de urgencia
            
        Returns:
            Tupla (éxito, message_sid)
        """
        try:
            # Extraer interés específico del mensaje original
            specific_interest = self._extract_specific_interest(original_message)
            
            # Generar mensaje para el asesor
            advisor_message = self.templates.advisor_notification_message(
                user_phone=user_phone,
                user_name=user_memory.name or "Usuario",
                user_role=user_memory.role or "No especificado",
                specific_interest=specific_interest,
                urgency_level=urgency_level
            )
            
            # Crear mensaje saliente
            outgoing_message = OutgoingMessage(
                to_number=settings.advisor_phone_number,
                body=advisor_message
            )
            
            # Enviar mensaje
            result = await self.twilio_client.send_message(outgoing_message)
            
            if result.get('success', False):
                logger.info(f"Asesor notificado exitosamente para lead {user_memory.user_id} - SID: {result.get('message_sid')}")
                return True, result.get('message_sid')
            else:
                logger.error(f"Error enviando notificación al asesor: {result.get('error')}")
                return False, None
                
        except Exception as e:
            logger.error(f"Excepción enviando notificación al asesor: {e}")
            return False, None