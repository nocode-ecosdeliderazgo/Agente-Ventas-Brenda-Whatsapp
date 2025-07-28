#!/usr/bin/env python3
"""
Test de conexión con Supabase PostgreSQL.
Este script verifica la conexión con la base de datos Supabase y ejecuta consultas básicas.
"""
import asyncio
import logging
import sys
from datetime import datetime
from app.infrastructure.database.client import database_client
from app.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def test_basic_connection():
    """Prueba la conexión básica a Supabase."""
    print("🔗 Probando conexión básica a Supabase...")
    print(f"📋 URL de base de datos: {settings.database_url[:50]}..." if settings.database_url else "❌ No DATABASE_URL configurada")
    
    # Conectar a la base de datos
    connection_success = await database_client.connect()
    
    if not connection_success:
        print("❌ FALLO: No se pudo conectar a Supabase")
        return False
    
    print("✅ ÉXITO: Conexión establecida con Supabase")
    return True


async def test_health_check():
    """Prueba el health check de la base de datos."""
    print("\n🏥 Probando health check...")
    
    health_ok = await database_client.health_check()
    
    if health_ok:
        print("✅ ÉXITO: Health check OK")
        return True
    else:
        print("❌ FALLO: Health check falló")
        return False


async def test_basic_queries():
    """Prueba consultas básicas."""
    print("\n📊 Probando consultas básicas...")
    
    try:
        # Consulta de información del sistema
        print("   🔍 Probando SELECT version()...")
        version_result = await database_client.execute_query(
            "SELECT version() as db_version",
            fetch_mode="one"
        )
        
        if version_result:
            print(f"   ✅ Versión de PostgreSQL: {version_result[0]['db_version'][:50]}...")
        else:
            print("   ❌ No se pudo obtener la versión")
            return False
        
        # Consulta de fecha/hora actual
        print("   🕐 Probando SELECT now()...")
        time_result = await database_client.execute_query(
            "SELECT now() as current_time, current_database() as db_name",
            fetch_mode="one"
        )
        
        if time_result:
            print(f"   ✅ Fecha/hora actual: {time_result[0]['current_time']}")
            print(f"   ✅ Base de datos: {time_result[0]['db_name']}")
        else:
            print("   ❌ No se pudo obtener fecha/hora")
            return False
        
        # Probar consulta de esquemas/tablas
        print("   📋 Probando consulta de tablas...")
        tables_result = await database_client.execute_query(
            """
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schemaname, tablename
            LIMIT 10
            """,
            fetch_mode="all"
        )
        
        if tables_result is not None:
            print(f"   ✅ Encontradas {len(tables_result)} tablas de usuario:")
            for table in tables_result:
                print(f"      - {table['schemaname']}.{table['tablename']}")
        else:
            print("   ❌ No se pudo consultar tablas")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en consultas básicas: {e}")
        return False


async def test_supabase_specific_features():
    """Prueba características específicas de Supabase."""
    print("\n🚀 Probando características específicas de Supabase...")
    
    try:
        # Verificar extensiones de Supabase
        print("   🔌 Verificando extensiones instaladas...")
        extensions_result = await database_client.execute_query(
            """
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname IN ('uuid-ossp', 'pgcrypto', 'pg_stat_statements', 'pg_trgm')
            ORDER BY extname
            """,
            fetch_mode="all"
        )
        
        if extensions_result is not None:
            print(f"   ✅ Extensiones encontradas ({len(extensions_result)}):")
            for ext in extensions_result:
                print(f"      - {ext['extname']} v{ext['extversion']}")
        else:
            print("   ⚠️  No se encontraron extensiones específicas")
        
        # Verificar configuración de timezone
        print("   🌍 Verificando configuración de zona horaria...")
        tz_result = await database_client.execute_query(
            "SELECT current_setting('timezone') as timezone",
            fetch_mode="one"
        )
        
        if tz_result:
            print(f"   ✅ Zona horaria: {tz_result[0]['timezone']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error verificando características de Supabase: {e}")
        return False


