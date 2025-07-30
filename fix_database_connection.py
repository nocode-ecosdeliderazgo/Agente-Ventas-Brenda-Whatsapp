#!/usr/bin/env python3
"""
Script para verificar y corregir la conexión a la base de datos
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.client import database_client
from app.infrastructure.database.repositories.course_repository import CourseRepository

def debug_print(message: str, function_name: str = ""):
    """Print de debug visual"""
    print(f"🔍 [{function_name}] {message}")

async def main():
    """Función principal"""
    print("🔍 VERIFICANDO Y CORRIGIENDO CONEXIÓN A BASE DE DATOS")
    print("="*60)
    
    # Paso 1: Verificar estado actual
    debug_print("🔍 VERIFICANDO ESTADO ACTUAL", "STATUS")
    print(f"   database_client.pool: {database_client.pool}")
    
    # Paso 2: Conectar si no está conectado
    if not database_client.pool:
        debug_print("🔌 CONECTANDO BASE DE DATOS", "CONNECT")
        connection_success = await database_client.connect()
        
        if connection_success:
            print("✅ Conexión establecida correctamente")
        else:
            print("❌ Error estableciendo conexión")
            return
    else:
        print("✅ Ya está conectado")
    
    # Paso 3: Verificar health check
    debug_print("🏥 VERIFICANDO HEALTH CHECK", "HEALTH")
    health_check = await database_client.health_check()
    
    if health_check:
        print("✅ Health check exitoso")
    else:
        print("❌ Health check falló")
        return
    
    # Paso 4: Probar CourseRepository
    debug_print("🔧 PROBANDO COURSE REPOSITORY", "REPOSITORY")
    course_repository = CourseRepository()
    
    try:
        # Importar UUID para la conversión
        from uuid import UUID
        course_id = UUID("11111111-1111-1111-1111-111111111111")
        
        course = await course_repository.get_course_by_id(course_id)
        
        if course:
            print(f"✅ CourseRepository funcionando: {course.name}")
            print(f"   ID: {course.id_course}")
            print(f"   Precio: {course.price} {course.currency}")
            print(f"   Duración: {course.total_duration_min} minutos")
        else:
            print("❌ CourseRepository no encontró el curso")
            return
    except Exception as e:
        print(f"❌ Error en CourseRepository: {e}")
        return
    
    print("\n" + "="*60)
    print("🎉 CONEXIÓN A BASE DE DATOS FUNCIONANDO CORRECTAMENTE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main()) 