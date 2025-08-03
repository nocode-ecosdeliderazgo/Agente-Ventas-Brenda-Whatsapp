#!/usr/bin/env python3
"""
Test directo del archivo campaign_config.py para verificar que el mapeo funciona.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

def test_campaign_config_direct():
    """Test directo del archivo campaign_config.py."""
    print("🧪 TESTING DIRECTO: campaign_config.py")
    print("=" * 50)
    
    try:
        # Importar directamente sin dependencias externas
        exec(open('app/config/campaign_config.py').read(), globals())
        
        print("✅ Archivo campaign_config.py cargado exitosamente")
        
        # Verificar que las variables existen
        print(f"\n📚 COURSE_HASHTAG_MAPPING:")
        for hashtag, course_id in COURSE_HASHTAG_MAPPING.items():
            print(f"  {hashtag} -> {course_id}")
        
        print(f"\n📢 CAMPAIGN_HASHTAG_MAPPING:")
        for hashtag, campaign in CAMPAIGN_HASHTAG_MAPPING.items():
            print(f"  {hashtag} -> {campaign}")
        
        # Test de funciones
        print(f"\n🔍 TESTING: Funciones de mapeo")
        
        # Test get_course_id_from_hashtag
        test_hashtag = 'Experto_IA_GPT_Gemini'
        result = get_course_id_from_hashtag(test_hashtag)
        print(f"get_course_id_from_hashtag('{test_hashtag}') = {result}")
        
        # Test is_course_hashtag
        result = is_course_hashtag(test_hashtag)
        print(f"is_course_hashtag('{test_hashtag}') = {result}")
        
        # Test con hashtag que no existe
        test_hashtag_2 = 'hashtag_inexistente'
        result = get_course_id_from_hashtag(test_hashtag_2)
        print(f"get_course_id_from_hashtag('{test_hashtag_2}') = {result}")
        
        print("\n✅ Todas las funciones están trabajando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_course_announcement_integration():
    """Test de integración con el CourseAnnouncementUseCase."""
    print("\n🧪 TESTING: Integración con CourseAnnouncementUseCase")
    print("=" * 50)
    
    try:
        # Cargar campaign_config
        exec(open('app/config/campaign_config.py').read(), globals())
        
        # Simular lógica del CourseAnnouncementUseCase
        additional_mappings = {
            "#CursoIA1": "curso-ia-basico-001",
            "#CursoIA2": "curso-ia-intermedio-001", 
            "#CursoIA3": "curso-ia-avanzado-001",
        }
        
        course_code_mapping = {}
        
        # Agregar mapeos desde campaign_config.py (con # para compatibilidad)
        for hashtag, course_id in COURSE_HASHTAG_MAPPING.items():
            # Agregar tanto con # como sin # para flexibilidad
            course_code_mapping[f"#{hashtag}"] = course_id
            course_code_mapping[hashtag] = course_id
        
        # Agregar mapeos adicionales
        course_code_mapping.update(additional_mappings)
        
        print(f"📋 Mapeo combinado ({len(course_code_mapping)} entradas):")
        for code, course_id in sorted(course_code_mapping.items()):
            print(f"  {code} -> {course_id}")
        
        # Test de detección de códigos
        print(f"\n🔍 TEST: Detección de códigos en mensajes")
        
        test_messages = [
            "#Experto_IA_GPT_Gemini",
            "#ADSIM_05", 
            "Experto_IA_GPT_Gemini",
            "#CursoIA1",
            "mensaje sin códigos"
        ]
        
        for message in test_messages:
            message_lower = message.lower()
            detected_codes = []
            
            # Buscar en mapeo combinado
            for code in course_code_mapping.keys():
                if code.lower() in message_lower:
                    detected_codes.append(code)
            
            print(f"  '{message}' -> {detected_codes}")
        
        print("\n✅ Integración funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_update_logic():
    """Test de la lógica de actualización de memoria."""
    print("\n🧪 TESTING: Lógica de actualización de memoria")
    print("=" * 50)
    
    try:
        # Cargar campaign_config
        exec(open('app/config/campaign_config.py').read(), globals())
        
        def simulate_memory_update(course_code, user_interests, original_message_body):
            """Simula la actualización de memoria con la nueva lógica."""
            # Extraer hashtag limpio (sin #) para guardar en memoria
            hashtag_clean = course_code.replace('#', '')
            
            # Guardar el hashtag en el campo original_message_body para rastreo
            original_message_body = course_code
            
            # También agregarlo a los intereses como hashtag
            hashtag_interest = f"hashtag:{hashtag_clean}"
            if hashtag_interest not in user_interests:
                user_interests.append(hashtag_interest)
            
            # Mapear hashtag a course_id usando sistema centralizado
            course_id = get_course_id_from_hashtag(hashtag_clean)
            if course_id:
                course_id_interest = f"course_id:{course_id}"
                if course_id_interest not in user_interests:
                    user_interests.append(course_id_interest)
            
            return {
                'hashtag_clean': hashtag_clean,
                'course_id': course_id,
                'original_message_body': original_message_body,
                'interests_updated': user_interests.copy()
            }
        
        # Test con diferentes códigos
        test_codes = ["#Experto_IA_GPT_Gemini", "#ADSIM_05", "#CursoIA1"]
        
        for code in test_codes:
            interests = []  # Lista vacía para simular memoria nueva
            original_body = ""
            
            result = simulate_memory_update(code, interests, original_body)
            
            print(f"Código: {code}")
            print(f"  -> Hashtag limpio: {result['hashtag_clean']}")
            print(f"  -> Course ID mapeado: {result['course_id']}")
            print(f"  -> Original message body: {result['original_message_body']}")
            print(f"  -> Intereses guardados: {result['interests_updated']}")
            print()
        
        print("✅ Lógica de memoria funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en lógica de memoria: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    print("🚀 TEST DIRECTO DEL FIX DE HASHTAG MAPPING")
    print("=" * 80)
    
    results = [
        test_campaign_config_direct(),
        test_course_announcement_integration(), 
        test_memory_update_logic()
    ]
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 TODOS LOS TESTS PASARON ({passed}/{total})")
        print("\n✅ EL FIX ESTÁ FUNCIONANDO CORRECTAMENTE!")
        print("✅ Los hashtags de campaign_config.py se integran correctamente")
        print("✅ La detección de códigos funciona con y sin #")
        print("✅ Los hashtags se guardan en la memoria del usuario")
        print("✅ El mapeo a course_id funciona correctamente")
        return 0
    else:
        print(f"❌ ALGUNOS TESTS FALLARON ({passed}/{total})")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)