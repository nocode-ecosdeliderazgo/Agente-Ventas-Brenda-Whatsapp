"""
Tests para la detección rápida de PAYMENT_CONFIRMATION en AnalyzeMessageIntentUseCase.
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase, AFFIRMATIVE_SHORT_REGEX
from app.domain.entities.message import IncomingMessage


class TestDetectIntent:
    """Tests para la detección de intención."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock del cliente OpenAI."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_memory_use_case(self):
        """Mock del caso de uso de memoria."""
        return MagicMock()
    
    @pytest.fixture
    def analyze_intent_use_case(self, mock_openai_client, mock_memory_use_case):
        """Instancia del caso de uso para análisis de intención."""
        return AnalyzeMessageIntentUseCase(
            openai_client=mock_openai_client,
            memory_use_case=mock_memory_use_case
        )
    
    @pytest.fixture
    def mock_user_memory(self):
        """Mock de la memoria del usuario."""
        memory = MagicMock()
        memory.name = "Juan"
        memory.interaction_count = 5
        memory.purchase_bonus_sent = True  # Simula que se enviaron datos bancarios
        return memory
    
    @pytest.fixture
    def sample_message(self):
        """Mensaje de ejemplo para testing."""
        return IncomingMessage(
            from_number="+525512345678",
            to_number="+525598765432",
            body="si",
            message_sid="test_sid_123",
            timestamp=datetime.now(),
            raw_data={}
        )
    
    def test_affirmative_short_regex_constant(self):
        """Test: Verificar que la constante AFFIRMATIVE_SHORT_REGEX esté definida."""
        import re
        
        # Verificar que la constante existe
        assert hasattr(AFFIRMATIVE_SHORT_REGEX, '__str__')
        
        # Verificar que el regex funciona con casos positivos
        positive_cases = ["si", "sí", "ok", "claro", "vale", "hecho"]
        for case in positive_cases:
            assert re.match(AFFIRMATIVE_SHORT_REGEX, case, re.IGNORECASE), f"Regex no coincide con: {case}"
        
        # Verificar que el regex no coincide con casos negativos
        negative_cases = ["hola", "no", "tal vez", "quizás", "si pero", "ok gracias"]
        for case in negative_cases:
            assert not re.match(AFFIRMATIVE_SHORT_REGEX, case, re.IGNORECASE), f"Regex coincide incorrectamente con: {case}"
    
    @pytest.mark.asyncio
    async def test_affirmative_short_confirmation(self, analyze_intent_use_case, mock_user_memory, sample_message):
        """Test: Verificar detección rápida de PAYMENT_CONFIRMATION con mensajes afirmativos cortos."""
        
        # Configurar mock de memoria
        analyze_intent_use_case.memory_use_case.get_user_memory.return_value = mock_user_memory
        
        # Casos de prueba positivos
        positive_cases = ["si", "sí", "ok", "claro", "vale", "hecho"]
        
        for message_text in positive_cases:
            # Crear mensaje con texto específico
            test_message = IncomingMessage(
                from_number="+525512345678",
                to_number="+525598765432",
                body=message_text,
                message_sid="test_sid_123",
                timestamp=datetime.now(),
                raw_data={}
            )
            
            # Ejecutar análisis
            result = await analyze_intent_use_case.execute(
                user_id="test_user_123",
                message=test_message
            )
            
            # Verificar que se activó la detección rápida
            assert result['success'] is True
            assert result['intent_analysis']['category'] == 'PAYMENT_CONFIRMATION'
            assert result['intent_analysis']['confidence'] == 0.9
            assert result['intent_analysis']['detection_method'] == 'fast_rule'
            assert result['intent_analysis']['message_length'] <= 5
            assert result['intent_analysis']['matched_pattern'] == message_text
    
    @pytest.mark.asyncio
    async def test_affirmative_short_confirmation_negative_cases(self, analyze_intent_use_case, mock_user_memory):
        """Test: Verificar que NO se active la detección rápida con mensajes que no cumplen condiciones."""
        
        # Configurar mock de memoria
        analyze_intent_use_case.memory_use_case.get_user_memory.return_value = mock_user_memory
        
        # Casos de prueba negativos
        negative_cases = [
            "hola",  # No coincide con regex
            "no",  # No coincide con regex
            "si pero necesito más información",  # Más de 5 palabras
            "ok gracias por la información",  # Más de 5 palabras
            "claro que sí, me interesa mucho",  # Más de 5 palabras
        ]
        
        for message_text in negative_cases:
            # Crear mensaje con texto específico
            test_message = IncomingMessage(
                from_number="+525512345678",
                to_number="+525598765432",
                body=message_text,
                message_sid="test_sid_123",
                timestamp=datetime.now(),
                raw_data={}
            )
            
            # Mock del resultado de OpenAI para simular análisis normal
            analyze_intent_use_case.openai_client.analyze_and_respond.return_value = {
                'success': True,
                'intent_analysis': {'category': 'GENERAL_QUESTION', 'confidence': 0.7},
                'extracted_info': {},
                'response': 'Respuesta de prueba'
            }
            
            # Ejecutar análisis
            result = await analyze_intent_use_case.execute(
                user_id="test_user_123",
                message=test_message
            )
            
            # Verificar que NO se activó la detección rápida
            assert result['success'] is True
            assert result['intent_analysis']['category'] != 'PAYMENT_CONFIRMATION'
            assert 'detection_method' not in result['intent_analysis']
    
    @pytest.mark.asyncio
    async def test_affirmative_short_confirmation_no_purchase_bonus_sent(self, analyze_intent_use_case, sample_message):
        """Test: Verificar que NO se active la detección rápida si no se enviaron datos bancarios."""
        
        # Crear memoria sin purchase_bonus_sent
        mock_user_memory = MagicMock()
        mock_user_memory.name = "Juan"
        mock_user_memory.interaction_count = 5
        mock_user_memory.purchase_bonus_sent = False  # No se enviaron datos bancarios
        
        # Configurar mock de memoria
        analyze_intent_use_case.memory_use_case.get_user_memory.return_value = mock_user_memory
        
        # Mock del resultado de OpenAI para simular análisis normal
        analyze_intent_use_case.openai_client.analyze_and_respond.return_value = {
            'success': True,
            'intent_analysis': {'category': 'GENERAL_QUESTION', 'confidence': 0.7},
            'extracted_info': {},
            'response': 'Respuesta de prueba'
        }
        
        # Ejecutar análisis
        result = await analyze_intent_use_case.execute(
            user_id="test_user_123",
            message=sample_message
        )
        
        # Verificar que NO se activó la detección rápida
        assert result['success'] is True
        assert result['intent_analysis']['category'] != 'PAYMENT_CONFIRMATION'
        assert 'detection_method' not in result['intent_analysis']
    
    @pytest.mark.asyncio
    async def test_affirmative_short_confirmation_memory_without_attribute(self, analyze_intent_use_case, sample_message):
        """Test: Verificar que NO se active la detección rápida si la memoria no tiene el atributo purchase_bonus_sent."""
        
        # Crear memoria sin el atributo purchase_bonus_sent
        mock_user_memory = MagicMock()
        mock_user_memory.name = "Juan"
        mock_user_memory.interaction_count = 5
        # No definir purchase_bonus_sent
        
        # Configurar mock de memoria
        analyze_intent_use_case.memory_use_case.get_user_memory.return_value = mock_user_memory
        
        # Mock del resultado de OpenAI para simular análisis normal
        analyze_intent_use_case.openai_client.analyze_and_respond.return_value = {
            'success': True,
            'intent_analysis': {'category': 'GENERAL_QUESTION', 'confidence': 0.7},
            'extracted_info': {},
            'response': 'Respuesta de prueba'
        }
        
        # Ejecutar análisis
        result = await analyze_intent_use_case.execute(
            user_id="test_user_123",
            message=sample_message
        )
        
        # Verificar que NO se activó la detección rápida
        assert result['success'] is True
        assert result['intent_analysis']['category'] != 'PAYMENT_CONFIRMATION'
        assert 'detection_method' not in result['intent_analysis']
    
    @pytest.mark.asyncio
    async def test_fast_confirmation_fallback(self, analyze_intent_use_case, sample_message):
        """Test: Verificar que se active la detección rápida con fallback cuando no hay flag pero sí hay datos bancarios en historial."""
        
        # Crear memoria sin purchase_bonus_sent pero con historial que contiene datos bancarios
        mock_user_memory = MagicMock()
        mock_user_memory.name = "Juan"
        mock_user_memory.interaction_count = 5
        # No definir purchase_bonus_sent (flag no está presente)
        
        # Simular historial con datos bancarios enviados
        mock_user_memory.message_history = [
            {
                'timestamp': '2024-01-01T10:00:00Z',
                'action': 'purchase_bonus_sent',
                'description': 'Datos bancarios y bono workbook enviados al usuario',
                'banking_data_sent': True,
                'clabe': '012345678901234567',
                'banco': 'BBVA'
            }
        ]
        
        # Configurar mock de memoria
        analyze_intent_use_case.memory_use_case.get_user_memory.return_value = mock_user_memory
        
        # Ejecutar análisis
        result = await analyze_intent_use_case.execute(
            user_id="test_user_123",
            message=sample_message
        )
        
        # Verificar que SÍ se activó la detección rápida por fallback
        assert result['success'] is True
        assert result['intent_analysis']['category'] == 'PAYMENT_CONFIRMATION'
        assert result['intent_analysis']['confidence'] == 0.9
        assert result['intent_analysis']['detection_method'] == 'fast_rule'
        assert result['intent_analysis']['purchase_bonus_sent'] is False
        assert result['intent_analysis']['bank_data_sent'] is True
    
    @pytest.mark.asyncio
    async def test_fast_confirmation_fallback_with_clabe_text(self, analyze_intent_use_case, sample_message):
        """Test: Verificar que se active la detección rápida cuando el historial contiene 'Cuenta CLABE' en la descripción."""
        
        # Crear memoria sin purchase_bonus_sent pero con historial que contiene 'Cuenta CLABE'
        mock_user_memory = MagicMock()
        mock_user_memory.name = "Juan"
        mock_user_memory.interaction_count = 5
        # No definir purchase_bonus_sent
        
        # Simular historial con descripción que contiene 'Cuenta CLABE'
        mock_user_memory.message_history = [
            {
                'timestamp': '2024-01-01T10:00:00Z',
                'action': 'message_sent',
                'description': 'Mensaje enviado con Cuenta CLABE: 012345678901234567',
                'content': '💳 DATOS PARA TRANSFERENCIA: Cuenta CLABE: 012345678901234567'
            }
        ]
        
        # Configurar mock de memoria
        analyze_intent_use_case.memory_use_case.get_user_memory.return_value = mock_user_memory
        
        # Ejecutar análisis
        result = await analyze_intent_use_case.execute(
            user_id="test_user_123",
            message=sample_message
        )
        
        # Verificar que SÍ se activó la detección rápida por fallback con texto CLABE
        assert result['success'] is True
        assert result['intent_analysis']['category'] == 'PAYMENT_CONFIRMATION'
        assert result['intent_analysis']['confidence'] == 0.9
        assert result['intent_analysis']['detection_method'] == 'fast_rule'
        assert result['intent_analysis']['purchase_bonus_sent'] is False
        assert result['intent_analysis']['bank_data_sent'] is True
    
    @pytest.mark.asyncio
    async def test_fast_confirmation_message_history(self, analyze_intent_use_case, sample_message):
        """Test: Verificar que se active la detección rápida cuando purchase_bonus_sent=False pero hay historial con datos bancarios."""
        
        # Crear memoria sin purchase_bonus_sent pero con historial específico
        mock_user_memory = MagicMock()
        mock_user_memory.name = "Juan"
        mock_user_memory.interaction_count = 5
        mock_user_memory.purchase_bonus_sent = False  # Flag explícitamente en False
        
        # Simular historial con mensaje que contiene datos bancarios
        mock_user_memory.message_history = [
            {
                'timestamp': '2024-01-01T10:00:00Z',
                'action': 'message_sent',
                'description': 'Datos bancarios y bono workbook enviados',
                'content': 'Mensaje con datos de transferencia'
            }
        ]
        
        # Configurar mock de memoria
        analyze_intent_use_case.memory_use_case.get_user_memory = MagicMock(return_value=mock_user_memory)
        
        # Ejecutar análisis con mensaje 'si'
        result = await analyze_intent_use_case.execute(
            user_id="test_user_123",
            message=sample_message
        )
        
        # Verificar que SÍ se activó la detección rápida por el historial
        assert result['success'] is True
        assert result['intent_analysis']['category'] == 'PAYMENT_CONFIRMATION'
        assert result['intent_analysis']['confidence'] == 0.9
        assert result['intent_analysis']['detection_method'] == 'fast_rule'
        assert result['intent_analysis']['purchase_bonus_sent'] is False
        assert result['intent_analysis']['bank_data_sent'] is True
    
    def test_bot_already_sent_bank_data_helper(self, analyze_intent_use_case):
        """Test: Verificar la función helper _bot_already_sent_bank_data."""
        
        # Caso 1: Sin historial
        mock_user_memory = MagicMock()
        mock_user_memory.message_history = []
        result = analyze_intent_use_case._bot_already_sent_bank_data(mock_user_memory)
        assert result is False
        
        # Caso 2: Con historial que contiene purchase_bonus_sent
        mock_user_memory.message_history = [
            {'action': 'purchase_bonus_sent', 'description': 'Datos enviados'}
        ]
        result = analyze_intent_use_case._bot_already_sent_bank_data(mock_user_memory)
        assert result is True
        
        # Caso 3: Con historial que contiene 'Cuenta CLABE' en descripción
        mock_user_memory.message_history = [
            {'action': 'message_sent', 'description': 'Mensaje con Cuenta CLABE: 012345678901234567'}
        ]
        result = analyze_intent_use_case._bot_already_sent_bank_data(mock_user_memory)
        assert result is True
        
        # Caso 4: Con historial que contiene banking_data_sent
        mock_user_memory.message_history = [
            {'action': 'message_sent', 'banking_data_sent': True}
        ]
        result = analyze_intent_use_case._bot_already_sent_bank_data(mock_user_memory)
        assert result is True
        
        # Caso 5: Con historial que no contiene datos bancarios
        mock_user_memory.message_history = [
            {'action': 'message_sent', 'description': 'Mensaje normal sin datos bancarios'}
        ]
        result = analyze_intent_use_case._bot_already_sent_bank_data(mock_user_memory)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_expanded_affirmative_regex(self, analyze_intent_use_case, mock_user_memory):
        """Test NUEVO: Verificar regex expandido con más variantes afirmativas."""
        
        # Configurar mock de memoria
        analyze_intent_use_case.memory_use_case.get_user_memory.return_value = mock_user_memory
        
        # Casos de prueba positivos expandidos
        expanded_positive_cases = ["si", "sí", "sip", "ok", "okay", "claro", "vale", "hecho", "👍", "✅"]
        
        for message_text in expanded_positive_cases:
            # Crear mensaje con texto específico
            test_message = IncomingMessage(
                from_number="+525512345678",
                to_number="+525598765432",
                body=message_text,
                message_sid="test_sid_123",
                timestamp=datetime.now(),
                raw_data={}
            )
            
            # Ejecutar análisis
            result = await analyze_intent_use_case.execute(
                user_id="test_user_123",
                message=test_message
            )
            
            # Verificar que se activó la detección rápida
            assert result['success'] is True, f"Falló para mensaje: {message_text}"
            assert result['intent_analysis']['category'] == 'PAYMENT_CONFIRMATION', f"Categoría incorrecta para: {message_text}"
            assert result['intent_analysis']['confidence'] == 0.9, f"Confianza incorrecta para: {message_text}"
            assert result['intent_analysis']['detection_method'] == 'fast_rule', f"Método incorrecto para: {message_text}"
    
    @pytest.mark.asyncio
    async def test_fallback_warning_log(self, analyze_intent_use_case, sample_message, caplog):
        """Test NUEVO: Verificar que se genera WARNING cuando flag=False pero historial tiene datos."""
        
        # Crear memoria con purchase_bonus_sent=False y historial con datos bancarios
        mock_user_memory = MagicMock()
        mock_user_memory.name = "Juan"
        mock_user_memory.interaction_count = 5
        mock_user_memory.purchase_bonus_sent = False  # Flag en False
        
        # Historial con datos bancarios
        mock_user_memory.message_history = [
            {
                'timestamp': '2024-01-01T10:00:00Z',
                'action': 'purchase_bonus_sent',
                'description': 'Datos bancarios y bono workbook enviados',
                'banking_data_sent': True
            }
        ]
        
        # Configurar mock
        analyze_intent_use_case.memory_use_case.get_user_memory.return_value = mock_user_memory
        
        # Ejecutar análisis
        with caplog.at_level(logging.WARNING):
            result = await analyze_intent_use_case.execute(
                user_id="test_user_123",
                message=sample_message
            )
        
        # Verificar que se detectó PAYMENT_CONFIRMATION
        assert result['intent_analysis']['category'] == 'PAYMENT_CONFIRMATION'
        
        # Verificar que se generó el WARNING de fallback
        warning_found = any(
            "FALLBACK ACTIVADO: purchase_bonus_sent=False pero se encontró CLABE en historial" in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        )
        assert warning_found, "No se encontró el WARNING de fallback activado"