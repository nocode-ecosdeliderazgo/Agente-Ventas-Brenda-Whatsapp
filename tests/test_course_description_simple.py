"""
Tests simplificados para el sistema de descripciones de cursos (sin async).
"""
import pytest
from unittest.mock import Mock
from app.config.course_catalog import FALLBACK_COURSES, get_fallback_course_description


class TestCourseDescriptionBasics:
    """Tests básicos para el sistema de descripciones sin componentes async."""
    
    def test_fallback_courses_have_both_descriptions(self):
        """Test: verificar que las constantes de fallback tienen ambas descripciones."""
        course_code = 'EXPERTO_IA_GPT_GEMINI'
        
        # Verificar que el curso existe en fallback
        assert course_code in FALLBACK_COURSES
        assert 'short' in FALLBACK_COURSES[course_code]
        assert 'long' in FALLBACK_COURSES[course_code]
        
        # Verificar que tienen contenido
        assert FALLBACK_COURSES[course_code]['short'] != ""
        assert FALLBACK_COURSES[course_code]['long'] != ""
        assert len(FALLBACK_COURSES[course_code]['short']) > 100  # Descripción corta debe tener contenido
        assert len(FALLBACK_COURSES[course_code]['long']) > 500   # Descripción larga debe ser sustancial
    
    def test_get_fallback_course_description_short(self):
        """Test: obtener descripción corta desde fallback."""
        course_code = 'EXPERTO_IA_GPT_GEMINI'
        result = get_fallback_course_description(course_code, 'short')
        
        expected = FALLBACK_COURSES[course_code]['short']
        assert result == expected
        assert "ChatGPT + Gemini" in result
        assert "PyMEs" in result
    
    def test_get_fallback_course_description_long(self):
        """Test: obtener descripción larga desde fallback."""
        course_code = 'EXPERTO_IA_GPT_GEMINI'
        result = get_fallback_course_description(course_code, 'long')
        
        expected = FALLBACK_COURSES[course_code]['long']
        assert result == expected
        assert "EXPERTO EN IA PARA PROFESIONALES" in result
        assert "TEMARIO DETALLADO" in result
        assert "BENEFICIOS ESPECÍFICOS" in result
        assert "INSTRUCTORES EXPERTOS" in result
    
    def test_get_fallback_course_description_unknown_course(self):
        """Test: curso desconocido debe retornar string vacío."""
        unknown_course = 'CURSO_INEXISTENTE'
        result = get_fallback_course_description(unknown_course, 'short')
        assert result == ""
    
    def test_get_fallback_course_description_invalid_level(self):
        """Test: nivel inválido debe retornar string vacío."""
        course_code = 'EXPERTO_IA_GPT_GEMINI'
        result = get_fallback_course_description(course_code, 'invalid_level')
        assert result == ""


class TestDescriptionLevelDetection:
    """Tests para la lógica de detección de nivel de descripción."""
    
    def test_determine_description_level_short_cases(self):
        """Test: casos que deben retornar descripción 'short'."""
        from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
        
        # Crear instancia mock del use case para testear el método
        use_case = GenerateIntelligentResponseUseCase(
            intent_analyzer=Mock(),
            twilio_client=Mock(),
            openai_client=Mock(),
            db_client=Mock(),
            course_repository=Mock()
        )
        
        short_messages = [
            "¿de qué trata el curso?",
            "qué aprendo",
            "contenido del curso",
            "temario",
            "programa"
        ]
        
        for message in short_messages:
            result = use_case._determine_description_level(message)
            assert result == 'short', f"Mensaje '{message}' debería retornar 'short' pero retornó '{result}'"
    
    def test_determine_description_level_long_cases(self):
        """Test: casos que deben retornar descripción 'long'."""
        from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
        
        # Crear instancia mock del use case para testear el método
        use_case = GenerateIntelligentResponseUseCase(
            intent_analyzer=Mock(),
            twilio_client=Mock(),
            openai_client=Mock(),
            db_client=Mock(),
            course_repository=Mock()
        )
        
        long_messages = [
            "temario detallado",
            "programa completo",
            "beneficios completos",
            "quiero ver todo el contenido",
            "información completa del curso",
            "detalle de módulos",
            "cronograma completo",
            "todo sobre el curso",
            "recursos incluidos"
        ]
        
        for message in long_messages:
            result = use_case._determine_description_level(message)
            assert result == 'long', f"Mensaje '{message}' debería retornar 'long' pero retornó '{result}'"
    
    def test_determine_description_level_edge_cases(self):
        """Test: casos límite y especiales."""
        from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
        
        use_case = GenerateIntelligentResponseUseCase(
            intent_analyzer=Mock(),
            twilio_client=Mock(),
            openai_client=Mock(),
            db_client=Mock(),
            course_repository=Mock()
        )
        
        # Casos que deben ser 'short' por defecto
        assert use_case._determine_description_level("") == 'short'
        assert use_case._determine_description_level("hola") == 'short'
        assert use_case._determine_description_level("precio") == 'short'
        
        # Casos que deben ser 'long'
        assert use_case._determine_description_level("dame toda la información completa") == 'long'
        assert use_case._determine_description_level("PROGRAMA COMPLETO") == 'long'  # Mayúsculas
        assert use_case._determine_description_level("quiero detalles") == 'long'


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"])