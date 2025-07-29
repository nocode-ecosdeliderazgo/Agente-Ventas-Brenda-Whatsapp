"""
Anti-Hallucination Use Case

This use case prevents AI hallucination by enforcing strict validation rules
and providing safe fallback responses when database information is insufficient.
"""

import logging
from typing import Dict, Optional, Any, List
import json
import re

from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.application.usecases.validate_response_use_case import ValidateResponseUseCase, ValidationResult
from prompts.anti_hallucination_prompts import get_anti_hallucination_prompt, get_course_validation_rules

logger = logging.getLogger(__name__)

class AntiHallucinationUseCase:
    """
    Prevents AI hallucination by validating responses and providing safe alternatives.
    """
    
    def __init__(
        self, 
        openai_client: OpenAIClient,
        course_repository: CourseRepository,
        validate_response_use_case: ValidateResponseUseCase
    ):
        self.openai_client = openai_client
        self.course_repository = course_repository
        self.validate_response_use_case = validate_response_use_case
        
        # Indicadores de que el usuario busca información específica
        self.specific_info_keywords = [
            'precio', 'costo', 'cuánto', 'duración', 'tiempo', 'horas',
            'módulos', 'sesiones', 'certificado', 'cuando empieza',
            'requisitos', 'incluye', 'contenido', 'temario'
        ]

    async def generate_safe_response(
        self,
        user_message: str,
        user_memory: Any,
        intent_analysis: Dict,
        course_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generates a safe, validated response that prevents hallucination.
        
        Args:
            user_message: User's message
            user_memory: User memory object
            intent_analysis: Intent analysis result
            course_info: Course information from database
            
        Returns:
            Dict with safe response and validation metadata
        """
        try:
            # 1. Determinar si necesita información específica verificada
            needs_specific_info = self._user_needs_specific_info(user_message, intent_analysis)
            
            # 2. Verificar disponibilidad de datos en BD
            data_availability = await self._check_data_availability(course_info, needs_specific_info)
            
            # 3. Generar respuesta según disponibilidad de datos
            if data_availability['has_sufficient_data']:
                # Generar respuesta con datos verificados
                response = await self._generate_verified_response(
                    user_message, user_memory, intent_analysis, course_info
                )
            else:
                # Generar respuesta segura sin datos específicos
                response = await self._generate_fallback_response(
                    user_message, user_memory, intent_analysis, data_availability
                )
            
            # 4. Validar la respuesta generada
            validation_result = await self.validate_response_use_case.validate_response(
                response['message'], course_info, user_message
            )
            
            # 5. Usar respuesta corregida si la validación falla
            if not validation_result.is_valid and validation_result.corrected_response:
                logger.warning(f"Respuesta corregida por validación. Issues: {validation_result.issues}")
                response['message'] = validation_result.corrected_response
                response['validation_corrected'] = True
            
            # 6. Agregar metadata de validación
            response.update({
                'anti_hallucination_applied': True,
                'validation_result': {
                    'is_valid': validation_result.is_valid,
                    'confidence_score': validation_result.confidence_score,
                    'issues_count': len(validation_result.issues)
                },
                'data_availability': data_availability
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in anti-hallucination use case: {e}")
            return await self._generate_emergency_fallback(user_message)

    def _user_needs_specific_info(self, user_message: str, intent_analysis: Dict) -> bool:
        """Determina si el usuario busca información específica que requiere validación"""
        message_lower = user_message.lower()
        
        # Verificar keywords específicos
        has_specific_keywords = any(keyword in message_lower for keyword in self.specific_info_keywords)
        
        # Verificar intención de exploración de detalles
        exploration_categories = ['EXPLORATION_COURSE_DETAILS', 'EXPLORATION_PRICING', 'EXPLORATION_SCHEDULE']
        has_exploration_intent = intent_analysis.get('category') in exploration_categories
        
        return has_specific_keywords or has_exploration_intent

    async def _check_data_availability(self, course_info: Optional[Dict], needs_specific: bool) -> Dict[str, Any]:
        """Verifica disponibilidad de datos requeridos en BD"""
        
        if not course_info:
            return {
                'has_sufficient_data': False,
                'missing_data': ['course_info'],
                'reason': 'No course information available'
            }
        
        if not needs_specific:
            # Para información general, datos básicos son suficientes
            basic_fields = ['name', 'short_description']
            missing_basic = [field for field in basic_fields if not course_info.get(field)]
            
            return {
                'has_sufficient_data': len(missing_basic) == 0,
                'missing_data': missing_basic,
                'reason': 'Basic information check'
            }
        
        # Para información específica, verificar campos detallados
        detailed_fields = ['name', 'short_description', 'price', 'total_duration_min', 'level', 'session_count']
        missing_detailed = [field for field in detailed_fields if not course_info.get(field)]
        
        return {
            'has_sufficient_data': len(missing_detailed) <= 2,  # Tolerar hasta 2 campos faltantes
            'missing_data': missing_detailed,
            'available_data': [field for field in detailed_fields if course_info.get(field)],
            'reason': 'Detailed information check'
        }

    async def _generate_verified_response(
        self,
        user_message: str,
        user_memory: Any,
        intent_analysis: Dict,
        course_info: Dict
    ) -> Dict[str, Any]:
        """Genera respuesta usando solo datos verificados de BD"""
        
        # Preparar contexto verificado
        verified_context = self._prepare_verified_context(course_info)
        
        # Prompt con validación estricta
        system_prompt = f"""
        {get_anti_hallucination_prompt()}
        
        INFORMACIÓN VERIFICADA DISPONIBLE:
        {json.dumps(verified_context, indent=2, ensure_ascii=False)}
        
        INSTRUCCIONES ESPECÍFICAS:
        1. USA SOLO la información del contexto verificado
        2. Si mencionas precios, duración o detalles: cita la fuente como "según nuestra base de datos"
        3. NO inventes datos que no estén en el contexto verificado
        4. Si faltan datos específicos solicitados, di "déjame consultar esa información específica"
        """
        
        # Generar respuesta con OpenAI
        response = await self.openai_client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Usuario pregunta: {user_message}"}
            ],
            model="gpt-4o-mini",
            max_tokens=500,
            temperature=0.3  # Baja temperatura para respuestas más consistentes
        )
        
        return {
            'message': response,
            'generation_method': 'verified_data',
            'verified_context_used': verified_context
        }

    async def _generate_fallback_response(
        self,
        user_message: str,
        user_memory: Any,
        intent_analysis: Dict,
        data_availability: Dict
    ) -> Dict[str, Any]:
        """Genera respuesta segura cuando no hay datos suficientes"""
        
        # Determinar tipo de fallback según la intención
        fallback_type = self._determine_fallback_type(intent_analysis, data_availability)
        
        if fallback_type == 'consultation_offer':
            message = """¡Excelente pregunta! Para darte información exacta y actualizada, déjame consultar los detalles específicos en nuestra base de datos.

¿Te gustaría que revise información específica sobre:
- Modalidad y estructura del curso
- Inversión y opciones de pago  
- Cronograma y duración
- Beneficios específicos para tu perfil profesional

¡Te ayudo con datos precisos verificados! 😊"""

        elif fallback_type == 'general_benefits':
            message = """¡Me da mucho gusto tu interés en capacitarte en IA! 

La Inteligencia Artificial puede transformar significativamente tu productividad profesional, sin importar tu sector. Nuestros cursos están diseñados específicamente para líderes de PyMEs que buscan ventaja competitiva.

Para darte información específica sobre nuestro programa, déjame consultar los detalles exactos. ¿Qué aspecto te interesa más conocer?"""

        else:  # 'data_collection'
            message = """¡Hola! Me encanta que estés explorando cómo la IA puede impulsar tu negocio.

Para recomendarte el programa más adecuado y darte información precisa, me gustaría conocer un poco más sobre ti:

¿En qué sector trabajas y cuál es tu rol principal? Esto me ayudará a darte información más relevante sobre nuestros cursos de IA.

¡Conversemos! 😊"""

        return {
            'message': message,
            'generation_method': 'safe_fallback',
            'fallback_type': fallback_type,
            'data_availability': data_availability
        }

    def _prepare_verified_context(self, course_info: Dict) -> Dict[str, Any]:
        """Prepara contexto con solo datos verificados"""
        verified_context = {}
        
        # Campos seguros para usar
        safe_fields = [
            'name', 'short_description', 'long_description', 'price', 'currency',
            'level', 'modality', 'session_count', 'total_duration_min'
        ]
        
        for field in safe_fields:
            if course_info.get(field):
                verified_context[field] = course_info[field]
        
        # Formatear duración si está disponible
        if 'total_duration_min' in verified_context:
            minutes = verified_context['total_duration_min']
            if minutes:
                hours = round(minutes / 60, 1)
                verified_context['duration_formatted'] = f"{hours} horas"
        
        return verified_context

    def _determine_fallback_type(self, intent_analysis: Dict, data_availability: Dict) -> str:
        """Determina el tipo de respuesta fallback más apropiada"""
        
        category = intent_analysis.get('category', '')
        
        if category in ['EXPLORATION_PRICING', 'EXPLORATION_SCHEDULE']:
            return 'consultation_offer'
        elif category in ['EXPLORATION_GENERAL', 'EXPLORATION_BENEFITS']:
            return 'general_benefits'
        else:
            return 'data_collection'

    async def _generate_emergency_fallback(self, user_message: str) -> Dict[str, Any]:
        """Genera respuesta de emergencia cuando todo falla"""
        
        message = """¡Hola! Gracias por tu interés en nuestros cursos de IA.

En este momento estoy consultando la información más actualizada para darte datos precisos. 

¡Te ayudo en un momento! 😊"""
        
        return {
            'message': message,
            'generation_method': 'emergency_fallback',
            'anti_hallucination_applied': True,
            'validation_result': {
                'is_valid': True,
                'confidence_score': 1.0,
                'issues_count': 0
            }
        }

    async def validate_existing_response(self, response_text: str, course_info: Optional[Dict] = None) -> ValidationResult:
        """
        Valida una respuesta ya generada (útil para testing o validación posterior).
        
        Args:
            response_text: Respuesta a validar
            course_info: Información del curso para validación
            
        Returns:
            ValidationResult: Resultado de la validación
        """
        return await self.validate_response_use_case.validate_response(
            response_text, course_info
        )