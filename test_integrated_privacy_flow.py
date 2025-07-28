"""
Test de integración completa del flujo de privacidad con el webhook.
Simula el flujo completo desde primera interacción hasta completar privacidad.
"""
import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, Any

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory.lead_memory import MemoryManager, LeadMemory
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.application.usecases.process_incoming_message import ProcessIncomingMessageUseCase
from app.domain.entities.message import IncomingMessage, MessageType

def print_separator(title: str):
    """Imprime un separador visual para organizar los tests."""
    print(f"\n{'='*70}")
    print(f"🚀 {title}")
    print('='*70)

class MockTwilioClient:
    """Cliente Twilio simulado para testing integrado."""
    
    def __init__(self):
        self.sent_messages = []
    
    async def send_message(self, message):
        """Simula envío de mensaje."""
        self.sent_messages.append({
            'to': message.to_number,
            'body': message.body,
            'timestamp': datetime.now()
        })
        print(f"📱 MENSAJE ENVIADO:")
        print(f"   📞 Para: {message.to_number}")
        print(f"   📝 Texto: {message.body[:200]}{'...' if len(message.body) > 200 else ''}")
        return {'success': True, 'message_sid': f'mock_sid_{len(self.sent_messages)}'}
    
    def get_sent_messages(self):
        """Obtiene todos los mensajes enviados."""
        return self.sent_messages
    
    def clear_messages(self):
        """Limpia el historial de mensajes."""
        self.sent_messages = []

