"""
Test específico para el flujo de consentimiento de privacidad.
Valida toda la interacción desde primera vez hasta completar el flujo.
"""
import sys
import os
import asyncio
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory.lead_memory import MemoryManager, LeadMemory
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.domain.entities.message import IncomingMessage, MessageType
from app.templates.privacy_flow_templates import PrivacyFlowTemplates

def print_separator(title: str):
    """Imprime un separador visual para organizar los tests."""
    print(f"\n{'='*60}")
    print(f"🔐 {title}")
    print('='*60)

def print_test_result(test_name: str, result: dict, success: bool):
    """Imprime el resultado de un test de manera organizada."""
    status = "✅ ÉXITO" if success else "❌ FALLO"
    print(f"\n📋 {test_name}: {status}")
    
    if success:
        print(f"   🎯 Stage: {result.get('stage', 'N/A')}")
        print(f"   📨 Mensaje enviado: {result.get('message_sent', False)}")
        print(f"   ⏳ Esperando: {result.get('waiting_for', 'N/A')}")
        if 'user_name' in result:
            print(f"   👤 Nombre: {result['user_name']}")
        if 'privacy_accepted' in result:
            print(f"   🔒 Privacidad: {result['privacy_accepted']}")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")

class MockTwilioClient:
    """Cliente Twilio simulado para testing."""
    
    def __init__(self):
        self.sent_messages = []
    
    async def send_message(self, message):
        """Simula envío de mensaje."""
        self.sent_messages.append({
            'to': message.to_number,
            'body': message.body,
            'timestamp': datetime.now()
        })
        print(f"📱 MENSAJE SIMULADO ENVIADO A {message.to_number}:")
        print(f"   📝 Contenido ({len(message.body)} chars): {message.body[:100]}{'...' if len(message.body) > 100 else ''}")
        return {'success': True, 'message_sid': f'mock_sid_{len(self.sent_messages)}'}
    
    def get_last_message(self):
        """Obtiene el último mensaje enviado."""
        return self.sent_messages[-1] if self.sent_messages else None
    
    def clear_messages(self):
        """Limpia el historial de mensajes."""
        self.sent_messages = []

