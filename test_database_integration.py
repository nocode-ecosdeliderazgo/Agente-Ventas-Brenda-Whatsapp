#!/usr/bin/env python3
"""
Script de prueba para verificar la integración completa de la base de datos
con la nueva estructura relacional de cursos.
"""
import asyncio
import sys
from uuid import UUID
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from prompts.agent_prompts import get_response_generation_prompt

def debug_print(message: str):
    """Print con formato visual para debug"""
    print(f"🔍 [TEST] {message}")

async def test_database_integration():
    """Prueba completa de integración de base de datos"""
    
    debug_print("INICIANDO PRUEBAS DE INTEGRACIÓN DE BASE DE DATOS")
    debug_print("=" * 60)
    
    # 1. Inicializar repositorio y use case
    debug_print("1. Inicializando componentes...")
    course_repo = CourseRepository()
    query_use_case = QueryCourseInformationUseCase()
    
    # Inicializar conexión
    init_success = await query_use_case.initialize()
    if not init_success:
        debug_print("❌ FALLO: No se pudo inicializar la conexión a la base de datos")
        return False
    
    debug_print("✅ Conexión a base de datos inicializada")
    
    # 2. Probar consulta de cursos básica
    debug_print("\n2. Probando consulta básica de cursos...")
    try:
        all_courses = await course_repo.get_all_courses(limit=3)
        debug_print(f"✅ Encontrados {len(all_courses)} cursos")
        
        if all_courses:
            first_course = all_courses[0]
            debug_print(f"   - Primer curso: {first_course.name} (ID: {first_course.id_course})")
        else:
            debug_print("⚠️ No se encontraron cursos en la base de datos")
            return False
            
    except Exception as e:
        debug_print(f"❌ Error en consulta básica: {e}")
        return False
    
    # 3. Probar consulta de información detallada
    debug_print("\n3. Probando consulta de información detallada...")
    try:
        course_id = all_courses[0].id_course
        detailed_content = await course_repo.get_course_detailed_content(course_id)
        
        if detailed_content:
            course_data = detailed_content.get('course', {})
            sessions_data = detailed_content.get('sessions', [])
            bonds_data = detailed_content.get('bonds', [])
            
            debug_print(f"✅ Información detallada obtenida:")
            debug_print(f"   - Curso: {course_data.get('name', 'N/A')}")
            debug_print(f"   - Sesiones: {len(sessions_data)}")
            debug_print(f"   - Bonos: {len(bonds_data)}")
            debug_print(f"   - Estructura generada: {len(detailed_content.get('course_structure', ''))} caracteres")
        else:
            debug_print("⚠️ No se pudo obtener información detallada del curso")
            
    except Exception as e:
        debug_print(f"❌ Error obteniendo información detallada: {e}")
        return False
    
    # 4. Probar formateo para chat
    debug_print("\n4. Probando formateo para WhatsApp...")
    try:
        # Formato básico
        basic_formatted = await query_use_case.format_course_for_chat(all_courses[0])
        debug_print(f"✅ Formato básico generado ({len(basic_formatted)} caracteres)")
        
        # Formato detallado si tenemos información
        if detailed_content:
            detailed_formatted = await query_use_case.format_detailed_course_for_chat(detailed_content)
            debug_print(f"✅ Formato detallado generado ({len(detailed_formatted)} caracteres)")
            debug_print(f"\n📱 EJEMPLO DE FORMATO DETALLADO:\n{detailed_formatted[:500]}...")
        
    except Exception as e:
        debug_print(f"❌ Error en formateo: {e}")
        return False
    
    # 5. Probar integración con prompts
    debug_print("\n5. Probando integración con sistema de prompts...")
    try:
        # Crear datos de prueba para user_memory
        class MockUserMemory:
            def __init__(self):
                self.name = "Carlos Empresario"
                self.role = "Director de Marketing"
                self.interests = ["marketing", "automatización"]
                self.pain_points = ["reportes manuales", "falta de tiempo"]
                self.stage = "course_selection"
                self.interaction_count = 3
                self.lead_score = 75
                self.automation_needs = {"reports": "semanales", "content": "diario"}
        
        mock_user_memory = MockUserMemory()
        
        # Datos de análisis de intención mock
        intent_analysis = {
            'category': 'EXPLORATION_SECTOR',
            'buyer_persona_match': 'lucia_copypro',
            'business_pain_detected': 'content_creation',
            'roi_opportunity': 'high',
            'confidence': 0.8,
            'response_focus': 'Enfoque consultivo empresarial',
            'recommended_action': 'provide_course_details',
            'implementation_timeline': '30_days',
            'urgency_level': 'medium'
        }
        
        # Generar prompt con información de curso
        prompt = get_response_generation_prompt(
            user_message="Me interesa saber más sobre automatización de marketing",
            user_memory=mock_user_memory,
            intent_analysis=intent_analysis,
            context_info="Usuario explora automatización específica",
            course_detailed_info=detailed_content if detailed_content else None
        )
        
        debug_print(f"✅ Prompt generado exitosamente ({len(prompt)} caracteres)")
        debug_print(f"   - Incluye información detallada: {'Sí' if detailed_content else 'No'}")
        
        # Mostrar una muestra del prompt
        debug_print(f"\n📋 MUESTRA DEL PROMPT GENERADO:\n{prompt[:800]}...")
        
    except Exception as e:
        debug_print(f"❌ Error en integración con prompts: {e}")
        return False
    
    # 6. Probar estadísticas y resumen
    debug_print("\n6. Probando estadísticas del catálogo...")
    try:
        stats = await course_repo.get_course_statistics()
        debug_print(f"✅ Estadísticas obtenidas:")
        debug_print(f"   - Total cursos: {stats.get('total_courses', 0)}")
        debug_print(f"   - Niveles disponibles: {stats.get('total_levels', 0)}")
        debug_print(f"   - Modalidades: {stats.get('total_modalities', 0)}")
        debug_print(f"   - Promedio sesiones: {stats.get('avg_sessions', 0)}")
        debug_print(f"   - Promedio duración: {stats.get('avg_duration_hours', 0)} horas")
        
        # Resumen del catálogo
        catalog_summary = await query_use_case.get_course_catalog_summary()
        debug_print(f"✅ Resumen del catálogo generado")
        debug_print(f"   - Cursos destacados: {len(catalog_summary.get('featured_courses', []))}")
        
    except Exception as e:
        debug_print(f"❌ Error obteniendo estadísticas: {e}")
        return False
    
    # 7. Probar búsquedas específicas
    debug_print("\n7. Probando búsquedas específicas...")
    try:
        # Búsqueda por texto
        search_results = await query_use_case.search_courses_by_keyword("IA", limit=2)
        debug_print(f"✅ Búsqueda por 'IA': {len(search_results)} resultados")
        
        # Obtener niveles y modalidades disponibles
        options = await query_use_case.get_available_options()
        debug_print(f"✅ Opciones disponibles:")
        debug_print(f"   - Niveles: {options.get('levels', [])}")
        debug_print(f"   - Modalidades: {options.get('modalities', [])}")
        
    except Exception as e:
        debug_print(f"❌ Error en búsquedas: {e}")
        return False
    
    debug_print("\n" + "=" * 60)
    debug_print("🎉 TODAS LAS PRUEBAS DE INTEGRACIÓN PASARON EXITOSAMENTE!")
    debug_print("✅ La base de datos está correctamente integrada con:")
    debug_print("   - Repositorio de cursos con estructura relacional completa")
    debug_print("   - Consultas de información detallada (sesiones, actividades, bonos)")
    debug_print("   - Formateo optimizado para WhatsApp")
    debug_print("   - Integración con sistema de prompts del agente")
    debug_print("   - Búsquedas y filtros")
    debug_print("   - Estadísticas del catálogo")
    
    return True

async def main():
    """Función principal"""
    try:
        success = await test_database_integration()
        if success:
            print("\n🚀 Sistema listo para usar con información rica de base de datos!")
            sys.exit(0)
        else:
            print("\n❌ Hay problemas con la integración de base de datos")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error crítico en las pruebas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())