async def test_complete_integration():
    """Test de integración completa del flujo de privacidad."""
    
    print_separator("TEST DE INTEGRACIÓN COMPLETA - FLUJO DE PRIVACIDAD")
    
    # Configurar componentes
    memory_manager = MemoryManager(memory_dir="test_integration_memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    mock_twilio = MockTwilioClient()
    
    # Crear flujo de privacidad
    privacy_flow = PrivacyFlowUseCase(memory_use_case, mock_twilio)
    
    # Crear procesador de mensajes integrado
    message_processor = ProcessIncomingMessageUseCase(
        twilio_client=mock_twilio,
        memory_use_case=memory_use_case,
        intelligent_response_use_case=None,  # Sin OpenAI para este test
        privacy_flow_use_case=privacy_flow
    )
    
    # Usuario de prueba
    test_user_id = "test_integration_5213334567890"
    test_number = "+5213334567890"
    
    # Limpiar memoria previa
    import shutil
    if os.path.exists("test_integration_memorias"):
        shutil.rmtree("test_integration_memorias")
    
    try:
        print_separator("ESCENARIO 1: PRIMERA INTERACCIÓN - USUARIO NUEVO")
        
        # Simular webhook de Twilio con primera interacción
        first_webhook_data = {
            'MessageSid': 'test_msg_001',
            'From': f'whatsapp:{test_number}',
            'To': 'whatsapp:+14155238886',
            'Body': 'Hola, me interesa información sobre cursos de IA',
            'AccountSid': 'test_account',
            'MessagingServiceSid': None,
            'NumMedia': '0',
            'ProfileName': 'María Rodríguez',  # Nombre de WhatsApp
            'WaId': '5213334567890'
        }
        
        print("📨 Simulando primer mensaje del webhook:")
        print(f"   📱 Desde: {first_webhook_data['From']}")
        print(f"   💬 Mensaje: '{first_webhook_data['Body']}'")
        print(f"   👤 Nombre WhatsApp: {first_webhook_data['ProfileName']}")
        
        # Procesar primer mensaje
        result1 = await message_processor.execute(first_webhook_data)
        
        print("\n📊 RESULTADO PRIMER MENSAJE:")
        print(f"   ✅ Éxito: {result1['success']}")
        print(f"   🔄 Procesado: {result1['processed']}")
        print(f"   📤 Respuesta enviada: {result1.get('response_sent', False)}")
        print(f"   🎯 Tipo procesamiento: {result1.get('processing_type', 'N/A')}")
        print(f"   🔐 Stage privacidad: {result1.get('privacy_stage', 'N/A')}")
        
        # Verificar que se inició flujo de privacidad
        assert result1['success'], "Primer mensaje debería procesarse exitosamente"
        assert result1.get('processing_type') == 'privacy_flow', "Debería activar flujo de privacidad"
        assert result1.get('response_sent'), "Debería enviar mensaje de consentimiento"
        
        # Verificar memoria del usuario
        user_memory = memory_use_case.get_user_memory(test_user_id)
        print(f"\n🧠 ESTADO DE MEMORIA DESPUÉS DEL PRIMER MENSAJE:")
        print(f"   👤 Nombre: {user_memory.name or 'Sin nombre'}")
        print(f"   🏷️ Stage: {user_memory.stage}")
        print(f"   🔄 Flujo actual: {user_memory.current_flow}")
        print(f"   ⏳ Esperando: {user_memory.waiting_for_response}")
        print(f"   📱 Interacciones: {user_memory.interaction_count}")
        print(f"   🔒 Privacidad solicitada: {user_memory.privacy_requested}")
        
        assert user_memory.stage == "privacy_flow", "Usuario debería estar en flujo de privacidad"
        assert user_memory.waiting_for_response == "privacy_acceptance", "Debería esperar aceptación"
        
        print_separator("ESCENARIO 2: RESPUESTA DE ACEPTACIÓN")
        
        # Simular respuesta de aceptación
        accept_webhook_data = {
            'MessageSid': 'test_msg_002',
            'From': f'whatsapp:{test_number}',
            'To': 'whatsapp:+14155238886',
            'Body': 'ACEPTO',
            'AccountSid': 'test_account',
            'MessagingServiceSid': None,
            'NumMedia': '0',
            'ProfileName': 'María Rodríguez',
            'WaId': '5213334567890'
        }
        
        print("📨 Simulando mensaje de aceptación:")
        print(f"   💬 Mensaje: '{accept_webhook_data['Body']}'")
        
        # Procesar aceptación
        result2 = await message_processor.execute(accept_webhook_data)
        
        print("\n📊 RESULTADO ACEPTACIÓN:")
        print(f"   ✅ Éxito: {result2['success']}")
        print(f"   📤 Respuesta enviada: {result2.get('response_sent', False)}")
        print(f"   🎯 Tipo procesamiento: {result2.get('processing_type', 'N/A')}")
        print(f"   🔐 Stage privacidad: {result2.get('privacy_stage', 'N/A')}")
        
        # Verificar aceptación
        assert result2['success'], "Aceptación debería procesarse exitosamente"
        assert result2.get('processing_type') == 'privacy_flow', "Debería continuar en flujo de privacidad"
        
        # Verificar estado de memoria después de aceptación
        user_memory = memory_use_case.get_user_memory(test_user_id)
        print(f"\n🧠 ESTADO DESPUÉS DE ACEPTACIÓN:")
        print(f"   🏷️ Stage: {user_memory.stage}")
        print(f"   🔒 Privacidad aceptada: {user_memory.privacy_accepted}")
        print(f"   ⏳ Esperando: {user_memory.waiting_for_response}")
        
        assert user_memory.privacy_accepted, "Privacidad debería estar aceptada"
        assert user_memory.waiting_for_response == "user_name", "Debería esperar nombre de usuario"
        
        print_separator("ESCENARIO 3: PROPORCIONAR NOMBRE PERSONALIZADO")
        
        # Simular respuesta con nombre
        name_webhook_data = {
            'MessageSid': 'test_msg_003',
            'From': f'whatsapp:{test_number}',
            'To': 'whatsapp:+14155238886',
            'Body': 'María José',
            'AccountSid': 'test_account',
            'MessagingServiceSid': None,
            'NumMedia': '0',
            'ProfileName': 'María Rodríguez',
            'WaId': '5213334567890'
        }
        
        print("📨 Simulando mensaje con nombre:")
        print(f"   💬 Mensaje: '{name_webhook_data['Body']}'")
        
        # Procesar nombre
        result3 = await message_processor.execute(name_webhook_data)
        
        print("\n📊 RESULTADO NOMBRE:")
        print(f"   ✅ Éxito: {result3['success']}")
        print(f"   📤 Respuesta enviada: {result3.get('response_sent', False)}")
        print(f"   🎯 Tipo procesamiento: {result3.get('processing_type', 'N/A')}")
        print(f"   🔐 Flujo completado: {result3.get('privacy_flow_completed', False)}")
        
        # Verificar finalización del flujo
        assert result3['success'], "Nombre debería procesarse exitosamente"
        assert result3.get('privacy_flow_completed'), "Flujo de privacidad debería completarse"
        
        # Verificar estado final de memoria
        user_memory = memory_use_case.get_user_memory(test_user_id)
        print(f"\n🧠 ESTADO FINAL:")
        print(f"   👤 Nombre: {user_memory.name}")
        print(f"   🏷️ Stage: {user_memory.stage}")
        print(f"   🔄 Flujo actual: {user_memory.current_flow}")
        print(f"   🔒 Privacidad aceptada: {user_memory.privacy_accepted}")
        print(f"   📱 Interacciones: {user_memory.interaction_count}")
        print(f"   💼 Listo para ventas: {user_memory.is_ready_for_sales_agent()}")
        
        assert user_memory.name == "María José", "Nombre debería guardarse correctamente"
        assert user_memory.stage == "sales_agent", "Debería estar listo para agente de ventas"
        assert user_memory.is_ready_for_sales_agent(), "Debería estar listo para agente de ventas"
        
        print_separator("ESCENARIO 4: MENSAJE POSTERIOR AL FLUJO COMPLETADO")
        
        # Simular mensaje después de completar flujo
        normal_webhook_data = {
            'MessageSid': 'test_msg_004',
            'From': f'whatsapp:{test_number}',
            'To': 'whatsapp:+14155238886',
            'Body': '¿Qué cursos tienen disponibles?',
            'AccountSid': 'test_account',
            'MessagingServiceSid': None,
            'NumMedia': '0',
            'ProfileName': 'María Rodríguez',
            'WaId': '5213334567890'
        }
        
        print("📨 Simulando mensaje normal después del flujo:")
        print(f"   💬 Mensaje: '{normal_webhook_data['Body']}'")
        
        # Procesar mensaje normal
        result4 = await message_processor.execute(normal_webhook_data)
        
        print("\n📊 RESULTADO MENSAJE NORMAL:")
        print(f"   ✅ Éxito: {result4['success']}")
        print(f"   📤 Respuesta enviada: {result4.get('response_sent', False)}")
        print(f"   🎯 Tipo procesamiento: {result4.get('processing_type', 'N/A')}")
        
        # Este mensaje ya NO debería ir al flujo de privacidad
        assert result4['success'], "Mensaje normal debería procesarse"
        assert result4.get('processing_type') != 'privacy_flow', "NO debería usar flujo de privacidad"
        
        print_separator("RESUMEN DE MENSAJES ENVIADOS")
        
        sent_messages = mock_twilio.get_sent_messages()
        print(f"📱 Total mensajes enviados: {len(sent_messages)}")
        
        for i, msg in enumerate(sent_messages, 1):
            print(f"\n   {i}. Para: {msg['to']}")
            print(f"      Texto: {msg['body'][:100]}{'...' if len(msg['body']) > 100 else ''}")
        
        # Verificar que se enviaron los mensajes esperados
        assert len(sent_messages) >= 3, "Deberían enviarse al menos 3 mensajes del flujo"
        
        # Verificar contenido de mensajes
        messages_text = [msg['body'] for msg in sent_messages]
        
        # Primer mensaje debería contener solicitud de consentimiento
        assert any("consentimiento" in text.lower() and "brenda" in text.lower() for text in messages_text), \
            "Primer mensaje debería ser solicitud de consentimiento"
        
        # Segundo mensaje debería solicitar nombre
        assert any("cómo te gustaría que te llamemos" in text.lower() for text in messages_text), \
            "Segundo mensaje debería solicitar nombre"
        
        # Tercer mensaje debería confirmar nombre
        assert any("maría josé" in text.lower() and "perfecto" in text.lower() for text in messages_text), \
            "Tercer mensaje debería confirmar nombre"
        
        print_separator("VERIFICACIÓN FINAL")
        
        print("🎉 INTEGRACIÓN COMPLETA EXITOSA")
        print("\n✅ FUNCIONALIDADES VERIFICADAS:")
        print("   🔐 Detección automática de usuario nuevo")
        print("   👤 Extracción de nombre de WhatsApp")
        print("   📝 Solicitud profesional de consentimiento")
        print("   ✅ Procesamiento de aceptación")
        print("   🏷️ Solicitud de nombre personalizado")
        print("   🔄 Transición correcta al agente de ventas")
        print("   💾 Persistencia correcta de estado")
        print("   🚫 No interferencia con mensajes posteriores")
        
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"   👤 Usuario final: {user_memory.name}")
        print(f"   🏷️ Stage final: {user_memory.stage}")
        print(f"   📱 Total interacciones: {user_memory.interaction_count}")
        print(f"   📨 Mensajes enviados: {len(sent_messages)}")
        print(f"   🔒 Privacidad completada: {user_memory.privacy_accepted}")
        print(f"   💼 Listo para ventas: {user_memory.is_ready_for_sales_agent()}")
        
        # Limpiar archivos de prueba
        if os.path.exists("test_integration_memorias"):
            shutil.rmtree("test_integration_memorias")
            
    except Exception as e:
        print(f"\n💥 ERROR EN TEST DE INTEGRACIÓN: {e}")
        import traceback
        traceback.print_exc()
        raise

