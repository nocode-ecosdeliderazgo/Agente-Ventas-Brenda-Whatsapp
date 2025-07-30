#!/usr/bin/env python3
"""
Script de prueba para simular el flujo completo:
1. Usuario nuevo envía hashtags de anuncio
2. Se activa flujo de privacidad
3. Usuario acepta privacidad
4. Usuario da nombre
5. Se activa automáticamente el flujo de anuncios
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.application.usecases.process_incoming_message import ProcessIncomingMessageUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.application.usecases.detect_ad_hashtags_use_case import DetectAdHashtagsUseCase
from app.application.usecases.process_ad_flow_use_case import ProcessAdFlowUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.database.client import DatabaseClient
from app.domain.entities.message import IncomingMessage
from memory.lead_memory import MemoryManager

class ConsoleTwilioClient(TwilioWhatsAppClient):
    """Cliente Twilio simulado para pruebas en consola."""
    
    def __init__(self):
        # Inicializar la clase padre correctamente
        super().__init__()  # Esto inicializa self.from_number
        self.message_count = 0
    
    async def send_whatsapp_message(self, to_number: str, message: str) -> str:
        """Simula envío de mensaje WhatsApp."""
        self.message_count += 1
        sid = f"console_sim_{self.message_count}"
        
        print(f"\n📱 [TWILIO SIMULADO] Enviando mensaje:")
        print(f"   Para: {to_number}")
        print(f"   Mensaje: {message}")
        print(f"   SID: {sid}")
        
        return sid
    
    async def send_message(self, message):
        """Simula envío de mensaje genérico."""
        sid = await self.send_whatsapp_message(message.to_number, message.body)
        return {
            'success': True,
            'message_sid': sid,
            'error': None
        }

async def test_complete_flow():
    """Prueba el flujo completo de privacidad + anuncios."""
    
    print("🚀 INICIANDO PRUEBA DE FLUJO COMPLETO")
    print("=" * 60)
    
    # Configurar componentes
    twilio_client = ConsoleTwilioClient()
    memory_manager = MemoryManager()
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    privacy_flow_use_case = PrivacyFlowUseCase(memory_use_case, twilio_client)
    detect_hashtags_use_case = DetectAdHashtagsUseCase()
    course_query_use_case = QueryCourseInformationUseCase()
    process_ad_flow_use_case = ProcessAdFlowUseCase(memory_use_case, twilio_client, course_query_use_case)
    
    # Crear procesador principal
    processor = ProcessIncomingMessageUseCase(
        twilio_client=twilio_client,
        memory_use_case=memory_use_case,
        privacy_flow_use_case=privacy_flow_use_case,
        detect_ad_hashtags_use_case=detect_hashtags_use_case,
        process_ad_flow_use_case=process_ad_flow_use_case
    )
    
    # Usuario de prueba
    user_id = "test_user_complete_flow"
    user_number = "+1234567890"
    
    # Limpiar memoria existente
    memory_file = f"memorias/memory_{user_id}.json"
    if os.path.exists(memory_file):
        os.remove(memory_file)
        print(f"🗑️ Memoria eliminada: {memory_file}")
    
    print(f"\n👤 Usuario de prueba: {user_id}")
    print(f"📱 Número: {user_number}")
    
    # PASO 1: Usuario envía hashtags de anuncio (primera interacción)
    print(f"\n{'='*60}")
    print("PASO 1: Usuario envía hashtags de anuncio")
    print("="*60)
    
    webhook_data_1 = {
        'From': f"whatsapp:{user_number}",
        'Body': '#Experto_IA_GPT_Gemini #ADSIM_05',
        'MessageSid': 'test_msg_1',
        'To': 'whatsapp:+1234567890'
    }
    
    result_1 = await processor.execute(webhook_data_1)
    print(f"\n✅ Resultado PASO 1: {result_1['processing_type']}")
    
    # PASO 2: Usuario acepta privacidad
    print(f"\n{'='*60}")
    print("PASO 2: Usuario acepta privacidad")
    print("="*60)
    
    webhook_data_2 = {
        'From': f"whatsapp:{user_number}",
        'Body': 'Acepto',
        'MessageSid': 'test_msg_2',
        'To': 'whatsapp:+1234567890'
    }
    
    result_2 = await processor.execute(webhook_data_2)
    print(f"\n✅ Resultado PASO 2: {result_2['processing_type']}")
    
    # PASO 3: Usuario da nombre
    print(f"\n{'='*60}")
    print("PASO 3: Usuario da nombre")
    print("="*60)
    
    webhook_data_3 = {
        'From': f"whatsapp:{user_number}",
        'Body': 'Gael',
        'MessageSid': 'test_msg_3',
        'To': 'whatsapp:+1234567890'
    }
    
    result_3 = await processor.execute(webhook_data_3)
    print(f"\n✅ Resultado PASO 3: {result_3['processing_type']}")
    
    # PASO 4: Usuario da rol
    print(f"\n{'='*60}")
    print("PASO 4: Usuario da rol")
    print("="*60)
    
    webhook_data_4 = {
        'From': f"whatsapp:{user_number}",
        'Body': 'Marketing',
        'MessageSid': 'test_msg_4',
        'To': 'whatsapp:+1234567890'
    }
    
    result_4 = await processor.execute(webhook_data_4)
    print(f"\n✅ Resultado PASO 4: {result_4['processing_type']}")
    
    # Verificar si se activó el flujo de anuncios automáticamente
    if result_4.get('ad_flow_activated'):
        print(f"\n🎉 ¡ÉXITO! Flujo de anuncios activado automáticamente")
    else:
        print(f"\n❌ El flujo de anuncios NO se activó automáticamente")
    
    # Mostrar memoria final
    final_memory = memory_use_case.get_user_memory(user_id)
    print(f"\n📋 Memoria final:")
    print(f"   Stage: {final_memory.stage}")
    print(f"   Privacy accepted: {final_memory.privacy_accepted}")
    print(f"   Name: {final_memory.name}")
    print(f"   Role: {final_memory.role}")
    print(f"   Original message: {final_memory.original_message_body}")
    
    print(f"\n{'='*60}")
    print("PRUEBA COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_complete_flow()) 