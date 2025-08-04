#!/usr/bin/env python3
"""
Pytest test suite for generate_intelligent_response module.
Tests price inquiry handling with mocked tool_db integration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# Import the module under test
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.domain.entities.message import IncomingMessage, MessageType


class TestGenerateIntelligentResponseToolDBIntegration:
    """Test suite for tool_db integration in intelligent response generation."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mocked dependencies for GenerateIntelligentResponseUseCase."""
        dependencies = {
            'intent_analyzer': AsyncMock(),
            'twilio_client': MagicMock(),
            'openai_client': AsyncMock(),
            'db_client': MagicMock(),
            'course_repository': AsyncMock(),
            'validate_response_use_case': AsyncMock(),
            'anti_hallucination_use_case': AsyncMock(),
            'extract_user_info_use_case': AsyncMock(),
            'personalize_response_use_case': AsyncMock(),
            'dynamic_course_info_provider': AsyncMock(),
            'bonus_activation_use_case': AsyncMock(),
            'purchase_bonus_use_case': AsyncMock(),
            'faq_knowledge_provider': AsyncMock()
        }
        return dependencies
    
    @pytest.fixture
    def response_use_case(self, mock_dependencies):
        """Create GenerateIntelligentResponseUseCase with mocked dependencies."""
        return GenerateIntelligentResponseUseCase(**mock_dependencies)
    
    @pytest.fixture
    def sample_user_message(self):
        """Create sample user message."""
        return IncomingMessage(
            sid="test-sid",
            from_number="+123456789",
            to_number="+987654321",
            body="¿Cuánto cuesta el curso?",
            message_type=MessageType.TEXT,
            media_url=None,
            timestamp="2025-08-04T10:00:00Z"
        )
    
    @pytest.fixture
    def sample_user_memory(self):
        """Create sample user memory object."""
        return MagicMock(
            user_id="user-123",
            phone_number="+123456789",
            first_name="Juan",
            buyer_persona="Marcos Multitask",
            lead_score=75
        )
    
    @pytest.mark.asyncio
    async def test_price_inquiry_detection(self, response_use_case, sample_user_message, sample_user_memory):
        """Test that price inquiries are properly detected."""
        # Mock intent analysis to return PRICE_INQUIRY
        response_use_case.intent_analyzer.analyze_message_intent.return_value = {
            'category': 'PRICE_INQUIRY',
            'confidence': 0.95,
            'intent': 'user_wants_price_info'
        }
        
        # Mock course repository to return course info
        response_use_case.course_repository.get_course_by_name.return_value = {
            'name': 'Experto en IA para Profesionales',
            'price': 4500,
            'currency': 'MXN'
        }
        
        with patch('app.infrastructure.tools.tool_db.get_tool_db') as mock_get_tool_db:
            # Mock tool_db query
            mock_tool_db = AsyncMock()
            mock_tool_db.query.return_value = [
                {
                    'id_course': 'course-123',
                    'name': 'Experto en IA para Profesionales',
                    'price': 4500,
                    'currency': 'MXN',
                    'session_count': 8,
                    'total_duration_min': 720
                }
            ]
            mock_get_tool_db.return_value = mock_tool_db
            
            # Mock the _detect_course_in_message method to return course info
            with patch.object(response_use_case, '_detect_course_in_message', return_value='Experto en IA'):
                
                # Execute the method
                result = await response_use_case._handle_specific_database_inquiry(
                    sample_user_message.body,
                    sample_user_memory,
                    {'category': 'PRICE_INQUIRY', 'confidence': 0.95}
                )
                
                # Verify response
                assert result is not None
                assert 'message' in result
                assert '4500' in result['message']
                assert 'MXN' in result['message']
                assert 'Experto en IA' in result['message']
                
                # Verify tool_db was called
                mock_tool_db.query.assert_called_once_with('ai_courses', {}, limit=3)
    
    @pytest.mark.asyncio
    async def test_session_inquiry_detection(self, response_use_case, sample_user_memory):
        """Test that session inquiries are properly detected."""
        session_message = IncomingMessage(
            sid="test-sid",
            from_number="+123456789",
            to_number="+987654321",
            body="¿Cuántas sesiones tiene el curso?",
            message_type=MessageType.TEXT,
            media_url=None,
            timestamp="2025-08-04T10:00:00Z"
        )
        
        with patch('app.infrastructure.tools.tool_db.get_tool_db') as mock_get_tool_db:
            mock_tool_db = AsyncMock()
            mock_tool_db.query.return_value = [
                {
                    'id_course': 'course-123',
                    'name': 'Experto en IA para Profesionales',
                    'session_count': 8,
                    'total_duration_min': 720
                }
            ]
            mock_get_tool_db.return_value = mock_tool_db
            
            with patch.object(response_use_case, '_detect_course_in_message', return_value='Experto en IA'):
                
                result = await response_use_case._handle_specific_database_inquiry(
                    session_message.body,
                    sample_user_memory,
                    {'category': 'SESSION_INQUIRY', 'confidence': 0.90}
                )
                
                assert result is not None
                assert 'message' in result
                assert '8' in result['message']  # Session count
                assert 'sesiones' in result['message'].lower()
    
    @pytest.mark.asyncio
    async def test_duration_inquiry_detection(self, response_use_case, sample_user_memory):
        """Test that duration inquiries are properly detected."""
        duration_message = IncomingMessage(
            sid="test-sid",
            from_number="+123456789",
            to_number="+987654321",
            body="¿Cuánto dura el curso?",
            message_type=MessageType.TEXT,
            media_url=None,
            timestamp="2025-08-04T10:00:00Z"
        )
        
        with patch('app.infrastructure.tools.tool_db.get_tool_db') as mock_get_tool_db:
            mock_tool_db = AsyncMock()
            mock_tool_db.query.return_value = [
                {
                    'id_course': 'course-123',
                    'name': 'Experto en IA para Profesionales',
                    'total_duration_min': 720  # 12 hours
                }
            ]
            mock_get_tool_db.return_value = mock_tool_db
            
            with patch.object(response_use_case, '_detect_course_in_message', return_value='Experto en IA'):
                
                result = await response_use_case._handle_specific_database_inquiry(
                    duration_message.body,
                    sample_user_memory,
                    {'category': 'DURATION_INQUIRY', 'confidence': 0.88}
                )
                
                assert result is not None
                assert 'message' in result
                assert '12' in result['message']  # Hours
                assert 'horas' in result['message'].lower()
    
    @pytest.mark.asyncio
    async def test_tool_db_fallback_when_no_data(self, response_use_case, sample_user_message, sample_user_memory):
        """Test fallback behavior when tool_db returns no data."""
        with patch('app.infrastructure.tools.tool_db.get_tool_db') as mock_get_tool_db:
            mock_tool_db = AsyncMock()
            mock_tool_db.query.return_value = []  # No data
            mock_get_tool_db.return_value = mock_tool_db
            
            with patch.object(response_use_case, '_detect_course_in_message', return_value='Curso Inexistente'):
                
                result = await response_use_case._handle_specific_database_inquiry(
                    sample_user_message.body,
                    sample_user_memory,
                    {'category': 'PRICE_INQUIRY', 'confidence': 0.95}
                )
                
                # Should return None to trigger fallback
                assert result is None
    
    @pytest.mark.asyncio
    async def test_tool_db_error_handling(self, response_use_case, sample_user_message, sample_user_memory):
        """Test error handling when tool_db fails."""
        with patch('app.infrastructure.tools.tool_db.get_tool_db') as mock_get_tool_db:
            mock_tool_db = AsyncMock()
            mock_tool_db.query.side_effect = Exception("Database connection failed")
            mock_get_tool_db.return_value = mock_tool_db
            
            with patch.object(response_use_case, '_detect_course_in_message', return_value='Experto en IA'):
                
                result = await response_use_case._handle_specific_database_inquiry(
                    sample_user_message.body,
                    sample_user_memory,
                    {'category': 'PRICE_INQUIRY', 'confidence': 0.95}
                )
                
                # Should return None to trigger fallback
                assert result is None
    
    @pytest.mark.asyncio
    async def test_course_detection_in_message(self, response_use_case):
        """Test course detection logic in messages."""
        # Test with explicit course reference
        course_name = response_use_case._detect_course_in_message("¿Cuánto cuesta el curso Experto en IA?")
        assert course_name == "Experto en IA"
        
        # Test with generic course reference
        generic_course = response_use_case._detect_course_in_message("¿Cuánto cuesta el curso?")
        assert generic_course == "curso"  # Generic fallback
        
        # Test with no course reference
        no_course = response_use_case._detect_course_in_message("Hola, ¿cómo estás?")
        assert no_course == "curso"  # Default fallback
    
    @pytest.mark.asyncio
    async def test_inquiry_categorization(self, response_use_case):
        """Test categorization of different inquiry types."""
        # Price inquiries
        price_inquiries = [
            "¿Cuánto cuesta el curso?",
            "¿Cuál es el precio?",
            "¿Qué precio tiene?",
            "¿Cuánto vale?"
        ]
        
        for inquiry in price_inquiries:
            category = response_use_case._categorize_specific_inquiry(inquiry)
            assert category == 'PRICE_INQUIRY'
        
        # Session inquiries
        session_inquiries = [
            "¿Cuántas sesiones tiene?",
            "¿Cuántas clases son?",
            "¿Qué sesiones incluye?"
        ]
        
        for inquiry in session_inquiries:
            category = response_use_case._categorize_specific_inquiry(inquiry)
            assert category == 'SESSION_INQUIRY'
        
        # Duration inquiries
        duration_inquiries = [
            "¿Cuánto dura el curso?",
            "¿Cuántas horas son?",
            "¿Qué duración tiene?"
        ]
        
        for inquiry in duration_inquiries:
            category = response_use_case._categorize_specific_inquiry(inquiry)
            assert category == 'DURATION_INQUIRY'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])