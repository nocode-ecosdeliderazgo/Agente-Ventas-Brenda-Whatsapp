#!/usr/bin/env python3
"""
Script para verificar cursos en la base de datos.
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.application.usecases.query_course_information import QueryCourseInformationUseCase

async def test_database_courses():
    """Prueba la conexión a la base de datos y lista cursos"""
    print("🗄️ VERIFICANDO CURSOS EN BASE DE DATOS")
    print("="*50)
    
    # Inicializar sistema de cursos
    course_query_use_case = QueryCourseInformationUseCase()
    
    # Inicializar conexión
    print("🔌 Conectando a PostgreSQL...")
    initialized = await course_query_use_case.initialize()
    
    if not initialized:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    print("✅ Conexión exitosa")
    
    # Buscar todos los cursos
    print("\n🔍 Buscando cursos...")
    try:
        # Buscar por palabra clave para obtener todos
        courses = await course_query_use_case.search_courses_by_keyword("", limit=10)
        
        if courses:
            print(f"✅ Encontrados {len(courses)} cursos:")
            for i, course in enumerate(courses, 1):
                print(f"\n📚 Curso {i}:")
                print(f"   ID: {course.id_course}")
                print(f"   Nombre: {course.name}")
                print(f"   Descripción: {course.short_description[:100] if course.short_description else 'Sin descripción'}...")
                print(f"   Precio: ${course.price} {course.currency}")
                print(f"   Duración: {course.total_duration_min} minutos")
                print(f"   Nivel: {course.level}")
        else:
            print("❌ No se encontraron cursos")
            
    except Exception as e:
        print(f"❌ Error buscando cursos: {e}")

if __name__ == "__main__":
    asyncio.run(test_database_courses()) 