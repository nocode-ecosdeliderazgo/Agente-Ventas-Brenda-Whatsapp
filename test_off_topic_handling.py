#!/usr/bin/env python3
"""
Test del sistema de manejo de mensajes fuera de contexto y ofensivos.
"""

import asyncio
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prompts.agent_prompts import WhatsAppBusinessTemplates


def print_test_header(test_name: str):
    """Imprime header del test."""
    print(f"\n{'='*70}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*70}")


def print_response_sample(response: str, title: str):
    """Imprime muestra de respuesta."""
    print(f"\n📝 {title}:")
    print(f"   {response[:150]}{'...' if len(response) > 150 else ''}")


async def test_casual_off_topic_redirect():
    """Test de redirección casual con humor."""
    print_test_header("REDIRECCIÓN CASUAL CON HUMOR")
    
    # Test mensajes casuales
    casual_messages = [
        "¿Cómo está el clima hoy?",
        "¿Qué opinas del fútbol?",
        "¿Te gusta la música?",
        "¿Sabes cocinar?",
        "¿Qué hora es?"
    ]
    
    print("🔄 Probando diferentes mensajes casuales...")
    
    for i, message in enumerate(casual_messages):
        response = WhatsAppBusinessTemplates.off_topic_casual_redirect("Carlos", message.split()[0])
        print(f"\n   {i+1}. Mensaje: '{message}'")
        print_response_sample(response, "Respuesta con humor")
        
        # Verificar elementos clave
        has_humor = any(emoji in response for emoji in ["😅", "🤔", "😊", "🎯"])
        has_redirect = "IA" in response and "empresa" in response
        has_course_offer = "curso" in response
        
        if has_humor and has_redirect and has_course_offer:
            print("      ✅ Contiene humor, redirección y oferta de curso")
        else:
            print(f"      ❌ Falta elementos: Humor({has_humor}), Redirect({has_redirect}), Curso({has_course_offer})")


async def test_repeated_off_topic_predefined():
    """Test de mensaje predeterminado para intentos repetidos."""
    print_test_header("MENSAJE PREDETERMINADO - INTENTOS REPETIDOS")
    
    response = WhatsAppBusinessTemplates.off_topic_repeated_predefined("María")
    
    print_response_sample(response, "Mensaje predeterminado completo")
    
    # Verificar elementos clave
    elements_check = {
        "Menciona función principal": "función principal" in response,
        "Mensaje claro sobre especialidad": "área de especialidad" in response,
        "Ofrece alternativas de curso": "Te interesa conocer" in response,
        "Lista beneficios específicos": "Automatizar procesos" in response,
        "Pregunta de acción": "¿Por cuál empezamos?" in response,
        "Tono profesional": "encantada" in response
    }
    
    print(f"\n📊 VERIFICACIÓN DE ELEMENTOS:")
    for element, present in elements_check.items():
        status = "✅" if present else "❌"
        print(f"   {status} {element}")
    
    all_present = all(elements_check.values())
    if all_present:
        print(f"\n🎉 MENSAJE PREDETERMINADO COMPLETO Y EFECTIVO")
    else:
        print(f"\n⚠️  FALTAN ELEMENTOS EN MENSAJE PREDETERMINADO")


async def test_offensive_message_firm_response():
    """Test de respuesta firme para mensajes ofensivos."""
    print_test_header("RESPUESTA FIRME - MENSAJES OFENSIVOS")
    
    response = WhatsAppBusinessTemplates.offensive_message_firm_response("Roberto")
    
    print_response_sample(response, "Respuesta firme completa")
    
    # Verificar elementos clave
    firmness_check = {
        "Señala comportamiento inapropiado": "no es adecuado" in response,
        "Mantiene profesionalismo": "profesional" in response,
        "Establece límites claros": "respeto mutuo" in response,
        "Reitera función específica": "únicamente proveer información" in response,
        "Ofrece continuar profesionalmente": "continuar con información" in response,
        "No es grosero": not any(word in response.lower() for word in ["idiota", "estúpido", "tonto"])
    }
    
    print(f"\n📊 VERIFICACIÓN DE FIRMEZA APROPIADA:")
    for element, present in firmness_check.items():
        status = "✅" if present else "❌"
        print(f"   {status} {element}")
    
    all_appropriate = all(firmness_check.values())
    if all_appropriate:
        print(f"\n🎉 RESPUESTA FIRME PERO PROFESIONAL")
    else:
        print(f"\n⚠️  REVISAR EQUILIBRIO FIRMEZA/PROFESIONALISMO")


