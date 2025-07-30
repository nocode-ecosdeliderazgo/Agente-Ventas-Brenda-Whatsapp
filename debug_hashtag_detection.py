#!/usr/bin/env python3
"""
Script de debug para verificar la detección de hashtags y flujo de anuncios
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.application.usecases.detect_ad_hashtags_use_case import DetectAdHashtagsUseCase
from app.application.usecases.process_ad_flow_use_case import ProcessAdFlowUseCase
from app.config.campaign_config import (
    get_course_id_from_hashtag, 
    get_campaign_name_from_hashtag,
    is_course_hashtag,
    is_campaign_hashtag,
    COURSE_HASHTAG_MAPPING,
    CAMPAIGN_HASHTAG_MAPPING
)

def debug_print(message: str, function_name: str = ""):
    """Print de debug visual"""
    print(f"🔍 [{function_name}] {message}")

class HashtagDebugger:
    """Clase para debug de detección de hashtags"""
    
    def __init__(self):
        self.detect_ad_hashtags_use_case = DetectAdHashtagsUseCase()
    
    def debug_config_mappings(self):
        """Debug de mapeos de configuración"""
        debug_print("🔧 DEBUGGING CONFIGURACIÓN DE HASHTAGS", "CONFIG")
        
        print("\n📋 COURSE_HASHTAG_MAPPING:")
        for hashtag, course_id in COURSE_HASHTAG_MAPPING.items():
            print(f"   '{hashtag}' → '{course_id}'")
        
        print("\n📋 CAMPAIGN_HASHTAG_MAPPING:")
        for hashtag, campaign_name in CAMPAIGN_HASHTAG_MAPPING.items():
            print(f"   '{hashtag}' → '{campaign_name}'")
        
        print("\n🔍 FUNCIONES DE CONFIGURACIÓN:")
        print(f"   is_course_hashtag('Experto_IA_GPT_Gemini'): {is_course_hashtag('Experto_IA_GPT_Gemini')}")
        print(f"   is_campaign_hashtag('ADSIM_05'): {is_campaign_hashtag('ADSIM_05')}")
        print(f"   get_course_id_from_hashtag('Experto_IA_GPT_Gemini'): {get_course_id_from_hashtag('Experto_IA_GPT_Gemini')}")
        print(f"   get_campaign_name_from_hashtag('ADSIM_05'): {get_campaign_name_from_hashtag('ADSIM_05')}")
    
    async def debug_hashtag_detection(self, message_text: str):
        """Debug de detección de hashtags"""
        debug_print(f"🔍 DEBUGGING DETECCIÓN DE HASHTAGS", "DETECTION")
        debug_print(f"📨 Mensaje: '{message_text}'", "DETECTION")
        
        # Ejecutar detección
        result = await self.detect_ad_hashtags_use_case.execute(message_text)
        
        print(f"\n📊 RESULTADO DE DETECCIÓN:")
        print(f"   is_ad: {result.get('is_ad')}")
        print(f"   course_hashtags: {result.get('course_hashtags')}")
        print(f"   campaign_hashtags: {result.get('campaign_hashtags')}")
        print(f"   all_hashtags: {result.get('all_hashtags')}")
        print(f"   course_id: {result.get('course_id')}")
        print(f"   campaign_name: {result.get('campaign_name')}")
        
        if result.get('error'):
            print(f"   ❌ ERROR: {result.get('error')}")
        
        return result
    
    def debug_hashtag_extraction(self, message_text: str):
        """Debug de extracción de hashtags"""
        debug_print(f"🔍 DEBUGGING EXTRACCIÓN DE HASHTAGS", "EXTRACTION")
        
        # Extraer hashtags usando regex
        import re
        hashtag_pattern = r'#([a-zA-Z0-9_]+)'
        hashtags = re.findall(hashtag_pattern, message_text)
        
        print(f"📨 Mensaje: '{message_text}'")
        print(f"🔍 Hashtags extraídos: {hashtags}")
        
        for hashtag in hashtags:
            print(f"\n🔍 Analizando hashtag: '{hashtag}'")
            print(f"   is_course_hashtag: {is_course_hashtag(hashtag)}")
            print(f"   is_campaign_hashtag: {is_campaign_hashtag(hashtag)}")
            print(f"   get_course_id: {get_course_id_from_hashtag(hashtag)}")
            print(f"   get_campaign_name: {get_campaign_name_from_hashtag(hashtag)}")
    
    async def debug_ad_flow_activation(self, message_text: str):
        """Debug de activación del flujo de anuncios"""
        debug_print(f"🔍 DEBUGGING ACTIVACIÓN DE FLUJO DE ANUNCIOS", "AD_FLOW")
        
        # Simular datos del webhook
        webhook_data = {
            'MessageSid': 'test_debug_sid',
            'From': 'whatsapp:+1234567890',
            'To': 'whatsapp:+0987654321',
            'Body': message_text,
            'AccountSid': 'test_account',
            'MessagingServiceSid': 'test_service'
        }
        
        # Detectar hashtags
        hashtags_info = await self.detect_ad_hashtags_use_case.execute(message_text)
        
        print(f"\n📊 INFORMACIÓN DE HASHTAGS:")
        print(f"   is_ad: {hashtags_info.get('is_ad')}")
        print(f"   course_id: {hashtags_info.get('course_id')}")
        print(f"   campaign_name: {hashtags_info.get('campaign_name')}")
        
        if hashtags_info.get('is_ad'):
            debug_print("✅ ANUNCIO DETECTADO - Debería activar flujo de anuncios", "AD_FLOW")
        else:
            debug_print("❌ NO SE DETECTÓ ANUNCIO - Verificar configuración", "AD_FLOW")
        
        return hashtags_info

async def main():
    """Función principal"""
    print("🔍 DEBUG DE DETECCIÓN DE HASHTAGS Y FLUJO DE ANUNCIOS")
    print("="*60)
    
    debugger = HashtagDebugger()
    
    # Debug de configuración
    debugger.debug_config_mappings()
    
    print("\n" + "="*60)
    
    # Mensaje de prueba
    test_message = "#Experto_IA_GPT_Gemini #ADSIM_05"
    
    # Debug de extracción
    debugger.debug_hashtag_extraction(test_message)
    
    print("\n" + "="*60)
    
    # Debug de detección completa
    await debugger.debug_hashtag_detection(test_message)
    
    print("\n" + "="*60)
    
    # Debug de activación de flujo
    await debugger.debug_ad_flow_activation(test_message)
    
    print("\n" + "="*60)
    print("🎯 ANÁLISIS COMPLETO TERMINADO")

if __name__ == "__main__":
    asyncio.run(main()) 