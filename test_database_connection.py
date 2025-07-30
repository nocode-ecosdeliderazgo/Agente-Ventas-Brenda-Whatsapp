#!/usr/bin/env python3
"""
Script para verificar el estado de la conexión a la base de datos
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.client import DatabaseClient
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.config import settings

def debug_print(message: str, function_name: str = ""):
    """Print de debug visual"""
    print(f"🔍 [{function_name}] {message}")

class DatabaseConnectionTester:
    """Clase para testing de conexión a base de datos"""
    
    def __init__(self):
        self.db_client = DatabaseClient()
        # Usar la instancia global que ya está configurada
        from app.infrastructure.database.client import database_client
        self.course_repository = CourseRepository()
    
    async def test_database_connection(self):
        """Test de conexión básica a la base de datos"""
        debug_print("🔍 TESTING CONEXIÓN A BASE DE DATOS", "DB_CONNECTION")
        
        print(f"\n📋 CONFIGURACIÓN:")
        print(f"   database_url: {settings.database_url}")
        print(f"   app_environment: {settings.app_environment}")
        
        # Test 1: Conexión básica
        print(f"\n🔌 PASO 1: CONEXIÓN BÁSICA")
        connection_success = await self.db_client.connect()
        
        if connection_success:
            print("✅ Conexión establecida correctamente")
        else:
            print("❌ Error estableciendo conexión")
            return False
        
        # Test 2: Health check
        print(f"\n🏥 PASO 2: HEALTH CHECK")
        health_check = await self.db_client.health_check()
        
        if health_check:
            print("✅ Health check exitoso")
        else:
            print("❌ Health check falló")
            return False
        
        # Test 3: Query simple
        print(f"\n📊 PASO 3: QUERY SIMPLE")
        try:
            result = await self.db_client.execute_query("SELECT 1 as test")
            if result and len(result) > 0:
                print(f"✅ Query simple exitosa: {result}")
            else:
                print("❌ Query simple falló")
                return False
        except Exception as e:
            print(f"❌ Error en query simple: {e}")
            return False
        
        # Test 4: Query de cursos
        print(f"\n📚 PASO 4: QUERY DE CURSOS")
        try:
            result = await self.db_client.execute_query("SELECT * FROM ai_courses LIMIT 5")
            if result:
                print(f"✅ Query de cursos exitosa: {len(result)} cursos encontrados")
                for course in result:
                    print(f"   - ID: {course.get('id_course')}, Nombre: {course.get('name')}")
            else:
                print("❌ Query de cursos falló")
                return False
        except Exception as e:
            print(f"❌ Error en query de cursos: {e}")
            return False
        
        # Test 5: CourseRepository
        print(f"\n🔧 PASO 5: COURSE REPOSITORY")
        try:
            course = await self.course_repository.get_course_by_id("11111111-1111-1111-1111-111111111111")
            if course:
                print(f"✅ CourseRepository funcionando: {course.name}")
            else:
                print("❌ CourseRepository no encontró el curso")
                return False
        except Exception as e:
            print(f"❌ Error en CourseRepository: {e}")
            return False
        
        return True
    
    async def test_ad_flow_database_integration(self):
        """Test de integración de base de datos en flujo de anuncios"""
        debug_print("🔍 TESTING INTEGRACIÓN DE BD EN FLUJO DE ANUNCIOS", "AD_FLOW_DB")
        
        from app.application.usecases.process_ad_flow_use_case import ProcessAdFlowUseCase
        from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
        from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
        from app.application.usecases.query_course_information import QueryCourseInformationUseCase
        from memory.lead_memory import MemoryManager
        
        # Inicializar componentes
        memory_manager = MemoryManager(memory_dir="memorias")
        memory_use_case = ManageUserMemoryUseCase(memory_manager)
        privacy_flow_use_case = PrivacyFlowUseCase(memory_use_case, None)
        course_query_use_case = QueryCourseInformationUseCase()
        
        process_ad_flow_use_case = ProcessAdFlowUseCase(
            memory_use_case, 
            privacy_flow_use_case, 
            course_query_use_case
        )
        
        # Simular datos de hashtags
        hashtags_info = {
            'is_ad': True,
            'course_id': '11111111-1111-1111-1111-111111111111',
            'campaign_name': 'facebook_campaign_2025'
        }
        
        # Simular datos de webhook
        webhook_data = {
            'MessageSid': 'test_db_sid',
            'From': 'whatsapp:+1234567890',
            'To': 'whatsapp:+0987654321',
            'Body': '#Experto_IA_GPT_Gemini #ADSIM_05',
            'AccountSid': 'test_account',
            'MessagingServiceSid': 'test_service'
        }
        
        # Simular datos de usuario
        user_data = {
            'id': 'test_user_db',
            'first_name': 'Usuario Test'
        }
        
        print(f"\n📢 EJECUTANDO FLUJO DE ANUNCIOS CON BD")
        try:
            result = await process_ad_flow_use_case.execute(webhook_data, user_data, hashtags_info)
            
            print(f"📊 RESULTADO FLUJO DE ANUNCIOS:")
            print(f"   success: {result.get('success')}")
            print(f"   ad_flow_completed: {result.get('ad_flow_completed')}")
            print(f"   course_id: {result.get('course_id')}")
            print(f"   response_text: {result.get('response_text', '')[:100]}...")
            
            if result.get('success') and result.get('ad_flow_completed'):
                print("✅ Flujo de anuncios con BD funcionando correctamente")
                return True
            else:
                print("❌ Flujo de anuncios con BD falló")
                return False
                
        except Exception as e:
            print(f"❌ Error en flujo de anuncios con BD: {e}")
            return False

async def main():
    """Función principal"""
    print("🔍 TEST DE CONEXIÓN A BASE DE DATOS")
    print("="*60)
    
    tester = DatabaseConnectionTester()
    
    # Test de conexión básica
    print("\n" + "="*60)
    print("TEST 1: CONEXIÓN BÁSICA")
    print("="*60)
    
    connection_ok = await tester.test_database_connection()
    
    if connection_ok:
        print("\n" + "="*60)
        print("TEST 2: INTEGRACIÓN CON FLUJO DE ANUNCIOS")
        print("="*60)
        
        ad_flow_ok = await tester.test_ad_flow_database_integration()
        
        if ad_flow_ok:
            print("\n🎉 TODOS LOS TESTS EXITOSOS")
        else:
            print("\n❌ ERROR EN INTEGRACIÓN CON FLUJO DE ANUNCIOS")
    else:
        print("\n❌ ERROR EN CONEXIÓN BÁSICA")
    
    print("\n" + "="*60)
    print("🎯 TEST COMPLETADO")

if __name__ == "__main__":
    asyncio.run(main()) 