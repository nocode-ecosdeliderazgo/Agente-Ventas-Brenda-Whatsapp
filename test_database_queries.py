#!/usr/bin/env python3
"""
Script para probar consultas de la base de datos directamente.
Verifica que las consultas funcionen antes de integrarlas al bot.
"""

import asyncio
import logging
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar componentes de la base de datos
from app.infrastructure.database.client import database_client
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.application.usecases.query_course_information import QueryCourseInformationUseCase


async def test_basic_connection():
    """Prueba la conexión básica a PostgreSQL."""
    print("🔌 Probando conexión básica a PostgreSQL...")
    
    try:
        connected = await database_client.connect()
        if connected:
            print("✅ Conexión exitosa")
            
            # Health check
            health = await database_client.health_check()
            print(f"🏥 Health check: {'✅ OK' if health else '❌ FALLÓ'}")
            
            return True
        else:
            print("❌ No se pudo conectar a PostgreSQL")
            return False
            
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
        return False


async def test_simple_queries():
    """Prueba consultas simples directamente."""
    print("\n📊 Probando consultas simples...")
    
    try:
        # Query 1: Contar cursos
        query1 = "SELECT COUNT(*) as total FROM ai_courses"
        result1 = await database_client.execute_query(query1)
        print(f"📚 Total de cursos: {result1[0]['total'] if result1 else 'N/A'}")
        
        # Query 2: Obtener algunos cursos
        query2 = """
            SELECT id_course, Name, Short_description, status, modality
            FROM ai_courses 
            LIMIT 3
        """
        result2 = await database_client.execute_query(query2)
        print(f"📋 Cursos encontrados: {len(result2) if result2 else 0}")
        
        if result2:
            for i, course in enumerate(result2, 1):
                print(f"  {i}. {course.get('name', 'Sin nombre')} - {course.get('status', 'Sin estado')}")
        else:
            print("  No se encontraron cursos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en consultas simples: {e}")
        return False


async def test_course_repository():
    """Prueba el repositorio de cursos."""
    print("\n🏪 Probando repositorio de cursos...")
    
    try:
        repo = CourseRepository()
        
        # Test 1: Obtener cursos activos
        print("🔍 Buscando cursos activos...")
        active_courses = await repo.get_active_courses(limit=3)
        print(f"✅ Cursos activos encontrados: {len(active_courses)}")
        
        for i, course in enumerate(active_courses, 1):
            print(f"  {i}. {course.name} - {course.modality}")
        
        # Test 2: Buscar por texto
        print("\n🔍 Buscando cursos por texto 'IA'...")
        search_results = await repo.search_courses_by_text("IA", limit=3)
        print(f"✅ Resultados de búsqueda: {len(search_results)}")
        
        for i, course in enumerate(search_results, 1):
            print(f"  {i}. {course.name} - {course.short_description[:50] if course.short_description else 'Sin descripción'}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en repositorio: {e}")
        return False


async def test_query_use_case():
    """Prueba el caso de uso de consulta de cursos."""
    print("\n🎯 Probando caso de uso de consulta...")
    
    try:
        use_case = QueryCourseInformationUseCase()
        
        # Test 1: Inicializar
        print("🔧 Inicializando caso de uso...")
        initialized = await use_case.initialize()
        print(f"✅ Inicialización: {'✅ OK' if initialized else '❌ FALLÓ'}")
        
        if initialized:
            # Test 2: Obtener resumen del catálogo
            print("\n📊 Obteniendo resumen del catálogo...")
            summary = await use_case.get_course_catalog_summary()
            print(f"✅ Resumen obtenido: {len(summary)} elementos")
            
            if summary:
                print("📋 Contenido del resumen:")
                for key, value in summary.items():
                    if isinstance(value, list):
                        print(f"  {key}: {len(value)} elementos")
                    else:
                        print(f"  {key}: {value}")
            
            # Test 3: Buscar cursos por keyword
            print("\n🔍 Buscando cursos por keyword 'curso'...")
            courses = await use_case.search_courses_by_keyword("curso", limit=3)
            print(f"✅ Cursos encontrados: {len(courses)}")
            
            for i, course in enumerate(courses, 1):
                print(f"  {i}. {course.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en caso de uso: {e}")
        return False


async def test_formatted_output():
    """Prueba el formateo de cursos para chat."""
    print("\n💬 Probando formateo para chat...")
    
    try:
        use_case = QueryCourseInformationUseCase()
        await use_case.initialize()
        
        # Obtener algunos cursos
        courses = await use_case.search_courses_by_keyword("", limit=2)
        
        if courses:
            print("📝 Formato de curso individual:")
            formatted = await use_case.format_course_for_chat(courses[0])
            print(formatted)
            
            print("\n📋 Formato de lista de cursos:")
            formatted_list = await use_case.format_course_list_for_chat(courses)
            print(formatted_list)
        else:
            print("⚠️ No hay cursos para formatear")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en formateo: {e}")
        return False


async def main():
    """Función principal de pruebas."""
    print("🚀 INICIANDO PRUEBAS DE BASE DE DATOS")
    print("=" * 50)
    
    tests = [
        ("Conexión básica", test_basic_connection),
        ("Consultas simples", test_simple_queries),
        ("Repositorio de cursos", test_course_repository),
        ("Caso de uso de consulta", test_query_use_case),
        ("Formateo para chat", test_formatted_output),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = await test_func()
            results.append((test_name, success))
            print(f"✅ {test_name}: {'PASÓ' if success else 'FALLÓ'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! La base de datos está lista para el bot.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores antes de continuar.")


if __name__ == "__main__":
    asyncio.run(main()) 