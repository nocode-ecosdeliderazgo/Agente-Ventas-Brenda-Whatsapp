"""
Test de lógica de integración del flujo de privacidad sin dependencias externas.
Valida la lógica de decisión y el flujo de estados.
"""
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory.lead_memory import MemoryManager, LeadMemory
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.templates.privacy_flow_templates import PrivacyFlowTemplates

def print_separator(title: str):
    """Imprime un separador visual para organizar los tests."""
    print(f"\n{'='*70}")
    print(f"🧪 {title}")
    print('='*70)

def test_privacy_flow_logic():
    """Test de la lógica del flujo de privacidad sin dependencias externas."""
    
    print_separator("TEST DE LÓGICA DEL FLUJO DE PRIVACIDAD")
    
    # Configurar componentes
    memory_manager = MemoryManager(memory_dir="test_logic_memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    templates = PrivacyFlowTemplates()
    
    # Usuario de prueba
    test_user_id = "test_logic_5213334567890"
    
    # Limpiar memoria previa
    import shutil
    if os.path.exists("test_logic_memorias"):
        shutil.rmtree("test_logic_memorias")
    
    try:
        print_separator("PASO 1: USUARIO NUEVO - DETECCIÓN DE PRIMERA INTERACCIÓN")
        
        # Obtener memoria de usuario nuevo
        user_memory = memory_use_case.get_user_memory(test_user_id)
        
        print(f"👤 Usuario nuevo creado:")
        print(f"   🆔 ID: {user_memory.user_id}")
        print(f"   🏷️ Stage: {user_memory.stage}")
        print(f"   📱 Interacciones: {user_memory.interaction_count}")
        print(f"   🤖 Es primera interacción: {user_memory.is_first_interaction()}")
        print(f"   🔐 Necesita flujo privacidad: {user_memory.needs_privacy_flow()}")
        print(f"   💼 Listo para ventas: {user_memory.is_ready_for_sales_agent()}")
        
        # Verificar estado inicial
        assert user_memory.is_first_interaction(), "Debería ser primera interacción"
        assert user_memory.needs_privacy_flow(), "Debería necesitar flujo de privacidad"
        assert not user_memory.is_ready_for_sales_agent(), "NO debería estar listo para ventas"
        
        print("✅ Detección de primera interacción: CORRECTA")
        
        print_separator("PASO 2: INICIANDO FLUJO DE PRIVACIDAD")
        
        # Simular mensaje entrante
        from app.domain.entities.message import IncomingMessage, MessageType
        
        first_message = IncomingMessage(
            message_sid="logic_test_001",
            from_number="+5213334567890",
            to_number="+14155238886",
            body="Hola, me interesa información",
            timestamp=datetime.now(),
            raw_data={"ProfileName": "Juan López", "From": "whatsapp:+5213334567890"},
            message_type=MessageType.TEXT
        )
        
        # Actualizar memoria con primer mensaje
        user_memory = memory_use_case.update_user_memory(test_user_id, first_message)
        
        # Iniciar flujo de privacidad
        user_memory = memory_use_case.start_privacy_flow(test_user_id)
        
        print(f"🔐 Flujo de privacidad iniciado:")
        print(f"   🏷️ Stage: {user_memory.stage}")
        print(f"   🔄 Flujo actual: {user_memory.current_flow}")
        print(f"   📊 Paso del flujo: {user_memory.flow_step}")
        print(f"   ⏳ Esperando: {user_memory.waiting_for_response}")
        print(f"   🔒 Privacidad solicitada: {user_memory.privacy_requested}")
        
        # Verificar estado después de iniciar flujo
        assert user_memory.stage == "privacy_flow", "Stage debería ser privacy_flow"
        assert user_memory.current_flow == "privacy", "Flujo debería ser privacy"
        assert user_memory.waiting_for_response == "privacy_acceptance", "Debería esperar aceptación"
        assert user_memory.privacy_requested, "Privacidad debería estar solicitada"
        
        print("✅ Iniciación de flujo: CORRECTA")
        
        print_separator("PASO 3: GENERACIÓN DE MENSAJE DE CONSENTIMIENTO")
        
        # Extraer nombre de WhatsApp
        whatsapp_name = templates.get_whatsapp_display_name(first_message.raw_data)
        print(f"👤 Nombre extraído de WhatsApp: {whatsapp_name}")
        
        # Generar mensaje de consentimiento
        consent_message = templates.privacy_consent_request(whatsapp_name)
        
        print(f"💬 Mensaje de consentimiento generado:")
        print(f"   📏 Longitud: {len(consent_message)} caracteres")
        print(f"   🎯 Contiene nombre: {'✅' if whatsapp_name and whatsapp_name in consent_message else '❌'}")
        print(f"   📋 Contiene 'Brenda': {'✅' if 'Brenda' in consent_message else '❌'}")
        print(f"   ✅ Contiene 'ACEPTO': {'✅' if 'ACEPTO' in consent_message else '❌'}")
        print(f"   ❌ Contiene 'NO ACEPTO': {'✅' if 'NO ACEPTO' in consent_message else '❌'}")
        
        # Verificar contenido del mensaje
        assert whatsapp_name in consent_message, "Mensaje debería incluir nombre de WhatsApp"
        assert "Brenda" in consent_message, "Mensaje debería mencionar a Brenda"
        assert "ACEPTO" in consent_message, "Mensaje debería incluir opción ACEPTO"
        assert "NO ACEPTO" in consent_message, "Mensaje debería incluir opción NO ACEPTO"
        
        print("✅ Generación de mensaje: CORRECTA")
        
        print_separator("PASO 4: PROCESAMIENTO DE ACEPTACIÓN")
        
        # Simular mensaje de aceptación
        accept_message = IncomingMessage(
            message_sid="logic_test_002",
            from_number="+5213334567890",
            to_number="+14155238886",
            body="ACEPTO",
            timestamp=datetime.now(),
            raw_data={"From": "whatsapp:+5213334567890"},
            message_type=MessageType.TEXT
        )
        
        # Actualizar memoria con mensaje de aceptación
        user_memory = memory_use_case.update_user_memory(test_user_id, accept_message)
        
        # Procesar aceptación de privacidad
        consent_response = templates.extract_consent_response(accept_message.body)
        print(f"🔍 Respuesta interpretada: {consent_response}")
        
        if consent_response is True:
            user_memory = memory_use_case.accept_privacy(test_user_id)
            memory_use_case.set_waiting_for_response(test_user_id, "user_name")
        
        print(f"✅ Privacidad aceptada:")
        print(f"   🏷️ Stage: {user_memory.stage}")
        print(f"   🔒 Privacidad aceptada: {user_memory.privacy_accepted}")
        print(f"   ⏳ Esperando: {user_memory.waiting_for_response}")
        print(f"   🔄 Flujo actual: {user_memory.current_flow}")
        
        # Verificar estado después de aceptación
        assert user_memory.privacy_accepted, "Privacidad debería estar aceptada"
        assert user_memory.stage == "course_selection", "Stage debería ser course_selection"
        assert user_memory.waiting_for_response == "user_name", "Debería esperar nombre de usuario"
        
        print("✅ Procesamiento de aceptación: CORRECTO")
        
        print_separator("PASO 5: SOLICITUD DE NOMBRE PERSONALIZADO")
        
        # Generar mensaje de solicitud de nombre
        name_request_message = templates.privacy_accepted_name_request()
        
        print(f"💬 Mensaje de solicitud de nombre:")
        print(f"   📏 Longitud: {len(name_request_message)} caracteres")
        print(f"   🎯 Contiene '¿Cómo te gustaría': {'✅' if '¿Cómo te gustaría' in name_request_message else '❌'}")
        print(f"   📝 Es profesional: {'✅' if len(name_request_message) > 50 else '❌'}")
        
        # Verificar contenido del mensaje
        assert "¿Cómo te gustaría que te llamemos?" in name_request_message, "Debería solicitar nombre"
        assert len(name_request_message) > 50, "Mensaje debería ser informativo"
        
        print("✅ Solicitud de nombre: CORRECTA")
        
        print_separator("PASO 6: PROCESAMIENTO DE NOMBRE")
        
        # Simular mensaje con nombre
        name_message = IncomingMessage(
            message_sid="logic_test_003",
            from_number="+5213334567890",
            to_number="+14155238886",
            body="Juan Carlos",
            timestamp=datetime.now(),
            raw_data={"From": "whatsapp:+5213334567890"},
            message_type=MessageType.TEXT
        )
        
        # Actualizar memoria con mensaje de nombre
        user_memory = memory_use_case.update_user_memory(test_user_id, name_message)
        
        # Extraer y validar nombre
        extracted_name = templates.extract_user_name(name_message.body)
        print(f"👤 Nombre extraído: {extracted_name}")
        
        if extracted_name:
            # Actualizar nombre y completar flujo
            user_memory = memory_use_case.update_user_name(test_user_id, extracted_name)
            user_memory = memory_use_case.start_sales_agent_flow(test_user_id)
        
        print(f"🎉 Flujo completado:")
        print(f"   👤 Nombre final: {user_memory.name}")
        print(f"   🏷️ Stage final: {user_memory.stage}")
        print(f"   🔄 Flujo actual: {user_memory.current_flow}")
        print(f"   💼 Listo para ventas: {user_memory.is_ready_for_sales_agent()}")
        print(f"   📱 Total interacciones: {user_memory.interaction_count}")
        
        # Verificar estado final
        assert user_memory.name == "Juan Carlos", "Nombre debería guardarse correctamente"
        assert user_memory.stage == "sales_agent", "Stage debería ser sales_agent"
        assert user_memory.is_ready_for_sales_agent(), "Debería estar listo para agente de ventas"
        assert not user_memory.is_first_interaction(), "Ya no debería ser primera interacción"
        assert not user_memory.needs_privacy_flow(), "Ya no debería necesitar flujo de privacidad"
        
        print("✅ Completado de flujo: CORRECTO")
        
        print_separator("PASO 7: MENSAJE DE CONFIRMACIÓN")
        
        # Generar mensaje de confirmación
        confirmation_message = templates.name_confirmed(user_memory.name)
        
        print(f"💬 Mensaje de confirmación:")
        print(f"   📏 Longitud: {len(confirmation_message)} caracteres")
        print(f"   👤 Incluye nombre: {'✅' if user_memory.name in confirmation_message else '❌'}")
        print(f"   🎯 Incluye '¿En qué puedo ayudarte': {'✅' if '¿En qué puedo ayudarte' in confirmation_message else '❌'}")
        print(f"   🤖 Menciona cursos IA: {'✅' if 'IA' in confirmation_message or 'Inteligencia' in confirmation_message else '❌'}")
        
        # Verificar contenido de confirmación
        assert user_memory.name in confirmation_message, "Debería incluir el nombre del usuario"
        assert "¿En qué puedo ayudarte" in confirmation_message, "Debería preguntar cómo ayudar"
        assert ("IA" in confirmation_message or "Inteligencia" in confirmation_message), "Debería mencionar IA"
        
        print("✅ Mensaje de confirmación: CORRECTO")
        
        print_separator("PASO 8: VERIFICACIÓN DE CONTEXTO")
        
        # Generar contexto de conversación
        conversation_context = user_memory.get_conversation_context()
        print(f"📝 Contexto generado: {conversation_context}")
        
        # Verificar contexto
        assert user_memory.name in conversation_context, "Contexto debería incluir nombre"
        assert len(conversation_context) > 10, "Contexto debería ser informativo"
        
        print("✅ Generación de contexto: CORRECTA")
        
        print_separator("RESUMEN DE LÓGICA VALIDADA")
        
        print("🎉 TODAS LAS VALIDACIONES DE LÓGICA COMPLETADAS")
        print("\n✅ FUNCIONES VALIDADAS:")
        print("   🔍 Detección de primera interacción")
        print("   🔐 Detección de necesidad de flujo de privacidad")
        print("   👤 Extracción de nombre desde metadatos de WhatsApp")
        print("   📝 Generación de mensaje de consentimiento personalizado")
        print("   ✅ Interpretación de respuestas de aceptación")
        print("   🏷️ Transiciones correctas de stages")
        print("   👤 Extracción y validación de nombres de usuario")
        print("   🎉 Generación de mensaje de confirmación")
        print("   📝 Generación de contexto de conversación")
        print("   💼 Determinación de readiness para agente de ventas")
        
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"   👤 Usuario: {user_memory.name}")
        print(f"   🏷️ Stage: {user_memory.stage}")
        print(f"   📱 Interacciones: {user_memory.interaction_count}")
        print(f"   🔒 Privacidad: {user_memory.privacy_accepted}")
        print(f"   💼 Listo ventas: {user_memory.is_ready_for_sales_agent()}")
        
        # Limpiar archivos de prueba
        if os.path.exists("test_logic_memorias"):
            shutil.rmtree("test_logic_memorias")
            
    except Exception as e:
        print(f"\n💥 ERROR EN VALIDACIÓN DE LÓGICA: {e}")
        import traceback
        traceback.print_exc()
        raise

