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
        db_client: Optional[DatabaseClient] = None, 
        course_repository: Optional[CourseRepository] = None,
        course_query_use_case: Optional[Any] = None
    ):
        self.intent_analyzer = intent_analyzer
        self.twilio_client = twilio_client
        self.openai_client = openai_client
        
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
                response_text = await self._generate_contextual_response(
                    analysis_result, incoming_message, user_id
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

    async def _generate_contextual_response(
        self,
        analysis_result: Dict[str, Any],
        incoming_message: IncomingMessage,
        user_id: str
    ) -> str:
        """
        Genera la respuesta forzando a la IA a usar el contexto hardcodeado.
        """
        try:
            user_memory = analysis_result.get('updated_memory')
            user_name = user_memory.name if user_memory and user_memory.name else "Cliente"
            intent_analysis = analysis_result.get('intent_analysis', {})

            # 1. Construir el contexto de conocimiento a partir del archivo de config
            hardcoded_context = self._build_hardcoded_context_for_prompt(user_name)
            
            # 2. Generar la respuesta con OpenAI, pasando todos los parámetros necesarios
            debug_print("🤖 Llamando a OpenAI con contexto hardcodeado...", "_generate_contextual_response")
            
            # NOTA: La función 'generate_response' en el cliente de OpenAI es la que internamente
            # construye el prompt final. Le pasamos el contexto hardcodeado como 'context_info'.
            generated_response = await self.openai_client.generate_response(
                user_message=incoming_message.body,
                user_memory=user_memory,
                intent_analysis=intent_analysis,
                context_info=hardcoded_context
            )

            if not generated_response:
                raise ValueError("OpenAI no generó respuesta.")
            
            debug_print(f"✅ Respuesta cruda de OpenAI: {generated_response[:150]}...", "_generate_contextual_response")
            
            return generated_response

        except Exception as e:
            self.logger.error(f"❌ Error en _generate_contextual_response: {e}", exc_info=True)
            return WhatsAppMessageTemplates.business_error_fallback()

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