#!/usr/bin/env python3
"""
Script para obtener el ID real del curso desde la base de datos.
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.client import DatabaseClient
from app.infrastructure.database.repositories.course_repository import CourseRepository

async def get_real_course_id():
    """Obtiene el ID real del curso desde la BD"""
    print("🔍 OBTENIENDO ID REAL DEL CURSO")
    print("="*50)
    
    # Inicializar cliente de BD
    db_client = DatabaseClient()
    
    try:
        # Conectar a la BD
        print("🔌 Conectando a PostgreSQL...")
        if not await db_client.connect():
            print("❌ No se pudo conectar a la base de datos")
            return
        
        print("✅ Conexión exitosa")
        
        # Obtener repositorio de cursos
        course_repo = CourseRepository()
        
        # Buscar el curso por nombre
        print("\n🔍 Buscando curso 'Experto en IA para Profesionales'...")
        courses = await course_repo.search_courses_by_text("Experto en IA para Profesionales", limit=5)
        
        if courses:
            print(f"✅ Encontrados {len(courses)} cursos:")
            for i, course in enumerate(courses, 1):
                print(f"\n📚 Curso {i}:")
                print(f"   ID: {course.id}")
                print(f"   Nombre: {course.name}")
                print(f"   Descripción: {course.short_description[:100]}...")
                print(f"   Precio: ${course.price} {course.currency}")
                print(f"   Duración: {course.total_duration_min} minutos")
                print(f"   Nivel: {course.level}")
                
                # Este es el ID que debemos usar en el mapeo
                print(f"\n🎯 ID REAL PARA MAPEO: {course.id}")
        else:
            print("❌ No se encontraron cursos")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_real_course_id()) 