"""
Tests para verificar la integración de bonos automáticos en flujos post-compra.
Verifica que los bonos activos se incluyan correctamente en las respuestas del bot.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any

# Importar las clases que vamos a testear
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.infrastructure.tools.tool_db import ToolDB


class TestPostPurchaseBonuses:
    """Tests para verificar la integración de bonos en flujos post-compra."""
    
    @pytest.fixture
    def mock_tool_db(self):
        """Mock del ToolDB con bonos de prueba."""
        mock_db = AsyncMock(spec=ToolDB)
        
        # Mock de bonos activos de prueba
        mock_bonuses = [
            {
                'id_bond': '1',
                'content': 'Workbook interactivo en Coda.io',
                'bond_url': 'https://coda.io/workbook',
                'active': True
            },
            {
                'id_bond': '2', 
                'content': 'Acceso 100% online a grabaciones',
                'bond_url': 'https://masterclass.com',
                'active': True
            }
        ]
        
        mock_db.get_active_bonuses.return_value = mock_bonuses
        return mock_db
    
    @pytest.fixture
    def mock_user_memory(self):
        """Mock de la memoria del usuario."""
        memory = MagicMock()
        memory.name = "Juan"
        memory.stage = "post_purchase"
        memory.lead_score = 50
        memory.buying_signals = ["Confirmó que procederá con el pago"]
        return memory
    
    @pytest.mark.asyncio
    async def test_payment_confirmation_with_bonuses(self, mock_tool_db, mock_user_memory):
        """Test: Verificar que PAYMENT_CONFIRMATION incluya bonos activos."""
        
        # Mock de las dependencias
        with patch('app.application.usecases.generate_intelligent_response.get_tool_db', return_value=mock_tool_db):
            # Crear instancia del use case (mocks mínimos)
            use_case = GenerateIntelligentResponseUseCase(
                intent_analyzer=AsyncMock(),
                twilio_client=AsyncMock(),
                openai_client=AsyncMock(),
                db_client=AsyncMock(),
                course_repository=AsyncMock()
            )
            
            # Ejecutar el método
            response = await use_case._handle_post_purchase_intent(
                category='PAYMENT_CONFIRMATION',
                user_memory=mock_user_memory,
                user_id='test_user_123'
            )
            
            # Verificar que la respuesta contenga los bonos
            assert "🎁 **Bonos activos incluidos:**" in response
            assert "Workbook interactivo en Coda.io" in response
            assert "https://coda.io/workbook" in response
            assert "Acceso 100% online a grabaciones" in response
            assert "https://masterclass.com" in response
            
            # Verificar que se llamó al método de bonos
            mock_tool_db.get_active_bonuses.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_payment_completed_with_bonuses(self, mock_tool_db, mock_user_memory):
        """Test: Verificar que PAYMENT_COMPLETED incluya bonos activos."""
        
        with patch('app.application.usecases.generate_intelligent_response.get_tool_db', return_value=mock_tool_db):
            use_case = GenerateIntelligentResponseUseCase(
                intent_analyzer=AsyncMock(),
                twilio_client=AsyncMock(),
                openai_client=AsyncMock(),
                db_client=AsyncMock(),
                course_repository=AsyncMock()
            )
            
            response = await use_case._handle_post_purchase_intent(
                category='PAYMENT_COMPLETED',
                user_memory=mock_user_memory,
                user_id='test_user_123'
            )
            
            # Verificar contenido de bonos
            assert "🎁 **Bonos activos incluidos:**" in response
            assert "Workbook interactivo en Coda.io" in response
            assert "Acceso 100% online a grabaciones" in response
    
    @pytest.mark.asyncio
    async def test_comprobante_upload_with_bonuses(self, mock_tool_db, mock_user_memory):
        """Test: Verificar que COMPROBANTE_UPLOAD incluya bonos activos."""
        
        with patch('app.application.usecases.generate_intelligent_response.get_tool_db', return_value=mock_tool_db):
            use_case = GenerateIntelligentResponseUseCase(
                intent_analyzer=AsyncMock(),
                twilio_client=AsyncMock(),
                openai_client=AsyncMock(),
                db_client=AsyncMock(),
                course_repository=AsyncMock()
            )
            
            response = await use_case._handle_post_purchase_intent(
                category='COMPROBANTE_UPLOAD',
                user_memory=mock_user_memory,
                user_id='test_user_123'
            )
            
            # Verificar contenido de bonos
            assert "🎁 **Bonos activos incluidos:**" in response
            assert "Workbook interactivo en Coda.io" in response
            assert "Acceso 100% online a grabaciones" in response
    
    @pytest.mark.asyncio
    async def test_no_bonuses_fallback(self, mock_user_memory):
        """Test: Verificar fallback cuando no hay bonos activos."""
        
        # Mock con lista vacía de bonos
        mock_tool_db = AsyncMock(spec=ToolDB)
        mock_tool_db.get_active_bonuses.return_value = []
        
        with patch('app.application.usecases.generate_intelligent_response.get_tool_db', return_value=mock_tool_db):
            use_case = GenerateIntelligentResponseUseCase(
                intent_analyzer=AsyncMock(),
                twilio_client=AsyncMock(),
                openai_client=AsyncMock(),
                db_client=AsyncMock(),
                course_repository=AsyncMock()
            )
            
            response = await use_case._handle_post_purchase_intent(
                category='PAYMENT_CONFIRMATION',
                user_memory=mock_user_memory,
                user_id='test_user_123'
            )
            
            # Verificar mensaje de fallback
            assert "🎁 **Bonos activos incluidos:**" in response
            assert "(No hay bonos activos en este momento)" in response
    
    @pytest.mark.asyncio
    async def test_database_error_fallback(self, mock_user_memory):
        """Test: Verificar fallback cuando hay error en base de datos."""
        
        # Mock que simula error en base de datos
        mock_tool_db = AsyncMock(spec=ToolDB)
        mock_tool_db.get_active_bonuses.side_effect = Exception("Database error")
        
        with patch('app.application.usecases.generate_intelligent_response.get_tool_db', return_value=mock_tool_db):
            use_case = GenerateIntelligentResponseUseCase(
                intent_analyzer=AsyncMock(),
                twilio_client=AsyncMock(),
                openai_client=AsyncMock(),
                db_client=AsyncMock(),
                course_repository=AsyncMock()
            )
            
            response = await use_case._handle_post_purchase_intent(
                category='PAYMENT_CONFIRMATION',
                user_memory=mock_user_memory,
                user_id='test_user_123'
            )
            
            # Verificar que aún se genera respuesta con fallback
            assert "🎁 **Bonos activos incluidos:**" in response
            assert "(No hay bonos activos en este momento)" in response
    
    @pytest.mark.asyncio
    async def test_bonus_formatting(self, mock_tool_db, mock_user_memory):
        """Test: Verificar formato correcto de los bonos en la respuesta."""
        
        with patch('app.application.usecases.generate_intelligent_response.get_tool_db', return_value=mock_tool_db):
            use_case = GenerateIntelligentResponseUseCase(
                intent_analyzer=AsyncMock(),
                twilio_client=AsyncMock(),
                openai_client=AsyncMock(),
                db_client=AsyncMock(),
                course_repository=AsyncMock()
            )
            
            response = await use_case._handle_post_purchase_intent(
                category='PAYMENT_CONFIRMATION',
                user_memory=mock_user_memory,
                user_id='test_user_123'
            )
            
            # Verificar formato específico de los bonos
            lines = response.split('\n')
            bonus_section = False
            bonus_lines = []
            
            for line in lines:
                if "🎁 **Bonos activos incluidos:**" in line:
                    bonus_section = True
                    continue
                if bonus_section and line.strip().startswith('•'):
                    bonus_lines.append(line.strip())
                elif bonus_section and not line.strip().startswith('•'):
                    break
            
            # Verificar que hay al menos 2 líneas de bonos
            assert len(bonus_lines) >= 2
            
            # Verificar formato de cada bono
            for bonus_line in bonus_lines:
                assert bonus_line.startswith('• ')
                assert '👉' in bonus_line
                assert 'http' in bonus_line  # URL presente


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"]) 