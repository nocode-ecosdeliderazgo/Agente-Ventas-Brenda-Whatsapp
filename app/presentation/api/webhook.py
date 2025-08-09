"""
Webhook handler para recibir mensajes de Twilio WhatsApp.
"""
import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

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
from app.application.usecases.detect_ad_hashtags_use_case import DetectAdHashtagsUseCase
from app.application.usecases.process_ad_flow_use_case import ProcessAdFlowUseCase
from app.application.usecases.advisor_referral_use_case import AdvisorReferralUseCase
from app.application.usecases.faq_flow_use_case import FAQFlowUseCase
from app.application.usecases.threads_integration_use_case import ThreadsIntegrationUseCase
from app.presentation.api.webhook_openai import openai_webhook_handler

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

# Configurar servir archivos estáticos desde la carpeta resources
# Obtener path absoluto del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
resources_path = os.path.join(project_root, "resources")

print(f"🔍 Buscando resources en: {resources_path}")
if os.path.exists(resources_path):
    app.mount("/resources", StaticFiles(directory=resources_path), name="resources")
    print(f"📁 ✅ Archivos estáticos montados desde: {resources_path}")
    # Listar archivos para debug
    course_materials_path = os.path.join(resources_path, "course_materials")
    if os.path.exists(course_materials_path):
        files = os.listdir(course_materials_path)
        print(f"📂 Archivos disponibles: {files}")
    else:
        print(f"⚠️ Carpeta course_materials no encontrada")
else:
    print(f"❌ Carpeta resources no encontrada en: {resources_path}")

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
detect_ad_hashtags_use_case = None
process_ad_flow_use_case = None
advisor_referral_use_case = None
faq_flow_use_case = None
threads_integration_use_case = None

