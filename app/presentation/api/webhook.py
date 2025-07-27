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

def debug_print(message: str, function_name: str = "", file_name: str = "webhook.py"):
    """Print de debug visual para consola"""
    print(f"\n{'='*80}")
    print(f"🔍 DEBUG [{file_name}::{function_name}]")
    print(f"{'='*80}")
    print(f"📋 {message}")
    print(f"{'='*80}\n")

# Crear instancia de FastAPI
app = FastAPI(
    title="Bot Brenda - Webhook WhatsApp",
    description="Webhook para recibir mensajes de WhatsApp via Twilio",
    version="1.0.0"
)

# Instanciar dependencias
debug_print("Inicializando cliente Twilio...", "startup", "webhook.py")
twilio_client = TwilioWhatsAppClient()
debug_print("✅ Cliente Twilio inicializado correctamente", "startup", "webhook.py")

# Crear manager de memoria y caso de uso
debug_print("Inicializando sistema de memoria...", "startup", "webhook.py")
memory_manager = MemoryManager(memory_dir="memorias")
memory_use_case = ManageUserMemoryUseCase(memory_manager)
debug_print("✅ Sistema de memoria inicializado correctamente", "startup", "webhook.py")

# Intentar inicializar sistema completo
try:
    debug_print("🤖 Inicializando cliente OpenAI...", "startup", "webhook.py")
    # Inicializar cliente OpenAI
    openai_client = OpenAIClient()
    debug_print("✅ Cliente OpenAI inicializado correctamente", "startup", "webhook.py")
    
    debug_print("🧠 Inicializando analizador de intención...", "startup", "webhook.py")
    intent_analyzer = AnalyzeMessageIntentUseCase(openai_client, memory_use_case)
    debug_print("✅ Analizador de intención inicializado correctamente", "startup", "webhook.py")
    
    # Intentar inicializar sistema de cursos
    debug_print("🗄️ Intentando inicializar sistema de cursos PostgreSQL...", "startup", "webhook.py")
    course_query_use_case = None
    try:
        from app.application.usecases.query_course_information import QueryCourseInformationUseCase
        course_query_use_case = QueryCourseInformationUseCase()
        debug_print("📦 Clase QueryCourseInformationUseCase cargada", "startup", "webhook.py")
        
        # Inicializar conexión a BD de cursos en background
        course_init_success = False
        try:
            debug_print("🔌 Intentando conectar a PostgreSQL...", "startup", "webhook.py")
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            course_init_success = loop.run_until_complete(course_query_use_case.initialize())
            loop.close()
            
            if course_init_success:
                debug_print("✅ Conexión PostgreSQL establecida exitosamente", "startup", "webhook.py")
            else:
                debug_print("❌ Falló la conexión a PostgreSQL", "startup", "webhook.py")
                
        except Exception as course_init_error:
            debug_print(f"❌ Error conectando PostgreSQL: {course_init_error}", "startup", "webhook.py")
            course_query_use_case = None
        
        if course_init_success:
            debug_print("✅ Sistema de consulta de cursos inicializado", "startup", "webhook.py")
        else:
            debug_print("⚠️ Sistema de cursos no disponible, usando respuestas estándar", "startup", "webhook.py")
            course_query_use_case = None
            
    except ImportError as e:
        debug_print(f"❌ Dependencias de PostgreSQL no disponibles: {e}", "startup", "webhook.py")
        course_query_use_case = None
    
    # Crear generador de respuestas inteligentes (con o sin sistema de cursos)
    debug_print("🧩 Creando generador de respuestas inteligentes...", "startup", "webhook.py")
    intelligent_response_use_case = GenerateIntelligentResponseUseCase(
        intent_analyzer, twilio_client, course_query_use_case
    )
    debug_print("✅ Generador de respuestas inteligentes creado", "startup", "webhook.py")
    
    # Crear caso de uso de procesamiento con capacidades inteligentes
    debug_print("⚙️ Creando procesador de mensajes principal...", "startup", "webhook.py")
    process_message_use_case = ProcessIncomingMessageUseCase(
        twilio_client, memory_use_case, intelligent_response_use_case
    )
    debug_print("✅ Procesador de mensajes principal creado", "startup", "webhook.py")
    
    if course_query_use_case:
        debug_print("🎉 SISTEMA COMPLETO: OpenAI + PostgreSQL + Cursos inicializado correctamente", "startup", "webhook.py")
    else:
        debug_print("🎉 SISTEMA BÁSICO: OpenAI sin BD de cursos inicializado correctamente", "startup", "webhook.py")
    
