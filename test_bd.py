#!/usr/bin/env python3
"""
Test de conexión a base de datos PostgreSQL
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def test_database_connection():
    """Prueba la conexión a PostgreSQL"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print('❌ DATABASE_URL no configurado en .env')
            return False
            
        print(f'🔗 Intentando conectar a: {DATABASE_URL[:50]}...')
        
        # Conectar a la base de datos
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Ejecutar query simple
        result = await conn.fetchval('SELECT 1')
        print(f'✅ Query test exitoso: {result}')
        
        # Verificar tabla oa_threads_map
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'oa_threads_map'
            )
        """)
        
        print(f'📊 Tabla oa_threads_map existe: {table_exists}')
        
        # Cerrar conexión
        await conn.close()
        print('✅ Conexión a base de datos EXITOSA!')
        return True
        
    except Exception as e:
        print(f'❌ Error de conexión: {e}')
        print(f'❌ Tipo de error: {type(e).__name__}')
        return False

async def test_table_creation():
    """Prueba crear la tabla oa_threads_map si no existe"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Crear tabla si no existe
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS public.oa_threads_map (
                user_phone text PRIMARY KEY,
                thread_id text NOT NULL,
                created_at timestamp with time zone NOT NULL DEFAULT now(),
                updated_at timestamp with time zone DEFAULT now()
            )
        """)
        
        # Crear índice si no existe
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_oa_threads_map_thread_id 
            ON public.oa_threads_map(thread_id)
        """)
        
        print('✅ Tabla oa_threads_map verificada/creada')
        await conn.close()
        return True
        
    except Exception as e:
        print(f'❌ Error creando tabla: {e}')
        return False

async def main():
    """Función principal de testing"""
    print('🚀 === TEST DE CONEXIÓN A BASE DE DATOS ===')
    print()
    
    # Test 1: Conexión básica
    print('📍 TEST 1: Conexión básica')
    success1 = await test_database_connection()
    print()
    
    if success1:
        # Test 2: Creación de tabla
        print('📍 TEST 2: Verificación/creación de tabla')
        success2 = await test_table_creation()
        print()
        
        if success2:
            print('🎉 TODOS LOS TESTS PASARON')
            print('✅ Base de datos lista para OpenAI Threads')
        else:
            print('⚠️ Problema con la tabla oa_threads_map')
    else:
        print('💥 FALLO EN CONEXIÓN BÁSICA')
        print('🔧 Revisar DATABASE_URL en .env')

if __name__ == "__main__":
    asyncio.run(main())