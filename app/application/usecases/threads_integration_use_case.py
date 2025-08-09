"""
Use case para integración con OpenAI Assistants API (Threads).
Maneja el flujo completo de conversación usando threads y tool calling.
"""
import logging
from typing import Dict, Any, Optional

from app.config import settings
from app.infrastructure.openai.threads_adapter import ThreadsAdapter
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase

logger = logging.getLogger(__name__)


def debug_print(message: str, function_name: str = "", file_name: str = "threads_integration_use_case.py"):
    """Print de debug visual para consola"""
    print(f"🧵 [{file_name}::{function_name}] {message}")


class ThreadsIntegrationUseCase:
    """
    Use case para manejar conversaciones usando OpenAI Threads.
    
    Proporciona una alternativa al flujo tradicional de procesamiento,
    usando la memoria conversacional nativa de OpenAI Assistants API.
    """
    
    def __init__(
        self,
        twilio_client: TwilioWhatsAppClient,
        memory_use_case: ManageUserMemoryUseCase,
        assistant_id: Optional[str] = None
    ):
        """
        Inicializa el use case de threads.
        
        Args:
            twilio_client: Cliente de WhatsApp
            memory_use_case: Use case de memoria (para compatibilidad/backup)
            assistant_id: ID del assistant (opcional, toma de settings)
        """
        self.twilio_client = twilio_client
        self.memory_use_case = memory_use_case
        self.assistant_id = assistant_id or getattr(settings, 'assistant_id', None)
        
        if not self.assistant_id:
            raise ValueError("ASSISTANT_ID no está configurado para ThreadsIntegrationUseCase")
        
        self.threads_adapter = ThreadsAdapter(self.assistant_id)
        logger.info(f"✅ ThreadsIntegrationUseCase inicializado - Assistant: {self.assistant_id}")
    
    async def execute(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un mensaje usando OpenAI Threads.
        
        Args:
            webhook_data: Datos del webhook de Twilio
        
        Returns:
            Resultado del procesamiento con threads
        """
        try:
            # Extraer datos del mensaje
            user_phone = webhook_data.get("From", "")
            message_body = webhook_data.get("Body", "")
            message_sid = webhook_data.get("MessageSid", "")
            
            debug_print(f"🚀 PROCESANDO CON THREADS", "execute")
            debug_print(f"📱 Usuario: {user_phone}", "execute")
            debug_print(f"💬 Mensaje: '{message_body}'", "execute")
            debug_print(f"🎯 Assistant ID: {self.assistant_id}", "execute")
            
            if not user_phone or not message_body:
                debug_print(f"⚠️ Datos incompletos del webhook", "execute")
                return {
                    "success": False,
                    "error": "Datos incompletos del webhook",
                    "response_sent": False
                }
            
            # 1. Obtener o crear thread
            debug_print(f"🧵 Obteniendo/creando thread...", "execute")
            thread_id = await self.threads_adapter.get_or_create_thread_id(user_phone)
            debug_print(f"✅ Thread ID: {thread_id}", "execute")
            
            # 2. Añadir mensaje del usuario al thread
            debug_print(f"💬 Añadiendo mensaje del usuario...", "execute")
            message_id = await self.threads_adapter.add_user_message(thread_id, message_body)
            debug_print(f"✅ Mensaje añadido: {message_id}", "execute")
            
            # 3. Iniciar run del assistant
            debug_print(f"🚀 Iniciando run...", "execute")
            run_id = await self.threads_adapter.start_run(thread_id, self.assistant_id)
            debug_print(f"✅ Run iniciado: {run_id}", "execute")
            
            # 4. Esperar que el run termine (con tool calling si es necesario)
            debug_print(f"⏰ Esperando respuesta del assistant...", "execute")
            run_result = await self.threads_adapter.wait_for_run(thread_id, run_id, timeout_s=30)
            
            if not run_result.get("success", False):
                debug_print(f"❌ Run falló: {run_result.get('error', 'Error desconocido')}", "execute")
                # Fallback a respuesta genérica
                fallback_response = await self._get_fallback_response(user_phone, message_body)
                return await self._send_response_and_return(user_phone, fallback_response, 
                                                          {"source": "fallback", "run_error": run_result})
            
            debug_print(f"✅ Run completado: {run_result['status']}", "execute")
            
            # 5. Obtener respuesta del assistant
            debug_print(f"📥 Obteniendo respuesta del assistant...", "execute")
            assistant_response = await self.threads_adapter.fetch_last_assistant_message(thread_id)
            
            if not assistant_response:
                debug_print(f"⚠️ No se obtuvo respuesta del assistant", "execute")
                fallback_response = await self._get_fallback_response(user_phone, message_body)
                return await self._send_response_and_return(user_phone, fallback_response,
                                                          {"source": "fallback", "reason": "no_assistant_response"})
            
            debug_print(f"✅ Respuesta obtenida: '{assistant_response[:100]}{'...' if len(assistant_response) > 100 else ''}'", "execute")
            
            # 6. Enviar respuesta a WhatsApp
            return await self._send_response_and_return(user_phone, assistant_response, {
                "source": "threads",
                "thread_id": thread_id,
                "run_id": run_id,
                "run_result": run_result
            })
            
        except Exception as e:
            debug_print(f"❌ ERROR EN THREADS INTEGRATION: {e}", "execute")
            import traceback
            debug_print(f"📜 Traceback: {traceback.format_exc()}", "execute")
            
            # Fallback completo
            try:
                fallback_response = await self._get_fallback_response(user_phone, message_body)
                return await self._send_response_and_return(user_phone, fallback_response,
                                                          {"source": "error_fallback", "error": str(e)})
            except Exception as fallback_error:
                debug_print(f"💥 ERROR EN FALLBACK: {fallback_error}", "execute")
                return {
                    "success": False,
                    "error": f"Error en threads y fallback: {str(e)} | {str(fallback_error)}",
                    "response_sent": False
                }
    
    async def _send_response_and_return(
        self, 
        user_phone: str, 
        response_text: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Envía respuesta a WhatsApp y retorna resultado estructurado.
        
        Args:
            user_phone: Número del usuario
            response_text: Texto de respuesta
            metadata: Información adicional del procesamiento
        
        Returns:
            Resultado estructurado del procesamiento
        """
        try:
            debug_print(f"📤 Enviando respuesta a WhatsApp...", "_send_response_and_return")
            debug_print(f"📱 A: {user_phone}", "_send_response_and_return")
            debug_print(f"💬 Texto: '{response_text[:100]}{'...' if len(response_text) > 100 else ''}'", "_send_response_and_return")
            
            # Enviar mensaje usando cliente Twilio
            response_sid = await self.twilio_client.send_message(
                to=user_phone,
                body=response_text
            )
            
            if response_sid:
                debug_print(f"✅ Mensaje enviado exitosamente: {response_sid}", "_send_response_and_return")
                
                # También actualizar memoria local como backup
                try:
                    await self._update_memory_backup(user_phone, response_text, metadata)
                except Exception as memory_error:
                    debug_print(f"⚠️ Error actualizando memoria backup: {memory_error}", "_send_response_and_return")
                
                return {
                    "success": True,
                    "response_sent": True,
                    "response_text": response_text,
                    "response_sid": response_sid,
                    "processing_type": "threads_integration",
                    "metadata": metadata
                }
            else:
                debug_print(f"❌ Error enviando mensaje a WhatsApp", "_send_response_and_return")
                return {
                    "success": False,
                    "response_sent": False,
                    "error": "Error enviando mensaje",
                    "metadata": metadata
                }
                
        except Exception as e:
            debug_print(f"❌ Error en envío de respuesta: {e}", "_send_response_and_return")
            return {
                "success": False,
                "response_sent": False,
                "error": f"Error enviando respuesta: {str(e)}",
                "metadata": metadata
            }
    
    async def _get_fallback_response(self, user_phone: str, message_body: str) -> str:
        """
        Genera respuesta de fallback cuando threads falla.
        
        Args:
            user_phone: Número del usuario
            message_body: Mensaje original
        
        Returns:
            Respuesta de fallback
        """
        try:
            debug_print(f"🔄 Generando respuesta fallback", "_get_fallback_response")
            
            # Respuestas context-aware basadas en contenido del mensaje
            message_lower = message_body.lower()
            
            if any(word in message_lower for word in ['hola', 'hello', 'hi', 'buenos', 'buenas']):
                return """¡Hola! 👋

Gracias por contactarnos. Soy Brenda, tu asistente especializada en cursos de IA.

¿En qué puedo ayudarte hoy?"""
            
            elif any(word in message_lower for word in ['curso', 'cursos', 'aprender', 'estudiar']):
                return """¡Excelente! 🎓

Tenemos cursos especializados en IA que te van a fascinar.

¿Te gustaría conocer nuestro curso "Experto en IA para Profesionales"?"""
            
            elif any(word in message_lower for word in ['precio', 'costo', 'cuanto', 'cuánto']):
                return """¡Perfecto que preguntes por la inversión! 💰

Nuestro curso "Experto en IA para Profesionales" tiene un valor de $4,500 MXN.

¿Te gustaría conocer todo lo que incluye?"""
            
            elif any(word in message_lower for word in ['contacto', 'asesor', 'hablar', 'llamar']):
                return """¡Por supuesto! 👥

Te voy a conectar con uno de nuestros asesores especializados.

¿Estás listo/a para que iniciemos el contacto?"""
            
            else:
                return """¡Gracias por escribir! 😊

Estoy aquí para ayudarte con todo lo relacionado a nuestros cursos de IA.

¿En qué puedo asistirte específicamente?"""
                
        except Exception as e:
            debug_print(f"❌ Error generando fallback: {e}", "_get_fallback_response")
            return """¡Hola! 👋

Gracias por contactarnos. Estoy aquí para ayudarte con nuestros cursos de IA.

¿En qué puedo asistirte?"""
    
    async def _update_memory_backup(
        self, 
        user_phone: str, 
        response_text: str, 
        metadata: Dict[str, Any]
    ):
        """
        Actualiza memoria local como backup del sistema threads.
        
        Args:
            user_phone: Número del usuario
            response_text: Respuesta enviada
            metadata: Información del procesamiento
        """
        try:
            debug_print(f"💾 Actualizando memoria backup", "_update_memory_backup")
            
            # Cargar memoria existente
            user_memory = await self.memory_use_case.load_memory(user_phone)
            
            # Actualizar estadísticas básicas
            user_memory.interaction_count += 1
            user_memory.lead_score += 2  # Pequeño incremento por usar threads
            
            # Añadir información de threads a datos adicionales
            if 'threads_integration' not in user_memory.additional_data:
                user_memory.additional_data['threads_integration'] = {
                    'enabled': True,
                    'first_use': user_memory.updated_at.isoformat() if user_memory.updated_at else None,
                    'total_thread_interactions': 0
                }
            
            user_memory.additional_data['threads_integration']['total_thread_interactions'] += 1
            user_memory.additional_data['threads_integration']['last_thread_id'] = metadata.get('thread_id')
            
            # Guardar memoria actualizada
            await self.memory_use_case.save_memory(user_memory)
            debug_print(f"✅ Memoria backup actualizada", "_update_memory_backup")
            
        except Exception as e:
            debug_print(f"⚠️ Error actualizando memoria backup: {e}", "_update_memory_backup")
            # No propagar error, es solo backup
    
    @staticmethod
    def is_enabled() -> bool:
        """
        Verifica si la integración de threads está habilitada.
        
        Returns:
            True si ASSISTANT_ID está configurado
        """
        return bool(getattr(settings, 'assistant_id', None))
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado del sistema de threads.
        
        Returns:
            Estado del sistema
        """
        try:
            adapter_health = await self.threads_adapter.health_check()
            
            return {
                "threads_integration_enabled": True,
                "assistant_id_configured": bool(self.assistant_id),
                "adapter_health": adapter_health,
                "status": "healthy" if adapter_health else "degraded"
            }
            
        except Exception as e:
            return {
                "threads_integration_enabled": True,
                "assistant_id_configured": bool(self.assistant_id),
                "adapter_health": False,
                "error": str(e),
                "status": "error"
            }