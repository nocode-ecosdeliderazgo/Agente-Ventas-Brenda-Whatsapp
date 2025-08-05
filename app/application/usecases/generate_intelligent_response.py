"""
Caso de uso para generar respuestas inteligentes.
Combina análisis de intención y respuestas de IA con un sistema anti-inventos,
utilizando una fuente de datos hardcodeada como contexto principal.
"""
import logging
from typing import Dict, Any, Optional
import json

from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.validate_response_use_case import ValidateResponseUseCase
from app.application.usecases.anti_hallucination_use_case import AntiHallucinationUseCase
from app.application.usecases.personalize_response_use_case import PersonalizeResponseUseCase
from app.application.usecases.extract_user_info_use_case import ExtractUserInfoUseCase
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.database.client import DatabaseClient
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from prompts.agent_prompts import WhatsAppMessageTemplates
from app.config.intelligent_agent_config import INTELLIGENT_AGENT_CONFIG
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase


logger = logging.getLogger(__name__)

def debug_print(message: str, function_name: str = "", file_name: str = "generate_intelligent_response.py"):
    """Print de debug visual para consola"""
    print(f"💬 [{file_name}::{function_name}] {message}")


class GenerateIntelligentResponseUseCase:
    """
    Genera respuestas inteligentes forzando el uso de un contexto de conocimiento
    hardcodeado para garantizar la precisión y evitar alucinaciones.
    """
    
    def __init__(
        self,
        intent_analyzer: AnalyzeMessageIntentUseCase,
        twilio_client: TwilioWhatsAppClient,
        openai_client: OpenAIClient,
        memory_use_case: ManageUserMemoryUseCase, # Añadido
        db_client: Optional[DatabaseClient] = None, 
        course_repository: Optional[CourseRepository] = None,
        course_query_use_case: Optional[Any] = None
    ):
        self.intent_analyzer = intent_analyzer
        self.twilio_client = twilio_client
        self.openai_client = openai_client
        self.memory_use_case = memory_use_case # Añadido
        
        # Casos de uso de validación y personalización
        self.validate_response_use_case = None
        self.anti_hallucination_use_case = None
        if db_client and course_repository:
            self.validate_response_use_case = ValidateResponseUseCase(db_client, course_repository)
            self.anti_hallucination_use_case = AntiHallucinationUseCase(
                openai_client, course_repository, self.validate_response_use_case
            )
        
        self.extract_user_info_use_case = ExtractUserInfoUseCase(openai_client)
        self.personalize_response_use_case = PersonalizeResponseUseCase(
            openai_client, self.extract_user_info_use_case
        )
        
        self.logger = logging.getLogger(__name__)

    async def execute(
        self,
        user_id: str,
        incoming_message: IncomingMessage,
        context_info: str = ""
    ) -> Dict[str, Any]:
        try:
            debug_print(f"💬 INICIANDO RESPUESTA INTELIGENTE\n👤 Usuario: {user_id}\n📨 Mensaje: '{incoming_message.body}'", "execute")

            # 1. Analizar intención del mensaje
            analysis_result = await self.intent_analyzer.execute(
                user_id, incoming_message, context_info
            )
            
            if not analysis_result['success']:
                debug_print(f"❌ FALLO ANÁLISIS DE INTENCIÓN: {analysis_result.get('error')}", "execute")
                response_text = WhatsAppMessageTemplates.business_error_fallback()
            else:
                debug_print(f"✅ Análisis completado - Intención: {analysis_result.get('intent_analysis', {}).get('category', 'N/A')}", "execute")
                
                # 2. Generar respuesta basada en el contexto hardcodeado
                user_memory = self.memory_use_case.get_user_memory(user_id)
                category = analysis_result.get('intent_analysis', {}).get('category', 'GENERAL_QUESTION')
                intent_analysis = analysis_result.get('intent_analysis', {})
                response_text = await self._generate_contextual_response(
                    category, user_memory, user_id, incoming_message.body, intent_analysis
                )
                debug_print(f"✅ Respuesta generada: {response_text[:150]}...", "execute")

            # 3. Enviar respuesta
            send_result = await self._send_response(
                incoming_message.from_number, response_text
            )

            result = {
                'success': send_result['success'],
                'intent_analysis': analysis_result.get('intent_analysis', {}),
                'response_text': response_text,
                'response_sent': send_result['success'],
                'response_sid': send_result.get('message_sid'),
            }
            
            return result

        except Exception as e:
            self.logger.error(f"💥 Error fatal en generate_intelligent_response: {e}", exc_info=True)
            fallback_response = WhatsAppMessageTemplates.business_error_fallback()
            fallback_result = await self._send_response(
                incoming_message.from_number, fallback_response
            )
            return {
                'success': False, 'error': str(e), 'response_text': fallback_response,
                'response_sent': fallback_result['success'], 'response_sid': fallback_result.get('message_sid')
            }

    def _get_specific_context_for_intent(self, category: str) -> Optional[str]:
        """
        Busca en la configuración el contexto específico para una intención de FAQ.
        """
        faq_context = INTELLIGENT_AGENT_CONFIG.get("faq", {})
        for key, value in faq_context.items():
            # Asumimos que la categoría de la intención coincide con la clave en el FAQ_CONTEXT
            # Ej: 'instructor_profile'
            if key.lower() in category.lower():
                return value.get("answer")
        return None

    def _build_hardcoded_context_for_prompt(self, user_name: str) -> str:
        """
        Construye una cadena de texto con todo el conocimiento del negocio
        para inyectarla en el prompt de la IA.
        """
        context_str = "CONTEXTO DE CONOCIMIENTO:\n"
        
        # Información de Cursos
        context_str += "--- INFORMACIÓN DE CURSOS ---\n"
        for course_key, course_data in INTELLIGENT_AGENT_CONFIG["courses"].items():
            context_str += f"Curso '{course_key}':\n"
            context_str += f"Título: {course_data['title']}\n"
            context_str += f"Introducción: {course_data['intro']}\n"
            context_str += "Puntos clave:\n"
            for point in course_data['talking_points']:
                context_str += f"- {point['title']}: {point['body']}\n"
            context_str += f"Caso de estudio: {course_data['case_study']}\n"
            context_str += f"Siguiente paso sugerido: {course_data['next_step']}\n"
        
        # Información de FAQ
        context_str += "\n--- PREGUNTAS FRECUENTES (FAQ) ---\n"
        for faq_key, faq_data in INTELLIGENT_AGENT_CONFIG["faq"].items():
            context_str += f"Pregunta sobre '{faq_key}' (palabras claves: {', '.join(faq_data['keywords'])}):\n"
            answer = faq_data['answer']
            if isinstance(answer, str):
                context_str += f"Respuesta: {answer.format(user_name=user_name)}\n"
            else:
                context_str += f"Respuesta: {' '.join(answer).format(user_name=user_name)}\n"

        context_str += "--- FIN DEL CONTEXTO ---\n"
        return context_str

    async def _generate_contextual_response(self, category: str, user_memory: Any, user_id: str, incoming_message: str, intent_analysis: Dict[str, Any]) -> str:
        """
        Genera una respuesta contextual basada en la categoría detectada y la memoria del usuario.
        """
        try:
            debug_print(f"Generando respuesta contextual para categoría: {category}", "_generate_contextual_response")
            
            # ELIMINADO: Lógica restrictiva de sector_info_sent que causaba respuestas demasiado cortas
            # La IA ahora siempre generará respuestas completas e inteligentes
            
            # Buscar contexto específico en nuestra configuración
            specific_context = self._get_specific_context_for_intent(category)
            
            if specific_context:
                debug_print(f"✅ Contexto específico encontrado para {category}", "_generate_contextual_response")
                context_to_use = specific_context
            else:
                debug_print("INFO: Usando contexto general completo.", "_generate_contextual_response")
                # Usar todo el contexto disponible para generar respuestas ricas
                user_name = user_memory.name if user_memory.name else "Usuario"
                context_to_use = self._build_hardcoded_context_for_prompt(user_name)

            debug_print("🤖 Llamando a OpenAI con contexto seleccionado...", "_generate_contextual_response")
            
            # Generar respuesta con OpenAI usando la firma correcta
            generated_response = await self.openai_client.generate_response(
                user_message=incoming_message,
                user_memory=user_memory,
                intent_analysis=intent_analysis,
                context_info=context_to_use
            )
            
            debug_print(f"✅ Respuesta cruda de OpenAI: {generated_response[:150]}...", "_generate_contextual_response")
            
            return generated_response
            
        except Exception as e:
            debug_print(f"💥 Error en _generate_contextual_response: {e}", "_generate_contextual_response")
            user_name = user_memory.name if user_memory and user_memory.name else "Usuario"
            return f"Disculpa, {user_name}, estoy teniendo algunos problemas técnicos. ¿Podrías repetir tu pregunta?"

    async def _send_response(self, to_number: str, response_text: str) -> Dict[str, Any]:
        """Envía la respuesta al usuario."""
        try:
            message = OutgoingMessage(
                to_number=to_number,
                body=response_text,
                message_type=MessageType.TEXT
            )
            send_result = await self.twilio_client.send_message(message)
            return {'success': True, 'message_sid': send_result}
        except Exception as e:
            self.logger.error(f"❌ Error enviando mensaje vía Twilio: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}