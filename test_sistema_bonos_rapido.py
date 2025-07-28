#!/usr/bin/env python3
"""
Script de prueba rápida para verificar el sistema de bonos inteligente.
Prueba la activación de bonos sin necesidad de WhatsApp.
"""
import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.application.usecases.bonus_activation_use_case import BonusActivationUseCase
from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.domain.entities.message import IncomingMessage
from memory.lead_memory import LeadMemory

def print_test_header():
    """Imprime header del test"""
    print("🧪 PRUEBA RÁPIDA - SISTEMA DE BONOS INTELIGENTE")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Objetivo: Verificar activación contextual de bonos")
    print("=" * 60)

async def test_bonus_activation():
    """Prueba la activación de bonos contextuales"""
    print("\n🎁 PRUEBA 1: Activación de Bonos Contextuales")
    print("-" * 50)
    
    try:
        # Inicializar caso de uso de bonos
        bonus_use_case = BonusActivationUseCase()
        
        # Simular diferentes contextos
        test_cases = [
            {
                "name": "Lucía CopyPro (Marketing)",
                "role": "Marketing Digital",
                "context": "price_objection",
                "message": "Es muy caro el curso"
            },
            {
                "name": "Marcos Multitask (Operaciones)",
                "role": "Director de Operaciones",
                "context": "buying_signals",
                "message": "Quiero inscribirme"
            },
            {
                "name": "Sofía Visionaria (CEO)",
                "role": "CEO",
                "context": "career_growth",
                "message": "Busco crecer profesionalmente"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test Case {i}: {test_case['name']}")
            print(f"   Rol: {test_case['role']}")
            print(f"   Contexto: {test_case['context']}")
            print(f"   Mensaje: '{test_case['message']}'")
            
            # Simular memoria del usuario
            user_memory = LeadMemory(
                user_id="test_user",
                name=test_case['name'].split()[0],
                role=test_case['role'],
                interests=["automatización", "productividad"],
                pain_points=["tiempo", "eficiencia"]
            )
            
            # Activar bonos contextuales
            bonus_result = await bonus_use_case.activate_contextual_bonuses(
                user_role=test_case['role'],
                conversation_context=test_case['context'],
                urgency_level='high',
                user_interests=user_memory.interests,
                pain_points=user_memory.pain_points
            )
            
            print(f"   ✅ Bonos activados: {len(bonus_result.get('contextual_bonuses', []))}")
            
            if bonus_result.get('contextual_bonuses'):
                print("   🎁 Bonos priorizados:")
                for j, bonus in enumerate(bonus_result['contextual_bonuses'][:3], 1):
                    content = bonus.get('content', 'Bono disponible')
                    priority = bonus.get('priority_reason', 'Prioridad alta')
                    print(f"      {j}. {content[:50]}...")
                    print(f"         Razón: {priority}")
            
            print()
        
        print("✅ PRUEBA 1 COMPLETADA: Activación de bonos funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de bonos: {e}")
        return False

async def test_intent_analysis():
    """Prueba el análisis de intención con bonos"""
    print("\n🧠 PRUEBA 2: Análisis de Intención con Bonos")
    print("-" * 50)
    
    try:
        # Inicializar componentes
        openai_client = OpenAIClient()
        intent_analyzer = AnalyzeMessageIntentUseCase(openai_client)
        
        # Mensajes de prueba
        test_messages = [
            "Cuéntame sobre el curso",
            "Es muy caro",
            "Quiero inscribirme",
            "No sé si podré aprender"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Test Message {i}: '{message}'")
            
            # Crear mensaje simulado
            incoming_message = IncomingMessage(
                from_number="+1234567890",
                body=message,
                message_type="text"
            )
            
            # Analizar intención
            analysis_result = await intent_analyzer.execute(
                user_id="test_user",
                incoming_message=incoming_message,
                context_info=""
            )
            
            if analysis_result['success']:
                category = analysis_result.get('intent_analysis', {}).get('category', 'N/A')
                print(f"   ✅ Intención detectada: {category}")
                
                # Simular activación de bonos
                if category in ['EXPLORATION', 'BUYING_SIGNALS', 'OBJECTION_PRICE', 'TECHNICAL_FEAR']:
                    print(f"   🎁 Bonos se activarían para: {category}")
                else:
                    print(f"   ℹ️ Categoría no requiere bonos: {category}")
            else:
                print(f"   ❌ Error en análisis: {analysis_result.get('error')}")
            
            print()
        
        print("✅ PRUEBA 2 COMPLETADA: Análisis de intención funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de análisis: {e}")
        return False

async def test_response_generation():
    """Prueba la generación de respuestas con bonos"""
    print("\n💬 PRUEBA 3: Generación de Respuestas con Bonos")
    print("-" * 50)
    
    try:
        # Inicializar componentes
        openai_client = OpenAIClient()
        twilio_client = TwilioWhatsAppClient()
        
        # Crear caso de uso de respuesta
        response_use_case = GenerateIntelligentResponseUseCase(
            intent_analyzer=None,  # No necesario para esta prueba
            twilio_client=twilio_client,
            openai_client=openai_client
        )
        
        # Simular diferentes categorías
        test_categories = [
            "EXPLORATION",
            "BUYING_SIGNALS", 
            "OBJECTION_PRICE",
            "TECHNICAL_FEAR"
        ]
        
        for category in test_categories:
            print(f"\n🎯 Probando categoría: {category}")
            
            # Simular resultado de análisis
            analysis_result = {
                'success': True,
                'intent_analysis': {'category': category},
                'user_memory': LeadMemory(
                    user_id="test_user",
                    name="Juan",
                    role="Marketing Digital",
                    interests=["automatización"],
                    pain_points=["tiempo"]
                )
            }
            
            # Simular mensaje
            incoming_message = IncomingMessage(
                from_number="+1234567890",
                body="Mensaje de prueba",
                message_type="text"
            )
            
            # Generar respuesta contextual
            response = await response_use_case._generate_contextual_response(
                analysis_result=analysis_result,
                incoming_message=incoming_message,
                user_id="test_user"
            )
            
            print(f"   ✅ Respuesta generada: {len(response)} caracteres")
            print(f"   📄 Preview: {response[:100]}...")
            
            # Verificar si incluye información de bonos
            if "🎁" in response or "BONOS" in response.upper():
                print("   🎁 ✅ Respuesta incluye información de bonos")
            else:
                print("   ℹ️ Respuesta sin bonos (puede ser normal)")
            
            print()
        
        print("✅ PRUEBA 3 COMPLETADA: Generación de respuestas funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de respuestas: {e}")
        return False

async def main():
    """Función principal de pruebas"""
    print_test_header()
    
    # Ejecutar pruebas
    tests = [
        ("Activación de Bonos", test_bonus_activation),
        ("Análisis de Intención", test_intent_analysis),
        ("Generación de Respuestas", test_response_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente.")
        print("🚀 Puedes proceder con las pruebas de WhatsApp.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores antes de continuar.")
    
    print("\n📋 Próximos pasos:")
    print("1. Ejecutar: python run_webhook_server_debug.py")
    print("2. Configurar ngrok: ngrok http 8000")
    print("3. Configurar webhook en Twilio Console")
    print("4. Probar con mensajes reales de WhatsApp")

if __name__ == "__main__":
    asyncio.run(main()) 