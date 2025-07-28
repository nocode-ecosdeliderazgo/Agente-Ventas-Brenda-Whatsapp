#!/usr/bin/env python3
"""
Script para probar el sistema inteligente completo del bot Brenda.
Incluye análisis de intención, memoria y respuestas contextualizadas.
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
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.domain.entities.message import IncomingMessage, MessageType
from memory.lead_memory import MemoryManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_intelligent_system():
    """Prueba completa del sistema inteligente."""
    print("🤖 Iniciando pruebas del sistema inteligente...")
    
    try:
        # 1. Verificar configuración
        print("\n1️⃣ Verificando configuración...")
        if not settings.openai_api_key:
            print("❌ OPENAI_API_KEY no está configurada")
            print("📝 Agrega tu clave de OpenAI al archivo .env")
            return False
        
        print(f"✅ OpenAI API Key configurada: {settings.openai_api_key[:10]}...")
        print(f"✅ Twilio configurado: {settings.twilio_phone_number}")
        
        # 2. Inicializar componentes
        print("\n2️⃣ Inicializando componentes...")
        
        # Crear clientes
        openai_client = OpenAIClient()
        twilio_client = TwilioWhatsAppClient()
        
        # Crear manager de memoria
        memory_manager = MemoryManager(memory_dir="test_intelligent_memorias")
        memory_use_case = ManageUserMemoryUseCase(memory_manager)
        
        # Crear analizador de intención
        intent_analyzer = AnalyzeMessageIntentUseCase(openai_client, memory_use_case)
        
        # Crear generador de respuestas
        response_generator = GenerateIntelligentResponseUseCase(intent_analyzer, twilio_client)
        
        print("✅ Todos los componentes inicializados correctamente")
        
        # 3. Preparar usuario de prueba
        print("\n3️⃣ Preparando usuario de prueba...")
        test_user_id = "test123456789"
        test_phone = "+1234567890"
        
        # 4. Ejecutar flujo de conversación de prueba
        print("\n4️⃣ Ejecutando flujo de conversación de prueba...")
        
        # Simular conversación paso a paso
        conversation_flow = [
            "Hola",
            "Mi nombre es Ana García",
            "Trabajo en marketing digital",
            "¿Tienen recursos gratuitos?",
            "Me interesa automatizar la creación de contenido",
            "¿Cuál es el precio del curso?",
            "Me gustaría hablar con un asesor"
        ]
        
        for i, message_text in enumerate(conversation_flow, 1):
            print(f"\n--- Mensaje {i}: '{message_text}' ---")
            
            # Crear mensaje simulado
            mock_message = IncomingMessage(
                message_sid=f"TEST{i}",
                from_number=test_phone,
                to_number=settings.twilio_phone_number,
                body=message_text,
                message_type=MessageType.TEXT,
                timestamp=datetime.now(),
                raw_data={"From": f"whatsapp:{test_phone}"}
            )
            
            # Procesar mensaje con sistema inteligente
            try:
                result = await response_generator.execute(
                    test_user_id, mock_message
                )
                
                # Mostrar resultados
                if result['success']:
                    print(f"✅ Mensaje procesado exitosamente")
                    print(f"🔍 Intención detectada: {result.get('intent_analysis', {}).get('category', 'N/A')}")
                    if result.get('extracted_info'):
                        extracted = result['extracted_info']
                        if extracted.get('name'):
                            print(f"👤 Nombre extraído: {extracted['name']}")
                        if extracted.get('role'):
                            print(f"💼 Rol extraído: {extracted['role']}")
                        if extracted.get('interests'):
                            print(f"🎯 Intereses: {', '.join(extracted['interests'])}")
                    
                    print(f"💬 Respuesta generada:")
                    print(f"    {result['response_text'][:150]}{'...' if len(result['response_text']) > 150 else ''}")
                    
                    # Simular delay entre mensajes
                    await asyncio.sleep(1)
                else:
                    print(f"❌ Error procesando mensaje: {result.get('error', 'Error desconocido')}")
                    
            except Exception as e:
                print(f"💥 Error en mensaje {i}: {e}")
        
        # 5. Verificar memoria del usuario
        print(f"\n5️⃣ Verificando memoria del usuario...")
        final_memory = memory_use_case.get_user_memory(test_user_id)
        
        print(f"👤 Nombre: {final_memory.name}")
        print(f"💼 Rol: {final_memory.role}")
        print(f"📊 Score: {final_memory.lead_score}/100")
        print(f"🔄 Interacciones: {final_memory.interaction_count}")
        print(f"🎯 Intereses: {final_memory.interests}")
        print(f"💭 Pain points: {final_memory.pain_points}")
        print(f"📝 Historial: {len(final_memory.message_history)} mensajes")
        
        # 6. Probar análisis directo de intención
        print(f"\n6️⃣ Probando análisis directo de intención...")
        
        test_messages = [
            ("¿Cuánto cuesta?", "OBJECTION_PRICE"),
            ("Quiero recursos gratis", "FREE_RESOURCES"),
            ("Necesito automatizar reportes", "AUTOMATION_NEED"),
            ("Quiero hablar con alguien", "CONTACT_REQUEST")
        ]
        
        for msg, expected in test_messages:
            try:
                intent_result = await openai_client.analyze_intent(
                    msg, final_memory
                )
                detected = intent_result.get('category', 'UNKNOWN')
                confidence = intent_result.get('confidence', 0)
                
                status = "✅" if detected == expected else "⚠️"
                print(f"{status} '{msg}' → {detected} (conf: {confidence:.2f}) [esperado: {expected}]")
                
            except Exception as e:
                print(f"❌ Error analizando '{msg}': {e}")
        
        print(f"\n🎉 ¡Pruebas del sistema inteligente completadas!")
        print(f"📁 Archivos de memoria en: test_intelligent_memorias/")
        
        return True
        
    except Exception as e:
        print(f"💥 Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_files():
    """Limpia archivos de prueba."""
    import shutil
    test_dir = "test_intelligent_memorias"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"🧹 Archivos de prueba eliminados: {test_dir}/")

async def main():
    """Función principal."""
    try:
        success = await test_intelligent_system()
        
        if success:
            # Preguntar si limpiar archivos de prueba
            try:
                response = input("\n¿Eliminar archivos de prueba? (y/N): ").lower().strip()
                if response == 'y':
                    cleanup_test_files()
                else:
                    print("📁 Archivos de prueba conservados en test_intelligent_memorias/")
            except EOFError:
                # Si no se puede leer input (ej. en CI), conservar archivos
                print("📁 Archivos de prueba conservados en test_intelligent_memorias/")
        
    except KeyboardInterrupt:
        print("\n🛑 Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())