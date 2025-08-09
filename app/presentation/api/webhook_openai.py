"""
Webhook para eventos de OpenAI Assistants API.
Permite manejo asíncrono de eventos de threads, runs y tool calling.
"""
import logging
import hmac
import hashlib
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.infrastructure.openai.threads_adapter import ThreadsAdapter
from app.infrastructure.database.repositories.oa_threads_map_repository import OAThreadsMapRepository
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase

logger = logging.getLogger(__name__)


def debug_print(message: str, function_name: str = "", file_name: str = "webhook_openai.py"):
    """Print de debug visual para consola"""
    print(f"🎯 [{file_name}::{function_name}] {message}")


class OpenAIWebhookHandler:
    """
    Manejador de webhooks de OpenAI para eventos de Assistants API.
    
    Permite respuestas más rápidas y mejor control sobre el ciclo de vida
    de threads, runs y tool calling.
    """
    
    def __init__(self):
        """Inicializa el manejador de webhooks."""
        self.threads_adapter = None
        self.threads_repo = None
        self.twilio_client = None
        self.memory_use_case = None
        
        # Configurar webhook secret para validación de firma
        self.webhook_secret = getattr(settings, 'openai_webhook_secret', None)
        if self.webhook_secret:
            debug_print(f"✅ Webhook secret configurado", "__init__")
        else:
            debug_print(f"⚠️ Webhook secret no configurado - verificación de firma deshabilitada", "__init__")
    
    async def initialize(self):
        """Inicializa dependencias del webhook handler."""
        try:
            debug_print(f"🚀 Inicializando OpenAI Webhook Handler...", "initialize")
            
            # Inicializar componentes básicos
            self.threads_repo = OAThreadsMapRepository()
            await self.threads_repo.ensure_table_exists()
            
            self.twilio_client = TwilioWhatsAppClient()
            
            # Inicializar memoria
            from memory.lead_memory import MemoryManager
            memory_manager = MemoryManager(memory_dir="memorias")
            self.memory_use_case = ManageUserMemoryUseCase(memory_manager)
            
            # Verificar que threads integration esté habilitado
            if not getattr(settings, 'assistant_id', None):
                raise ValueError("ASSISTANT_ID no configurado - webhook OpenAI requiere threads integration")
            
            self.threads_adapter = ThreadsAdapter()
            
            debug_print(f"✅ OpenAI Webhook Handler inicializado correctamente", "initialize")
            return True
            
        except Exception as e:
            debug_print(f"❌ Error inicializando webhook handler: {e}", "initialize")
            return False
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verifica la firma del webhook de OpenAI.
        
        Args:
            payload: Contenido del webhook en bytes
            signature: Firma recibida en el header
        
        Returns:
            True si la firma es válida
        """
        if not self.webhook_secret:
            debug_print(f"⚠️ No hay webhook secret - saltando verificación", "verify_signature")
            return True
        
        try:
            # OpenAI envía firma como sha256=<hash>
            if not signature.startswith('sha256='):
                debug_print(f"❌ Formato de firma inválido", "verify_signature")
                return False
            
            expected_signature = signature[7:]  # Remover 'sha256=' prefix
            
            # Calcular firma esperada
            computed_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Comparación segura
            is_valid = hmac.compare_digest(computed_signature, expected_signature)
            
            if is_valid:
                debug_print(f"✅ Firma verificada correctamente", "verify_signature")
            else:
                debug_print(f"❌ Firma inválida", "verify_signature")
            
            return is_valid
            
        except Exception as e:
            debug_print(f"❌ Error verificando firma: {e}", "verify_signature")
            return False
    
    async def handle_event(self, event_data: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """
        Maneja un evento de OpenAI webhook.
        
        Args:
            event_data: Datos del evento
            background_tasks: FastAPI background tasks
        
        Returns:
            Respuesta del procesamiento
        """
        try:
            event_type = event_data.get('type')
            data = event_data.get('data', {})
            
            debug_print(f"📨 Evento recibido: {event_type}", "handle_event")
            debug_print(f"📊 Data keys: {list(data.keys()) if data else 'none'}", "handle_event")
            
            # Manejar diferentes tipos de eventos
            if event_type == 'thread.run.created':
                return await self._handle_run_created(data, background_tasks)
            
            elif event_type == 'thread.run.requires_action':
                return await self._handle_requires_action(data, background_tasks)
            
            elif event_type == 'thread.run.completed':
                return await self._handle_run_completed(data, background_tasks)
            
            elif event_type == 'thread.run.failed':
                return await self._handle_run_failed(data, background_tasks)
            
            elif event_type == 'thread.run.cancelled':
                return await self._handle_run_cancelled(data, background_tasks)
            
            else:
                debug_print(f"ℹ️ Evento no manejado: {event_type}", "handle_event")
                return {"status": "ignored", "event_type": event_type}
                
        except Exception as e:
            debug_print(f"❌ Error manejando evento: {e}", "handle_event")
            return {"status": "error", "error": str(e)}
    
    async def _handle_run_created(self, data: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Maneja evento thread.run.created."""
        debug_print(f"🚀 Run creado: {data.get('id')}", "_handle_run_created")
        
        # Por ahora solo logging, el polling normal maneja la lógica
        return {"status": "logged"}
    
    async def _handle_requires_action(self, data: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Maneja evento thread.run.requires_action."""
        try:
            run_id = data.get('id')
            thread_id = data.get('thread_id')
            
            debug_print(f"🔧 Run requiere acción - Thread: {thread_id}, Run: {run_id}", "_handle_requires_action")
            
            # Programar procesamiento en background
            background_tasks.add_task(
                self._process_requires_action_background,
                thread_id,
                run_id,
                data
            )
            
            return {"status": "scheduled", "thread_id": thread_id, "run_id": run_id}
            
        except Exception as e:
            debug_print(f"❌ Error en requires_action: {e}", "_handle_requires_action")
            return {"status": "error", "error": str(e)}
    
    async def _process_requires_action_background(self, thread_id: str, run_id: str, data: Dict[str, Any]):
        """Procesa tool calling en background task."""
        try:
            debug_print(f"🔧 Procesando tool calls en background - Thread: {thread_id}", "_process_requires_action_background")
            
            # Obtener run actual para procesar tool calls
            run = await self.threads_adapter.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            # Procesar tool calls usando el adapter
            success = await self.threads_adapter._handle_requires_action(thread_id, run_id, run)
            
            if success:
                debug_print(f"✅ Tool calls procesados correctamente", "_process_requires_action_background")
            else:
                debug_print(f"❌ Error procesando tool calls", "_process_requires_action_background")
                
        except Exception as e:
            debug_print(f"❌ Error en background processing: {e}", "_process_requires_action_background")
    
    async def _handle_run_completed(self, data: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Maneja evento thread.run.completed."""
        try:
            run_id = data.get('id')
            thread_id = data.get('thread_id')
            
            debug_print(f"✅ Run completado - Thread: {thread_id}, Run: {run_id}", "_handle_run_completed")
            
            # Programar envío de respuesta en background
            background_tasks.add_task(
                self._send_response_background,
                thread_id,
                run_id
            )
            
            return {"status": "response_scheduled", "thread_id": thread_id, "run_id": run_id}
            
        except Exception as e:
            debug_print(f"❌ Error en run_completed: {e}", "_handle_run_completed")
            return {"status": "error", "error": str(e)}
    
    async def _send_response_background(self, thread_id: str, run_id: str):
        """Envía respuesta del assistant a WhatsApp en background."""
        try:
            debug_print(f"📤 Enviando respuesta en background - Thread: {thread_id}", "_send_response_background")
            
            # Obtener último mensaje del assistant
            assistant_response = await self.threads_adapter.fetch_last_assistant_message(thread_id)
            
            if not assistant_response:
                debug_print(f"⚠️ No se obtuvo respuesta del assistant", "_send_response_background")
                return
            
            # Buscar número de WhatsApp asociado al thread
            user_phone = await self.threads_repo.get_user_phone_by_thread_id(thread_id)
            
            if not user_phone:
                debug_print(f"⚠️ No se encontró número de teléfono para thread {thread_id}", "_send_response_background")
                return
            
            # Enviar mensaje via WhatsApp
            response_sid = await self.twilio_client.send_message(
                to=user_phone,
                body=assistant_response
            )
            
            if response_sid:
                debug_print(f"✅ Respuesta enviada a {user_phone}: {response_sid}", "_send_response_background")
                
                # Actualizar memoria como backup
                await self._update_memory_backup(user_phone, assistant_response, {
                    "source": "openai_webhook",
                    "thread_id": thread_id,
                    "run_id": run_id
                })
            else:
                debug_print(f"❌ Error enviando respuesta a {user_phone}", "_send_response_background")
                
        except Exception as e:
            debug_print(f"❌ Error enviando respuesta: {e}", "_send_response_background")
    
    async def _handle_run_failed(self, data: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Maneja evento thread.run.failed."""
        debug_print(f"❌ Run falló: {data.get('id')} - {data.get('last_error', {}).get('message', 'Error desconocido')}", "_handle_run_failed")
        
        # Aquí podrías implementar lógica de retry o notificación
        return {"status": "logged"}
    
    async def _handle_run_cancelled(self, data: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Maneja evento thread.run.cancelled."""
        debug_print(f"⚠️ Run cancelado: {data.get('id')}", "_handle_run_cancelled")
        
        return {"status": "logged"}
    
    async def _update_memory_backup(self, user_phone: str, response_text: str, metadata: Dict[str, Any]):
        """Actualiza memoria local como backup."""
        try:
            user_memory = await self.memory_use_case.load_memory(user_phone)
            
            # Incrementar contadores
            user_memory.interaction_count += 1
            user_memory.lead_score += 1  # Pequeño incremento
            
            # Añadir info de webhook
            if 'openai_webhook_responses' not in user_memory.additional_data:
                user_memory.additional_data['openai_webhook_responses'] = 0
            
            user_memory.additional_data['openai_webhook_responses'] += 1
            user_memory.additional_data['last_webhook_response'] = metadata
            
            await self.memory_use_case.save_memory(user_memory)
            
        except Exception as e:
            debug_print(f"⚠️ Error actualizando memoria backup: {e}", "_update_memory_backup")


# Instancia global del handler
openai_webhook_handler = OpenAIWebhookHandler()


# FastAPI app para el webhook (puede integrarse en la app principal)
openai_webhook_app = FastAPI(
    title="OpenAI Webhook Handler",
    description="Webhook para eventos de OpenAI Assistants API",
    version="1.0.0"
)


@openai_webhook_app.on_event("startup")
async def startup_openai_webhook():
    """Inicializa el webhook handler al startup."""
    success = await openai_webhook_handler.initialize()
    if success:
        debug_print("✅ OpenAI Webhook startup completado", "startup")
    else:
        debug_print("❌ Error en OpenAI Webhook startup", "startup")


@openai_webhook_app.post("/webhooks/openai")
async def openai_webhook_endpoint(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint principal para webhooks de OpenAI.
    
    Este endpoint debe ser configurado en OpenAI Platform como webhook URL.
    """
    try:
        # Leer payload completo
        payload = await request.body()
        
        # Verificar firma si está configurada
        signature = request.headers.get('openai-signature', '')
        if signature and not openai_webhook_handler.verify_signature(payload, signature):
            debug_print("❌ Firma de webhook inválida", "openai_webhook_endpoint")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parsear JSON
        try:
            event_data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError as e:
            debug_print(f"❌ Error parseando JSON: {e}", "openai_webhook_endpoint")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # Procesar evento
        result = await openai_webhook_handler.handle_event(event_data, background_tasks)
        
        debug_print(f"📊 Evento procesado: {result.get('status', 'unknown')}", "openai_webhook_endpoint")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        debug_print(f"❌ Error en webhook endpoint: {e}", "openai_webhook_endpoint")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@openai_webhook_app.get("/webhooks/openai/health")
async def openai_webhook_health():
    """Health check para el webhook de OpenAI."""
    try:
        adapter_health = await openai_webhook_handler.threads_adapter.health_check() if openai_webhook_handler.threads_adapter else False
        
        return {
            "status": "healthy" if adapter_health else "degraded",
            "handler_initialized": openai_webhook_handler.threads_adapter is not None,
            "adapter_health": adapter_health,
            "webhook_secret_configured": bool(openai_webhook_handler.webhook_secret)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    debug_print("🚀 Iniciando OpenAI Webhook server...", "main")
    
    uvicorn.run(
        "app.presentation.api.webhook_openai:openai_webhook_app",
        host="0.0.0.0",
        port=8001,  # Puerto diferente al webhook principal
        reload=False
    )