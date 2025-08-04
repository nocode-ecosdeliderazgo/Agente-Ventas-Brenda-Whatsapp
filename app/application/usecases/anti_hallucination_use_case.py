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
from app.infrastructure.tools.tool_db import get_tool_db
from app.application.usecases.validate_response_use_case import ValidateResponseUseCase, ValidationResult
from prompts.anti_hallucination_prompts import get_anti_hallucination_prompt, get_course_validation_rules
from prompts.agent_prompts import DATABASE_TOOL_PROMPT

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
        self.tool_db = None  # Se inicializa bajo demanda
        
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
        course_info: Optional[Dict] = None,
        course_detailed_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generates a safe, validated response that prevents hallucination.
        
        Args:
            user_message: User's message
            user_memory: User memory object
            intent_analysis: Intent analysis result
            course_info: Course information from database
            course_detailed_info: Detailed course info for OpenAI (name, description, etc.)
            
        Returns:
            Dict with safe response and validation metadata
        """
        try:
            # 1. Determinar si necesita información específica verificada
            needs_specific_info = self._user_needs_specific_info(user_message, intent_analysis)
            
            # 2. Verificar disponibilidad de datos en BD
            # Combinar course_info y course_detailed_info para tener información completa
            combined_course_info = course_info or {}
            if course_detailed_info:
                combined_course_info.update(course_detailed_info)
                
            data_availability = await self._check_data_availability(combined_course_info, needs_specific_info)
            
            # 🆕 2.5. Si no hay datos suficientes, intentar obtener desde tool_db
            if not data_availability['has_sufficient_data'] and needs_specific_info:
                logger.info("🔍 Datos insuficientes - Intentando obtener desde tool_db")
                
                try:
                    if self.tool_db is None:
                        self.tool_db = await get_tool_db()
                    
                    # Obtener datos específicos desde BD usando tool_db
                    enhanced_course_info = await self._get_course_info_from_tool_db(user_message)
                    
                    if enhanced_course_info:
                        combined_course_info.update(enhanced_course_info)
                        # Re-evaluar disponibilidad de datos con información de tool_db
                        data_availability = await self._check_data_availability(combined_course_info, needs_specific_info)
                        logger.info(f"✅ tool_db mejoró disponibilidad de datos: {data_availability['has_sufficient_data']}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error usando tool_db en anti-hallucination: {e}")
            
            # 3. Generar respuesta según disponibilidad de datos
            if data_availability['has_sufficient_data']:
                # Generar respuesta con datos verificados
                response = await self._generate_verified_response(
                    user_message, user_memory, intent_analysis, combined_course_info
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
    
    async def _get_course_info_from_tool_db(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        Intenta obtener información del curso desde la base de datos usando tool_db.
        
        Args:
            user_message: Mensaje del usuario para detectar qué información necesita
            
        Returns:
            Diccionario con información del curso o None si no se encuentra
        """
        try:
            if self.tool_db is None:
                return None
            
            logger.info("🔍 Obteniendo información de curso desde tool_db")
            
            # Detectar qué tipo de información específica necesita el usuario
            message_lower = user_message.lower()
            
            # Obtener curso(s) principal(es)
            courses = await self.tool_db.query('ai_courses', {}, limit=3)
            
            if not courses:
                logger.warning("⚠️ No se encontraron cursos en tool_db")
                return None
            
            course_info = {}
            main_course = courses[0]  # Usar el primer curso como principal
            
            # Mapear información básica del curso
            course_info.update({
                'name': main_course.get('name', ''),
                'price': main_course.get('price', ''),
                'currency': main_course.get('currency', 'MXN'),
                'session_count': main_course.get('session_count', 0),
                'total_duration_min': main_course.get('total_duration_min', 0),
                'modality': main_course.get('modality', ''),
                'short_description': main_course.get('short_description', ''),
                'roi': main_course.get('roi', '')
            })
            
            # Si el usuario pregunta por contenido específico, obtener actividades
            if any(word in message_lower for word in ['contenido', 'temario', 'incluye', 'módulos']):
                course_id = main_course.get('id_course')
                if course_id:
                    activities = await self.tool_db.query('ai_tema_activity', {'id_course_fk': course_id}, limit=10)
                    if activities:
                        course_info['activities'] = activities
                        # Crear resumen de contenido
                        activity_types = list(set(act.get('item_type', '') for act in activities))
                        course_info['content_summary'] = f"Incluye: {', '.join(activity_types)}"
            
            # Si el usuario pregunta por bonos, obtener bonos activos
            if any(word in message_lower for word in ['bonos', 'recursos', 'adicional', 'extra']):
                course_id = main_course.get('id_course')
                if course_id:
                    bonuses = await self.tool_db.query('bond', {'active': True, 'id_courses_fk': course_id}, limit=5)
                    if bonuses:
                        course_info['bonuses'] = bonuses
                        course_info['bonus_count'] = len(bonuses)
            
            # Si el usuario pregunta por sesiones específicas, obtener sesiones
            if any(word in message_lower for word in ['sesiones', 'clases', 'módulos']):
                course_id = main_course.get('id_course')
                if course_id:
                    sessions = await self.tool_db.query('ai_course_session', {'id_course_fk': course_id}, limit=20)
                    if sessions:
                        course_info['sessions'] = sessions
                        course_info['session_details'] = [
                            {'title': s.get('title'), 'duration': s.get('duration_minutes')} 
                            for s in sessions
                        ]
            
            # Calcular duración en formato legible
            if course_info.get('total_duration_min'):
                hours = course_info['total_duration_min'] // 60
                minutes = course_info['total_duration_min'] % 60
                duration_text = f"{hours} horas"
                if minutes > 0:
                    duration_text += f" y {minutes} minutos"
                course_info['duration_formatted'] = duration_text
            
            logger.info(f"✅ Información de curso obtenida desde tool_db: {course_info.get('name', 'Sin nombre')}")
            return course_info
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo información de curso desde tool_db: {e}")
            return None