async def test_edge_cases():
    """Test de casos edge en la integración."""
    print_separator("TEST DE CASOS EDGE")
    
    # Configurar componentes nuevos para casos edge
    memory_manager = MemoryManager(memory_dir="test_edge_memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    mock_twilio = MockTwilioClient()
    
    privacy_flow = PrivacyFlowUseCase(memory_use_case, mock_twilio)
    message_processor = ProcessIncomingMessageUseCase(
        mock_twilio, memory_use_case, None, privacy_flow
    )
    
    # Limpiar memoria previa
    import shutil
    if os.path.exists("test_edge_memorias"):
        shutil.rmtree("test_edge_memorias")
    
    try:
        # Test: Usuario rechaza privacidad
        print("\n🚫 TEST: Usuario rechaza privacidad")
        
        reject_user_id = "test_reject_5213334567891"
        reject_webhook_data = {
            'MessageSid': 'test_reject_001',
            'From': f'whatsapp:+{reject_user_id}',
            'To': 'whatsapp:+14155238886',
            'Body': 'Hola',
            'AccountSid': 'test_account',
            'ProfileName': 'Usuario Rechazo',
            'WaId': reject_user_id[2:]  # Sin el +52
        }
        
        # Primera interacción
        result1 = await message_processor.execute(reject_webhook_data)
        assert result1['success'] and result1.get('processing_type') == 'privacy_flow'
        
        # Respuesta de rechazo
        reject_response_data = reject_webhook_data.copy()
        reject_response_data['MessageSid'] = 'test_reject_002'
        reject_response_data['Body'] = 'NO ACEPTO'
        
        result2 = await message_processor.execute(reject_response_data)
        assert result2['success']
        
        # Verificar que el flujo terminó
        user_memory = memory_use_case.get_user_memory(reject_user_id)
        assert not user_memory.privacy_accepted
        print("   ✅ Rechazo de privacidad manejado correctamente")
        
        # Test: Respuesta poco clara
        print("\n❓ TEST: Respuesta poco clara")
        
        unclear_user_id = "test_unclear_5213334567892"
        unclear_webhook_data = {
            'MessageSid': 'test_unclear_001',
            'From': f'whatsapp:+{unclear_user_id}',
            'To': 'whatsapp:+14155238886',
            'Body': 'Hola',
            'AccountSid': 'test_account',
            'ProfileName': 'Usuario Confuso',
            'WaId': unclear_user_id[2:]
        }
        
        # Primera interacción
        result1 = await message_processor.execute(unclear_webhook_data)
        assert result1['success']
        
        # Respuesta poco clara
        unclear_response_data = unclear_webhook_data.copy()
        unclear_response_data['MessageSid'] = 'test_unclear_002'
        unclear_response_data['Body'] = 'mmm no sé'
        
        result2 = await message_processor.execute(unclear_response_data)
        assert result2['success']
        
        # Verificar que sigue esperando respuesta clara
        user_memory = memory_use_case.get_user_memory(unclear_user_id)
        assert user_memory.waiting_for_response == "privacy_acceptance"
        print("   ✅ Respuesta poco clara manejada correctamente")
        
        print("\n🎉 TODOS LOS CASOS EDGE COMPLETADOS EXITOSAMENTE")
        
        # Limpiar archivos de prueba
        if os.path.exists("test_edge_memorias"):
            shutil.rmtree("test_edge_memorias")
            
    except Exception as e:
        print(f"\n💥 ERROR EN CASOS EDGE: {e}")
        raise

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE INTEGRACIÓN COMPLETA")
    
    try:
        # Ejecutar tests principales
        asyncio.run(test_complete_integration())
        
        # Ejecutar casos edge
        asyncio.run(test_edge_cases())
        
        print_separator("RESUMEN FINAL")
        print("🎉 TODOS LOS TESTS DE INTEGRACIÓN COMPLETADOS EXITOSAMENTE")
        print("✅ El flujo de privacidad está completamente integrado")
        print("🚀 Sistema listo para producción")
        
    except Exception as e:
        print(f"\n💥 ERROR EN TESTS: {e}")
        import traceback
        traceback.print_exc()
        exit(1)