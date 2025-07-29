"""
Response Validation Use Case

This use case validates AI-generated responses against database information
to prevent hallucination and ensure accuracy.
"""

import logging
from typing import Dict, Optional, List, Any
import re
from dataclasses import dataclass

from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.infrastructure.database.client import DatabaseClient

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of response validation"""
    is_valid: bool
    issues: List[str]
    corrected_response: Optional[str] = None
    confidence_score: float = 0.0

class ValidateResponseUseCase:
    """
    Validates AI responses against database information to prevent hallucination.
    """
    
    def __init__(self, db_client: DatabaseClient, course_repository: CourseRepository):
        self.db_client = db_client
        self.course_repository = course_repository
        
        # Patrones de riesgo que requieren validación
        self.risk_patterns = [
            r'\b\d+\s*módulos?\b',  # "12 módulos"
            r'\b\d+\s*semanas?\b',  # "8 semanas"
            r'\b\d+\s*días?\b',     # "30 días"
            r'\b\d+\s*horas?\b',    # "40 horas"
            r'precio.*\$\d+',       # precios específicos
            r'descuento.*\d+%',     # descuentos específicos
            r'certificado?',        # menciones de certificado
            r'comienza.*\w+',       # fechas de inicio
            r'incluye.*\d+',        # incluye X cantidad
        ]
        
        # Frases prohibidas que indican invención
        self.forbidden_phrases = [
            "el curso tiene",
            "incluye certificado",
            "la duración es de",
            "comenzamos el",
            "el precio tiene descuento",
            "son 12 módulos",
            "8 semanas de duración"
        ]

    async def validate_response(
        self, 
        response_text: str, 
        course_info: Optional[Dict] = None,
        user_query: Optional[str] = None
    ) -> ValidationResult:
        """
        Validates an AI response against database information.
        
        Args:
            response_text: The AI-generated response to validate
            course_info: Database information about the course (if applicable)
            user_query: Original user query for context
            
        Returns:
            ValidationResult: Validation result with issues and corrections
        """
        try:
            issues = []
            confidence_score = 1.0
            
            # 1. Verificar patrones de riesgo
            risk_issues = self._check_risk_patterns(response_text)
            issues.extend(risk_issues)
            
            # 2. Verificar frases prohibidas
            forbidden_issues = self._check_forbidden_phrases(response_text)
            issues.extend(forbidden_issues)
            
            # 3. Validar información de curso si está disponible
            if course_info:
                course_issues = await self._validate_course_information(response_text, course_info)
                issues.extend(course_issues)
            
            # 4. Verificar que mencione validación de BD cuando corresponde
            db_validation_issues = self._check_database_validation_mentions(response_text, course_info)
            issues.extend(db_validation_issues)
            
            # Calcular puntuación de confianza
            confidence_score = max(0.0, confidence_score - (len(issues) * 0.2))
            
            # Determinar si es válida (sin issues críticos)
            critical_issues = [issue for issue in issues if "CRÍTICO" in issue]
            is_valid = len(critical_issues) == 0
            
            # Generar respuesta corregida si es necesario
            corrected_response = None
            if not is_valid:
                corrected_response = await self._generate_safe_response(user_query, course_info)
            
            logger.info(f"Validación completada. Issues: {len(issues)}, Válida: {is_valid}")
            
            return ValidationResult(
                is_valid=is_valid,
                issues=issues,
                corrected_response=corrected_response,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error validating response: {e}")
            return ValidationResult(
                is_valid=False,
                issues=[f"Error en validación: {str(e)}"],
                confidence_score=0.0
            )

    def _check_risk_patterns(self, response_text: str) -> List[str]:
        """Verifica patrones de riesgo en la respuesta"""
        issues = []
        response_lower = response_text.lower()
        
        for pattern in self.risk_patterns:
            matches = re.findall(pattern, response_lower)
            if matches:
                issues.append(f"CRÍTICO: Patrón de riesgo detectado: {matches[0]}")
        
        return issues

    def _check_forbidden_phrases(self, response_text: str) -> List[str]:
        """Verifica frases prohibidas que indican invención"""
        issues = []
        response_lower = response_text.lower()
        
        for phrase in self.forbidden_phrases:
            if phrase in response_lower:
                issues.append(f"CRÍTICO: Frase prohibida detectada: '{phrase}'")
        
        return issues

    async def _validate_course_information(self, response_text: str, course_info: Dict) -> List[str]:
        """Valida información específica del curso"""
        issues = []
        response_lower = response_text.lower()
        
        # Verificar que datos mencionados existen en course_info
        
        # 1. Precio mencionado vs BD
        if any(word in response_lower for word in ['precio', 'cuesta', 'costo', '$']):
            if 'price' not in course_info or not course_info.get('price'):
                issues.append("ADVERTENCIA: Menciona precio sin datos verificados en BD")
        
        # 2. Duración mencionada vs BD
        if any(word in response_lower for word in ['duración', 'horas', 'tiempo']):
            if 'total_duration_min' not in course_info or not course_info.get('total_duration_min'):
                issues.append("ADVERTENCIA: Menciona duración sin datos verificados en BD")
        
        # 3. Nivel mencionado vs BD
        if any(word in response_lower for word in ['nivel', 'básico', 'intermedio', 'avanzado']):
            if 'level' not in course_info or not course_info.get('level'):
                issues.append("ADVERTENCIA: Menciona nivel sin datos verificados en BD")
        
        # 4. Sesiones mencionadas vs BD
        if any(word in response_lower for word in ['sesión', 'módulo', 'clase']):
            if 'session_count' not in course_info or not course_info.get('session_count'):
                issues.append("ADVERTENCIA: Menciona sesiones sin datos verificados en BD")
        
        return issues

    def _check_database_validation_mentions(self, response_text: str, course_info: Optional[Dict]) -> List[str]:
        """Verifica que mencione validación con BD cuando corresponde"""
        issues = []
        response_lower = response_text.lower()
        
        # Si hay información de curso pero no menciona validación
        if course_info and any(word in response_lower for word in ['curso', 'precio', 'duración']):
            validation_phrases = [
                'según la información',
                'basándome en',
                'según nuestra base de datos',
                'datos verificados',
                'información disponible'
            ]
            
            has_validation_mention = any(phrase in response_lower for phrase in validation_phrases)
            
            if not has_validation_mention:
                issues.append("RECOMENDACIÓN: Agregar mención de validación con BD")
        
        return issues

    async def _generate_safe_response(self, user_query: Optional[str], course_info: Optional[Dict]) -> str:
        """Genera una respuesta segura cuando la validación falla"""
        
        if course_info and course_info.get('name'):
            course_name = course_info['name']
            return f"""Hola! Te interesa información sobre **{course_name}**.

