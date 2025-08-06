from services.twilio_service import TwilioService
from prompts.agent_prompts import SYSTEM_PROMPT

# TODO: Integrar memoria, análisis de intención y herramientas

twilio = TwilioService()

def procesar_mensaje_entrante(from_number: str, body: str):
    # Aquí iría el análisis de intención y activación de herramientas
    respuesta = "¡Hola! Soy Brenda, tu asesora de IA. ¿En qué puedo ayudarte hoy?"
    twilio.enviar_whatsapp(from_number, respuesta)
    # TODO: Integrar lógica de memoria y herramientas 