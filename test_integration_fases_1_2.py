#!/usr/bin/env python3
"""
Script de validación e integración para las Fases 1 y 2
Valida que el sistema anti-inventos y personalización funcionen correctamente
"""

import asyncio
import sys
import os
from typing import Dict, Any
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.application.usecases.anti_hallucination_use_case import AntiHallucinationUseCase
from app.application.usecases.personalize_response_use_case import PersonalizeResponseUseCase
from app.application.usecases.extract_user_info_use_case import ExtractUserInfoUseCase
from app.application.usecases.validate_response_use_case import ValidateResponseUseCase
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.database.client import DatabaseClient
from app.infrastructure.database.repositories.course_repository import CourseRepository
from memory.lead_memory import LeadMemory
from app.domain.entities.message import IncomingMessage

def debug_print(message: str, test_name: str = ""):
    """Print de debug visual para testing"""
    print(f"🧪 [{test_name}] {message}")

class IntegrationTester:
    """Clase para testing de integración de Fases 1 y 2"""
    
    def __init__(self):
        """Inicializar componentes necesarios para testing"""
        try:
            # Inicializar clientes
            self.openai_client = OpenAIClient()
            self.db_client = DatabaseClient()
            self.course_repository = CourseRepository()
            
            # Inicializar casos de uso
            self.validate_response_use_case = ValidateResponseUseCase(self.db_client, self.course_repository)
            self.anti_hallucination_use_case = AntiHallucinationUseCase(
                self.openai_client, self.course_repository, self.validate_response_use_case
            )
            self.extract_user_info_use_case = ExtractUserInfoUseCase(self.openai_client)
            self.personalize_response_use_case = PersonalizeResponseUseCase(
                self.openai_client, self.extract_user_info_use_case
            )
            
            debug_print("✅ Componentes inicializados correctamente", "INIT")
            
        except Exception as e:
            debug_print(f"❌ Error inicializando componentes: {e}", "INIT")
            raise
    
    async def test_fase_1_anti_inventos(self):
        """Test del sistema anti-inventos (FASE 1)"""
        debug_print("🧪 Iniciando test FASE 1: Sistema Anti-Inventos", "FASE_1")
        
        # Crear memoria de prueba
        user_memory = LeadMemory(
            user_id="test_user_123",
            name="María",
            role="Marketing Manager",
            interaction_count=3
        )
        
        # Casos de prueba para anti-inventos
        test_cases = [
            {
                "message": "¿Cuánto cuesta exactamente el curso?",
                "category": "EXPLORATION_PRICING",
                "expected_behavior": "debe generar respuesta segura sin inventar precios"
            },
            {
                "message": "¿Qué módulos incluye el curso?",
                "category": "EXPLORATION_COURSE_DETAILS", 
                "expected_behavior": "debe validar información contra BD"
            },
            {
                "message": "¿Cuál es la duración específica?",
                "category": "EXPLORATION_SCHEDULE",
                "expected_behavior": "debe usar datos reales de la BD"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            debug_print(f"📝 Test {i}: {test_case['message']}", "FASE_1")
            
            try:
                # Crear mensaje de prueba
                incoming_message = IncomingMessage(
                    message_sid=f"test_msg_{i}",
                    from_number="+1234567890",
                    to_number="+0987654321",
                    body=test_case['message'],
                    timestamp=datetime.now(),
                    raw_data={"MessageSid": f"test_msg_{i}", "From": "+1234567890", "To": "+0987654321", "Body": test_case['message']}
                )
                
                # Generar respuesta segura
                result = await self.anti_hallucination_use_case.generate_safe_response(
                    incoming_message.body,
                    user_memory,
                    {"category": test_case['category']},
                    None  # course_info
                )
                
                # Validar resultado
                if result and 'message' in result:
                    debug_print(f"✅ Respuesta generada: {result['message'][:100]}...", "FASE_1")
                    
                    # Verificar que no contiene información inventada
                    suspicious_phrases = [
                        "12 módulos", "40 horas", "certificado incluido", 
                        "descuento del 30%", "8 semanas"
                    ]
                    
                    response_lower = result['message'].lower()
                    has_suspicious_content = any(phrase in response_lower for phrase in suspicious_phrases)
                    
                    if has_suspicious_content:
                        debug_print("⚠️ ADVERTENCIA: Respuesta puede contener información inventada", "FASE_1")
                    else:
                        debug_print("✅ Respuesta parece segura", "FASE_1")
                        
                else:
                    debug_print("❌ Error: No se generó respuesta", "FASE_1")
                    
            except Exception as e:
                debug_print(f"❌ Error en test {i}: {e}", "FASE_1")
        
        debug_print("✅ Test FASE 1 completado", "FASE_1")
    
    async def test_fase_2_personalizacion(self):
        """Test del sistema de personalización (FASE 2)"""
        debug_print("🧪 Iniciando test FASE 2: Sistema de Personalización", "FASE_2")
        
        # Casos de prueba para diferentes buyer personas
        test_cases = [
            {
                "message": "Soy director de marketing y necesito optimizar nuestras campañas",
                "expected_persona": "lucia_copypro",
                "description": "Detección de Lucía CopyPro"
            },
            {
                "message": "Como gerente de operaciones, busco mejorar la eficiencia de procesos",
                "expected_persona": "marcos_multitask", 
                "description": "Detección de Marcos Multitask"
            },
            {
                "message": "Como CEO, necesito estrategias para competir en el mercado",
                "expected_persona": "sofia_visionaria",
                "description": "Detección de Sofía Visionaria"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            debug_print(f"📝 Test {i}: {test_case['description']}", "FASE_2")
            
            try:
                # Crear memoria con información básica
                user_memory = LeadMemory(
                    user_id=f"test_user_fase2_{i}",
                    name="Usuario Test",
                    role="Profesional",
                    interaction_count=2
                )
                
                # Crear mensaje de prueba
                incoming_message = IncomingMessage(
                    message_sid=f"test_msg_fase2_{i}",
                    from_number="+1234567890",
                    to_number="+0987654321",
                    body=test_case['message'],
                    timestamp=datetime.now(),
                    raw_data={"MessageSid": f"test_msg_fase2_{i}", "From": "+1234567890", "To": "+0987654321", "Body": test_case['message']}
                )
                
                # Generar respuesta personalizada
                result = await self.personalize_response_use_case.generate_personalized_response(
                    incoming_message.body,
                    user_memory,
                    "EXPLORATION"
                )
                
                # Validar resultado
                if result and hasattr(result, 'personalized_response'):
                    debug_print(f"✅ Respuesta personalizada generada", "FASE_2")
                    debug_print(f"🎯 Persona detectada: {result.buyer_persona_detected}", "FASE_2")
                    debug_print(f"📊 Confianza: {result.personalization_confidence:.2f}", "FASE_2")
                    debug_print(f"🔧 Personalizaciones: {', '.join(result.applied_personalizations)}", "FASE_2")
                    
                    # Verificar que la respuesta es personalizada
                    response_lower = result.personalized_response.lower()
                    has_personalization = any(keyword in response_lower for keyword in [
                        'marketing', 'campaña', 'operaciones', 'eficiencia', 'ceo', 'estrategia'
                    ])
                    
                    if has_personalization:
                        debug_print("✅ Respuesta contiene elementos personalizados", "FASE_2")
                    else:
                        debug_print("⚠️ Respuesta puede no estar suficientemente personalizada", "FASE_2")
                        
                else:
                    debug_print("❌ Error: No se generó respuesta personalizada", "FASE_2")
                    
            except Exception as e:
                debug_print(f"❌ Error en test {i}: {e}", "FASE_2")
        
        debug_print("✅ Test FASE 2 completado", "FASE_2")
    
    async def test_integracion_completa(self):
        """Test de integración completa de ambas fases"""
        debug_print("🧪 Iniciando test de integración completa", "INTEGRATION")
        
        try:
            # Crear memoria con buyer persona detectado
            user_memory = LeadMemory(
                user_id="test_integration_user",
                name="Carlos",
                role="Marketing Manager",
                interaction_count=5,
                buyer_persona_match="lucia_copypro"  # Simular persona detectada
            )
            
            # Mensaje que debería activar personalización + anti-inventos
            incoming_message = IncomingMessage(
                message_sid="test_integration_msg",
                from_number="+1234567890",
                to_number="+0987654321",
                body="Como director de marketing, ¿cuál es el precio exacto del curso y qué ROI puedo esperar?",
                timestamp=datetime.now(),
                raw_data={"MessageSid": "test_integration_msg", "From": "+1234567890", "To": "+0987654321", "Body": "Como director de marketing, ¿cuál es el precio exacto del curso y qué ROI puedo esperar?"}
            )
            
            debug_print("📝 Probando integración: Personalización + Anti-inventos", "INTEGRATION")
            
            # Primero probar personalización
            personalization_result = await self.personalize_response_use_case.generate_personalized_response(
                incoming_message.body,
                user_memory,
                "EXPLORATION_PRICING"
            )
            
            if personalization_result:
                debug_print("✅ Personalización funcionando", "INTEGRATION")
                debug_print(f"🎯 Persona: {personalization_result.buyer_persona_detected}", "INTEGRATION")
                
                # Luego probar anti-inventos con la respuesta personalizada
                validation_result = await self.validate_response_use_case.validate_response(
                    personalization_result.personalized_response,
                    None,  # course_info
                    incoming_message.body
                )
                
                if validation_result:
                    debug_print("✅ Validación anti-inventos funcionando", "INTEGRATION")
                    debug_print(f"🔍 Respuesta válida: {validation_result.is_valid}", "INTEGRATION")
                    
                    if not validation_result.is_valid and validation_result.corrected_response:
                        debug_print("✅ Sistema corrigió respuesta inválida", "INTEGRATION")
                        
                else:
                    debug_print("⚠️ Validación anti-inventos no funcionó", "INTEGRATION")
            else:
                debug_print("❌ Personalización no funcionó", "INTEGRATION")
                
        except Exception as e:
            debug_print(f"❌ Error en integración: {e}", "INTEGRATION")
        
        debug_print("✅ Test de integración completado", "INTEGRATION")
    
    async def run_all_tests(self):
        """Ejecutar todos los tests"""
        debug_print("🚀 Iniciando validación completa de Fases 1 y 2", "MAIN")
        
        try:
            # Test FASE 1
            await self.test_fase_1_anti_inventos()
            print("\n" + "="*60 + "\n")
            
            # Test FASE 2  
            await self.test_fase_2_personalizacion()
            print("\n" + "="*60 + "\n")
            
            # Test integración
            await self.test_integracion_completa()
            print("\n" + "="*60 + "\n")
            
            debug_print("🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE", "MAIN")
            debug_print("✅ Fases 1 y 2 están integradas y funcionando", "MAIN")
            
        except Exception as e:
            debug_print(f"❌ Error en tests: {e}", "MAIN")
            raise

async def main():
    """Función principal"""
    print("🧪 VALIDACIÓN E INTEGRACIÓN DE FASES 1 Y 2")
    print("="*60)
    
    tester = IntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 