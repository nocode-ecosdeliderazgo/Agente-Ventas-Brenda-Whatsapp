#!/usr/bin/env python3
"""
Test de consistencia de la base de datos PostgreSQL.
Verifica que la conexión sea estable y que no devuelva 0 cursos intermitentemente.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.application.usecases.query_course_information import QueryCourseInformationUseCase

async def test_database_consistency():
    """Test de consistencia para la base de datos."""
    
    print("🔍 INICIANDO TEST DE CONSISTENCIA DE BASE DE DATOS")
    print("=" * 60)
    
    # Crear caso de uso de consulta de cursos
    course_query_use_case = QueryCourseInformationUseCase()
    
    # Intentar inicializar la conexión
    print("🔌 Inicializando conexión a PostgreSQL...")
    connection_ok = await course_query_use_case.initialize()
    
    if not connection_ok:
        print("❌ ERROR: No se pudo conectar a la base de datos PostgreSQL")
        print("🔧 Verifica que las variables de entorno estén configuradas:")
        print("   - DATABASE_URL")
        print("   - SUPABASE_URL") 
        print("   - SUPABASE_KEY")
        return False
    
    print("✅ Conexión PostgreSQL establecida correctamente")
    print()
    
    # Hacer múltiples consultas para verificar consistencia
    print("🔄 REALIZANDO MÚLTIPLES CONSULTAS PARA VERIFICAR CONSISTENCIA...")
    print("-" * 60)
    
    results = []
    for i in range(5):
        try:
            print(f"📊 Consulta #{i+1}:", end=" ")
            catalog_summary = await course_query_use_case.get_course_catalog_summary()
            
            if catalog_summary and 'statistics' in catalog_summary:
                total_courses = catalog_summary['statistics'].get('total_courses', 0)
                print(f"✅ {total_courses} cursos encontrados")
                results.append(total_courses)
            else:
                print("❌ Sin datos válidos")
                results.append(0)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(-1)
    
    print()
    print("📈 ANÁLISIS DE RESULTADOS:")
    print("-" * 30)
    
    # Analizar consistencia
    unique_results = set(results)
    consistent = len(unique_results) == 1 and results[0] > 0
    
    if consistent:
        print(f"✅ CONSISTENTE: Todas las consultas devolvieron {results[0]} cursos")
        print("🎉 La base de datos funciona correctamente")
        return True
    else:
        print(f"❌ INCONSISTENTE: Resultados variados: {results}")
        print("🔧 Problema detectado:")
        
        if 0 in results:
            print("   - Algunas consultas devuelven 0 cursos (conexión intermitente)")
        if -1 in results:
            print("   - Algunas consultas fallan con error")
        
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_database_consistency())
        if result:
            print("\n🎯 RESULTADO: Base de datos estable y consistente")
            sys.exit(0)
        else:
            print("\n⚠️  RESULTADO: Se detectaron problemas de consistencia")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        sys.exit(1)