except Exception as e:
    debug_print(f"❌ ERROR INICIALIZANDO OPENAI: {e}", "startup", "webhook.py")
    debug_print("🔄 Iniciando modo FALLBACK (sin OpenAI)...", "startup", "webhook.py")
    
    # Crear caso de uso de procesamiento básico sin IA
    process_message_use_case = ProcessIncomingMessageUseCase(twilio_client, memory_use_case)
    
    debug_print("⚠️ SISTEMA FALLBACK: Sin OpenAI ni BD de cursos inicializado correctamente", "startup", "webhook.py")


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
        debug_print(f"📨 MENSAJE RECIBIDO!\n📱 Desde: {From}\n💬 Texto: '{Body}'\n🆔 SID: {MessageSid}", "whatsapp_webhook", "webhook.py")
        
        # Verificar firma del webhook si está habilitado
        if settings.webhook_verify_signature:
            debug_print("🔐 Verificando firma de seguridad del webhook...", "whatsapp_webhook", "webhook.py")
            signature = request.headers.get('X-Twilio-Signature', '')
            url = str(request.url)
            
            # Obtener todos los parámetros del formulario
            form_data = await request.form()
            params = dict(form_data)
            
            if not twilio_client.verify_webhook_signature(signature, url, params):
                debug_print(f"❌ FIRMA INVÁLIDA desde {From}", "whatsapp_webhook", "webhook.py")
                raise HTTPException(status_code=403, detail="Invalid signature")
            else:
                debug_print("✅ Firma de webhook verificada correctamente", "whatsapp_webhook", "webhook.py")
        
        # Preparar datos del webhook
        debug_print("📦 Preparando datos del webhook...", "whatsapp_webhook", "webhook.py")
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
        debug_print("✅ Datos del webhook preparados correctamente", "whatsapp_webhook", "webhook.py")
        
        # Procesar mensaje en background para responder rápido a Twilio
        debug_print("🚀 Iniciando procesamiento en background...", "whatsapp_webhook", "webhook.py")
        background_tasks.add_task(
            process_message_in_background,
            webhook_data
        )
        
        # Responder inmediatamente a Twilio (requerido)
        debug_print("✅ Respondiendo OK a Twilio (200)", "whatsapp_webhook", "webhook.py")
        return PlainTextResponse("OK", status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        debug_print(f"💥 ERROR EN WEBHOOK: {e}", "whatsapp_webhook", "webhook.py")
        # Siempre responder 200 a Twilio para evitar reintentos
        return PlainTextResponse("ERROR", status_code=200)


async def process_message_in_background(webhook_data: Dict[str, Any]):
    """
    Procesa el mensaje en background para no bloquear la respuesta del webhook.
    
    Args:
        webhook_data: Datos del webhook de Twilio
    """
    try:
        debug_print("🔄 INICIANDO PROCESAMIENTO EN BACKGROUND", "process_message_in_background", "webhook.py")
        debug_print(f"📋 Datos recibidos: From={webhook_data.get('From')}, Body='{webhook_data.get('Body')}'", "process_message_in_background", "webhook.py")
        
        # Ejecutar caso de uso
        debug_print("⚙️ Ejecutando caso de uso principal (process_message_use_case)...", "process_message_in_background", "webhook.py")
        result = await process_message_use_case.execute(webhook_data)
        debug_print(f"📊 Resultado del procesamiento: {result}", "process_message_in_background", "webhook.py")
        
        if result['success'] and result['processed']:
            debug_print(
                f"✅ MENSAJE PROCESADO EXITOSAMENTE!\n"
                f"📤 Respuesta enviada: {result['response_sent']}\n"
                f"🔗 SID respuesta: {result.get('response_sid', 'N/A')}", 
                "process_message_in_background", "webhook.py"
            )
        else:
            debug_print(f"⚠️ MENSAJE NO PROCESADO: {result}", "process_message_in_background", "webhook.py")
            
    except Exception as e:
        debug_print(f"💥 ERROR EN BACKGROUND PROCESSING: {e}", "process_message_in_background", "webhook.py")
        import traceback
        debug_print(f"📜 Traceback: {traceback.format_exc()}", "process_message_in_background", "webhook.py")


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