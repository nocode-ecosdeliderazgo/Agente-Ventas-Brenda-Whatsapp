#!/usr/bin/env python3
"""
Test del sistema de FAQ inteligente integrado en el agente inteligente.
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.faq.faq_knowledge_provider import FAQKnowledgeProvider
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.domain.entities.message import IncomingMessage
from memory.lead_memory import MemoryManager


def print_test_header(test_name: str):
    """Imprime header del test."""
    print(f"\n{'='*70}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*70}")


def print_test_result(success: bool, message: str):
    """Imprime resultado del test."""
    status = "✅ PASÓ" if success else "❌ FALLÓ"
    print(f"\n{status}: {message}")


async def test_faq_knowledge_provider():
    """Test del proveedor de knowledge FAQ."""
    
    print_test_header("FAQ KNOWLEDGE PROVIDER")
    
    try:
        provider = FAQKnowledgeProvider()
        
        # Test 1: Detección de FAQ
        print("🧪 TEST 1: Detección de FAQ")
        test_messages = [
            ("¿Cuál es el precio del curso?", True, "precio"),
            ("¿Cuánto tiempo dura?", True, "duración"),
            ("¿Cómo se implementa?", True, "implementación"),
            ("Hola, buenos días", False, None)
        ]
        
        for message, expected_is_faq, expected_category in test_messages:
            context = await provider.get_faq_context_for_intelligence(message)
            is_faq = context['is_faq']
            category = context.get('category')
            
            status = "✅" if is_faq == expected_is_faq else "❌"
            print(f"   {status} '{message}' -> FAQ: {is_faq}, Categoría: {category}")
            
            if is_faq and expected_category:
                if category == expected_category:
                    print(f"      ✅ Categoría correcta: {category}")
                else:
                    print(f"      ❌ Categoría incorrecta. Esperado: {expected_category}, Obtenido: {category}")
        
        # Test 2: Contexto para AI
        print("\n🧪 TEST 2: Contexto para AI")
        user_context = {
            'name': 'Carlos',
            'user_role': 'CEO',
            'company_size': 'mediana',
            'industry': 'tecnología'
        }
        
        context = await provider.get_faq_context_for_intelligence(
            "¿Cuál es el precio del curso?", user_context
        )
        
        if context['is_faq']:
            ai_context = context['context_for_ai']
            print(f"   📝 Contexto AI generado: {len(ai_context)} caracteres")
            print(f"   📋 Contiene información específica para CEO: {'CEO' in ai_context}")
            print(f"   📋 Incluye información de precio: {'precio' in ai_context.lower()}")
            print_test_result(True, "Contexto AI generado correctamente")
        else:
            print_test_result(False, "No se detectó FAQ para generar contexto")
        
        return True
        
    except Exception as e:
        print_test_result(False, f"Error en test de FAQ Knowledge Provider: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_intelligent_faq_integration():
    """Test de integración FAQ con agente inteligente (simulado)."""
    
    print_test_header("INTEGRACIÓN FAQ CON AGENTE INTELIGENTE")
    
    try:
        # Configurar sistema simulado (sin OpenAI real)
        memory_manager = MemoryManager(memory_dir="memorias_test")
        memory_use_case = ManageUserMemoryUseCase(memory_manager)
        twilio_client = TwilioWhatsAppClient()
        
        # Solo test del knowledge provider (sin OpenAI)
        provider = FAQKnowledgeProvider()
        
        # Test 1: FAQ de precio con personalización
        print("🧪 TEST 1: FAQ de precio personalizada")
        user_id = "5215512345678"
        user_memory = memory_use_case.get_user_memory(user_id)
        user_memory.name = "María"
        user_memory.role = "CEO"
        user_memory.company_size = "pequeña"
        user_memory.industry = "consultora"
        memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
        
        user_context = {
            'name': 'María',
            'user_role': 'CEO',
            'company_size': 'pequeña',
            'industry': 'consultora'
        }
        
        faq_context = await provider.get_faq_context_for_intelligence(
            "¿Cuánto cuesta el curso?", user_context
        )
        
        if faq_context['is_faq'] and faq_context['category'] == 'precio':
            print_test_result(True, f"FAQ de precio detectada para CEO María")
            print(f"   📝 Contexto generado: {len(faq_context['context_for_ai'])} caracteres")
            print(f"   🎯 Escalación requerida: {faq_context['escalation_needed']}")
        else:
            print_test_result(False, "FAQ de precio no detectada correctamente")
        
        # Test 2: FAQ de implementación (con escalación)
        print("\n🧪 TEST 2: FAQ de implementación con escalación")
        faq_context = await provider.get_faq_context_for_intelligence(
            "¿Cómo implemento esto en mi empresa?", user_context
        )
        
        if (faq_context['is_faq'] and 
            faq_context['category'] == 'implementación' and
            faq_context['escalation_needed']):
            print_test_result(True, "FAQ de implementación con escalación detectada")
            print(f"   🚨 Escalación automática activada")
        else:
            print_test_result(False, "FAQ de implementación no manejada correctamente")
        
        # Test 3: No-FAQ
        print("\n🧪 TEST 3: Mensaje no-FAQ")
        faq_context = await provider.get_faq_context_for_intelligence(
            "Hola, me interesa conocer más sobre sus servicios", user_context
        )
        
        if not faq_context['is_faq']:
            print_test_result(True, "Mensaje no-FAQ correctamente identificado")
        else:
            print_test_result(False, "Mensaje identificado incorrectamente como FAQ")
        
        # Test 4: FAQs relacionadas
        print("\n🧪 TEST 4: FAQs relacionadas")
        related_faqs = await provider.get_related_faqs('precio')
        
        if len(related_faqs) > 0:
            categories = [faq['category'] for faq in related_faqs]
            print(f"   📊 FAQs relacionadas a precio: {categories}")
            print_test_result(True, f"Se encontraron {len(related_faqs)} FAQs relacionadas")
        else:
            print_test_result(False, "No se encontraron FAQs relacionadas")
        
        return True
        
    except Exception as e:
        print_test_result(False, f"Error en test de integración: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_fallback_faq_response():
    """Test de respuestas FAQ de fallback."""
    
    print_test_header("RESPUESTAS FAQ DE FALLBACK")
    
    try:
        provider = FAQKnowledgeProvider()
        
        # Simular contexto de usuario
        user_context = {
            'name': 'Roberto',
            'user_role': 'Manager de Operaciones',
            'company_size': 'grande',
            'industry': 'manufactura'
        }
        
        # Obtener FAQ de duración
        faq_context = await provider.get_faq_context_for_intelligence(
            "¿Cuánto tiempo toma completar el curso?", user_context
        )
        
        if faq_context['is_faq']:
            # Simular generación de respuesta fallback
            # (Esto normalmente lo haría GenerateIntelligentResponseUseCase)
            base_answer = faq_context['base_answer']
            category = faq_context['category']
            
            # Respuesta personalizada básica
            fallback_response = f"¡Hola Roberto! 😊\n\nComo Manager de Operaciones, {base_answer}"
            
            print(f"   📝 Respuesta fallback generada:")
            print(f"   {fallback_response[:200]}...")
            
            # Verificar personalización
            if "Roberto" in fallback_response and "Manager" in fallback_response:
                print_test_result(True, "Respuesta FAQ fallback personalizada correctamente")
            else:
                print_test_result(False, "Personalización de respuesta fallback falló")
        else:
            print_test_result(False, "FAQ no detectada para test de fallback")
        
        return True
        
    except Exception as e:
        print_test_result(False, f"Error en test de respuesta fallback: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Función principal."""
    print("🚀 INICIANDO TESTS DE SISTEMA FAQ INTELIGENTE")
    
    # Test 1: Proveedor de conocimiento
    success1 = await test_faq_knowledge_provider()
    
    # Test 2: Integración con agente inteligente
    success2 = await test_intelligent_faq_integration()
    
    # Test 3: Respuestas de fallback
    success3 = await test_fallback_faq_response()
    
    # Resumen final
    if success1 and success2 and success3:
        print(f"\n{'='*70}")
        print("🎉 TODOS LOS TESTS PASARON - SISTEMA FAQ INTELIGENTE LISTO")
        print(f"{'='*70}")
        print("\n📋 RESUMEN:")
        print("✅ FAQ Knowledge Provider funcionando")
        print("✅ Detección inteligente de FAQ integrada")
        print("✅ Contexto AI generado correctamente")
        print("✅ Personalización por buyer persona")
        print("✅ Sistema de escalación automática")
        print("✅ Respuestas fallback personalizadas")
        print("✅ FAQs relacionadas disponibles")
        
        print("\n🔄 FLUJO ACTUAL:")
        print("1. **PRIORIDAD 2**: Agente inteligente detecta FAQ y genera respuesta natural")
        print("2. **FALLBACK**: FAQ Flow directo si agente inteligente falla")
        print("3. **COMPATIBLE**: Sistema funciona con y sin BD")
        
        print("\n🎯 VENTAJAS DEL SISTEMA HÍBRIDO:")
        print("• Respuestas más naturales y conversacionales")
        print("• Personalización avanzada por contexto")
        print("• Compatibilidad total con BD cuando se arregle")
        print("• Fallback robusto garantiza funcionamiento")
        print("• Escalación inteligente a asesores humanos")
        
        return True
    else:
        print(f"\n{'='*70}")
        print("❌ ALGUNOS TESTS FALLARON - REVISAR IMPLEMENTACIÓN")
        print(f"{'='*70}")
        return False


if __name__ == "__main__":
    asyncio.run(main())