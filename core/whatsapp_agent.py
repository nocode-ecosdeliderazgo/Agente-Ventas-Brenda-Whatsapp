"""
Agente WhatsApp legacy - mantenido para compatibilidad.
NOTA: El sistema principal usa app/presentation/api/webhook.py
"""
import logging
from services.twilio_service import TwilioService
from prompts.agent_prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# TODO: Integrar memoria, análisis de intención y herramientas

try:
    twilio = TwilioService()
    logger.info("✅ TwilioService legacy inicializado")
except Exception as e:
    logger.error(f"❌ Error inicializando TwilioService legacy: {e}")
    twilio = None

def procesar_mensaje_entrante(from_number: str, body: str) -> dict:
    """
    Procesador de mensajes legacy.
    NOTA: Esta función está mantenida para compatibilidad pero el sistema
    principal usa app/application/usecases/process_incoming_message.py
    """
    if not twilio:
        logger.error("❌ TwilioService no disponible")
        return {'success': False, 'error': 'TwilioService no disponible'}
    
    try:
        # Sanitizar entrada
        from_number_clean = from_number.strip()
        body_clean = body.replace('\n', ' ').replace('\r', ' ').strip()
        
        logger.info(f"📨 Procesando mensaje legacy de {from_number_clean}")
        
        # Aquí iría el análisis de intención y activación de herramientas
        respuesta = "¡Hola! Soy Brenda, tu asesora de IA. ¿En qué puedo ayudarte hoy?"
        
        result = twilio.enviar_whatsapp(from_number_clean, respuesta)
        logger.info(f"📤 Respuesta enviada desde procesador legacy: {result.get('success', False)}")
        
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error procesando mensaje legacy de {from_number}")
        return {'success': False, 'error': str(e)}
    
    # TODO: Integrar lógica de memoria y herramientas 