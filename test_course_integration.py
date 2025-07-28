#!/usr/bin/env python3
"""
Script para probar la integración completa del sistema con base de datos de cursos.
Prueba el sistema inteligente con capacidades de consulta de cursos.
"""
import os
import sys
import asyncio
import logging
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.infrastructure.database.client import database_client
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.domain.entities.message import IncomingMessage, MessageType
from memory.lead_memory import MemoryManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_course_integration():
    """Prueba completa de la integración con base de datos de cursos."""
    print("🤖 Iniciando pruebas de integración con cursos...")
    
    try:
        # 1. Verificar configuración básica
        print("\n1️⃣ Verificando configuración básica...")
        if not settings.openai_api_key:
            print("❌ OPENAI_API_KEY no está configurada")
            return False
        
        if not settings.database_url:
            print("❌ DATABASE_URL no está configurada")
            print("📝 Agrega tu URL de PostgreSQL al archivo .env")
            print("   Ejemplo: DATABASE_URL=postgresql://user:password@localhost:5432/database")
            return False
        
        print(f"✅ OpenAI API Key configurada")
        print(f"✅ Database URL configurada")
        
        # 2. Inicializar componentes
        print("\n2️⃣ Inicializando componentes...")
        
        # Crear clientes básicos
        openai_client = OpenAIClient()
        twilio_client = TwilioWhatsAppClient()
        
        # Crear manager de memoria
        memory_manager = MemoryManager(memory_dir="test_course_memorias")
        memory_use_case = ManageUserMemoryUseCase(memory_manager)
        
        # Crear analizador de intención
        intent_analyzer = AnalyzeMessageIntentUseCase(openai_client, memory_use_case)
        
        print("✅ Componentes básicos inicializados")
        
        # 3. Probar conexión a base de datos
        print("\n3️⃣ Probando conexión a base de datos...")
        
        course_query_use_case = QueryCourseInformationUseCase()
        db_connected = await course_query_use_case.initialize()
        
        if not db_connected:
            print("❌ No se pudo conectar a la base de datos")
            print("📝 Verifica que PostgreSQL esté ejecutándose")
            print("📝 Verifica que la URL de conexión sea correcta")
            print("\n🔄 Continuando pruebas sin base de datos...")
            course_query_use_case = None
        else:
            print("✅ Conexión a PostgreSQL exitosa")
        
        # 4. Crear generador de respuestas inteligentes
        print("\n4️⃣ Creando generador de respuestas...")
        response_generator = GenerateIntelligentResponseUseCase(
            intent_analyzer, twilio_client, course_query_use_case
        )
        
        if course_query_use_case:
            print("✅ Sistema completo (IA + BD de cursos) inicializado")
        else:
            print("✅ Sistema básico (IA sin BD) inicializado")
        
        # 5. Probar consultas de cursos (si BD disponible)
        if course_query_use_case:
            print("\n5️⃣ Probando consultas de cursos...")
            await test_course_queries(course_query_use_case)
        else:
            print("\n5️⃣ ⏭️ Saltando pruebas de BD (no disponible)")
        
        # 6. Probar flujo de conversación mejorado
        print("\n6️⃣ Probando flujo de conversación mejorado...")
        await test_enhanced_conversation_flow(response_generator)
        
        print("\n🎉 ¡Pruebas de integración completadas!")
        return True
        
    except Exception as e:
        print(f"💥 Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_course_queries(course_query_use_case):
    """Prueba las consultas de cursos."""
    try:
        # Probar búsqueda por keyword
        print("  🔍 Probando búsqueda por keyword...")
        courses = await course_query_use_case.search_courses_by_keyword("IA", limit=2)
        print(f"    Cursos encontrados con 'IA': {len(courses)}")
        
        # Probar obtener opciones disponibles
        print("  📋 Probando opciones disponibles...")
        options = await course_query_use_case.get_available_options()
        print(f"    Niveles disponibles: {len(options.get('levels', []))}")
        print(f"    Modalidades disponibles: {len(options.get('modalities', []))}")
        
        # Probar resumen del catálogo
        print("  📊 Probando resumen del catálogo...")
        summary = await course_query_use_case.get_catalog_summary()
        print(f"    Estadísticas obtenidas: {bool(summary.get('statistics'))}")
        
        # Probar recomendaciones
        print("  💡 Probando recomendaciones...")
        recommendations = await course_query_use_case.get_recommended_courses(
            user_interests=["automatización", "marketing"],
            limit=2
        )
        print(f"    Cursos recomendados: {len(recommendations)}")
        
        if courses:
            print("  ✅ Sistema de cursos funcionando correctamente")
        else:
            print("  ⚠️ No se encontraron cursos (tabla vacía?)")
    
    except Exception as e:
        print(f"  ❌ Error en consultas de cursos: {e}")

async def test_enhanced_conversation_flow(response_generator):
    """Prueba el flujo de conversación mejorado."""
    try:
        test_user_id = "test_course_user_123"
        test_phone = "+1234567890"
        
        # Mensajes de prueba que deberían activar respuestas mejoradas
        test_messages = [
            ("Hola, soy María", "Presentación inicial"),
            ("Trabajo en marketing digital", "Información profesional"),
            ("¿Qué cursos tienen disponibles?", "Consulta directa de cursos"),
            ("Me interesa automatizar procesos", "Necesidad de automatización"),
            ("¿Cuál es el temario?", "Consulta de contenido"),
            ("Quiero hablar con un asesor", "Solicitud de contacto")
        ]
        
        for i, (message_text, description) in enumerate(test_messages, 1):
            print(f"\n  💬 Mensaje {i}: {description}")
            print(f"      📝 Texto: '{message_text}'")
            
            # Crear mensaje simulado
            mock_message = IncomingMessage(
                message_sid=f"TEST_COURSE_{i}",
                from_number=test_phone,
                to_number=settings.twilio_phone_number,
                body=message_text,
                message_type=MessageType.TEXT,
                timestamp=datetime.now(),
                raw_data={"From": f"whatsapp:{test_phone}"}
            )
            
            # Procesar mensaje
            try:
                result = await response_generator.execute(
                    test_user_id, mock_message
                )
                
                if result['success']:
                    intent = result.get('intent_analysis', {}).get('category', 'N/A')
                    response_preview = result['response_text'][:100] + "..." if len(result['response_text']) > 100 else result['response_text']
                    
                    print(f"      ✅ Procesado - Intención: {intent}")
                    print(f"      💭 Respuesta: {response_preview}")
                    
                    # Verificar si se usó información de cursos
                    if any(keyword in result['response_text'].lower() for keyword in ['curso', 'programa', 'modalidad', 'sesión']):
                        print(f"      🎯 Respuesta incluye información de cursos")
                    
                else:
                    print(f"      ❌ Error: {result.get('error', 'Error desconocido')}")
                
                # Pausa breve entre mensajes
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"      💥 Excepción: {e}")
        
        print("\n  ✅ Flujo de conversación mejorado completado")
        
    except Exception as e:
        print(f"  ❌ Error en flujo de conversación: {e}")

def cleanup_test_files():
    """Limpia archivos de prueba."""
    import shutil
    test_dirs = ["test_course_memorias"]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"🧹 Archivos de prueba eliminados: {test_dir}/")

async def main():
    """Función principal."""
    try:
        success = await test_course_integration()
        
        if success:
            # Preguntar si limpiar archivos de prueba
            try:
                response = input("\n¿Eliminar archivos de prueba? (y/N): ").lower().strip()
                if response == 'y':
                    cleanup_test_files()
                else:
                    print("📁 Archivos de prueba conservados")
            except EOFError:
                print("📁 Archivos de prueba conservados")
        
    except KeyboardInterrupt:
        print("\n🛑 Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())