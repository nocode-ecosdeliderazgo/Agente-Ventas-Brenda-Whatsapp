"""
Webhook handler para recibir mensajes de Twilio WhatsApp.
"""
import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.infrastructure.openai.client import OpenAIClient
from app.application.usecases.process_incoming_message import ProcessIncomingMessageUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from memory.lead_memory import MemoryManager

logger = logging.getLogger(__name__)

# Crear instancia de FastAPI
app = FastAPI(
    title="Bot Brenda - Webhook WhatsApp",
    description="Webhook para recibir mensajes de WhatsApp via Twilio",
    version="1.0.0"
)

# Instanciar dependencias
twilio_client = TwilioWhatsAppClient()

# Crear manager de memoria y caso de uso
memory_manager = MemoryManager(memory_dir="memorias")
memory_use_case = ManageUserMemoryUseCase(memory_manager)

# Intentar inicializar sistema completo
try:
    # Inicializar cliente OpenAI
    openai_client = OpenAIClient()
    intent_analyzer = AnalyzeMessageIntentUseCase(openai_client, memory_use_case)
    
    # Intentar inicializar sistema de cursos
    course_query_use_case = None
    try:
        from app.application.usecases.query_course_information import QueryCourseInformationUseCase
        course_query_use_case = QueryCourseInformationUseCase()
        
        # Inicializar conexión a BD de cursos en background
        course_init_success = False
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            course_init_success = loop.run_until_complete(course_query_use_case.initialize())
            loop.close()
        except Exception as course_init_error:
            logger.warning(f"⚠️ No se pudo inicializar sistema de cursos: {course_init_error}")
            course_query_use_case = None
        
        if course_init_success:
            logger.info("✅ Sistema de consulta de cursos inicializado")
        else:
            logger.warning("⚠️ Sistema de cursos no disponible, usando respuestas estándar")
            course_query_use_case = None
            
    except ImportError as e:
        logger.warning(f"⚠️ Dependencias de PostgreSQL no disponibles: {e}")
        course_query_use_case = None
    
    # Crear generador de respuestas inteligentes (con o sin sistema de cursos)
    intelligent_response_use_case = GenerateIntelligentResponseUseCase(
        intent_analyzer, twilio_client, course_query_use_case
    )
    
    # Crear caso de uso de procesamiento con capacidades inteligentes
    process_message_use_case = ProcessIncomingMessageUseCase(
        twilio_client, memory_use_case, intelligent_response_use_case
    )
    
    if course_query_use_case:
        logger.info("✅ Sistema inteligente completo (OpenAI + Cursos) inicializado correctamente")
    else:
        logger.info("✅ Sistema inteligente básico (OpenAI sin BD de cursos) inicializado correctamente")
    
except Exception as e:
    logger.warning(f"⚠️ No se pudo inicializar OpenAI, usando modo básico: {e}")
    
    # Crear caso de uso de procesamiento básico sin IA
    process_message_use_case = ProcessIncomingMessageUseCase(twilio_client, memory_use_case)
    
    logger.info("📱 Sistema básico (sin OpenAI ni BD de cursos) inicializado correctamente")


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