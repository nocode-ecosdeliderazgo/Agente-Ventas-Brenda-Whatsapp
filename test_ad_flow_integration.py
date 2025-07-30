#!/usr/bin/env python3
"""
Script de prueba específico para verificar la integración del flujo de anuncios
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.application.usecases.process_incoming_message import ProcessIncomingMessageUseCase
from app.application.usecases.detect_ad_hashtags_use_case import DetectAdHashtagsUseCase
from app.application.usecases.process_ad_flow_use_case import ProcessAdFlowUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.database.client import DatabaseClient
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.application.usecases.tool_activation_use_case import ToolActivationUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from memory.lead_memory import MemoryManager

def debug_print(message: str, function_name: str = ""):
    """Print de debug visual"""
    print(f"🔍 [{function_name}] {message}")

class ConsoleTwilioClient(TwilioWhatsAppClient):
    """Cliente Twilio simulado para consola"""
    
    def __init__(self):
        self.sent_messages = []
        
    async def send_message(self, message):
        """Simula el envío de mensaje via Twilio"""
        message_data = {
            'to_number': message.to_number,
            'body': message.body,
            'message_type': message.message_type.value,
            'timestamp': '2024-07-29T18:30:00Z',
            'message_sid': f"console_sim_{len(self.sent_messages)}"
        }
        
        self.sent_messages.append(message_data)
        
        print(f"📱 [TWILIO SIMULADO] Enviando mensaje:")
        print(f"   Para: {message.to_number}")
        print(f"   Mensaje: {message.body}")
        print(f"   SID: {message_data['message_sid']}")
        
        return {
            'success': True,
            'message_sid': message_data['message_sid'],
            'error': None
        }

class AdFlowIntegrationTester:
    """Clase para testing de integración del flujo de anuncios"""
    
    def __init__(self):
        self.twilio_client = ConsoleTwilioClient()
        self.memory_manager = MemoryManager(memory_dir="memorias")
        self.memory_use_case = ManageUserMemoryUseCase(self.memory_manager)
        self.privacy_flow_use_case = PrivacyFlowUseCase(self.memory_use_case, self.twilio_client)
        self.openai_client = OpenAIClient()
        self.db_client = DatabaseClient()
        self.course_repository = CourseRepository()
        self.intent_analyzer = AnalyzeMessageIntentUseCase(self.openai_client, self.memory_use_case)
        self.course_query_use_case = QueryCourseInformationUseCase()
        self.intelligent_response_use_case = GenerateIntelligentResponseUseCase(
            self.intent_analyzer, 
            self.twilio_client, 
            self.openai_client, 
            self.db_client,
            self.course_repository,
            self.course_query_use_case
        )
        self.tool_activation_use_case = ToolActivationUseCase()
        self.detect_ad_hashtags_use_case = DetectAdHashtagsUseCase()
        self.process_ad_flow_use_case = ProcessAdFlowUseCase(
            self.memory_use_case, 
            self.privacy_flow_use_case, 
            self.course_query_use_case
        )
        self.process_message_use_case = ProcessIncomingMessageUseCase(
            self.twilio_client, 
            self.memory_use_case, 
            self.intelligent_response_use_case, 
            self.privacy_flow_use_case, 
            self.tool_activation_use_case,
            detect_ad_hashtags_use_case=self.detect_ad_hashtags_use_case,
            process_ad_flow_use_case=self.process_ad_flow_use_case
        )
    
    async def test_hashtag_detection(self, message_text: str):
        """Test de detección de hashtags"""
        debug_print(f"🔍 TESTING DETECCIÓN DE HASHTAGS", "HASHTAG_TEST")
        debug_print(f"📨 Mensaje: '{message_text}'", "HASHTAG_TEST")
        
        result = await self.detect_ad_hashtags_use_case.execute(message_text)
        
        print(f"\n📊 RESULTADO DETECCIÓN:")
        print(f"   is_ad: {result.get('is_ad')}")
        print(f"   course_hashtags: {result.get('course_hashtags')}")
        print(f"   campaign_hashtags: {result.get('campaign_hashtags')}")
        print(f"   course_id: {result.get('course_id')}")
        print(f"   campaign_name: {result.get('campaign_name')}")
        
        return result
    
    async def test_ad_flow_processing(self, message_text: str):
        """Test de procesamiento del flujo de anuncios"""
        debug_print(f"🔍 TESTING PROCESAMIENTO DE FLUJO DE ANUNCIOS", "AD_FLOW_TEST")
        
        # Crear datos del webhook
        webhook_data = {
            'MessageSid': 'test_ad_flow_sid',
            'From': 'whatsapp:+1234567890',
            'To': 'whatsapp:+0987654321',
            'Body': message_text,
            'AccountSid': 'test_account',
            'MessagingServiceSid': 'test_service'
        }
        
        # Procesar mensaje
        result = await self.process_message_use_case.execute(webhook_data)
        
        print(f"\n📊 RESULTADO PROCESAMIENTO:")
        print(f"   success: {result.get('success')}")
        print(f"   processed: {result.get('processed')}")
        print(f"   processing_type: {result.get('processing_type')}")
        print(f"   response_sent: {result.get('response_sent')}")
        print(f"   response_text: {result.get('response_text', '')[:100]}...")
        print(f"   ad_flow_completed: {result.get('ad_flow_completed')}")
        
        return result
    
    async def test_full_integration(self, message_text: str):
        """Test de integración completa"""
        debug_print(f"🔍 TESTING INTEGRACIÓN COMPLETA", "FULL_TEST")
        
        print(f"\n📨 MENSAJE DE PRUEBA: '{message_text}'")
        
        # Paso 1: Detección de hashtags
        print("\n" + "="*50)
        print("PASO 1: DETECCIÓN DE HASHTAGS")
        hashtag_result = await self.test_hashtag_detection(message_text)
        
        # Paso 2: Procesamiento completo
        print("\n" + "="*50)
        print("PASO 2: PROCESAMIENTO COMPLETO")
        processing_result = await self.test_ad_flow_processing(message_text)
        
        # Análisis final
        print("\n" + "="*50)
        print("ANÁLISIS FINAL:")
        
        if hashtag_result.get('is_ad'):
            print("✅ Hashtags detectados correctamente")
        else:
            print("❌ Hashtags NO detectados")
        
        if processing_result.get('processing_type') == 'ad_flow':
            print("✅ Flujo de anuncios activado correctamente")
        else:
            print(f"❌ Flujo de anuncios NO activado (tipo: {processing_result.get('processing_type')})")
        
        if processing_result.get('ad_flow_completed'):
            print("✅ Flujo de anuncios completado")
        else:
            print("❌ Flujo de anuncios NO completado")
        
        return {
            'hashtag_detection': hashtag_result,
            'processing': processing_result
        }

async def main():
    """Función principal"""
    print("🔍 TEST DE INTEGRACIÓN DEL FLUJO DE ANUNCIOS")
    print("="*60)
    
    tester = AdFlowIntegrationTester()
    
    # Test con mensaje que debería activar el flujo
    test_message = "#Experto_IA_GPT_Gemini #ADSIM_05"
    
    result = await tester.test_full_integration(test_message)
    
    print("\n" + "="*60)
    print("🎯 TEST COMPLETADO")

if __name__ == "__main__":
    asyncio.run(main()) 