async def test_privacy_flow_complete():
    """Test completo del flujo de privacidad."""
    
    print_separator("INICIANDO TEST COMPLETO DEL FLUJO DE PRIVACIDAD")
    
    # Configurar componentes
    memory_manager = MemoryManager(memory_dir="test_privacy_memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    mock_twilio = MockTwilioClient()
    privacy_flow = PrivacyFlowUseCase(memory_use_case, mock_twilio)
    
    # Usuario de prueba
    test_user_id = "test_privacy_5213334567890"
    test_number = "+5213334567890"
    
    # Limpiar memoria previa
    import shutil
    if os.path.exists("test_privacy_memorias"):
        shutil.rmtree("test_privacy_memorias")
    
    try:
        print_separator("PASO 1: PRIMERA INTERACCIÓN - INICIO DE FLUJO")
        
        # Simular primera interacción con metadatos de WhatsApp
        first_message = IncomingMessage(
            message_sid="test_msg_001",
            from_number=test_number,
            to_number="+14155238886",
            body="Hola, me interesa información sobre cursos de IA",
            timestamp=datetime.now(),
            raw_data={
                "ProfileName": "Juan García",  # Nombre de WhatsApp
                "From": f"whatsapp:{test_number}",
                "To": "whatsapp:+14155238886",
                "WaId": "5213334567890"
            },
            message_type=MessageType.TEXT
        )
        
        # Ejecutar flujo
        result = await privacy_flow.handle_privacy_flow(test_user_id, first_message)
        
        # Validar resultado
        success = (
            result['success'] and 
            result['in_privacy_flow'] and 
            result.get('stage') == 'privacy_consent_requested' and
            result.get('whatsapp_name_extracted') == "Juan García"
        )
        
        print_test_result("Inicio flujo privacidad", result, success)
        assert success, f"Error en inicio de flujo: {result}"
        
        # Verificar mensaje enviado
        last_message = mock_twilio.get_last_message()
        assert "Soy **Brenda**" in last_message['body'], "Mensaje de consentimiento incorrecto"
        assert "Juan García" in last_message['body'], "Nombre de WhatsApp no incluido"
        assert "ACEPTO" in last_message['body'], "Opciones de respuesta no incluidas"
        
        print_separator("PASO 2: RESPUESTA AFIRMATIVA DE PRIVACIDAD")
        
        # Simular respuesta de aceptación
        accept_message = IncomingMessage(
            message_sid="test_msg_002",
            from_number=test_number,
            to_number="+14155238886",
            body="ACEPTO",
            timestamp=datetime.now(),
            raw_data={"From": f"whatsapp:{test_number}"},
            message_type=MessageType.TEXT
        )
        
        # Ejecutar flujo
        result = await privacy_flow.handle_privacy_flow(test_user_id, accept_message)
        
        # Validar resultado
        success = (
            result['success'] and 
            result['in_privacy_flow'] and 
            result.get('stage') == 'name_requested' and
            result.get('privacy_accepted') == True
        )
        
        print_test_result("Aceptación privacidad", result, success)
        assert success, f"Error en aceptación: {result}"
        
        # Verificar mensaje de solicitud de nombre
        last_message = mock_twilio.get_last_message()
        assert "¿Cómo te gustaría que te llamemos?" in last_message['body'], "Solicitud de nombre incorrecta"
        
        print_separator("PASO 3: RESPUESTA CON NOMBRE PERSONALIZADO")
        
        # Simular respuesta con nombre
        name_message = IncomingMessage(
            message_sid="test_msg_003",
            from_number=test_number,
            to_number="+14155238886",
            body="Juan Carlos",
            timestamp=datetime.now(),
            raw_data={"From": f"whatsapp:{test_number}"},
            message_type=MessageType.TEXT
        )
        
        # Ejecutar flujo
        result = await privacy_flow.handle_privacy_flow(test_user_id, name_message)
        
        # Validar resultado
        success = (
            result['success'] and 
            not result['in_privacy_flow'] and  # Flujo completado
            result.get('stage') == 'privacy_flow_completed' and
            result.get('user_name') == 'Juan Carlos' and
            result.get('ready_for_sales_agent') == True
        )
        
        print_test_result("Nombre personalizado", result, success)
        assert success, f"Error con nombre: {result}"
        
        # Verificar mensaje de confirmación
        last_message = mock_twilio.get_last_message()
        assert "Juan Carlos" in last_message['body'], "Nombre no incluido en confirmación"
        assert "¿En qué puedo ayudarte hoy?" in last_message['body'], "Transición a agente no incluida"
        
        print_separator("PASO 4: VERIFICAR ESTADO FINAL DE MEMORIA")
        
        # Verificar estado final de la memoria
        final_memory = memory_use_case.get_user_memory(test_user_id)
        
        memory_checks = [
            (final_memory.name == "Juan Carlos", "Nombre guardado"),
            (final_memory.privacy_accepted == True, "Privacidad aceptada"),
            (final_memory.stage == "sales_agent", "Stage correcto"),
            (final_memory.current_flow == "sales_conversation", "Flujo correcto"),
            (final_memory.is_ready_for_sales_agent() == True, "Listo para agente"),
            (not final_memory.is_first_interaction(), "Ya no es primera interacción"),
            (not final_memory.needs_privacy_flow(), "Ya no necesita flujo de privacidad")
        ]
        
        print("\n📊 VERIFICACIÓN DE MEMORIA FINAL:")
        all_memory_ok = True
        for check, description in memory_checks:
            status = "✅" if check else "❌"
            print(f"   {status} {description}")
            if not check:
                all_memory_ok = False
        
        assert all_memory_ok, "Estado de memoria incorrecto"
        
        print_separator("PASO 5: TEST DE CASOS EDGE")
        
        # Test respuesta poco clara
        await test_unclear_privacy_response(privacy_flow, mock_twilio)
        
        # Test rechazo de privacidad  
        await test_privacy_rejection(privacy_flow, mock_twilio)
        
        # Test nombre inválido
        await test_invalid_name(privacy_flow, mock_twilio)
        
        print_separator("RESUMEN FINAL")
        
        print("🎉 TODOS LOS TESTS DEL FLUJO DE PRIVACIDAD COMPLETADOS")
        print("\n✅ FUNCIONALIDADES VALIDADAS:")
        print("   🔐 Inicio automático de flujo para usuarios nuevos")
        print("   👤 Extracción de nombre desde metadatos de WhatsApp")
        print("   📝 Solicitud profesional de consentimiento")
        print("   ✅ Procesamiento de aceptación de privacidad")
        print("   🏷️  Solicitud y validación de nombre personalizado")
        print("   🔄 Transición correcta al agente de ventas")
        print("   💾 Persistencia correcta de estado en memoria")
        print("   ⚠️  Manejo de casos edge (rechazos, respuestas poco claras)")
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   📱 Mensajes enviados: {len(mock_twilio.sent_messages)}")
        print(f"   👤 Usuario final: {final_memory.name}")
        print(f"   🏷️  Stage final: {final_memory.stage}")
        print(f"   📱 Interacciones: {final_memory.interaction_count}")
        
        # Limpiar archivos de prueba
        if os.path.exists("test_privacy_memorias"):
            shutil.rmtree("test_privacy_memorias")
            
    except Exception as e:
        print(f"\n💥 ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
        raise

async def test_unclear_privacy_response(privacy_flow, mock_twilio):
    """Test de respuesta poco clara en privacidad."""
    print("\n🔍 TEST: Respuesta poco clara de privacidad")
    
    # Configurar usuario en flujo de privacidad
    test_user = "test_unclear_5213334567891"
    memory_manager = MemoryManager(memory_dir="test_privacy_memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    
    # Simular usuario esperando respuesta de privacidad
    memory = memory_use_case.get_user_memory(test_user)
    memory = memory_use_case.start_privacy_flow(test_user)
    
    # Mensaje poco claro
    unclear_message = IncomingMessage(
        message_sid="test_unclear_001",
        from_number="+5213334567891",
        to_number="+14155238886",
        body="mmm no sé, tal vez",
        timestamp=datetime.now(),
        raw_data={"From": "whatsapp:+5213334567891"},
        message_type=MessageType.TEXT
    )
    
    privacy_flow_unclear = PrivacyFlowUseCase(memory_use_case, mock_twilio)
    result = await privacy_flow_unclear.handle_privacy_flow(test_user, unclear_message)
    
    success = (
        result['success'] and
        result['in_privacy_flow'] and
        result.get('stage') == 'privacy_clarification_requested'
    )
    
    print(f"   {'✅' if success else '❌'} Respuesta poco clara manejada correctamente")
    assert success, "Error manejando respuesta poco clara"

async def test_privacy_rejection(privacy_flow, mock_twilio):
    """Test de rechazo de privacidad."""
    print("\n🚫 TEST: Rechazo de privacidad")
    
    test_user = "test_reject_5213334567892"  
    memory_manager = MemoryManager(memory_dir="test_privacy_memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    
    # Simular usuario en flujo de privacidad
    memory = memory_use_case.start_privacy_flow(test_user)
    
    # Mensaje de rechazo
    reject_message = IncomingMessage(
        message_sid="test_reject_001",
        from_number="+5213334567892", 
        to_number="+14155238886",
        body="NO ACEPTO",
        timestamp=datetime.now(),
        raw_data={"From": "whatsapp:+5213334567892"},
        message_type=MessageType.TEXT
    )
    
    privacy_flow_reject = PrivacyFlowUseCase(memory_use_case, mock_twilio)
    result = await privacy_flow_reject.handle_privacy_flow(test_user, reject_message)
    
    success = (
        result['success'] and
        not result['in_privacy_flow'] and  # Flujo terminado
        result.get('privacy_accepted') == False and
        result.get('flow_completed') == True
    )
    
    print(f"   {'✅' if success else '❌'} Rechazo de privacidad manejado correctamente")
    assert success, "Error manejando rechazo de privacidad"

async def test_invalid_name(privacy_flow, mock_twilio):
    """Test de nombre inválido.""" 
    print("\n👤 TEST: Nombre inválido")
    
    test_user = "test_invalid_name_5213334567893"
    memory_manager = MemoryManager(memory_dir="test_privacy_memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    
    # Simular usuario esperando nombre
    memory = memory_use_case.start_privacy_flow(test_user)
    memory = memory_use_case.accept_privacy(test_user)
    memory_use_case.set_waiting_for_response(test_user, "user_name")
    
    # Mensaje con nombre inválido
    invalid_name_message = IncomingMessage(
        message_sid="test_invalid_001",
        from_number="+5213334567893",
        to_number="+14155238886", 
        body="no se",
        timestamp=datetime.now(),
        raw_data={"From": "whatsapp:+5213334567893"},
        message_type=MessageType.TEXT
    )
    
    privacy_flow_invalid = PrivacyFlowUseCase(memory_use_case, mock_twilio)
    result = await privacy_flow_invalid.handle_privacy_flow(test_user, invalid_name_message)
    
    success = (
        result['success'] and
        result['in_privacy_flow'] and
        result.get('stage') == 'name_reminder_sent'
    )
    
    print(f"   {'✅' if success else '❌'} Nombre inválido manejado correctamente")
    assert success, "Error manejando nombre inválido"

def test_template_utilities():
    """Test de utilidades de templates."""
    print_separator("TEST DE UTILIDADES DE TEMPLATES")
    
    templates = PrivacyFlowTemplates()
    
    # Test extracción de nombre de WhatsApp
    test_data = {
        "ProfileName": "María González",
        "From": "whatsapp:+5213334567890"
    }
    
    extracted_name = templates.get_whatsapp_display_name(test_data)
    assert extracted_name == "María González", f"Error extrayendo nombre: {extracted_name}"
    print("   ✅ Extracción de nombre de WhatsApp")
    
    # Test detección de respuesta de consentimiento
    test_cases = [
        ("ACEPTO", True),
        ("acepto", True),
        ("sí", True),
        ("ok", True),
        ("NO ACEPTO", False),
        ("no", False),
        ("tal vez", None),
        ("no sé", None)
    ]
    
    for text, expected in test_cases:
        result = templates.extract_consent_response(text)
        assert result == expected, f"Error con '{text}': esperado {expected}, obtenido {result}"
    
    print("   ✅ Detección de respuestas de consentimiento")
    
    # Test validación de nombres
    name_cases = [
        ("Juan", "Juan"),
        ("maría josé", "María José"),
        ("dr. garcía", "Dr. García"),
        ("no sé", None),
        ("", None),
        ("a", None)
    ]
    
    for text, expected in name_cases:
        result = templates.extract_user_name(text)
        assert result == expected, f"Error con nombre '{text}': esperado {expected}, obtenido {result}"
    
    print("   ✅ Validación de nombres de usuario")
    
    print("\n🎉 TODOS LOS TESTS DE UTILIDADES COMPLETADOS")

if __name__ == "__main__":
    print("🚀 INICIANDO SUITE DE TESTS DEL FLUJO DE PRIVACIDAD")
    
    try:
        # Ejecutar tests síncronos
        test_template_utilities()
        
        # Ejecutar tests asíncronos
        asyncio.run(test_privacy_flow_complete())
        
        print("\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("✅ El flujo de privacidad está listo para producción")
        
    except Exception as e:
        print(f"\n💥 ERROR EN TESTS: {e}")
        import traceback
        traceback.print_exc()
        exit(1)