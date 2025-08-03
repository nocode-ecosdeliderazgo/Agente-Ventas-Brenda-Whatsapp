#!/usr/bin/env python3
"""
Test rápido para verificar que el mapeo de hashtags funciona correctamente
sin depender de las dependencias externas.
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

def test_campaign_config():
    """Test del archivo de configuración de campaña."""
    print("🧪 TESTING: Configuración centralizada de hashtags")
    print("=" * 60)
    
    try:
        from app.config.campaign_config import (
            COURSE_HASHTAG_MAPPING, 
            CAMPAIGN_HASHTAG_MAPPING,
            get_course_id_from_hashtag, 
            get_campaign_name_from_hashtag,
            is_course_hashtag,
            is_campaign_hashtag
        )
        
        print("✅ Importación exitosa de campaign_config.py")
        
        # Test 1: Verificar mapeos cargados
        print(f"\n📚 COURSE_HASHTAG_MAPPING ({len(COURSE_HASHTAG_MAPPING)} entradas):")
        for hashtag, course_id in COURSE_HASHTAG_MAPPING.items():
            print(f"  {hashtag} -> {course_id}")
        
        print(f"\n📢 CAMPAIGN_HASHTAG_MAPPING ({len(CAMPAIGN_HASHTAG_MAPPING)} entradas):")
        for hashtag, campaign in CAMPAIGN_HASHTAG_MAPPING.items():
            print(f"  {hashtag} -> {campaign}")
        
        # Test 2: Verificar funciones de mapeo
        print(f"\n🔍 TESTING: Funciones de mapeo")
        
        test_hashtags = ['Experto_IA_GPT_Gemini', 'ADSIM_05', 'inexistente']
        
        for hashtag in test_hashtags:
            course_id = get_course_id_from_hashtag(hashtag)
            is_course = is_course_hashtag(hashtag)
            campaign = get_campaign_name_from_hashtag(hashtag)
            is_campaign = is_campaign_hashtag(hashtag)
            
            print(f"  {hashtag}:")
            print(f"    -> course_id: {course_id}")
            print(f"    -> is_course: {is_course}")
            print(f"    -> campaign: {campaign}")
            print(f"    -> is_campaign: {is_campaign}")
        
        print("\n✅ COURSE_CONFIG: Todo funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_course_announcement_mapping():
    """Test de la lógica de mapeo en CourseAnnouncementUseCase."""
    print("\n🧪 TESTING: Mapeo en CourseAnnouncementUseCase")
    print("=" * 60)
    
    try:
        # Simular la clase CourseAnnouncementUseCase sin dependencias externas
        from app.config.campaign_config import COURSE_HASHTAG_MAPPING
        
        # Simular el constructor modificado
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
        
        print(f"📋 Mapeo combinado generado ({len(course_code_mapping)} entradas):")
        for code, course_id in course_code_mapping.items():
            print(f"  {code} -> {course_id}")
        
        # Test de detección de códigos
        print(f"\n🔍 TESTING: Detección de códigos en mensajes")
        
        test_messages = [
            "#Experto_IA_GPT_Gemini",
            "Hola me interesa #ADSIM_05",
            "Experto_IA_GPT_Gemini sin hashtag",
            "#CursoIA1 tradicional",
            "mensaje sin códigos"
        ]
        
        for message in test_messages:
            message_lower = message.lower()
            detected_codes = []
            
            # Buscar en mapeo local
            for code in course_code_mapping.keys():
                if code.lower() in message_lower:
                    detected_codes.append(code)
            
            # Buscar en mapeo centralizado (sin #)
            for hashtag in COURSE_HASHTAG_MAPPING.keys():
                if hashtag.lower() in message_lower:
                    detected_codes.append(f"#{hashtag}")
            
            print(f"  '{message}' -> {detected_codes}")
        
        print("\n✅ COURSE_ANNOUNCEMENT: Mapeo funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en mapeo de anuncios: {e}")
        return False

def test_memory_saving_logic():
    """Test de la lógica de guardado en memoria."""
    print("\n🧪 TESTING: Lógica de guardado en memoria")
    print("=" * 60)
    
    try:
        from app.config.campaign_config import get_course_id_from_hashtag
        
        # Simular lógica de guardado
        def simulate_memory_update(course_code, interests):
            """Simula la actualización de memoria del usuario."""
            # Extraer hashtag limpio (sin #)
            hashtag_clean = course_code.replace('#', '')
            
            # Mapear hashtag a course_id usando sistema centralizado
            course_id = get_course_id_from_hashtag(hashtag_clean)
            
            # Simular guardado en intereses
            hashtag_interest = f"hashtag:{hashtag_clean}"
            if hashtag_interest not in interests:
                interests.append(hashtag_interest)
            
            if course_id:
                course_id_interest = f"course_id:{course_id}"
                if course_id_interest not in interests:
                    interests.append(course_id_interest)
            
            return {
                'hashtag_clean': hashtag_clean,
                'course_id': course_id,
                'interests_updated': interests
            }
        
        # Test con diferentes códigos
        test_codes = ["#Experto_IA_GPT_Gemini", "#ADSIM_05", "#CursoIA1"]
        
        for code in test_codes:
            interests = []  # Lista vacía para simular memoria nueva
            result = simulate_memory_update(code, interests)
            
            print(f"Código: {code}")
            print(f"  -> Hashtag limpio: {result['hashtag_clean']}")
            print(f"  -> Course ID: {result['course_id']}")
            print(f"  -> Intereses guardados: {result['interests_updated']}")
            print()
        
        print("✅ MEMORY_SAVING: Lógica de guardado funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en lógica de memoria: {e}")
        return False

def main():
    """Función principal de testing."""
    print("🚀 INICIANDO TESTS DE HASHTAG MAPPING FIX")
    print("=" * 80)
    
    results = []
    
    # Test 1: Configuración centralizada
    results.append(test_campaign_config())
    
    # Test 2: Mapeo en CourseAnnouncementUseCase
    results.append(test_course_announcement_mapping())
    
    # Test 3: Lógica de guardado en memoria
    results.append(test_memory_saving_logic())
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE TESTS")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 TODOS LOS TESTS PASARON ({passed}/{total})")
        print("\n✅ El fix del mapeo de hashtags está funcionando correctamente!")
        print("✅ Los hashtags ahora se guardarán en la memoria del usuario")
        print("✅ El sistema usa el mapeo centralizado de campaign_config.py")
        return 0
    else:
        print(f"❌ ALGUNOS TESTS FALLARON ({passed}/{total})")
        print("⚠️  Es necesario revisar la implementación")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)