Para darte información exacta y verificada, déjame consultar los detalles específicos que necesitas de nuestra base de datos.

¿Qué te gustaría saber específicamente? Por ejemplo:
- Información general del curso
- Modalidad y duración  
- Proceso de inscripción
- Beneficios de la capacitación en IA

¡Te ayudo con datos precisos! 😊"""
        
        return """¡Hola! Para darte información exacta sobre nuestros cursos de IA, déjame consultar los detalles específicos en nuestra base de datos.

¿Qué te gustaría saber específicamente sobre nuestros cursos? ¡Te ayudo con datos verificados! 😊"""

    async def check_course_data_integrity(self, course_id: str) -> Dict[str, Any]:
        """
        Verifica la integridad de datos de un curso específico en BD.
        
        Args:
            course_id: ID del curso a verificar
            
        Returns:
            Dict con el estado de integridad de datos
        """
        try:
            course_info = await self.course_repository.get_course_by_id(course_id)
            
            if not course_info:
                return {
                    "is_valid": False,
                    "error": "Curso no encontrado en BD",
                    "missing_fields": ["all"]
                }
            
            # Campos críticos requeridos
            required_fields = ['name', 'short_description', 'price', 'level', 'modality']
            missing_fields = [field for field in required_fields if not course_info.get(field)]
            
            return {
                "is_valid": len(missing_fields) == 0,
                "course_info": course_info,
                "missing_fields": missing_fields,
                "available_fields": list(course_info.keys())
            }
            
        except Exception as e:
            logger.error(f"Error checking course data integrity: {e}")
            return {
                "is_valid": False,  
                "error": str(e),
                "missing_fields": ["error"]
            }