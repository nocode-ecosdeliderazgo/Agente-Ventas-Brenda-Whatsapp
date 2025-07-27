"""
Webhook handler para recibir mensajes de Twilio WhatsApp.
"""
import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.application.usecases.process_incoming_message import ProcessIncomingMessageUseCase

logger = logging.getLogger(__name__)

# Crear instancia de FastAPI
app = FastAPI(
    title="Bot Brenda - Webhook WhatsApp",
    description="Webhook para recibir mensajes de WhatsApp via Twilio",
    version="1.0.0"
)

# Instanciar dependencias
twilio_client = TwilioWhatsAppClient()
process_message_use_case = ProcessIncomingMessageUseCase(twilio_client)


@app.get("/")
async def health_check():
    """Endpoint de health check."""
    return {
        "status": "ok",
        "service": "Bot Brenda Webhook",
        "environment": settings.app_environment
    }


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    # Parámetros típicos del webhook de Twilio
    MessageSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    # Parámetros opcionales
    AccountSid: str = Form(None),
    MessagingServiceSid: str = Form(None),
    NumMedia: str = Form("0"),
    ProfileName: str = Form(None),
    WaId: str = Form(None)
):
    """
    Webhook para recibir mensajes entrantes de WhatsApp.
    
    Twilio enviará una petición POST a este endpoint cada vez que
    se reciba un mensaje en el número de WhatsApp configurado.
    """
    try:
        logger.info(f"📨 Webhook recibido de {From}: {Body}")
        
        # Verificar firma del webhook si está habilitado
        if settings.webhook_verify_signature:
            signature = request.headers.get('X-Twilio-Signature', '')
            url = str(request.url)
            
            # Obtener todos los parámetros del formulario
            form_data = await request.form()
            params = dict(form_data)
            
            if not twilio_client.verify_webhook_signature(signature, url, params):
                logger.warning(f"⚠️ Firma de webhook inválida desde {From}")
                raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Preparar datos del webhook
        webhook_data = {
            'MessageSid': MessageSid,
            'From': From,
            'To': To,
            'Body': Body,
            'AccountSid': AccountSid,
            'MessagingServiceSid': MessagingServiceSid,
            'NumMedia': NumMedia,
            'ProfileName': ProfileName,
            'WaId': WaId
        }
        
        # Procesar mensaje en background para responder rápido a Twilio
        background_tasks.add_task(
            process_message_in_background,
            webhook_data
        )
        
        # Responder inmediatamente a Twilio (requerido)
        return PlainTextResponse("OK", status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error en webhook: {e}")
        # Siempre responder 200 a Twilio para evitar reintentos
        return PlainTextResponse("ERROR", status_code=200)


async def process_message_in_background(webhook_data: Dict[str, Any]):
    """
    Procesa el mensaje en background para no bloquear la respuesta del webhook.
    
    Args:
        webhook_data: Datos del webhook de Twilio
    """
    try:
        logger.info("🔄 Procesando mensaje en background...")
        
        # Ejecutar caso de uso
        result = await process_message_use_case.execute(webhook_data)
        
        if result['success'] and result['processed']:
            logger.info(
                f"✅ Mensaje procesado exitosamente. "
                f"Respuesta enviada: {result['response_sent']}"
            )
        else:
            logger.warning(f"⚠️ Mensaje no procesado: {result}")
            
    except Exception as e:
        logger.error(f"💥 Error en background processing: {e}")


@app.get("/webhook/whatsapp")
async def whatsapp_webhook_verification(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """
    Verificación del webhook (usado por algunos servicios).
    Por ahora solo para compatibilidad futura.
    """
    logger.info("🔍 Solicitud de verificación de webhook recibida")
    return PlainTextResponse("OK", status_code=200)


if __name__ == "__main__":
    import uvicorn
    
    # Configurar logging
    logging.basicConfig(
        level=settings.get_log_level(),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Iniciando servidor webhook...")
    logger.info(f"🌍 Entorno: {settings.app_environment}")
    logger.info(f"📱 Número Twilio: {settings.twilio_phone_number}")
    
    uvicorn.run(
        "app.presentation.api.webhook:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )