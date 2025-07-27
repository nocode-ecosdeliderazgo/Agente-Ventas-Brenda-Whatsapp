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
    PromptConfig
)

logger = logging.getLogger(__name__)


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
            prompt = get_intent_analysis_prompt(user_message, user_memory, recent_messages)
            config = PromptConfig.get_config('intent_analysis')
            
            self.logger.info(f"🔍 Analizando intención: '{user_message[:50]}...'")
            
            response = await self.client.chat.completions.create(
                model=config['model'],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                messages=[
                    {"role": "system", "content": "Eres un analizador de intención experto. Responde SOLO con JSON válido."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content.strip()
            
            # Intentar parsear JSON
            try:
                intent_data = json.loads(content)
                self.logger.info(f"✅ Intención detectada: {intent_data.get('category', 'UNKNOWN')}")
                return intent_data
            except json.JSONDecodeError as e:
                self.logger.error(f"❌ Error parseando JSON de intención: {e}")
                self.logger.error(f"Respuesta recibida: {content}")
                
                # Fallback con intención genérica
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
            self.logger.error(f"💥 Error en análisis de intención: {e}")
            # Fallback para asegurar que el bot funcione
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
            
            content = response.choices[0].message.content.strip()
            
            try:
                extracted_data = json.loads(content)
                self.logger.info(f"✅ Información extraída exitosamente")
                return extracted_data
            except json.JSONDecodeError as e:
                self.logger.error(f"❌ Error parseando JSON de extracción: {e}")
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
            
            generated_response = response.choices[0].message.content.strip()
            
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
            
            # 2. Extraer información (en paralelo)
            extracted_info = await self.extract_information(
                user_message, user_memory
            )
            
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