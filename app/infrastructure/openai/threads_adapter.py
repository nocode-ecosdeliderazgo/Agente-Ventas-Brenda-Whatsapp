"""
Adapter para integración con OpenAI Assistants API (Threads).
Maneja Threads, Messages, Runs y tool calling para memoria conversacional.
"""
import logging
import json
import time
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI

from app.config import settings
from app.infrastructure.database.repositories.oa_threads_map_repository import OAThreadsMapRepository
from app.infrastructure.database.repositories.course_repository import CourseRepository

logger = logging.getLogger(__name__)


def debug_print(message: str, function_name: str = "", file_name: str = "threads_adapter.py"):
    """Print de debug visual para consola"""
    print(f"🧵 [{file_name}::{function_name}] {message}")


class ThreadsAdapter:
    """
    Adapter para OpenAI Assistants API (Threads).
    
    Responsabilidades:
    - Mapeo user_phone ↔ thread_id
    - Gestión de Threads, Messages y Runs
    - Function calling para herramientas de cursos
    - Manejo de errores y timeouts
    """
    
    def __init__(self, assistant_id: Optional[str] = None):
        """
        Inicializa el adapter de Threads.
        
        Args:
            assistant_id: ID del Assistant de OpenAI (si no se pasa, se toma de env)
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.threads_repo = OAThreadsMapRepository()
        self.course_repo = CourseRepository()
        
        # Assistant ID desde parámetro o variable de entorno
        self.assistant_id = assistant_id or getattr(settings, 'assistant_id', None)
        if not self.assistant_id:
            logger.warning("⚠️ ASSISTANT_ID no configurado - funcionalidad limitada")
        
        logger.info(f"✅ ThreadsAdapter inicializado - Assistant ID: {self.assistant_id}")
    
    async def get_or_create_thread_id(self, user_phone: str) -> str:
        """
        Obtiene thread_id existente o crea uno nuevo.
        
        Args:
            user_phone: Número de WhatsApp en formato Twilio
        
        Returns:
            Thread ID de OpenAI
        """
        try:
            debug_print(f"🔍 Buscando thread para {user_phone}", "get_or_create_thread_id")
            
            # Asegurar que la tabla existe
            await self.threads_repo.ensure_table_exists()
            
            # Buscar thread existente
            existing_thread_id = await self.threads_repo.get_thread_id(user_phone)
            
            if existing_thread_id:
                debug_print(f"✅ Thread encontrado: {existing_thread_id}", "get_or_create_thread_id")
                
                # Verificar que el thread aún existe en OpenAI
                try:
                    await self.client.beta.threads.retrieve(existing_thread_id)
                    debug_print(f"✅ Thread válido en OpenAI", "get_or_create_thread_id")
                    return existing_thread_id
                except Exception as e:
                    debug_print(f"⚠️ Thread inválido en OpenAI: {e}, creando nuevo", "get_or_create_thread_id")
            
            # Crear nuevo thread
            debug_print(f"🆕 Creando nuevo thread para {user_phone}", "get_or_create_thread_id")
            thread = await self.client.beta.threads.create()
            
            thread_id = thread.id
            debug_print(f"✅ Thread creado: {thread_id}", "get_or_create_thread_id")
            
            # Guardar mapeo en BD
            success = await self.threads_repo.save_thread_id(user_phone, thread_id)
            if success:
                debug_print(f"✅ Mapeo guardado en BD", "get_or_create_thread_id")
            else:
                debug_print(f"⚠️ Error guardando mapeo, continuando", "get_or_create_thread_id")
            
            return thread_id
            
        except Exception as e:
            debug_print(f"❌ Error obteniendo/creando thread: {e}", "get_or_create_thread_id")
            raise
    
    async def add_user_message(
        self, 
        thread_id: str, 
        text: str, 
        attachments: Optional[List[str]] = None
    ) -> str:
        """
        Añade mensaje del usuario al thread.
        
        Args:
            thread_id: ID del thread
            text: Texto del mensaje
            attachments: URLs de archivos adjuntos (opcional)
        
        Returns:
            ID del mensaje creado
        """
        try:
            debug_print(f"💬 Añadiendo mensaje de usuario a thread {thread_id}", "add_user_message")
            debug_print(f"📝 Texto: '{text[:100]}{'...' if len(text) > 100 else ''}'", "add_user_message")
            
            # Por ahora solo texto, attachments para futuro
            message = await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=text
            )
            
            debug_print(f"✅ Mensaje añadido: {message.id}", "add_user_message")
            return message.id
            
        except Exception as e:
            debug_print(f"❌ Error añadiendo mensaje: {e}", "add_user_message")
            raise
    
    async def start_run(self, thread_id: str, assistant_id: Optional[str] = None) -> str:
        """
        Inicia un Run en el thread.
        
        Args:
            thread_id: ID del thread
            assistant_id: ID del assistant (opcional, usa el por defecto)
        
        Returns:
            ID del run creado
        """
        try:
            assistant_to_use = assistant_id or self.assistant_id
            if not assistant_to_use:
                raise ValueError("No se ha configurado ASSISTANT_ID")
            
            debug_print(f"🚀 Iniciando run en thread {thread_id} con assistant {assistant_to_use}", "start_run")
            
            run = await self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_to_use
            )
            
            debug_print(f"✅ Run iniciado: {run.id}", "start_run")
            return run.id
            
        except Exception as e:
            debug_print(f"❌ Error iniciando run: {e}", "start_run")
            raise
    
    async def wait_for_run(self, thread_id: str, run_id: str, timeout_s: int = 25) -> Dict[str, Any]:
        """
        Espera a que el run termine con polling y maneja tool calling.
        
        Args:
            thread_id: ID del thread
            run_id: ID del run
            timeout_s: Timeout en segundos
        
        Returns:
            Dict con información del run completado
        """
        try:
            debug_print(f"⏰ Esperando run {run_id} (timeout: {timeout_s}s)", "wait_for_run")
            
            start_time = time.time()
            polling_interval = 0.5  # Medio segundo entre polls
            
            while time.time() - start_time < timeout_s:
                # Obtener estado actual del run
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id
                )
                
                debug_print(f"📊 Estado del run: {run.status}", "wait_for_run")
                
                if run.status == "completed":
                    debug_print(f"✅ Run completado exitosamente", "wait_for_run")
                    return {
                        "status": "completed",
                        "run_id": run_id,
                        "usage": run.usage.dict() if run.usage else {},
                        "success": True
                    }
                
                elif run.status == "failed":
                    error_msg = f"Run falló: {run.last_error.message if run.last_error else 'Error desconocido'}"
                    debug_print(f"❌ {error_msg}", "wait_for_run")
                    return {
                        "status": "failed",
                        "run_id": run_id,
                        "error": error_msg,
                        "success": False
                    }
                
                elif run.status == "cancelled":
                    debug_print(f"⚠️ Run cancelado", "wait_for_run")
                    return {
                        "status": "cancelled", 
                        "run_id": run_id,
                        "success": False
                    }
                
                elif run.status == "requires_action":
                    debug_print(f"🔧 Run requiere action - procesando tool calls", "wait_for_run")
                    
                    # Procesar tool calls
                    success = await self._handle_requires_action(thread_id, run_id, run)
                    if not success:
                        debug_print(f"❌ Error procesando tool calls", "wait_for_run")
                        return {
                            "status": "failed",
                            "run_id": run_id, 
                            "error": "Error procesando tool calls",
                            "success": False
                        }
                    
                    # Continuar el polling después de enviar tool outputs
                    debug_print(f"🔄 Tool calls procesados, continuando polling...", "wait_for_run")
                
                # Esperar antes del siguiente poll
                await self._async_sleep(polling_interval)
            
            # Timeout alcanzado
            debug_print(f"⏰ Timeout alcanzado para run {run_id}", "wait_for_run")
            return {
                "status": "timeout",
                "run_id": run_id,
                "error": f"Timeout después de {timeout_s} segundos",
                "success": False
            }
            
        except Exception as e:
            debug_print(f"❌ Error esperando run: {e}", "wait_for_run")
            return {
                "status": "error",
                "run_id": run_id,
                "error": str(e),
                "success": False
            }
    
    async def _handle_requires_action(self, thread_id: str, run_id: str, run) -> bool:
        """
        Maneja tool calls cuando el run requiere acción.
        
        Args:
            thread_id: ID del thread
            run_id: ID del run
            run: Objeto run de OpenAI
        
        Returns:
            True si se procesaron exitosamente los tool calls
        """
        try:
            if not run.required_action or not run.required_action.submit_tool_outputs:
                debug_print(f"⚠️ Run requiere acción pero no hay tool calls", "_handle_requires_action")
                return False
            
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            debug_print(f"🔧 Procesando {len(tool_calls)} tool calls", "_handle_requires_action")
            
            tool_outputs = []
            
            for tool_call in tool_calls:
                debug_print(f"🛠️ Ejecutando tool: {tool_call.function.name}", "_handle_requires_action")
                debug_print(f"📋 Argumentos: {tool_call.function.arguments}", "_handle_requires_action")
                
                # Ejecutar la función
                result = await self._execute_tool_call(tool_call)
                
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result) if isinstance(result, (dict, list)) else str(result)
                })
                
                debug_print(f"✅ Tool ejecutado: {tool_call.function.name}", "_handle_requires_action")
            
            # Enviar tool outputs de vuelta a OpenAI
            debug_print(f"📤 Enviando {len(tool_outputs)} tool outputs", "_handle_requires_action")
            
            await self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
            
            debug_print(f"✅ Tool outputs enviados exitosamente", "_handle_requires_action")
            return True
            
        except Exception as e:
            debug_print(f"❌ Error manejando tool calls: {e}", "_handle_requires_action")
            return False
    
    async def _execute_tool_call(self, tool_call) -> Dict[str, Any]:
        """
        Ejecuta un tool call específico.
        
        Args:
            tool_call: Objeto tool call de OpenAI
        
        Returns:
            Resultado de la ejecución
        """
        try:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            debug_print(f"🎯 Ejecutando función: {function_name}", "_execute_tool_call")
            debug_print(f"📊 Argumentos parseados: {arguments}", "_execute_tool_call")
            
            if function_name == "buscar_curso":
                return await self._buscar_curso(arguments)
            elif function_name == "detalle_curso":
                return await self._detalle_curso(arguments)
            else:
                debug_print(f"⚠️ Función no reconocida: {function_name}", "_execute_tool_call")
                return {
                    "error": f"Función no reconocida: {function_name}",
                    "success": False
                }
                
        except Exception as e:
            debug_print(f"❌ Error ejecutando tool call: {e}", "_execute_tool_call")
            return {
                "error": str(e),
                "success": False
            }
    
    async def _buscar_curso(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Herramienta: Buscar cursos por nombre o nivel.
        
        Args:
            args: Argumentos de la función (name, level)
        
        Returns:
            Lista de cursos encontrados
        """
        try:
            name = args.get("name")
            level = args.get("level")
            
            debug_print(f"🔍 Buscando cursos - name: {name}, level: {level}", "_buscar_curso")
            
            if name:
                # Buscar por nombre
                courses = await self.course_repo.search_courses_by_text(name, limit=5)
            elif level:
                # Buscar por nivel
                courses = await self.course_repo.get_courses_by_level(level, limit=5)
            else:
                # Obtener cursos activos
                courses = await self.course_repo.get_active_courses(limit=5)
            
            # Convertir a dict para JSON serialization
            courses_data = []
            for course in courses:
                courses_data.append({
                    "id_course": str(course.id_course),
                    "name": course.name,
                    "short_description": course.short_description,
                    "price": course.price,
                    "currency": course.currency,
                    "level": course.level,
                    "session_count": course.session_count,
                    "total_duration_min": course.total_duration_min,
                    "modality": course.modality
                })
            
            debug_print(f"✅ Encontrados {len(courses_data)} cursos", "_buscar_curso")
            
            return {
                "courses": courses_data,
                "total_found": len(courses_data),
                "search_criteria": {"name": name, "level": level},
                "success": True
            }
            
        except Exception as e:
            debug_print(f"❌ Error en buscar_curso: {e}", "_buscar_curso")
            return {
                "error": str(e),
                "courses": [],
                "success": False
            }
    
    async def _detalle_curso(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Herramienta: Obtener detalle completo de un curso.
        
        Args:
            args: Argumentos con id_course
        
        Returns:
            Información detallada del curso
        """
        try:
            from uuid import UUID
            
            id_course_str = args.get("id_course")
            if not id_course_str:
                return {"error": "id_course es requerido", "success": False}
            
            # Convertir string a UUID
            id_course = UUID(id_course_str)
            
            debug_print(f"📋 Obteniendo detalle de curso: {id_course}", "_detalle_curso")
            
            # Obtener información completa
            course_info = await self.course_repo.get_course_complete_info(id_course)
            
            if not course_info:
                debug_print(f"⚠️ Curso no encontrado: {id_course}", "_detalle_curso")
                return {
                    "error": f"Curso no encontrado: {id_course}",
                    "success": False
                }
            
            # Preparar datos serializables
            result = {
                "course": {
                    "id_course": str(course_info.course.id_course),
                    "name": course_info.course.name,
                    "short_description": course_info.course.short_description,
                    "long_description": course_info.course.long_descrption,  # Nota: typo en BD
                    "price": course_info.course.price,
                    "currency": course_info.course.currency,
                    "level": course_info.course.level,
                    "session_count": course_info.course.session_count,
                    "total_duration_min": course_info.course.total_duration_min,
                    "modality": course_info.course.modality,
                    "course_url": course_info.course.course_url,
                    "purchase_url": course_info.course.purchase_url
                },
                "sessions": [],
                "bonds": [],
                "total_activities": course_info.total_activities,
                "success": True
            }
            
            # Añadir sesiones
            for session in course_info.sessions:
                result["sessions"].append({
                    "session_index": session.session_index,
                    "title": session.title,
                    "objective": session.objective,
                    "duration_minutes": session.duration_minutes
                })
            
            # Añadir bonos
            for bond in course_info.bonds:
                result["bonds"].append({
                    "type_bond": bond.type_bond,
                    "content": bond.content,
                    "emisor": bond.emisor,
                    "active": bond.active
                })
            
            debug_print(f"✅ Detalle obtenido - {len(result['sessions'])} sesiones, {len(result['bonds'])} bonos", "_detalle_curso")
            
            return result
            
        except Exception as e:
            debug_print(f"❌ Error en detalle_curso: {e}", "_detalle_curso")
            return {
                "error": str(e),
                "success": False
            }
    
    async def fetch_last_assistant_message(self, thread_id: str) -> str:
        """
        Obtiene el último mensaje del assistant en el thread.
        
        Args:
            thread_id: ID del thread
        
        Returns:
            Texto del último mensaje del assistant o string vacío
        """
        try:
            debug_print(f"📥 Obteniendo último mensaje de thread {thread_id}", "fetch_last_assistant_message")
            
            messages = await self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=10
            )
            
            # Buscar el primer mensaje del assistant
            for message in messages.data:
                if message.role == "assistant":
                    # Extraer contenido de texto
                    content_text = ""
                    for content_block in message.content:
                        if hasattr(content_block, 'text'):
                            content_text += content_block.text.value
                    
                    debug_print(f"✅ Mensaje encontrado: '{content_text[:100]}{'...' if len(content_text) > 100 else ''}'", "fetch_last_assistant_message")
                    return content_text.strip()
            
            debug_print(f"⚠️ No se encontraron mensajes del assistant", "fetch_last_assistant_message")
            return ""
            
        except Exception as e:
            debug_print(f"❌ Error obteniendo último mensaje: {e}", "fetch_last_assistant_message")
            return ""
    
    async def _async_sleep(self, seconds: float):
        """Sleep async helper."""
        import asyncio
        await asyncio.sleep(seconds)
    
    async def health_check(self) -> bool:
        """Verifica que el adapter funcione correctamente."""
        try:
            # Verificar cliente OpenAI
            models = await self.client.models.list()
            if not models:
                return False
            
            # Verificar repositorio
            return await self.threads_repo.health_check()
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False