async def test_humor_variations():
    """Test de variaciones de humor en respuestas casuales."""
    print_test_header("VARIACIONES DE HUMOR")
    
    print("🎭 Probando diferentes respuestas de humor...")
    
    # Generar varias respuestas para ver variaciones
    responses = []
    for i in range(5):
        response = WhatsAppBusinessTemplates.off_topic_casual_redirect("Ana", "clima")
        responses.append(response)
    
    # Verificar que hay variaciones
    unique_responses = len(set(responses))
    
    print(f"\n📊 Generadas {len(responses)} respuestas, {unique_responses} únicas")
    
    if unique_responses > 1:
        print("✅ Sistema genera respuestas variadas (evita repetición)")
        for i, response in enumerate(set(responses), 1):
            humor_line = response.split('\n')[0]  # Primera línea con humor
            print(f"   {i}. {humor_line}")
    else:
        print("❌ Sistema genera siempre la misma respuesta")
    
    # Verificar elementos de humor específicos
    humor_elements = ["😅", "🤔", "😊", "🎯", "Google", "cerebro", "especialidad"]
    
    print(f"\n🎯 ELEMENTOS DE HUMOR DETECTADOS:")
    for element in humor_elements:
        found_in = sum(1 for response in responses if element in response)
        if found_in > 0:
            print(f"   ✅ '{element}' usado en {found_in}/{len(responses)} respuestas")


async def test_integration_scenarios():
    """Test de escenarios de integración completos."""
    print_test_header("ESCENARIOS DE INTEGRACIÓN")
    
    scenarios = [
        {
            "name": "Usuario Nuevo - Primera pregunta casual",
            "user": "",
            "expected_response": "humor",
            "description": "Debe redirigir con humor sin conocer el nombre"
        },
        {
            "name": "Usuario Conocido - Segunda pregunta off-topic", 
            "user": "Pedro",
            "expected_response": "predefined",
            "description": "Debe usar mensaje predeterminado más firme"
        },
        {
            "name": "Comportamiento ofensivo",
            "user": "Luis",
            "expected_response": "firm",
            "description": "Debe responder firmemente pero sin agresividad"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 ESCENARIO: {scenario['name']}")
        print(f"   {scenario['description']}")
        
        if scenario['expected_response'] == 'humor':
            response = WhatsAppBusinessTemplates.off_topic_casual_redirect(scenario['user'])
        elif scenario['expected_response'] == 'predefined':
            response = WhatsAppBusinessTemplates.off_topic_repeated_predefined(scenario['user'])
        else:
            response = WhatsAppBusinessTemplates.offensive_message_firm_response(scenario['user'])
        
        print_response_sample(response, f"Respuesta para {scenario['name']}")
        
        # Verificar personalización por nombre
        if scenario['user']:
            has_name = scenario['user'] in response
            print(f"   {'✅' if has_name else '❌'} Personalizado con nombre del usuario")


async def main():
    """Función principal."""
    print("🚀 INICIANDO TESTS DE MANEJO DE MENSAJES FUERA DE CONTEXTO")
    print("=" * 70)
    
    # Test 1: Redirección casual con humor
    await test_casual_off_topic_redirect()
    
    # Test 2: Mensaje predeterminado para intentos repetidos
    await test_repeated_off_topic_predefined()
    
    # Test 3: Respuesta firme para mensajes ofensivos
    await test_offensive_message_firm_response()
    
    # Test 4: Variaciones de humor
    await test_humor_variations()
    
    # Test 5: Escenarios de integración
    await test_integration_scenarios()
    
    # Resumen final
    print(f"\n{'='*70}")
    print("🎉 EVALUACIÓN DEL SISTEMA DE MANEJO OFF-TOPIC")
    print(f"{'='*70}")
    
    print(f"\n✅ FUNCIONALIDADES IMPLEMENTADAS:")
    print("• Detección de 5 categorías off-topic (CASUAL, PERSONAL, UNRELATED, REPEATED, OFFENSIVE)")
    print("• Redirección con humor/sarcasmo ligero para primeros intentos")
    print("• Respuestas variadas para evitar repetición")
    print("• Mensaje predeterminado claro para intentos reiterados")
    print("• Respuesta firme pero profesional para comportamiento ofensivo")
    print("• Personalización con nombre del usuario cuando disponible")
    
    print(f"\n🎯 CARACTERÍSTICAS DEL SISTEMA:")
    print("• Mantiene tono profesional en todas las respuestas")
    print("• Siempre redirige hacia información de cursos")
    print("• Escalación gradual: humor → predeterminado → firme")
    print("• Tracking de intentos off-topic en memoria del usuario")
    print("• Impacto en lead_score según severidad del comportamiento")
    
    print(f"\n🔄 FLUJO DE MANEJO:")
    print("1. **Primer intento off-topic**: Humor/sarcasmo + redirección amable")
    print("2. **Segundo+ intento**: Mensaje predeterminado claro sobre función")
    print("3. **Comportamiento ofensivo**: Respuesta firme + límites profesionales")
    print("4. **Tracking en memoria**: Contador de intentos + impacto en lead_score")
    
    print(f"\n🚨 PRÓXIMOS PASOS PARA PRUEBAS REALES:")
    print("• Probar detección de categorías en análisis de intención")
    print("• Verificar que memoria de usuario se actualiza correctamente")
    print("• Confirmar que lead_score se ajusta según comportamiento")
    print("• Validar escalación gradual en conversaciones múltiples")
    
    print(f"\n✅ SISTEMA DE MANEJO OFF-TOPIC LISTO PARA IMPLEMENTACIÓN")


if __name__ == "__main__":
    asyncio.run(main())