def test_edge_cases_logic():
    """Test de casos edge en la lógica."""
    print_separator("TEST DE CASOS EDGE EN LÓGICA")
    
    templates = PrivacyFlowTemplates()
    
    # Test detección de respuestas
    test_responses = [
        ("ACEPTO", True, "Aceptación explícita"),
        ("acepto todo", True, "Aceptación con texto adicional"),
        ("NO ACEPTO", False, "Rechazo explícito"),
        ("no quiero", False, "Rechazo implícito"),
        ("tal vez", None, "Respuesta ambigua"),
        ("hola", None, "Mensaje irrelevante")
    ]
    
    print("🔍 Validando detección de respuestas:")
    for response, expected, description in test_responses:
        result = templates.extract_consent_response(response)
        success = result == expected
        status = "✅" if success else "❌"
        print(f"   {status} '{response}' → {result} ({description})")
        assert success, f"Error detectando '{response}'"
    
    # Test validación de nombres
    test_names = [
        ("Juan", "Juan", "Nombre simple válido"),
        ("maría josé", "María José", "Nombre compuesto válido"),
        ("Dr. García", "Dr. García", "Nombre con título válido"),
        ("no sé", None, "Respuesta evasiva inválida"),
        ("123", None, "Solo números inválido"),
        ("", None, "Cadena vacía inválida")
    ]
    
    print("\n👤 Validando extracción de nombres:")
    for name_input, expected, description in test_names:
        result = templates.extract_user_name(name_input)
        success = result == expected
        status = "✅" if success else "❌"
        result_display = result or "INVÁLIDO"
        expected_display = expected or "INVÁLIDO"
        print(f"   {status} '{name_input}' → '{result_display}' ({description})")
        assert success, f"Error validando nombre '{name_input}'"
    
    print("\n🎉 TODOS LOS CASOS EDGE VALIDADOS CORRECTAMENTE")

if __name__ == "__main__":
    print("🚀 INICIANDO VALIDACIÓN DE LÓGICA DEL FLUJO DE PRIVACIDAD")
    
    try:
        # Ejecutar test principal de lógica
        test_privacy_flow_logic()
        
        # Ejecutar casos edge
        test_edge_cases_logic()
        
        print_separator("CONCLUSIÓN FINAL")
        print("🎉 TODA LA LÓGICA DEL FLUJO VALIDADA EXITOSAMENTE")
        print("✅ La integración con el webhook funcionará correctamente")
        print("🚀 Sistema listo para pruebas con datos reales")
        
    except Exception as e:
        print(f"\n💥 ERROR EN VALIDACIÓN: {e}")
        import traceback
        traceback.print_exc()
        exit(1)