@app.on_event("startup")
async def startup_event():
    """Evento de startup para inicializar todas las dependencias."""
    global twilio_client, memory_use_case, intent_analyzer, course_query_use_case, intelligent_response_use_case, process_message_use_case, privacy_flow_use_case, tool_activation_use_case, course_announcement_use_case, detect_ad_hashtags_use_case, process_ad_flow_use_case, advisor_referral_use_case, faq_flow_use_case, threads_integration_use_case
    
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
            # Crear db_client y course_repository como en test_webhook_simulation.py
            db_client = DatabaseClient()
            course_repository = CourseRepository()
            
            # Conectar la instancia global de base de datos (COMO EN test_webhook_simulation.py)
            from app.infrastructure.database.client import database_client
            await database_client.connect()
            
            # QueryCourseInformationUseCase no necesita parámetros adicionales
            course_query_use_case = QueryCourseInformationUseCase()
            
            # Inicializar el sistema de cursos (COMO EN test_webhook_simulation.py)
            course_db_initialized = await course_query_use_case.initialize()
            
            if course_db_initialized:
                debug_print("✅ Sistema de cursos PostgreSQL inicializado correctamente", "startup", "webhook.py")
            else:
                debug_print("⚠️ Sistema de cursos PostgreSQL no disponible, usando modo básico", "startup", "webhook.py")
                course_query_use_case = None
                
        except Exception as e:
            debug_print(f"⚠️ Error inicializando PostgreSQL: {e}", "startup", "webhook.py")
            debug_print("🔄 Continuando sin sistema de cursos...", "startup", "webhook.py")
            course_query_use_case = None
            course_repository = None
            db_client = None
        
        # Crear generador de respuestas inteligentes (sin sistema de cursos)
        debug_print("🧩 Creando generador de respuestas inteligentes...", "startup", "webhook.py")
        try:
            intelligent_response_use_case = GenerateIntelligentResponseUseCase(
                intent_analyzer, 
                twilio_client, 
                openai_client, 
                memory_use_case, # Añadido
                db_client,
                course_repository,
                course_query_use_case
            )
            debug_print("✅ Generador de respuestas inteligentes creado", "startup", "webhook.py")
        except Exception as e:
            debug_print(f"⚠️ Error creando generador inteligente: {e}", "startup", "webhook.py")
            intelligent_response_use_case = None
        
        # Inicializar sistema de herramientas de conversión
        debug_print("🛠️ Inicializando sistema de herramientas de conversión...", "startup", "webhook.py")
        try:
            tool_activation_use_case = ToolActivationUseCase()
            debug_print("✅ Sistema de herramientas inicializado correctamente", "startup", "webhook.py")
        except Exception as e:
            debug_print(f"⚠️ Error con herramientas: {e}", "startup", "webhook.py")
            tool_activation_use_case = None
        
        # Inicializar sistema de anuncios de cursos
        debug_print("📚 Inicializando sistema de anuncios de cursos...", "startup", "webhook.py")
        course_announcement_use_case = CourseAnnouncementUseCase(
            course_query_use_case, 
            memory_use_case, 
            twilio_client
        )
        debug_print("✅ Sistema de anuncios de cursos inicializado correctamente", "startup", "webhook.py")

        # Inicializar flujo de privacidad AHORA que course_announcement_use_case existe
        debug_print("🔐 Inicializando flujo de privacidad...", "startup", "webhook.py")
        privacy_flow_use_case = PrivacyFlowUseCase(memory_use_case, twilio_client, course_announcement_use_case)
        debug_print("✅ Flujo de privacidad inicializado correctamente", "startup", "webhook.py")
        
        # Inicializar sistema de flujo de anuncios
        debug_print("📢 Inicializando sistema de flujo de anuncios...", "startup", "webhook.py")
        detect_ad_hashtags_use_case = DetectAdHashtagsUseCase()
        process_ad_flow_use_case = ProcessAdFlowUseCase(
            memory_use_case, 
            privacy_flow_use_case, 
            course_query_use_case,
            twilio_client
        )
        debug_print("✅ Sistema de flujo de anuncios inicializado correctamente", "startup", "webhook.py")
        
        # Inicializar flujo de bienvenida genérico
        debug_print("🎯 Inicializando flujo de bienvenida genérico...", "startup", "webhook.py")
        try:
            welcome_flow_use_case = WelcomeFlowUseCase(
                privacy_flow_use_case, course_query_use_case, memory_use_case, twilio_client, course_announcement_use_case
            )
            debug_print("✅ Flujo de bienvenida genérico inicializado correctamente", "startup", "webhook.py")
        except Exception as e:
            debug_print(f"⚠️ Error con flujo de bienvenida: {e}", "startup", "webhook.py")
            welcome_flow_use_case = None
        
        # Inicializar sistema de referencia a asesores
        debug_print("👨‍💼 Inicializando sistema de referencia a asesores...", "startup", "webhook.py")
        try:
            advisor_referral_use_case = AdvisorReferralUseCase(twilio_client)
            debug_print("✅ Sistema de referencia a asesores inicializado correctamente", "startup", "webhook.py")
        except Exception as e:
            debug_print(f"⚠️ Error con sistema de asesores: {e}", "startup", "webhook.py")
            advisor_referral_use_case = None
        
        # Inicializar sistema de FAQ
        debug_print("❓ Inicializando sistema de FAQ...", "startup", "webhook.py")
        try:
            faq_flow_use_case = FAQFlowUseCase(memory_use_case, twilio_client)
            debug_print("✅ Sistema de FAQ inicializado correctamente", "startup", "webhook.py")
        except Exception as e:
            debug_print(f"⚠️ Error con sistema de FAQ: {e}", "startup", "webhook.py")
            faq_flow_use_case = None
        
        # Inicializar sistema de Threads Integration (OpenAI Assistants API)
        debug_print("🧵 Verificando configuración de OpenAI Threads...", "startup", "webhook.py")
        try:
            if ThreadsIntegrationUseCase.is_enabled():
                debug_print("🧵 ASSISTANT_ID configurado, inicializando Threads Integration...", "startup", "webhook.py")
                threads_integration_use_case = ThreadsIntegrationUseCase(twilio_client, memory_use_case)
                debug_print("✅ Sistema de Threads Integration inicializado correctamente", "startup", "webhook.py")
                
                # Inicializar webhook handler de OpenAI también
                debug_print("🎯 Inicializando OpenAI Webhook Handler...", "startup", "webhook.py")
                try:
                    openai_handler_success = await openai_webhook_handler.initialize()
                    if openai_handler_success:
                        debug_print("✅ OpenAI Webhook Handler inicializado correctamente", "startup", "webhook.py")
                    else:
                        debug_print("⚠️ Error inicializando OpenAI Webhook Handler", "startup", "webhook.py")
                except Exception as webhook_error:
                    debug_print(f"⚠️ Error con OpenAI Webhook Handler: {webhook_error}", "startup", "webhook.py")
            else:
                debug_print("ℹ️ ASSISTANT_ID no configurado, Threads Integration deshabilitado", "startup", "webhook.py")
                threads_integration_use_case = None
        except Exception as e:
            debug_print(f"⚠️ Error inicializando Threads Integration: {e}", "startup", "webhook.py")
            debug_print("🔄 Continuando con flujo tradicional...", "startup", "webhook.py")
            threads_integration_use_case = None
        
        # Crear caso de uso de procesamiento con capacidades inteligentes
        debug_print("⚙️ Creando procesador de mensajes principal...", "startup", "webhook.py")
        process_message_use_case = ProcessIncomingMessageUseCase(
            twilio_client, 
            memory_use_case, 
            intelligent_response_use_case, 
            privacy_flow_use_case, 
            tool_activation_use_case,
            course_announcement_use_case,
            detect_ad_hashtags_use_case=detect_ad_hashtags_use_case,
            process_ad_flow_use_case=process_ad_flow_use_case,
            welcome_flow_use_case=welcome_flow_use_case,
            advisor_referral_use_case=advisor_referral_use_case,
            faq_flow_use_case=faq_flow_use_case
        )
        debug_print("✅ Procesador de mensajes principal creado", "startup", "webhook.py")
        
        debug_print("🎉 SISTEMA BÁSICO: OpenAI + Memoria local inicializado correctamente", "startup", "webhook.py")
        
    except Exception as e:
        debug_print(f"❌ ERROR INICIALIZANDO OPENAI: {e}", "startup", "webhook.py")
        debug_print("🔄 Iniciando modo FALLBACK (sin OpenAI)...", "startup", "webhook.py")
        
        # Crear sistema básico sin OpenAI
        try:
            # Intentar crear course_query_use_case básico
            course_query_use_case = QueryCourseInformationUseCase()
            debug_print("✅ Sistema de cursos básico inicializado", "startup", "webhook.py")
        except Exception as db_error:
            debug_print(f"⚠️ Error con BD: {db_error}", "startup", "webhook.py")
            course_query_use_case = None
        
        # Crear sistema de anuncios de cursos básico
        course_announcement_use_case = CourseAnnouncementUseCase(
            course_query_use_case, memory_use_case, twilio_client
        )
        
        # Crear flujo de bienvenida básico
        welcome_flow_use_case = WelcomeFlowUseCase(
            privacy_flow_use_case, course_query_use_case, memory_use_case, twilio_client, course_announcement_use_case
        )
        
        # Crear sistema de referencia a asesores básico
        advisor_referral_use_case = AdvisorReferralUseCase(twilio_client)
        
        # Crear sistema de FAQ básico
        faq_flow_use_case = FAQFlowUseCase(memory_use_case, twilio_client)
        
        # Crear caso de uso de procesamiento básico
        process_message_use_case = ProcessIncomingMessageUseCase(
            twilio_client, 
            memory_use_case, 
            None,  # intelligent_response_use_case
            privacy_flow_use_case, 
            None,  # tool_activation_use_case
            course_announcement_use_case,
            welcome_flow_use_case=welcome_flow_use_case,
            advisor_referral_use_case=advisor_referral_use_case,
            faq_flow_use_case=faq_flow_use_case
        )
        
        debug_print("⚠️ SISTEMA FALLBACK: Funcionalidad básica disponible", "startup", "webhook.py")
    
    debug_print("🎯 SISTEMA LISTO PARA RECIBIR MENSAJES", "startup", "webhook.py")


