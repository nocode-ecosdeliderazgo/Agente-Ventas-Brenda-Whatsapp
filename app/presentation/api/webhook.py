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
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.application.usecases.tool_activation_use_case import ToolActivationUseCase
from app.application.usecases.course_announcement_use_case import CourseAnnouncementUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.application.usecases.welcome_flow_use_case import WelcomeFlowUseCase
from memory.lead_memory import MemoryManager

logger = logging.getLogger(__name__)

def debug_print(message: str, function_name: str = "", file_name: str = "webhook.py"):
    """Print de debug visual para consola"""
    print(f"🔍 [{file_name}::{function_name}] {message}")

# Crear instancia de FastAPI
app = FastAPI(
    title="Bot Brenda - Webhook WhatsApp",
    description="Webhook para recibir mensajes de WhatsApp via Twilio",
    version="1.0.0"
)

# Variables globales para las dependencias
twilio_client = None
memory_use_case = None
intent_analyzer = None
course_query_use_case = None
intelligent_response_use_case = None
process_message_use_case = None
privacy_flow_use_case = None
tool_activation_use_case = None
course_announcement_use_case = None
welcome_flow_use_case = None

@app.on_event("startup")
async def startup_event():
    """Evento de startup para inicializar todas las dependencias."""
    global twilio_client, memory_use_case, intent_analyzer, course_query_use_case, intelligent_response_use_case, process_message_use_case, privacy_flow_use_case, tool_activation_use_case, course_announcement_use_case
    
    debug_print("🚀 INICIANDO SISTEMA BOT BRENDA...", "startup", "webhook.py")
    
    # Inicializar cliente Twilio
    debug_print("Inicializando cliente Twilio...", "startup", "webhook.py")
    twilio_client = TwilioWhatsAppClient()
    debug_print("✅ Cliente Twilio inicializado correctamente", "startup", "webhook.py")

    # Crear manager de memoria y caso de uso
    debug_print("Inicializando sistema de memoria...", "startup", "webhook.py")
    memory_manager = MemoryManager(memory_dir="memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    debug_print("✅ Sistema de memoria inicializado correctamente", "startup", "webhook.py")

    # Inicializar flujo de privacidad
    debug_print("🔐 Inicializando flujo de privacidad...", "startup", "webhook.py")
    privacy_flow_use_case = PrivacyFlowUseCase(memory_use_case, twilio_client)
    debug_print("✅ Flujo de privacidad inicializado correctamente", "startup", "webhook.py")

    # Inicializar sistema con OpenAI (sin PostgreSQL por ahora)
    try:
        debug_print("🤖 Inicializando cliente OpenAI...", "startup", "webhook.py")
        # Inicializar cliente OpenAI
        openai_client = OpenAIClient()
        debug_print("✅ Cliente OpenAI inicializado correctamente", "startup", "webhook.py")
        
        debug_print("🧠 Inicializando analizador de intención...", "startup", "webhook.py")
        intent_analyzer = AnalyzeMessageIntentUseCase(openai_client, memory_use_case)
        debug_print("✅ Analizador de intención inicializado correctamente", "startup", "webhook.py")
        
        # Inicializar sistema de cursos PostgreSQL
        debug_print("📚 Inicializando sistema de cursos PostgreSQL...", "startup", "webhook.py")
        from app.infrastructure.database.client import DatabaseClient
        from app.infrastructure.database.repositories.course_repository import CourseRepository
        
        try:
            db_client = DatabaseClient()
            course_repo = CourseRepository(db_client)
            course_query_use_case = QueryCourseInformationUseCase(course_repo)
            debug_print("✅ Sistema de cursos PostgreSQL inicializado correctamente", "startup", "webhook.py")
        except Exception as e:
            debug_print(f"⚠️ Error inicializando PostgreSQL: {e}", "startup", "webhook.py")
            debug_print("🔄 Continuando sin sistema de cursos...", "startup", "webhook.py")
            course_query_use_case = None
        
        # Crear generador de respuestas inteligentes (sin sistema de cursos)
        debug_print("🧩 Creando generador de respuestas inteligentes...", "startup", "webhook.py")
        intelligent_response_use_case = GenerateIntelligentResponseUseCase(
            intent_analyzer, twilio_client, openai_client, course_query_use_case
        )
        debug_print("✅ Generador de respuestas inteligentes creado", "startup", "webhook.py")
        
        # Inicializar sistema de herramientas de conversión
        debug_print("🛠️ Inicializando sistema de herramientas de conversión...", "startup", "webhook.py")
        tool_activation_use_case = ToolActivationUseCase()
        debug_print("✅ Sistema de herramientas inicializado correctamente", "startup", "webhook.py")
        
        # Inicializar sistema de anuncios de cursos
        debug_print("📚 Inicializando sistema de anuncios de cursos...", "startup", "webhook.py")
        course_announcement_use_case = CourseAnnouncementUseCase(
            course_query_use_case, memory_use_case, twilio_client
        )
        debug_print("✅ Sistema de anuncios de cursos inicializado correctamente", "startup", "webhook.py")
        
        # Inicializar flujo de bienvenida genérico
        debug_print("🎯 Inicializando flujo de bienvenida genérico...", "startup", "webhook.py")
        welcome_flow_use_case = WelcomeFlowUseCase(
            privacy_flow_use_case, course_query_use_case, memory_use_case, twilio_client
        )
        debug_print("✅ Flujo de bienvenida genérico inicializado correctamente", "startup", "webhook.py")
        
        # Crear caso de uso de procesamiento con capacidades inteligentes
        debug_print("⚙️ Creando procesador de mensajes principal...", "startup", "webhook.py")
        process_message_use_case = ProcessIncomingMessageUseCase(
            twilio_client, memory_use_case, intelligent_response_use_case, privacy_flow_use_case, tool_activation_use_case, course_announcement_use_case, welcome_flow_use_case=welcome_flow_use_case
        )
        debug_print("✅ Procesador de mensajes principal creado", "startup", "webhook.py")
        
        debug_print("🎉 SISTEMA BÁSICO: OpenAI + Memoria local inicializado correctamente", "startup", "webhook.py")
        
    except Exception as e:
        debug_print(f"❌ ERROR INICIALIZANDO OPENAI: {e}", "startup", "webhook.py")
        debug_print("🔄 Iniciando modo FALLBACK (sin OpenAI)...", "startup", "webhook.py")
        
        # Crear sistema de anuncios de cursos básico (sin OpenAI)
        course_announcement_use_case = CourseAnnouncementUseCase(
            None, memory_use_case, twilio_client  # Sin course_query_use_case
        )
        
        # Crear caso de uso de procesamiento básico sin IA
        process_message_use_case = ProcessIncomingMessageUseCase(
            twilio_client, memory_use_case, None, privacy_flow_use_case, None, course_announcement_use_case
        )
        
        debug_print("⚠️ SISTEMA FALLBACK: Sin OpenAI ni BD de cursos inicializado correctamente", "startup", "webhook.py")
    
    debug_print("🎯 SISTEMA LISTO PARA RECIBIR MENSAJES", "startup", "webhook.py")


@app.get("/")
async def health_check():
    """Endpoint de health check."""
    return {
        "status": "ok",
        "service": "Bot Brenda Webhook",
        "environment": settings.app_environment
    }


@app.post("/")
async def root_webhook(
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
    Webhook en la ruta raíz para manejar webhooks de Twilio.
    Redirige al mismo handler que /webhook.
    """
    # Usar el mismo handler que /webhook
    return await whatsapp_webhook(
        request, background_tasks, MessageSid, From, To, Body,
        AccountSid, MessagingServiceSid, NumMedia, ProfileName, WaId
    )


@app.post("/webhook")
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
        if False:  # Deshabilitado temporalmente para desarrollo
            debug_print("🔐 Verificando firma de seguridad del webhook...", "whatsapp_webhook", "webhook.py")
            
            # Debug: imprimir path de la request
            request_path = request.url.path
            debug_print(f"🛣️ PATH de la request: '{request_path}'", "whatsapp_webhook", "webhook.py")
            
            signature = request.headers.get('X-Twilio-Signature', '')
            
            # URL FIJA que coincide con la configurada en Twilio Console
            # Debe ser exactamente igual a la URL que pusiste en "When a message comes in"
            url_for_validation = "https://lightly-right-toucan.ngrok-free.app"
            debug_print(f"🌐 URL para validación (FIJA): '{url_for_validation}'", "whatsapp_webhook", "webhook.py")
            debug_print(f"📍 URL local (NO USAR): '{str(request.url)}'", "whatsapp_webhook", "webhook.py")
            
            # Obtener todos los parámetros del formulario
            form_data = await request.form()
            params = dict(form_data)
            
            # Debug: imprimir todos los campos del formulario
            debug_print(f"📋 FORM DATA de Twilio:\n{params}", "whatsapp_webhook", "webhook.py")
            
            # Debug: verificar campos específicos
            debug_print(f"🔍 Body: '{params.get('Body', 'NO_BODY')}'", "whatsapp_webhook", "webhook.py")
            debug_print(f"🔍 From: '{params.get('From', 'NO_FROM')}'", "whatsapp_webhook", "webhook.py")
            debug_print(f"🔍 To: '{params.get('To', 'NO_TO')}'", "whatsapp_webhook", "webhook.py")
            debug_print(f"🔍 Signature: '{signature}'", "whatsapp_webhook", "webhook.py")
            
            if not twilio_client.verify_webhook_signature(signature, url_for_validation, params):
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
        
        # Procesar mensaje de forma síncrona (sin background tasks)
        debug_print("🚀 INICIANDO PROCESAMIENTO SÍNCRONO...", "whatsapp_webhook", "webhook.py")
        result = await process_message_use_case.execute(webhook_data)
        debug_print(f"📊 Resultado del procesamiento: {result}", "whatsapp_webhook", "webhook.py")
        
        if result['success'] and result['processed']:
            debug_print(
                f"✅ MENSAJE PROCESADO EXITOSAMENTE!\n"
                f"📤 Respuesta enviada: {result['response_sent']}\n"
                f"🔗 SID respuesta: {result.get('response_sid', 'N/A')}", 
                "whatsapp_webhook", "webhook.py"
            )
            # Responder solo confirmación (sin "PROCESSED")
            return PlainTextResponse("", status_code=200)
        else:
            debug_print(f"⚠️ MENSAJE NO PROCESADO: {result}", "whatsapp_webhook", "webhook.py")
            # Responder solo confirmación (sin "ERROR")
            return PlainTextResponse("", status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        debug_print(f"💥 ERROR EN WEBHOOK: {e}", "whatsapp_webhook", "webhook.py")
        # Siempre responder 200 a Twilio para evitar reintentos
        return PlainTextResponse("ERROR", status_code=200)


@app.get("/webhook")
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