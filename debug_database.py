#!/usr/bin/env python3
"""
Script para debuggear la base de datos directamente.
"""

import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar cliente de base de datos
from app.infrastructure.database.client import database_client


async def debug_database():
    """Debuggear la base de datos."""
    print("🔍 DEBUGGEANDO BASE DE DATOS")
    print("=" * 40)
    
    try:
        # Conectar
        connected = await database_client.connect()
        if not connected:
            print("❌ No se pudo conectar")
            return
        
        print("✅ Conectado a PostgreSQL")
        
        # Query 1: Ver estructura de la tabla
        print("\n📋 Estructura de la tabla ai_courses:")
        query1 = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'ai_courses' 
            ORDER BY ordinal_position
        """
        result1 = await database_client.execute_query(query1)
        if result1:
            for col in result1:
                print(f"  {col['column_name']}: {col['data_type']}")
        
        # Query 2: Ver datos directamente
        print("\n📊 Datos de la tabla ai_courses:")
        query2 = "SELECT * FROM ai_courses LIMIT 3"
        result2 = await database_client.execute_query(query2)
        if result2:
            for i, row in enumerate(result2, 1):
                print(f"  Registro {i}:")
                for key, value in row.items():
                    print(f"    {key}: {value}")
        else:
            print("  No hay datos")
        
        # Query 3: Probar consulta con alias
        print("\n🔍 Probando consulta con alias:")
        query3 = """
            SELECT 
                id_course, 
                Name as name, 
                Short_description as short_description,
                status, 
                modality
            FROM ai_courses 
            LIMIT 1
        """
        result3 = await database_client.execute_query(query3)
        if result3:
            print("  ✅ Consulta con alias funcionó:")
            for key, value in result3[0].items():
                print(f"    {key}: {value}")
        else:
            print("  ❌ Consulta con alias falló")
        
        # Query 4: Probar WHERE con nombres exactos
        print("\n🔍 Probando WHERE con nombres exactos:")
        query4 = """
            SELECT 
                id_course, 
                Name as name, 
                Short_description as short_description,
                status, 
                modality
            FROM ai_courses 
            WHERE Name ILIKE '%IA%'
            LIMIT 1
        """
        result4 = await database_client.execute_query(query4)
        if result4:
            print("  ✅ WHERE con nombres exactos funcionó")
        else:
            print("  ❌ WHERE con nombres exactos falló")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(debug_database()) 