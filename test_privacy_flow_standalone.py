"""
Test independiente para el flujo de privacidad sin dependencias externas.
Solo prueba los templates y la lógica de extracción de datos.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.templates.privacy_flow_templates import PrivacyFlowTemplates

def print_separator(title: str):
    """Imprime un separador visual para organizar los tests."""
    print(f"\n{'='*60}")
    print(f"🔐 {title}")
    print('='*60)

def test_whatsapp_name_extraction():
    """Test de extracción de nombre desde metadatos de WhatsApp."""
    print_separator("TEST: EXTRACCIÓN DE NOMBRE DE WHATSAPP")
    
    templates = PrivacyFlowTemplates()
    
    # Test casos positivos
    test_cases = [
        # Caso con ProfileName
        {
            "raw_data": {"ProfileName": "Juan García", "From": "whatsapp:+5213334567890"},
            "expected": "Juan García",
            "description": "ProfileName disponible"
        },
        # Caso con ContactName
        {
            "raw_data": {"ContactName": "María López", "From": "whatsapp:+5213334567891"},
            "expected": "María López", 
            "description": "ContactName disponible"
        },
        # Caso sin nombre
        {
            "raw_data": {"From": "whatsapp:+5213334567892"},
            "expected": None,
            "description": "Sin información de nombre"
        },
        # Caso con WaId diferente
        {
            "raw_data": {"WaId": "Dr.Martinez", "From": "whatsapp:+5213334567893"},
            "expected": "Dr.Martinez",
            "description": "WaId como nombre"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        result = templates.get_whatsapp_display_name(case["raw_data"])
        success = result == case["expected"]
        
        print(f"   {i}. {case['description']}: {'✅' if success else '❌'}")
        if success:
            print(f"      Nombre extraído: {result or 'No disponible'}")
        else:
            print(f"      Esperado: {case['expected']}, Obtenido: {result}")
        
        assert success, f"Error en caso {i}: {case['description']}"
    
    print("\n🎉 EXTRACCIÓN DE NOMBRES: TODOS LOS CASOS EXITOSOS")

def test_consent_response_detection():
    """Test de detección de respuestas de consentimiento."""
    print_separator("TEST: DETECCIÓN DE RESPUESTAS DE CONSENTIMIENTO")
    
    templates = PrivacyFlowTemplates()
    
    # Test casos de respuestas
    test_cases = [
        # Respuestas afirmativas
        ("ACEPTO", True, "Aceptación explícita mayúscula"),
        ("acepto", True, "Aceptación explícita minúscula"),
        ("Sí", True, "Sí con acento"),
        ("si", True, "Si sin acento"),
        ("OK", True, "OK mayúscula"),
        ("ok", True, "ok minúscula"),
        ("de acuerdo", True, "De acuerdo"),
        ("está bien", True, "Está bien"),
        ("perfecto", True, "Perfecto"),
        ("adelante", True, "Adelante"),
        
        # Respuestas negativas
        ("NO ACEPTO", False, "Rechazo explícito mayúscula"),
        ("no acepto", False, "Rechazo explícito minúscula"),
        ("NO", False, "No mayúscula"),
        ("no", False, "No minúscula"),
        ("nop", False, "Nop"),
        ("rechazo", False, "Rechazo"),
        ("no quiero", False, "No quiero"),
        ("no deseo", False, "No deseo"),
        
        # Respuestas poco claras
        ("tal vez", None, "Tal vez"),
        ("no sé", None, "No sé"),
        ("mmm", None, "Mmm"),
        ("depende", None, "Depende"),
        ("qué es eso", None, "Pregunta"),
        ("hola", None, "Saludo irrelevante")
    ]
    
    for message, expected, description in test_cases:
        result = templates.extract_consent_response(message)
        success = result == expected
        
        status = "✅" if success else "❌"
        result_text = "ACEPTA" if result is True else "RECHAZA" if result is False else "NO CLARO"
        
        print(f"   {status} '{message}' → {result_text} ({description})")
        
        if not success:
            expected_text = "ACEPTA" if expected is True else "RECHAZA" if expected is False else "NO CLARO"
            print(f"       ❌ Esperado: {expected_text}, Obtenido: {result_text}")
        
        assert success, f"Error detectando '{message}': esperado {expected}, obtenido {result}"
    
    print("\n🎉 DETECCIÓN DE CONSENTIMIENTO: TODOS LOS CASOS EXITOSOS")

def test_name_extraction_and_validation():
    """Test de extracción y validación de nombres."""
    print_separator("TEST: EXTRACCIÓN Y VALIDACIÓN DE NOMBRES")
    
    templates = PrivacyFlowTemplates()
    
    # Test casos de nombres
    test_cases = [
        # Nombres válidos
        ("Juan", "Juan", "Nombre simple"),
        ("maría", "María", "Nombre con minúscula inicial"),
        ("CARLOS", "Carlos", "Nombre en mayúsculas"),
        ("juan carlos", "Juan Carlos", "Nombre compuesto"),
        ("maría josé", "María José", "Nombre compuesto femenino"),
        ("Dr. García", "Dr. García", "Nombre con título"),
        ("Ana-Sofía", "Ana-Sofía", "Nombre con guión"),
        ("José María", "José María", "Nombre masculino compuesto"),
        
        # Nombres inválidos
        ("no sé", None, "Respuesta evasiva"),
        ("no tengo", None, "No tengo"),
        ("da igual", None, "Da igual"),
        ("cualquiera", None, "Cualquiera"),
        ("", None, "Cadena vacía"),
        ("a", None, "Muy corto"),
        ("123", None, "Solo números"),
        ("@#$%", None, "Solo símbolos"),
        ("x" * 60, None, "Muy largo"),
        ("nada", None, "Nada")
    ]
    
    for input_name, expected, description in test_cases:
        result = templates.extract_user_name(input_name)
        success = result == expected
        
        status = "✅" if success else "❌"
        result_display = result or "INVÁLIDO"
        
        print(f"   {status} '{input_name}' → '{result_display}' ({description})")
        
        if not success:
            expected_display = expected or "INVÁLIDO"
            print(f"       ❌ Esperado: '{expected_display}', Obtenido: '{result_display}'")
        
        assert success, f"Error validando '{input_name}': esperado {expected}, obtenido {result}"
    
    print("\n🎉 VALIDACIÓN DE NOMBRES: TODOS LOS CASOS EXITOSOS")

def test_message_templates():
    """Test de generación de templates de mensajes."""
    print_separator("TEST: GENERACIÓN DE TEMPLATES DE MENSAJES")
    
    templates = PrivacyFlowTemplates()
    
    # Test mensaje de consentimiento sin nombre
    consent_message = templates.privacy_consent_request()
    
    required_elements = [
        ("¡Hola!", "Saludo genérico"),
        ("Soy **Brenda**", "Presentación"),
        ("consentimiento", "Solicitud consentimiento"),
        ("ACEPTO", "Opción aceptar"),
        ("NO ACEPTO", "Opción rechazar"),
        ("privacidad", "Mención privacidad")
    ]
    
    print("   📝 Mensaje de consentimiento (sin nombre):")
    for element, description in required_elements:
        present = element in consent_message
        status = "✅" if present else "❌"
        print(f"      {status} {description}: '{element}'")
        assert present, f"Elemento faltante: {element}"
    
    # Test mensaje de consentimiento con nombre
    consent_with_name = templates.privacy_consent_request("María García")
    
    name_checks = [
        ("¡Hola María García!", "Saludo personalizado"),
        ("Soy **Brenda**", "Presentación mantenida")
    ]
    
    print("\n   📝 Mensaje de consentimiento (con nombre):")
    for element, description in name_checks:
        present = element in consent_with_name
        status = "✅" if present else "❌"
        print(f"      {status} {description}: '{element}'")
        assert present, f"Elemento faltante con nombre: {element}"
    
    # Test otros templates
    other_templates = [
        (templates.privacy_accepted_name_request(), "Solicitud de nombre", "¿Cómo te gustaría que te llamemos?"),
        (templates.privacy_rejected(), "Rechazo profesional", "Entiendo perfectamente"),
        (templates.name_confirmed("Carlos"), "Confirmación nombre", "Carlos"),
        (templates.invalid_privacy_response(), "Respuesta inválida", "respuesta clara"),
        (templates.name_request_reminder(), "Recordatorio nombre", "nombre preferido")
    ]
    
    print("\n   📝 Otros templates:")
    for template, description, key_element in other_templates:
        present = key_element in template
        status = "✅" if present else "❌"
        print(f"      {status} {description}: contiene '{key_element}'")
        assert present, f"Template {description} no contiene {key_element}"
    
    print("\n🎉 GENERACIÓN DE TEMPLATES: TODOS LOS CASOS EXITOSOS")

def test_privacy_flow_detection():
    """Test de detección de mensajes del flujo de privacidad."""
    print_separator("TEST: DETECCIÓN DE MENSAJES DE FLUJO")
    
    templates = PrivacyFlowTemplates()
    
    # Test casos de mensajes relacionados con privacidad
    test_cases = [
        ("ACEPTO", True, "Aceptación explícita"),
        ("no acepto", True, "Rechazo explícito"),
        ("privacidad", True, "Mención privacidad"),
        ("consentimiento", True, "Mención consentimiento"),  
        ("términos", True, "Mención términos"),
        ("datos", True, "Mención datos"),
        ("hola", False, "Saludo simple"),
        ("¿qué cursos tienen?", False, "Pregunta sobre cursos"),
        ("gracias", False, "Agradecimiento"),
        ("información", False, "Solicitud información")
    ]
    
    for message, expected, description in test_cases:
        result = templates.is_privacy_flow_message(message)
        success = result == expected
        
        status = "✅" if success else "❌"
        result_text = "SÍ" if result else "NO"
        
        print(f"   {status} '{message}' → {result_text} ({description})")
        
        assert success, f"Error detectando '{message}': esperado {expected}, obtenido {result}"
    
    print("\n🎉 DETECCIÓN DE MENSAJES: TODOS LOS CASOS EXITOSOS")

def display_sample_messages():
    """Muestra ejemplos de mensajes generados."""
    print_separator("EJEMPLOS DE MENSAJES GENERADOS")
    
    templates = PrivacyFlowTemplates()
    
    print("📱 MENSAJE DE CONSENTIMIENTO (con nombre extraído):")
    print("-" * 50)
    consent_msg = templates.privacy_consent_request("Juan García")
    print(consent_msg)
    
    print("\n📱 SOLICITUD DE NOMBRE:")
    print("-" * 50)
    name_request = templates.privacy_accepted_name_request()
    print(name_request)
    
    print("\n📱 CONFIRMACIÓN FINAL:")
    print("-" * 50)
    confirmation = templates.name_confirmed("Juan Carlos")
    print(confirmation)
    
    print("\n📊 ESTADÍSTICAS DE MENSAJES:")
    print(f"   📏 Consentimiento: {len(consent_msg)} caracteres")
    print(f"   📏 Solicitud nombre: {len(name_request)} caracteres")
    print(f"   📏 Confirmación: {len(confirmation)} caracteres")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS INDEPENDIENTES DEL FLUJO DE PRIVACIDAD")
    
    try:
        # Ejecutar todos los tests
        test_whatsapp_name_extraction()
        test_consent_response_detection()
        test_name_extraction_and_validation()
        test_message_templates()
        test_privacy_flow_detection()
        
        # Mostrar ejemplos
        display_sample_messages()
        
        print_separator("RESUMEN FINAL")
        print("🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("\n✅ FUNCIONALIDADES VALIDADAS:")
        print("   👤 Extracción de nombres desde metadatos de WhatsApp")
        print("   🔍 Detección precisa de respuestas de consentimiento")
        print("   📝 Validación robusta de nombres de usuario")
        print("   💬 Generación correcta de todos los templates")
        print("   🎯 Detección de mensajes del flujo de privacidad")
        print("   📱 Mensajes profesionales y bien estructurados")
        
        print("\n🚀 EL FLUJO DE PRIVACIDAD ESTÁ LISTO PARA INTEGRACIÓN")
        
    except AssertionError as e:
        print(f"\n❌ ERROR EN TEST: {e}")
        exit(1)
    except Exception as e:
        print(f"\n💥 ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        exit(1)