"""
Tests para el sistema de descripciones de cursos con fallback.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.config.course_catalog import FALLBACK_COURSES


class TestCourseDescriptionSystem:
    """Tests para el sistema de descripciones de cursos con fallback hard-codeado."""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock del cliente de base de datos."""
        mock_client = Mock()
        mock_client.execute_query = AsyncMock()
        return mock_client
    
    @pytest.fixture
    def course_repository(self, mock_db_client):
        """Repositorio de cursos con BD mockeada."""
        repo = CourseRepository()
        repo.db = mock_db_client
        return repo
    
    @pytest.mark.asyncio
    async def test_get_course_description_from_db_success_short(self, course_repository, mock_db_client):
        """Test: obtener descripción corta desde BD cuando todo funciona correctamente."""
        # Arrange
        course_code = 'EXPERTO_IA_GPT_GEMINI'
        expected_short = "Descripción corta desde BD"
        expected_long = "Descripción larga desde BD"
        
        mock_db_client.execute_query.return_value = [{
            'short_description': expected_short,
            'long_description': expected_long
        }]
        
        # Act
        result = await course_repository.get_course_description(course_code, 'short')
        
        # Assert
        assert result == expected_short
        mock_db_client.execute_query.assert_called_once()
        call_args = mock_db_client.execute_query.call_args
        assert course_code in call_args[0]  # Verificar que se pasó el course_code
    
    @pytest.mark.asyncio
    async def test_get_course_description_from_db_success_long(self, course_repository, mock_db_client):
        """Test: obtener descripción larga desde BD cuando todo funciona correctamente."""
        # Arrange
        course_code = 'EXPERTO_IA_GPT_GEMINI'
        expected_short = "Descripción corta desde BD"
        expected_long = "Descripción larga desde BD"
        
        mock_db_client.execute_query.return_value = [{
            'short_description': expected_short,
            'long_description': expected_long
        }]
        
        # Act
        result = await course_repository.get_course_description(course_code, 'long')
        
        # Assert
        assert result == expected_long
        mock_db_client.execute_query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_course_description_db_error_uses_fallback(self, course_repository, mock_db_client):
        """Test: cuando la BD falla, debe usar fallback hard-codeado."""
        # Arrange
        course_code = 'EXPERTO_IA_GPT_GEMINI'
        mock_db_client.execute_query.side_effect = Exception("Connection timeout")
        
        # Act
        result = await course_repository.get_course_description(course_code, 'short')
        
        # Assert
        # Debe retornar la descripción de fallback
        expected_fallback = FALLBACK_COURSES[course_code]['short']
        assert result == expected_fallback
        assert result != ""  # Verificar que no está vacío
    
    @pytest.mark.asyncio
    async def test_get_course_description_course_not_found_uses_fallback(self, course_repository, mock_db_client):
        """Test: cuando el curso no existe en BD, debe usar fallback."""
        # Arrange
        course_code = 'EXPERTO_IA_GPT_GEMINI'
        mock_db_client.execute_query.return_value = []  # No se encontró el curso
        
        # Act
        result = await course_repository.get_course_description(course_code, 'short')
        
        # Assert
        # Debe retornar la descripción de fallback
        expected_fallback = FALLBACK_COURSES[course_code]['short']
        assert result == expected_fallback
    
    @pytest.mark.asyncio
    async def test_get_course_description_empty_field_uses_fallback(self, course_repository, mock_db_client):
        """Test: cuando el campo de descripción está vacío en BD, debe usar fallback."""
        # Arrange
        course_code = 'EXPERTO_IA_GPT_GEMINI'
        mock_db_client.execute_query.return_value = [{
            'short_description': None,  # Campo vacío
            'long_description': "Descripción larga desde BD"
        }]
        
        # Act
        result = await course_repository.get_course_description(course_code, 'short')
        
        # Assert
        # Debe retornar la descripción de fallback porque short_description está vacío
        expected_fallback = FALLBACK_COURSES[course_code]['short']
        assert result == expected_fallback
    
    @pytest.mark.asyncio
    async def test_get_course_description_unknown_course_returns_empty(self, course_repository, mock_db_client):
        """Test: cuando el curso no existe ni en BD ni en fallback, retorna vacío."""
        # Arrange
        unknown_course_code = 'CURSO_INEXISTENTE'
        mock_db_client.execute_query.return_value = []  # No se encontró en BD
        
        # Act
        result = await course_repository.get_course_description(unknown_course_code, 'short')
        
        # Assert
        assert result == ""  # Debe retornar string vacío
    
    def test_fallback_courses_have_both_descriptions(self):
        """Test: verificar que las constantes de fallback tienen ambas descripciones."""
        # Arrange
        course_code = 'EXPERTO_IA_GPT_GEMINI'
        
        # Assert
        assert course_code in FALLBACK_COURSES
        assert 'short' in FALLBACK_COURSES[course_code]
        assert 'long' in FALLBACK_COURSES[course_code]
        assert FALLBACK_COURSES[course_code]['short'] != ""
        assert FALLBACK_COURSES[course_code]['long'] != ""
        assert len(FALLBACK_COURSES[course_code]['short']) > 100  # Descripción corta debe tener contenido
        assert len(FALLBACK_COURSES[course_code]['long']) > 500   # Descripción larga debe ser sustancial


class TestGenerateIntelligentResponseIntegration:
    """Tests de integración para el sistema de descripciones en respuestas inteligentes."""
    
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
    
    @pytest.mark.asyncio
    async def test_concise_content_response_uses_course_description(self):
        """Test de integración: verificar que las respuestas de contenido usan el nuevo sistema."""
        from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
        
        # Arrange
        mock_course_repo = Mock()
        mock_course_repo.get_course_description = AsyncMock(return_value="Descripción desde repositorio")
        
        mock_dynamic_provider = Mock()
        mock_dynamic_provider.get_primary_course_info = AsyncMock(return_value={
            'name': 'Curso Test',
            'session_count': 4
        })
        
        use_case = GenerateIntelligentResponseUseCase(
            intent_analyzer=Mock(),
            twilio_client=Mock(),
            openai_client=Mock(),
            db_client=Mock(),
            course_repository=mock_course_repo
        )
        use_case.dynamic_course_provider = mock_dynamic_provider
        
        # Mock user_memory
        mock_user_memory = Mock()
        mock_user_memory.last_message_text = "contenido del curso"
        
        # Act
        result = await use_case._get_concise_specific_response('content', 'Test User', 'gerente', mock_user_memory)
        
        # Assert
        assert result == "Descripción desde repositorio"
        mock_course_repo.get_course_description.assert_called_once_with('EXPERTO_IA_GPT_GEMINI', 'short')


if __name__ == "__main__":
    # Ejecutar tests
    import sys
    import os
    
    # Añadir el directorio raíz al path para imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Ejecutar tests específicos
    pytest.main([__file__, "-v"])