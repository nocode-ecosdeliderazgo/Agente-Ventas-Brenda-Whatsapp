"""
Cliente OpenAI para integración con GPT-4o-mini.
Maneja análisis de intención, extracción de información y generación de respuestas.
"""
import logging
import json
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

from app.config import settings
from prompts.agent_prompts import (
    get_intent_analysis_prompt,
    get_information_extraction_prompt,
    get_response_generation_prompt,
    get_validation_prompt,
    PromptConfig
)

logger = logging.getLogger(__name__)

def debug_print(message: str, function_name: str = "", file_name: str = "openai_client.py"):
    """Print de debug visual para consola"""
    print(f"🤖 [{file_name}::{function_name}] {message}")


class OpenAIClient:
    """
    Cliente especializado para interacciones con OpenAI GPT-4o-mini.
    
    Responsabilidades:
    - Análisis de intención de mensajes
    - Extracción de información de usuarios
    - Generación de respuestas inteligentes
    - Manejo de errores y configuración
    """
    
    def __init__(self):
        """Inicializa el cliente OpenAI con configuración."""
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )
        self.logger = logging.getLogger(__name__)
    
    async def analyze_intent(
        self,
        user_message: str,
        user_memory,
        recent_messages: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Analiza la intención del mensaje del usuario.
        
        Args:
            user_message: Mensaje del usuario a analizar
            user_memory: Memoria del usuario con contexto
            recent_messages: Mensajes recientes para contexto
            
        Returns:
            Dict con análisis de intención estructurado
        """
        try:
            debug_print(f"🔍 ANALIZANDO INTENCIÓN\n💬 Mensaje: '{user_message}'\n👤 Usuario: {user_memory.name if user_memory.name else 'Anónimo'}", "analyze_intent", "openai_client.py")
            
            prompt = get_intent_analysis_prompt(user_message, user_memory, recent_messages)
            config = PromptConfig.get_config('intent_analysis')
            
            debug_print(f"⚙️ Configuración OpenAI:\n🤖 Modelo: {config['model']}\n🌡️ Temperature: {config['temperature']}\n📏 Max tokens: {config['max_tokens']}", "analyze_intent", "openai_client.py")
            
            debug_print(f"📝 PROMPT ENVIADO A OPENAI:\n{prompt[:500]}{'...' if len(prompt) > 500 else ''}", "analyze_intent", "openai_client.py")
            
            debug_print("🚀 Enviando petición a OpenAI...", "analyze_intent", "openai_client.py")
            response = await self.client.chat.completions.create(
                model=config['model'],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                messages=[
                    {"role": "system", "content": "Eres un analizador de intención experto. Responde SOLO con JSON válido."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content
            if content:
                content = content.strip()
            else:
                content = ""
            debug_print(f"📥 RESPUESTA CRUDA DE OPENAI:\n{content}", "analyze_intent", "openai_client.py")
            
            # Intentar parsear JSON
            try:
                debug_print("🔄 Parseando respuesta JSON...", "analyze_intent", "openai_client.py")
                intent_data = json.loads(content)
                debug_print(f"✅ JSON PARSEADO EXITOSAMENTE!\n🎯 Categoría: {intent_data.get('category', 'UNKNOWN')}\n📊 Confianza: {intent_data.get('confidence', 'N/A')}", "analyze_intent", "openai_client.py")
                return intent_data
            except json.JSONDecodeError as e:
                debug_print(f"❌ ERROR PARSEANDO JSON: {e}\n📄 Respuesta recibida: {content}", "analyze_intent", "openai_client.py")
                
                # Fallback con intención genérica
                debug_print("🔄 Usando respuesta FALLBACK genérica", "analyze_intent", "openai_client.py")
                return {
                    "category": "GENERAL_QUESTION",
                    "confidence": 0.5,
                    "should_ask_more": False,
                    "key_topics": ["general"],
                    "response_focus": "Responder de manera útil y amigable",
                    "recommended_action": "continue_conversation",
                    "urgency_level": "medium"
                }
                
        except Exception as e:
            debug_print(f"💥 ERROR CRÍTICO EN ANÁLISIS: {e}", "analyze_intent", "openai_client.py")
            import traceback
            debug_print(f"📜 Traceback completo: {traceback.format_exc()}", "analyze_intent", "openai_client.py")
            
            # Fallback para asegurar que el bot funcione
            debug_print("🚨 Usando FALLBACK CRÍTICO", "analyze_intent", "openai_client.py")
            return {
                "category": "GENERAL_QUESTION",
                "confidence": 0.3,
                "should_ask_more": False,
                "key_topics": ["error"],
                "response_focus": "Responder de manera amigable",
                "recommended_action": "continue_conversation",
                "urgency_level": "low"
            }
    
    async def extract_information(
        self,
        user_message: str,
        user_memory
    ) -> Dict[str, Any]:
        """
        Extrae información relevante del mensaje del usuario.
        
        Args:
            user_message: Mensaje del usuario
            user_memory: Contexto previo del usuario
            
        Returns:
            Dict con información extraída estructurada
        """
        try:
            prompt = get_information_extraction_prompt(user_message, user_memory)
            config = PromptConfig.get_config('information_extraction')
            
            self.logger.info(f"📊 Extrayendo información de: '{user_message[:50]}...'")
            
            response = await self.client.chat.completions.create(
                model=config['model'],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                messages=[
                    {"role": "system", "content": "Eres un extractor de información experto. Responde SOLO con JSON válido."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content
            if content:
                content = content.strip()
            else:
                content = ""
            
            # Verificar si la respuesta está vacía
            if not content:
                self.logger.warning("⚠️ Respuesta vacía de OpenAI para extracción de información")
                return {}
            
            try:
                extracted_data = json.loads(content)
                self.logger.info(f"✅ Información extraída exitosamente")
                return extracted_data
            except json.JSONDecodeError as e:
                self.logger.error(f"❌ Error parseando JSON de extracción: {e}")
                self.logger.error(f"📄 Contenido recibido: '{content}'")
                return {}
                
        except Exception as e:
            self.logger.error(f"💥 Error en extracción de información: {e}")
            return {}
    
    async def generate_response(
        self,
        user_message: str,
        user_memory,
        intent_analysis: Dict[str, Any],
        context_info: str = ""
    ) -> str:
        """
        Genera una respuesta inteligente basada en intención y contexto.
        
        Args:
            user_message: Mensaje del usuario
            user_memory: Memoria del usuario
            intent_analysis: Resultado del análisis de intención
            context_info: Información adicional de contexto
            
        Returns:
            Respuesta generada por GPT-4o-mini
        """
        try:
            prompt = get_response_generation_prompt(
                user_message, user_memory, intent_analysis, context_info
            )
            config = PromptConfig.get_config('main_agent')
            
            self.logger.info(f"💬 Generando respuesta para categoría: {intent_analysis.get('category', 'UNKNOWN')}")
            
            response = await self.client.chat.completions.create(
                model=config['model'],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            generated_response = response.choices[0].message.content
            if generated_response:
                generated_response = generated_response.strip()
            else:
                generated_response = ""
            
            # Validar que la respuesta no esté vacía
            if not generated_response:
                self.logger.warning("⚠️ Respuesta vacía de OpenAI, usando fallback")
                return self._get_fallback_response(intent_analysis.get('category'))
            
            self.logger.info(f"✅ Respuesta generada: {len(generated_response)} caracteres")
            return generated_response
            
        except Exception as e:
            self.logger.error(f"💥 Error generando respuesta: {e}")
            # Fallback para asegurar que siempre responda algo
            return self._get_fallback_response(intent_analysis.get('category', 'GENERAL_QUESTION'))
    
    def _get_fallback_response(self, category: str) -> str:
        """
        Genera respuesta de fallback según la categoría.
        
        Args:
            category: Categoría de intención detectada
            
        Returns:
            Respuesta de fallback apropiada
        """
        fallback_responses = {
            'FREE_RESOURCES': """¡Por supuesto! 📚
            
Te voy a compartir algunos recursos gratuitos que te van a ayudar mucho.

¿Te gustaría que también te cuente sobre nuestro curso completo?""",
            
            'EXPLORATION': """¡Excelente pregunta! 🎯

Me encanta que estés explorando cómo la IA puede ayudarte.

¿En qué área específica te gustaría enfocarte? ¿Marketing, automatización, análisis de datos?""",
            
            'OBJECTION_PRICE': """Entiendo perfectamente tu preocupación por la inversión. 💰

Lo que me gusta es que veas esto como una inversión, no como un gasto.

¿Te gustaría que conversemos sobre el retorno de inversión que puedes esperar?""",
            
            'CONTACT_REQUEST': """¡Perfecto! 👥

Te voy a conectar directamente con uno de nuestros asesores especializados.

¿Estás listo/a para que iniciemos el contacto?""",
            
            'GENERAL_QUESTION': """¡Excelente pregunta! 😊

Me encanta tu curiosidad sobre la IA.

¿En qué puedo ayudarte específicamente? ¿Te interesa automatizar algún proceso en particular?"""
        }
        
        return fallback_responses.get(category, """¡Hola! 👋

Gracias por escribir. Estoy aquí para ayudarte con todo lo relacionado a nuestros cursos de IA.

¿En qué puedo asistirte hoy?""")
    
    async def analyze_and_respond(
        self,
        user_message: str,
        user_memory,
        recent_messages: Optional[list] = None,
        context_info: str = ""
    ) -> Dict[str, Any]:
        """
        Proceso completo: analiza intención y genera respuesta.
        
        Args:
            user_message: Mensaje del usuario
            user_memory: Memoria del usuario
            recent_messages: Mensajes recientes
            context_info: Información de contexto
            
        Returns:
            Dict con análisis e información extraída y respuesta generada
        """
        try:
            # 1. Analizar intención
            intent_analysis = await self.analyze_intent(
                user_message, user_memory, recent_messages
            )
            
            # 2. Extraer información (con manejo de errores mejorado)
            try:
                extracted_info = await self.extract_information(
                    user_message, user_memory
                )
            except Exception as extraction_error:
                self.logger.warning(f"⚠️ Error en extracción de información: {extraction_error}")
                extracted_info = {}
            
            # 3. Generar respuesta basada en intención
            response = await self.generate_response(
                user_message, user_memory, intent_analysis, context_info
            )
            
            return {
                'intent_analysis': intent_analysis,
                'extracted_info': extracted_info,
                'response': response,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"💥 Error en proceso completo: {e}")
            return {
                'intent_analysis': {'category': 'GENERAL_QUESTION', 'confidence': 0.3},
                'extracted_info': {},
                'response': self._get_fallback_response('GENERAL_QUESTION'),
                'success': False,
                'error': str(e)
            }
    
    async def validate_response(
        self,
        response: str,
        course_data: dict = None,
        bonuses_data: list = None,
        all_courses_data: list = None
    ) -> Dict[str, Any]:
        """
        Valida una respuesta usando el validador anti-alucinación.
        
        Args:
            response: Respuesta del agente a validar
            course_data: Datos del curso para validación
            bonuses_data: Lista de bonos disponibles
            all_courses_data: Lista de todos los cursos
            
        Returns:
            Dict con resultado de validación
        """
        try:
            debug_print(f"🔍 VALIDANDO RESPUESTA\n📝 Texto: '{response[:100]}{'...' if len(response) > 100 else ''}'", "validate_response", "openai_client.py")
            
            prompt = get_validation_prompt(response, course_data or {}, bonuses_data or [], all_courses_data or [])
            config = PromptConfig.get_config('intent_analysis')  # Usar misma config que intent_analysis
            
            debug_print("🚀 Enviando a OpenAI para validación...", "validate_response", "openai_client.py")
            validation_response = await self.client.chat.completions.create(
                model=config['model'],
                temperature=0.1,  # Muy baja para validación precisa
                max_tokens=300,
                messages=[
                    {"role": "system", "content": "Eres un validador anti-alucinación. Responde SOLO con JSON válido."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = validation_response.choices[0].message.content.strip()
            debug_print(f"📥 RESPUESTA DE VALIDACIÓN:\n{content}", "validate_response", "openai_client.py")
            
            try:
                validation_data = json.loads(content)
                debug_print(f"✅ Validación PARSEADA - Es válida: {validation_data.get('is_valid', True)}", "validate_response", "openai_client.py")
                return validation_data
            except json.JSONDecodeError as e:
                debug_print(f"❌ ERROR PARSEANDO JSON DE VALIDACIÓN: {e}", "validate_response", "openai_client.py")
                # En caso de error de parseo, aprobar por defecto (filosofía permisiva)
                return {
                    "is_valid": True,
                    "confidence": 0.8,
                    "issues": [],
                    "corrected_response": None,
                    "explanation": "Error parseando validación, aprobado por defecto"
                }
                
        except Exception as e:
            debug_print(f"💥 ERROR EN VALIDACIÓN: {e}", "validate_response", "openai_client.py")
            # En caso de error, aprobar por defecto (filosofía permisiva)
            return {
                "is_valid": True,
                "confidence": 0.7,
                "issues": [],
                "corrected_response": None,
                "explanation": f"Error en validación, aprobado por defecto: {str(e)}"
            }