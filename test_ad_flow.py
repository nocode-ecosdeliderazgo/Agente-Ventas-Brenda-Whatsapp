#!/usr/bin/env python3
"""
Script de prueba específico para el flujo de anuncios.
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.application.usecases.detect_ad_hashtags_use_case import DetectAdHashtagsUseCase
from app.application.usecases.process_ad_flow_use_case import ProcessAdFlowUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
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

async def test_ad_flow():
    """Prueba el flujo de anuncios"""
    print("🧪 PROBANDO FLUJO DE ANUNCIOS")
    print("="*50)
    
    # Inicializar componentes
    memory_manager = MemoryManager(memory_dir="memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    twilio_client = ConsoleTwilioClient()
    privacy_flow_use_case = PrivacyFlowUseCase(memory_use_case, twilio_client)
    course_query_use_case = QueryCourseInformationUseCase()
    
    # Inicializar casos de uso de anuncios
    detect_hashtags_use_case = DetectAdHashtagsUseCase()
    process_ad_flow_use_case = ProcessAdFlowUseCase(
        memory_use_case, 
        privacy_flow_use_case, 
        course_query_use_case
    )
    
    # Mensaje de prueba con ambos hashtags
    test_message = "Hola, me interesa el curso #Experto_IA_GPT_Gemini #ADSIM_05"
    
    print(f"📨 Mensaje de prueba: '{test_message}'")
    print("-" * 50)
    
    # 1. Detectar hashtags
    print("🔍 PASO 1: Detectando hashtags...")
    hashtags_info = await detect_hashtags_use_case.execute(test_message)
    print(f"✅ Resultado detección: {hashtags_info}")
    
    if hashtags_info.get('is_ad'):
        print("🎯 ¡ANUNCIO DETECTADO!")
        
        # 2. Procesar flujo de anuncios
        print("\n📢 PASO 2: Procesando flujo de anuncios...")
        webhook_data = {
            'MessageSid': 'test_sid',
            'From': 'whatsapp:+console_user_001',
            'To': 'whatsapp:+1234567890',
            'Body': test_message
        }
        
        user_data = {'id': 'console_user_001', 'first_name': 'Gael'}
        
        ad_flow_result = await process_ad_flow_use_case.execute(
            webhook_data, 
            user_data, 
            hashtags_info
        )
        
        print(f"✅ Resultado flujo de anuncios: {ad_flow_result}")
        
        if ad_flow_result.get('ad_flow_completed'):
            print("🎉 ¡FLUJO DE ANUNCIOS COMPLETADO EXITOSAMENTE!")
            print(f"📝 Respuesta: {ad_flow_result.get('response_text', '')}")
        else:
            print("❌ Error en flujo de anuncios")
    else:
        print("❌ No se detectó anuncio")
        print(f"🔍 Hashtags detectados: {hashtags_info}")

if __name__ == "__main__":
    asyncio.run(test_ad_flow()) 