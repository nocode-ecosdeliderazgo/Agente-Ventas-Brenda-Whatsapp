#!/usr/bin/env python3
"""
Script simple para probar consulta directa sin alias.
"""

import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar cliente de base de datos
from app.infrastructure.database.client import database_client


async def test_simple_query():
    """Probar consulta simple sin alias."""
    print("🔍 PROBANDO CONSULTA SIMPLE SIN ALIAS")
    print("=" * 40)
    
    try:
        # Conectar
        connected = await database_client.connect()
        if not connected:
            print("❌ No se pudo conectar")
            return
        
        print("✅ Conectado a PostgreSQL")
        
        # Query simple sin alias
        print("\n📊 Probando consulta simple sin alias:")
        query = """
            SELECT id_course, Name, Short_description, status, modality
            FROM ai_courses 
            LIMIT 1
        """
        result = await database_client.execute_query(query)
        
        if result:
            print("✅ Consulta exitosa:")
            for key, value in result[0].items():
                print(f"  {key}: {value}")
        else:
            print("❌ Consulta falló")
        
        # Query con WHERE
        print("\n🔍 Probando consulta con WHERE:")
        query2 = """
            SELECT id_course, Name, Short_description, status, modality
            FROM ai_courses 
            WHERE Name ILIKE '%IA%'
            LIMIT 1
        """
        result2 = await database_client.execute_query(query2)
        
        if result2:
            print("✅ Consulta con WHERE exitosa:")
            for key, value in result2[0].items():
                print(f"  {key}: {value}")
        else:
            print("❌ Consulta con WHERE falló")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_simple_query()) 