async def test_course_related_queries():
    """Prueba consultas relacionadas con el sistema de cursos si las tablas existen."""
    print("\n📚 Probando consultas relacionadas con cursos...")
    
    try:
        # Verificar si existe tabla de cursos
        print("   🔍 Verificando si existe tabla 'courses'...")
        table_check = await database_client.execute_query(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'courses'
            ) as table_exists
            """,
            fetch_mode="one"
        )
        
        if table_check and table_check[0]['table_exists']:
            print("   ✅ Tabla 'courses' encontrada")
            
            # Contar registros en courses
            count_result = await database_client.execute_query(
                "SELECT COUNT(*) as course_count FROM courses",
                fetch_mode="one"
            )
            
            if count_result:
                print(f"   ✅ Cursos en la base de datos: {count_result[0]['course_count']}")
                
                # Mostrar algunos cursos de ejemplo
                if count_result[0]['course_count'] > 0:
                    sample_courses = await database_client.execute_query(
                        "SELECT id, title, price FROM courses LIMIT 3",
                        fetch_mode="all"
                    )
                    
                    if sample_courses:
                        print("   📋 Cursos de ejemplo:")
                        for course in sample_courses:
                            print(f"      - ID: {course['id']}, Título: {course['title']}, Precio: ${course['price']}")
            
        else:
            print("   ⚠️  Tabla 'courses' no encontrada (puede ser normal si aún no se ha creado)")
        
        # Verificar tabla de usuarios/memoria
        print("   🔍 Verificando si existe tabla 'user_memory'...")
        user_table_check = await database_client.execute_query(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user_memory'
            ) as table_exists
            """,
            fetch_mode="one"
        )
        
        if user_table_check and user_table_check[0]['table_exists']:
            print("   ✅ Tabla 'user_memory' encontrada")
            
            user_count = await database_client.execute_query(
                "SELECT COUNT(*) as user_count FROM user_memory",
                fetch_mode="one"
            )
            
            if user_count:
                print(f"   ✅ Usuarios en memoria: {user_count[0]['user_count']}")
        else:
            print("   ⚠️  Tabla 'user_memory' no encontrada (puede ser normal si aún no se ha creado)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en consultas de cursos: {e}")
        return False


async def test_connection_pool():
    """Prueba el pool de conexiones."""
    print("\n🏊 Probando pool de conexiones...")
    
    try:
        # Ejecutar múltiples consultas simultáneas
        tasks = []
        for i in range(5):
            task = database_client.execute_query(
                f"SELECT {i+1} as query_number, pg_backend_pid() as backend_pid",
                fetch_mode="one"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_queries = 0
        backend_pids = set()
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   ❌ Query {i+1} falló: {result}")
            elif result and len(result) > 0:
                successful_queries += 1
                backend_pids.add(result[0]['backend_pid'])
                print(f"   ✅ Query {i+1}: Backend PID {result[0]['backend_pid']}")
        
        print(f"   📊 Consultas exitosas: {successful_queries}/5")
        print(f"   🔗 Backend PIDs únicos: {len(backend_pids)} (pool funcionando)")
        
        return successful_queries >= 4  # Al menos 4 de 5 deben funcionar
        
    except Exception as e:
        print(f"   ❌ Error probando pool de conexiones: {e}")
        return False


async def cleanup():
    """Limpia las conexiones."""
    print("\n🧹 Limpiando conexiones...")
    await database_client.disconnect()
    print("✅ Conexiones cerradas")


async def main():
    """Función principal de prueba."""
    print("=" * 60)
    print("🧪 PRUEBA DE CONEXIÓN CON SUPABASE")
    print("=" * 60)
    print(f"📅 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests_results = []
    
    try:
        # Test 1: Conexión básica
        tests_results.append(("Conexión básica", await test_basic_connection()))
        
        if not tests_results[-1][1]:
            print("\n❌ PRUEBA FALLIDA: No se pudo establecer conexión básica")
            return
        
        # Test 2: Health check
        tests_results.append(("Health check", await test_health_check()))
        
        # Test 3: Consultas básicas
        tests_results.append(("Consultas básicas", await test_basic_queries()))
        
        # Test 4: Características Supabase
        tests_results.append(("Características Supabase", await test_supabase_specific_features()))
        
        # Test 5: Consultas de cursos
        tests_results.append(("Consultas de cursos", await test_course_related_queries()))
        
        # Test 6: Pool de conexiones
        tests_results.append(("Pool de conexiones", await test_connection_pool()))
        
    except KeyboardInterrupt:
        print("\n⚠️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        await cleanup()
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed_tests = 0
    for test_name, result in tests_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 RESULTADO FINAL: {passed_tests}/{len(tests_results)} pruebas exitosas")
    
    if passed_tests == len(tests_results):
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! Supabase está funcionando correctamente.")
    elif passed_tests >= len(tests_results) * 0.8:  # 80% o más
        print("⚠️  La mayoría de pruebas pasaron, pero hay algunos problemas menores.")
    else:
        print("❌ Múltiples pruebas fallaron. Revisar configuración de Supabase.")
    
    print(f"📅 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())