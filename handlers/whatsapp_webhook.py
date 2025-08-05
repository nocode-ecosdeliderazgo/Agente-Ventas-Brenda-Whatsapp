"""
Webhook handler legacy - mantenido para compatibilidad.
NOTA: El sistema principal usa app/presentation/api/webhook.py
"""
import logging
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import PlainTextResponse
from core.whatsapp_agent import procesar_mensaje_entrante

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bot Brenda Legacy Webhook",
    description="Webhook legacy para WhatsApp - usar app/presentation/api/webhook.py para producción"
)

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Webhook legacy para WhatsApp.
    NOTA: Esta función está mantenida para compatibilidad pero el sistema
    principal usa app/presentation/api/webhook.py
    """
    try:
        data = await request.form()
        from_number = data.get('From', '').strip()
        body = data.get('Body', '').strip()
        message_sid = data.get('MessageSid', '')
        
        # Validación básica
        if not from_number or not body:
            logger.warning(f"⚠️ Datos incompletos: from={from_number}, body={body}")
            return PlainTextResponse("Missing data", status_code=status.HTTP_400_BAD_REQUEST)
        
        # Sanitizar logs
        from_clean = from_number.replace('\n', '').replace('\r', '')
        body_clean = body.replace('\n', ' ').replace('\r', ' ')[:100] + ('...' if len(body) > 100 else '')
        
        logger.info(f"📨 Webhook legacy: {from_clean} -> {body_clean}")
        
        # TODO: Integrar con el motor conversacional y memoria
        result = procesar_mensaje_entrante(from_number, body)
        
        if result.get('success'):
            logger.info(f"✅ Mensaje procesado exitosamente: {message_sid}")
            return PlainTextResponse("OK", status_code=status.HTTP_200_OK)
        else:
            logger.error(f"❌ Error procesando mensaje: {result.get('error')}")
            return PlainTextResponse("Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.exception(f"❌ Error en webhook legacy: {e}")
        return PlainTextResponse("Internal Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/health")
async def health_check():
    """Health check para el webhook legacy."""
    return {"status": "ok", "service": "Brenda Legacy Webhook", "note": "Use app/presentation/api/webhook.py for production"}

# TODO: Proteger endpoint y validar autenticidad de Twilio 