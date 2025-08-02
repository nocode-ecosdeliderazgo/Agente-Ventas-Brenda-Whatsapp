"""
Entidades de dominio para mensajes de WhatsApp.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class MessageType(Enum):
    """Tipos de mensaje soportados."""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"


class MessageStatus(Enum):
    """Estados del mensaje."""
    RECEIVED = "received"
    PROCESSING = "processing"
    RESPONDED = "responded"
    ERROR = "error"


@dataclass
class IncomingMessage:
    """Mensaje entrante de WhatsApp."""
    
    # Identificadores
    message_sid: str
    from_number: str
    to_number: str
    
    # Contenido
    body: str
    
    # Metadatos
    timestamp: datetime
    raw_data: Dict[str, Any]
    
    # Estado
    status: MessageStatus = MessageStatus.RECEIVED
    message_type: MessageType = MessageType.TEXT
    
    @classmethod
    def from_twilio_webhook(cls, webhook_data: Dict[str, Any]) -> 'IncomingMessage':
        """Crea un mensaje desde los datos del webhook de Twilio."""
        return cls(
            message_sid=webhook_data.get('MessageSid', ''),
            from_number=webhook_data.get('From', '').replace('whatsapp:', ''),
            to_number=webhook_data.get('To', '').replace('whatsapp:', ''),
            body=webhook_data.get('Body', ''),
            message_type=MessageType.TEXT,  # Por ahora solo texto
            timestamp=datetime.now(),
            raw_data=webhook_data
        )
    
    def is_whatsapp(self) -> bool:
        """Verifica si el mensaje viene de WhatsApp."""
        return 'whatsapp:' in self.raw_data.get('From', '')


@dataclass 
class OutgoingMessage:
    """Mensaje saliente para WhatsApp."""
    
    to_number: str
    body: str
    message_type: MessageType = MessageType.TEXT
    
    # Opcionales para multimedia
    media_url: Optional[str] = None
    
    def to_twilio_format(self) -> Dict[str, Any]:
        """Convierte el mensaje al formato requerido por Twilio."""
        data = {
            'body': self.body,
            'from_': f'whatsapp:{self.to_number}',  # Se ajustará en el servicio
            'to': f'whatsapp:{self.to_number}'
        }
        
        if self.media_url:
            data['media_url'] = [self.media_url]
            
        return data