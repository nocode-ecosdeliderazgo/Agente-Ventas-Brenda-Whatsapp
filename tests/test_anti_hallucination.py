#!/usr/bin/env python3
"""
Pytest test suite for anti_hallucination_use_case module.
Tests tool_db fallback functionality and data enhancement.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# Import the module under test
from app.application.usecases.anti_hallucination_use_case import AntiHallucinationUseCase
from app.application.usecases.validate_response_use_case import ValidationResult


class TestAntiHallucinationToolDBIntegration:
    """Test suite for tool_db integration in anti-hallucination system."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mocked dependencies for AntiHallucinationUseCase."""
        openai_client = AsyncMock()
        course_repository = AsyncMock()
        validate_response_use_case = AsyncMock()
        
        # Mock validation result
        validation_result = ValidationResult(
            is_valid=True,
            confidence_score=0.95,
            issues=[],
            corrected_response=None
        )
        validate_response_use_case.validate_response.return_value = validation_result
        
        return openai_client, course_repository, validate_response_use_case
    
    @pytest.fixture
    def anti_hallucination_use_case(self, mock_dependencies):
        """Create AntiHallucinationUseCase with mocked dependencies."""
        openai_client, course_repository, validate_response_use_case = mock_dependencies
        return AntiHallucinationUseCase(openai_client, course_repository, validate_response_use_case)
    
    @pytest.fixture
    def sample_user_memory(self):
        """Create sample user memory object."""
        return MagicMock(
            user_id="user-123",
            phone_number="+123456789",
            first_name="María",
            buyer_persona="Sofía Visionaria"
        )
    
    @pytest.mark.asyncio
    async def test_tool_db_fallback_activation(self, anti_hallucination_use_case, sample_user_memory):
        """Test that tool_db fallback is activated when data is insufficient."""
        user_message = "¿Cuánto cuesta el curso de IA?"
        intent_analysis = {'category': 'EXPLORATION_PRICING', 'confidence': 0.90}
        
        # Insufficient course info to trigger tool_db fallback
        insufficient_course_info = {'name': 'Curso IA'}  # Missing price, duration, etc.
        
        with patch('app.infrastructure.tools.tool_db.get_tool_db') as mock_get_tool_db:
            # Mock tool_db to return enhanced course info
            mock_tool_db = AsyncMock()
            mock_tool_db.query.return_value = [
                {
                    'id_course': 'course-123',
                    'name': 'Experto en IA para Profesionales',
                    'price': 4500,
                    'currency': 'MXN',
                    'session_count': 8,
                    'total_duration_min': 720,
                    'modality': 'online',
                    'short_description': 'Curso especializado para profesionales'
                }
            ]
            mock_get_tool_db.return_value = mock_tool_db
            
            # Mock OpenAI response
            anti_hallucination_use_case.openai_client.chat_completion.return_value = (
                "Según nuestra base de datos, el **Experto en IA para Profesionales** "
                "tiene un precio de $4,500 MXN."
            )
            
            result = await anti_hallucination_use_case.generate_safe_response(
                user_message,
                sample_user_memory,
                intent_analysis,
                course_info=insufficient_course_info
            )
            
            # Verify tool_db was called
            mock_tool_db.query.assert_called_once_with('ai_courses', {}, limit=3)
            
            # Verify response contains enhanced data
            assert result['message'] is not None
            assert 'anti_hallucination_applied' in result
            assert result['anti_hallucination_applied'] is True
    
    @pytest.mark.asyncio
    async def test_tool_db_course_info_enhancement(self, anti_hallucination_use_case):
        """Test _get_course_info_from_tool_db method for course info enhancement."""
        user_message = "¿Qué incluye el curso? ¿Cuántas sesiones tiene?"
        
        with patch('app.infrastructure.tools.tool_db.get_tool_db') as mock_get_tool_db:
            mock_tool_db = AsyncMock()
            
            # Mock course query
            mock_tool_db.query.side_effect = [
                # First call: ai_courses
                [
                    {
                        'id_course': 'course-123',
                        'name': 'Experto en IA para Profesionales',
                        'price': 4500,
                        'currency': 'MXN',
                        'session_count': 8,
                        'total_duration_min': 720,
                        'modality': 'online'
                    }
                ],
                # Second call: ai_tema_activity (content inquiry)
                [
                    {'item_type': 'practica', 'title_item': 'Práctica con ChatGPT'},
                    {'item_type': 'video', 'title_item': 'Video explicativo'},
                    {'item_type': 'template', 'title_item': 'Template Coda'}
                ],
                # Third call: ai_course_session (session inquiry)
                [
                    {'id_session': 1, 'title': 'Introducción a IA', 'duration_minutes': 90},
                    {'id_session': 2, 'title': 'ChatGPT Avanzado', 'duration_minutes': 90}
                ]
            ]
            
            mock_get_tool_db.return_value = mock_tool_db
            anti_hallucination_use_case.tool_db = mock_tool_db
            
            result = await anti_hallucination_use_case._get_course_info_from_tool_db(user_message)
            
            # Verify comprehensive course info was built
            assert result is not None
            assert result['name'] == 'Experto en IA para Profesionales'
            assert result['price'] == 4500
            assert result['session_count'] == 8
            assert 'activities' in result
            assert 'sessions' in result
            assert 'content_summary' in result
            assert 'session_details' in result
            assert 'duration_formatted' in result
            
            # Verify multiple queries were made
            assert mock_tool_db.query.call_count == 3
    
    @pytest.mark.asyncio
    async def test_tool_db_bonus_enhancement(self, anti_hallucination_use_case):
        """Test tool_db enhancement for bonus-related inquiries."""
        user_message = "¿Qué bonos incluye el curso?"
        
        with patch('app.infrastructure.tools.tool_db.get_tool_db') as mock_get_tool_db:
            mock_tool_db = AsyncMock()
            
            mock_tool_db.query.side_effect = [
                # Course query
                [
                    {
                        'id_course': 'course-123',
                        'name': 'Experto en IA para Profesionales',
                        'price': 4500
                    }
                ],
                # Bonus query
                [
                    {'id_bond': 1, 'content': 'Workbook PDF', 'active': True},
                    {'id_bond': 2, 'content': 'Templates Coda', 'active': True},
                    {'id_bond': 3, 'content': 'Video Bonus', 'active': True}
                ]
            ]
            
            mock_get_tool_db.return_value = mock_tool_db
            anti_hallucination_use_case.tool_db = mock_tool_db
            
            result = await anti_hallucination_use_case._get_course_info_from_tool_db(user_message)
            
            assert result is not None
            assert 'bonuses' in result
            assert result['bonus_count'] == 3
            assert len(result['bonuses']) == 3
    
    @pytest.mark.asyncio
    async def test_tool_db_error_handling(self, anti_hallucination_use_case, sample_user_memory):
        """Test error handling when tool_db fails."""
        user_message = "¿Cuánto cuesta el curso?"
        intent_analysis = {'category': 'EXPLORATION_PRICING', 'confidence': 0.90}
        insufficient_course_info = {'name': 'Curso IA'}
        
        with patch('app.infrastructure.tools.tool_db.get_tool_db') as mock_get_tool_db:
            mock_tool_db = AsyncMock()
            mock_tool_db.query.side_effect = Exception("Database connection failed")
            mock_get_tool_db.return_value = mock_tool_db
            
            # Should not crash, should fall back to safe response
            result = await anti_hallucination_use_case.generate_safe_response(
                user_message,
                sample_user_memory,
                intent_analysis,
                course_info=insufficient_course_info
            )
            
            # Verify it still returns a valid response
            assert result is not None
            assert 'message' in result
            assert 'generation_method' in result
    
    @pytest.mark.asyncio
    async def test_data_availability_check_with_enhanced_data(self, anti_hallucination_use_case):
        """Test data availability check with tool_db enhanced data."""
        # Original insufficient data
        insufficient_data = {'name': 'Curso IA'}
        
        availability = await anti_hallucination_use_case._check_data_availability(
            insufficient_data, needs_specific=True
        )
        assert not availability['has_sufficient_data']
        
        # Enhanced data from tool_db
        enhanced_data = {
            'name': 'Experto en IA para Profesionales',
            'price': 4500,
            'currency': 'MXN',
            'session_count': 8,
            'total_duration_min': 720,
            'short_description': 'Curso especializado'
        }
        
        enhanced_availability = await anti_hallucination_use_case._check_data_availability(
            enhanced_data, needs_specific=True
        )
        assert enhanced_availability['has_sufficient_data']
        assert len(enhanced_availability['missing_data']) <= 2  # Should be acceptable
    
    @pytest.mark.asyncio
    async def test_verified_response_generation_with_tool_db_data(self, anti_hallucination_use_case, sample_user_memory):
        """Test verified response generation using tool_db enhanced data."""
        user_message = "¿Cuánto cuesta y cuánto dura el curso?"
        intent_analysis = {'category': 'EXPLORATION_PRICING', 'confidence': 0.90}
        
        # Enhanced course info from tool_db
        enhanced_course_info = {
            'name': 'Experto en IA para Profesionales',
            'price': 4500,
            'currency': 'MXN',
            'total_duration_min': 720,
            'session_count': 8,
            'short_description': 'Curso especializado para profesionales'
        }
        
        # Mock OpenAI to return a verified response
        anti_hallucination_use_case.openai_client.chat_completion.return_value = (
            "Según nuestra base de datos:\n\n"
            "🎓 **Experto en IA para Profesionales**\n"
            "💰 **Precio**: $4,500 MXN\n"
            "⏱️ **Duración**: 12.0 horas (8 sesiones)\n\n"
            "¿Te gustaría conocer más detalles del programa?"
        )
        
        result = await anti_hallucination_use_case._generate_verified_response(
            user_message, sample_user_memory, intent_analysis, enhanced_course_info
        )
        
        assert result is not None
        assert result['generation_method'] == 'verified_data'
        assert 'verified_context_used' in result
        assert '$4,500 MXN' in result['message']
        assert '12.0 horas' in result['message']
    
    @pytest.mark.asyncio
    async def test_prepare_verified_context_with_tool_db_data(self, anti_hallucination_use_case):
        """Test verified context preparation with tool_db enhanced data."""
        enhanced_course_info = {
            'name': 'Experto en IA para Profesionales',
            'price': 4500,
            'currency': 'MXN',
            'total_duration_min': 720,
            'session_count': 8,
            'modality': 'online',
            'short_description': 'Curso especializado para profesionales',
            'activities': [{'item_type': 'practica'}, {'item_type': 'video'}],
            'bonuses': [{'content': 'Workbook PDF'}]
        }
        
        verified_context = anti_hallucination_use_case._prepare_verified_context(enhanced_course_info)
        
        # Verify safe fields are included
        assert verified_context['name'] == 'Experto en IA para Profesionales'
        assert verified_context['price'] == 4500
        assert verified_context['currency'] == 'MXN'
        assert verified_context['session_count'] == 8
        assert verified_context['total_duration_min'] == 720
        assert verified_context['duration_formatted'] == '12.0 horas'
        
        # Verify unsafe fields are excluded
        assert 'activities' not in verified_context  # Not in safe_fields
        assert 'bonuses' not in verified_context  # Not in safe_fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])