@app.get("/")
async def health_check():
    """Endpoint de health check."""
    health_info = {
        "status": "ok",
        "service": "Bot Brenda Webhook",
        "environment": settings.app_environment,
        "threads_integration": {
            "enabled": threads_integration_use_case is not None,
            "assistant_id_configured": bool(getattr(settings, 'assistant_id', None))
        }
    }
    
    # Añadir estado detallado de threads si está habilitado
    if threads_integration_use_case:
        try:
            threads_health = await threads_integration_use_case.health_check()
            health_info["threads_integration"].update(threads_health)
        except Exception as e:
            health_info["threads_integration"]["health_check_error"] = str(e)
    
    return health_info


@app.post("/")
async def root_webhook(request: Request):
    """
    Webhook en la ruta raíz para manejar webhooks de Twilio.
    Redirige al mismo handler que /webhook.
    """
    # Usar el mismo handler que /webhook
    return await whatsapp_webhook(request)


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Webhook principal para mensajes de WhatsApp.
    """
    try:
        # Obtener datos del webhook
        form_data = await request.form()
        
        # Extraer información del mensaje
        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "")
        message_sid = form_data.get("MessageSid", "")
        
        debug_print(f"📨 MENSAJE RECIBIDO!", "whatsapp_webhook", "webhook.py")
        debug_print(f"📱 Desde: {from_number}", "whatsapp_webhook", "webhook.py")
        debug_print(f"💬 Texto: '{message_body}'", "whatsapp_webhook", "webhook.py")
        debug_print(f"🆔 SID: {message_sid}", "whatsapp_webhook", "webhook.py")
        
        # Preparar datos del webhook
        debug_print(f"📦 Preparando datos del webhook...", "whatsapp_webhook", "webhook.py")
        webhook_data = {
            "MessageSid": message_sid,
            "From": from_number,
            "To": "whatsapp:+14155238886",  # Número de Twilio
            "Body": message_body
        }
        debug_print(f"✅ Datos del webhook preparados correctamente", "whatsapp_webhook", "webhook.py")
        
        # Procesar mensaje - decidir entre Threads Integration o flujo tradicional
        if threads_integration_use_case:
            debug_print(f"🧵 PROCESANDO CON THREADS INTEGRATION...", "whatsapp_webhook", "webhook.py")
            result = await threads_integration_use_case.execute(webhook_data)
        else:
            debug_print(f"🚀 PROCESANDO CON FLUJO TRADICIONAL...", "whatsapp_webhook", "webhook.py")
            result = await process_message_use_case.execute(webhook_data)
        
        # Mostrar resultado completo
        debug_print(f"📊 Resultado del procesamiento: {result}", "whatsapp_webhook", "webhook.py")
        
        # Mostrar respuesta enviada
        if result.get('response_sent') and result.get('response_text'):
            debug_print(f"📤 RESPUESTA ENVIADA A WHATSAPP:", "whatsapp_webhook", "webhook.py")
            debug_print(f"💬 Texto: '{result['response_text']}'", "whatsapp_webhook", "webhook.py")
            debug_print(f"🔗 SID: {result.get('response_sid', 'N/A')}", "whatsapp_webhook", "webhook.py")
        
        debug_print(f"✅ MENSAJE PROCESADO EXITOSAMENTE!", "whatsapp_webhook", "webhook.py")
        debug_print(f"📤 Respuesta enviada: {result.get('response_sent', False)}", "whatsapp_webhook", "webhook.py")
        debug_print(f"🔗 SID respuesta: {result.get('response_sid', 'N/A')}", "whatsapp_webhook", "webhook.py")
        
        return {"status": "success", "processed": True}
        
    except Exception as e:
        debug_print(f"❌ ERROR EN WEBHOOK: {str(e)}", "whatsapp_webhook", "webhook.py")
        return {"status": "error", "message": str(e)}


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


# === RUTAS DE OPENAI WEBHOOK ===

@app.post("/webhooks/openai")
async def openai_webhook_endpoint(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint para webhooks de OpenAI Assistants API.
    
    Permite manejo asíncrono de eventos de threads y runs.
    Configurar esta URL en OpenAI Platform como webhook URL.
    """
    import json
    from fastapi import HTTPException, BackgroundTasks
    
    try:
        # Leer payload completo
        payload = await request.body()
        
        # Verificar firma si está configurada
        signature = request.headers.get('openai-signature', '')
        if signature and not openai_webhook_handler.verify_signature(payload, signature):
            debug_print("❌ Firma de webhook OpenAI inválida", "openai_webhook_endpoint", "webhook.py")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parsear JSON
        try:
            event_data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError as e:
            debug_print(f"❌ Error parseando JSON de OpenAI: {e}", "openai_webhook_endpoint", "webhook.py")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        debug_print(f"📨 Evento OpenAI recibido: {event_data.get('type', 'unknown')}", "openai_webhook_endpoint", "webhook.py")
        
        # Procesar evento
        result = await openai_webhook_handler.handle_event(event_data, background_tasks)
        
        debug_print(f"✅ Evento OpenAI procesado: {result.get('status', 'unknown')}", "openai_webhook_endpoint", "webhook.py")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        debug_print(f"❌ Error en webhook OpenAI: {e}", "openai_webhook_endpoint", "webhook.py")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/webhooks/openai/health")
async def openai_webhook_health():
    """Health check específico para el webhook de OpenAI."""
    try:
        if not openai_webhook_handler.threads_adapter:
            return {
                "status": "disabled",
                "reason": "OpenAI webhook handler not initialized"
            }
        
        adapter_health = await openai_webhook_handler.threads_adapter.health_check()
        
        return {
            "status": "healthy" if adapter_health else "degraded",
            "handler_initialized": True,
            "adapter_health": adapter_health,
            "webhook_secret_configured": bool(openai_webhook_handler.webhook_secret),
            "assistant_id_configured": bool(getattr(settings, 'assistant_id', None))
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


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