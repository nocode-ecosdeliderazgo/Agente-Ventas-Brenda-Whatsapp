#!/usr/bin/env python3
"""
Script de prueba específico para el sistema de FAQ.
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.application.usecases.faq_flow_use_case import FAQFlowUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from memory.lead_memory import MemoryManager
from app.infrastructure.twilio.client import TwilioWhatsAppClient

class ConsoleTwilioClient(TwilioWhatsAppClient):
    """Cliente Twilio simulado para consola"""
    
    def __init__(self):
        super().__init__()
    
    async def send_message(self, message):
        """Simula envío de mensaje"""
        print(f"\n📱 [TWILIO SIMULADO] Enviando mensaje:")
        print(f"   Para: +console_user_001")
        print(f"   Mensaje: {message}")
        print(f"   SID: console_sim_test")
        return True

async def test_faq_system():
    """Prueba el sistema de FAQ"""
    print("❓ PROBANDO SISTEMA DE FAQ")
    print("="*50)
    
    # Inicializar componentes
    memory_manager = MemoryManager(memory_dir="memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    twilio_client = ConsoleTwilioClient()
    
    # Inicializar caso de uso de FAQ
    faq_flow_use_case = FAQFlowUseCase(
        memory_use_case, 
        twilio_client
    )
    
    # Simular usuario con datos completos
    user_data = {
        'id': 'console_user_001',
        'first_name': 'Gael',
        'phone': '+1234567890'
    }
    
    # Configurar memoria del usuario
    memory = memory_use_case.get_user_memory(user_data['id'])
    memory.user_name = 'Gael'
    memory.user_role = 'CEO'
    memory.company_size = 'Mediana'
    memory.industry = 'Tecnología'
    memory_use_case.memory_manager.save_lead_memory(user_data['id'], memory)
    
    # Escenario 1: Pregunta sobre precio
    print("\n💰 ESCENARIO 1: Pregunta sobre precio")
    print("-" * 50)
    
    test_message_1 = "¿Cuál es el precio del curso?"
    webhook_data_1 = {
        'MessageSid': 'test_sid_1',
        'From': 'whatsapp:+console_user_001',
        'To': 'whatsapp:+1234567890',
        'Body': test_message_1
    }
    
    print(f"📨 Mensaje: '{test_message_1}'")
    
    result_1 = await faq_flow_use_case.execute(webhook_data_1, user_data)
    print(f"✅ Resultado: {result_1}")
    
    # Escenario 2: Pregunta sobre duración
    print("\n⏰ ESCENARIO 2: Pregunta sobre duración")
    print("-" * 50)
    
    test_message_2 = "¿Cuánto tiempo dura el curso?"
    webhook_data_2 = {
        'MessageSid': 'test_sid_2',
        'From': 'whatsapp:+console_user_001',
        'To': 'whatsapp:+1234567890',
        'Body': test_message_2
    }
    
    print(f"📨 Mensaje: '{test_message_2}'")
    
    result_2 = await faq_flow_use_case.execute(webhook_data_2, user_data)
    print(f"✅ Resultado: {result_2}")
    
    # Escenario 3: Pregunta sobre implementación
    print("\n🚀 ESCENARIO 3: Pregunta sobre implementación")
    print("-" * 50)
    
    test_message_3 = "¿Cómo se implementa en mi empresa?"
    webhook_data_3 = {
        'MessageSid': 'test_sid_3',
        'From': 'whatsapp:+console_user_001',
        'To': 'whatsapp:+1234567890',
        'Body': test_message_3
    }
    
    print(f"📨 Mensaje: '{test_message_3}'")
    
    result_3 = await faq_flow_use_case.execute(webhook_data_3, user_data)
    print(f"✅ Resultado: {result_3}")
    
    # Escenario 4: Pregunta sobre ROI
    print("\n📊 ESCENARIO 4: Pregunta sobre ROI")
    print("-" * 50)
    
    test_message_4 = "¿Cuál es el ROI esperado?"
    webhook_data_4 = {
        'MessageSid': 'test_sid_4',
        'From': 'whatsapp:+console_user_001',
        'To': 'whatsapp:+1234567890',
        'Body': test_message_4
    }
    
    print(f"📨 Mensaje: '{test_message_4}'")
    
    result_4 = await faq_flow_use_case.execute(webhook_data_4, user_data)
    print(f"✅ Resultado: {result_4}")
    
    # Escenario 5: Pregunta no encontrada
    print("\n❓ ESCENARIO 5: Pregunta no encontrada")
    print("-" * 50)
    
    test_message_5 = "¿Cómo está el clima hoy?"
    webhook_data_5 = {
        'MessageSid': 'test_sid_5',
        'From': 'whatsapp:+console_user_001',
        'To': 'whatsapp:+1234567890',
        'Body': test_message_5
    }
    
    print(f"📨 Mensaje: '{test_message_5}'")
    
    result_5 = await faq_flow_use_case.execute(webhook_data_5, user_data)
    print(f"✅ Resultado: {result_5}")
    
    # Prueba de detección de intención de FAQ
    print("\n🎯 PRUEBA DE DETECCIÓN DE INTENCIÓN DE FAQ")
    print("-" * 50)
    
    test_messages = [
        "¿Cuál es el precio?",
        "¿Cuánto dura?",
        "¿Qué requisitos necesito?",
        "¿Hay casos de éxito?",
        "Hola, ¿cómo estás?",
        "Me gustaría información",
        "¿Cómo funciona?"
    ]
    
    for message in test_messages:
        is_faq_intent = await faq_flow_use_case.detect_faq_intent(message)
        print(f"📨 '{message}' → FAQ: {'✅' if is_faq_intent else '❌'}")
    
    # Prueba de sugerencias de FAQ
    print("\n💡 PRUEBA DE SUGERENCIAS DE FAQ")
    print("-" * 50)
    
    suggestions = await faq_flow_use_case.get_faq_suggestions(user_data['id'])
    print(f"📋 Sugerencias para el usuario: {suggestions}")
    
    print("\n🎉 ¡PRUEBA DE SISTEMA DE FAQ COMPLETADA!")

if __name__ == "__main__":
    asyncio.run(test_faq_system()) 