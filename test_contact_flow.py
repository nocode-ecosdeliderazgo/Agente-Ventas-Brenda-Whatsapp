#!/usr/bin/env python3
"""
Script de prueba específico para el flujo de contacto.
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.application.usecases.contact_flow_use_case import ContactFlowUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
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

async def test_contact_flow():
    """Prueba el flujo de contacto"""
    print("📞 PROBANDO FLUJO DE CONTACTO")
    print("="*50)
    
    # Inicializar componentes
    memory_manager = MemoryManager(memory_dir="memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    twilio_client = ConsoleTwilioClient()
    privacy_flow_use_case = PrivacyFlowUseCase(memory_use_case, twilio_client)
    
    # Inicializar caso de uso de contacto
    contact_flow_use_case = ContactFlowUseCase(
        memory_use_case, 
        privacy_flow_use_case, 
        twilio_client
    )
    
    # Simular usuario con datos completos
    user_data = {
        'id': 'console_user_001',
        'first_name': 'Gael',
        'phone': '+1234567890'
    }
    
    # Escenario 1: Usuario sin consentimiento de privacidad
    print("\n🔒 ESCENARIO 1: Usuario sin consentimiento de privacidad")
    print("-" * 50)
    
    test_message_1 = "Quiero hablar con un asesor"
    webhook_data_1 = {
        'MessageSid': 'test_sid_1',
        'From': 'whatsapp:+console_user_001',
        'To': 'whatsapp:+1234567890',
        'Body': test_message_1
    }
    
    print(f"📨 Mensaje: '{test_message_1}'")
    
    result_1 = await contact_flow_use_case.execute(webhook_data_1, user_data)
    print(f"✅ Resultado: {result_1}")
    
    # Simular que el usuario completa el flujo de privacidad
    print("\n🔒 Simulando completar flujo de privacidad...")
    memory = memory_use_case.get_user_memory(user_data['id'])
    memory.privacy_consent_given = True
    memory.user_name = 'Gael'
    memory.user_role = 'CEO'
    memory.company_size = 'Mediana'
    memory.industry = 'Tecnología'
    memory_use_case.memory_manager.save_lead_memory(user_data['id'], memory)
    
    # Escenario 2: Usuario con consentimiento, solicitud inicial
    print("\n📞 ESCENARIO 2: Solicitud inicial de contacto")
    print("-" * 50)
    
    test_message_2 = "Necesito hablar con un asesor sobre implementación"
    webhook_data_2 = {
        'MessageSid': 'test_sid_2',
        'From': 'whatsapp:+console_user_001',
        'To': 'whatsapp:+1234567890',
        'Body': test_message_2
    }
    
    print(f"📨 Mensaje: '{test_message_2}'")
    
    result_2 = await contact_flow_use_case.execute(webhook_data_2, user_data)
    print(f"✅ Resultado: {result_2}")
    
    # Escenario 3: Usuario proporciona información adicional
    print("\n📝 ESCENARIO 3: Proporcionando información adicional")
    print("-" * 50)
    
    test_message_3 = "Necesito información sobre precios y casos de éxito para implementar IA en mi empresa"
    webhook_data_3 = {
        'MessageSid': 'test_sid_3',
        'From': 'whatsapp:+console_user_001',
        'To': 'whatsapp:+1234567890',
        'Body': test_message_3
    }
    
    print(f"📨 Mensaje: '{test_message_3}'")
    
    result_3 = await contact_flow_use_case.execute(webhook_data_3, user_data)
    print(f"✅ Resultado: {result_3}")
    
    # Escenario 4: Usuario confirma la solicitud
    print("\n✅ ESCENARIO 4: Confirmando solicitud")
    print("-" * 50)
    
    test_message_4 = "Sí, confirmo"
    webhook_data_4 = {
        'MessageSid': 'test_sid_4',
        'From': 'whatsapp:+console_user_001',
        'To': 'whatsapp:+1234567890',
        'Body': test_message_4
    }
    
    print(f"📨 Mensaje: '{test_message_4}'")
    
    result_4 = await contact_flow_use_case.execute(webhook_data_4, user_data)
    print(f"✅ Resultado: {result_4}")
    
    # Escenario 5: Usuario intenta contactar nuevamente
    print("\n🔄 ESCENARIO 5: Intento de contacto nuevamente")
    print("-" * 50)
    
    test_message_5 = "Quiero hablar con un asesor"
    webhook_data_5 = {
        'MessageSid': 'test_sid_5',
        'From': 'whatsapp:+console_user_001',
        'To': 'whatsapp:+1234567890',
        'Body': test_message_5
    }
    
    print(f"📨 Mensaje: '{test_message_5}'")
    
    result_5 = await contact_flow_use_case.execute(webhook_data_5, user_data)
    print(f"✅ Resultado: {result_5}")
    
    # Prueba de detección de intención
    print("\n🎯 PRUEBA DE DETECCIÓN DE INTENCIÓN")
    print("-" * 50)
    
    test_messages = [
        "Quiero hablar con un asesor",
        "Necesito contacto humano",
        "Busco asesoría especializada",
        "¿Puedo hablar con alguien?",
        "Hola, ¿cómo estás?",
        "Información sobre el curso",
        "Me gustaría implementar IA"
    ]
    
    for message in test_messages:
        is_contact_intent = await contact_flow_use_case.detect_contact_intent(message)
        print(f"📨 '{message}' → Contacto: {'✅' if is_contact_intent else '❌'}")
    
    print("\n🎉 ¡PRUEBA DE FLUJO DE CONTACTO COMPLETADA!")

if __name__ == "__main__":
    asyncio.run(test_contact_flow()) 