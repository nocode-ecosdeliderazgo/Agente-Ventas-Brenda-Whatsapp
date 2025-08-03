#!/usr/bin/env python3
"""
Test completo para validar las mejoras en el sistema de buyer persona matching.
Verifica la precisión del matching específico con keywords avanzados y contexto empresarial.
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.application.usecases.extract_user_info_use_case import ExtractUserInfoUseCase
from app.infrastructure.openai.client import OpenAIClient
from memory.lead_memory import LeadMemory


def print_test_header(test_name: str):
    """Imprime header de test."""
    print(f"\n{'='*70}")
    print(f"🎯 TEST BUYER PERSONA MATCHING: {test_name}")
    print('='*70)


def print_success(message: str):
    """Imprime mensaje de éxito."""
    print(f"✅ {message}")


def print_error(message: str):
    """Imprime mensaje de error."""
    print(f"❌ {message}")


def print_info(message: str):
    """Imprime información."""
    print(f"ℹ️ {message}")


def print_result(persona_expected: str, persona_actual: str, score: float, confidence: float):
    """Imprime resultado de matching."""
    match_status = "✅ CORRECTO" if persona_expected == persona_actual else "❌ INCORRECTO"
    print(f"   {match_status} | Esperado: {persona_expected} | Obtenido: {persona_actual}")
    print(f"   Score: {score:.1f} | Confidence: {confidence:.2f}")
    

async def test_lucia_copypro_matching():
    """Test 1: Matching específico para Lucía CopyPro (Marketing Digital)."""
    print_test_header("Lucía CopyPro - Marketing Digital Manager")
    
    try:
        openai_client = OpenAIClient()
        extract_use_case = ExtractUserInfoUseCase(openai_client)
        
        # Casos de test específicos para Lucía
        test_cases = [
            {
                'name': 'Marketing Digital + Social Media',
                'conversation': """
                Nombre: Lucía Fernández
                Rol: Marketing Manager
                Conversación:
                - Manejo el marketing digital de nuestra agencia
                - Necesito crear contenido para social media más rápido
                - Tenemos 45 empleados y muchos clientes esperando campañas
                - El problema es generar ideas creativas constantemente
                """,
                'expected': 'lucia_copypro'
            },
            {
                'name': 'Content Manager + Agencia',
                'conversation': """
                Nombre: María López
                Rol: Content Manager
                Conversación:
                - Trabajo en una agencia de publicidad
                - Mi rol es content marketing y campaigns
                - Necesito automatizar la creación de posts
                - Los clientes siempre piden más contenido viral
                """,
                'expected': 'lucia_copypro'
            },
            {
                'name': 'Social Media + Creative Director',
                'conversation': """
                Nombre: Carlos Ruiz
                Rol: Creative Director
                Conversación:
                - Dirijo el equipo creativo de la agencia
                - Necesitamos automatizar el copywriting
                - Social media campaigns son nuestro fuerte
                - El engagement de los clientes es mi prioridad
                """,
                'expected': 'lucia_copypro'
            },
            {
                'name': 'Caso ambiguo - debería ser unknown',
                'conversation': """
                Nombre: Juan Pérez
                Rol: Marketing
                Conversación:
                - Trabajo en marketing
                - Necesito ayuda con mi empresa
                """,
                'expected': 'unknown'  # Muy poco específico
            }
        ]
        
        results = []
        
        for case in test_cases:
            print_info(f"🧪 Probando: {case['name']}")
            
            # Crear memoria con conversación específica
            user_memory = LeadMemory(
                user_id="test_lucia",
                name="Test User",
                role="Marketing Manager"
            )
            
            # Simular conversación
            user_memory.add_context_entry(case['conversation'])
            
            # Extraer insights
            insights = await extract_use_case.extract_insights_from_conversation(
                user_memory=user_memory,
                recent_messages=[case['conversation']]
            )
            
            # Verificar resultado
            expected = case['expected']
            actual = insights.buyer_persona_match
            
            print_result(expected, actual, 0.0, insights.confidence_score)
            
            is_correct = (expected == actual)
            results.append(is_correct)
            
            if not is_correct:
                print_error(f"   Expected {expected}, got {actual}")
        
        success_rate = sum(results) / len(results) * 100
        print_info(f"📊 Tasa de éxito Lucía CopyPro: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        
        return success_rate >= 75.0  # 75% mínimo de precisión
        
    except Exception as e:
        print_error(f"Error en test de Lucía CopyPro: {e}")
        return False


async def test_marcos_multitask_matching():
    """Test 2: Matching específico para Marcos Multitask (Operations)."""
    print_test_header("Marcos Multitask - Operations Manager")
    
    try:
        openai_client = OpenAIClient()
        extract_use_case = ExtractUserInfoUseCase(openai_client)
        
        test_cases = [
            {
                'name': 'Operations Manager + Manufactura',
                'conversation': """
                Nombre: Marcos Rodríguez
                Rol: Gerente de Operaciones
                Conversación:
                - Dirijo las operaciones de nuestra planta manufacturera
                - Tenemos 120 empleados en producción
                - Los procesos manuales nos están matando en costos
                - Necesito automatizar reportes de inventario y calidad
                """,
                'expected': 'marcos_multitask'
            },
            {
                'name': 'Plant Manager + Eficiencia',
                'conversation': """
                Nombre: Roberto Silva
                Rol: Plant Manager
                Conversación:
                - Manejo la planta de producción
                - Efficiency y productividad operativa son clave
                - Reportes de producción toman mucho tiempo manual
                - Necesito streamline operations urgentemente
                """,
                'expected': 'marcos_multitask'
            },
            {
                'name': 'Director Operativo + Procesos',
                'conversation': """
                Nombre: Ana Herrera
                Rol: Director Operativo
                Conversación:
                - Superviso todos los procesos empresariales
                - Fábrica con 80 empleados, muchas ineficiencias
                - Control de inventario es un nightmare manual
                - Necesito optimizar workflows ya
                """,
                'expected': 'marcos_multitask'
            }
        ]
        
        results = []
        
        for case in test_cases:
            print_info(f"🧪 Probando: {case['name']}")
            
            user_memory = LeadMemory(
                user_id="test_marcos",
                name="Test User",
                role="Operations Manager"
            )
            
            user_memory.add_context_entry(case['conversation'])
            
            insights = await extract_use_case.extract_insights_from_conversation(
                user_memory=user_memory,
                recent_messages=[case['conversation']]
            )
            
            expected = case['expected']
            actual = insights.buyer_persona_match
            
            print_result(expected, actual, 0.0, insights.confidence_score)
            
            is_correct = (expected == actual)
            results.append(is_correct)
        
        success_rate = sum(results) / len(results) * 100
        print_info(f"📊 Tasa de éxito Marcos Multitask: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        
        return success_rate >= 75.0
        
    except Exception as e:
        print_error(f"Error en test de Marcos Multitask: {e}")
        return False


async def test_sofia_visionaria_matching():
    """Test 3: Matching específico para Sofía Visionaria (CEO/Founder)."""
    print_test_header("Sofía Visionaria - CEO/Founder")
    
    try:
        openai_client = OpenAIClient()
        extract_use_case = ExtractUserInfoUseCase(openai_client)
        
        test_cases = [
            {
                'name': 'CEO + Estrategia Empresarial',
                'conversation': """
                Nombre: Sofía Vázquez
                Rol: CEO
                Conversación:
                - Soy CEO de una consultora de 95 empleados
                - La competencia feroz está afectando crecimiento
                - Necesito estrategia empresarial más inteligente
                - Falta innovación en nuestros servicios profesionales
                """,
                'expected': 'sofia_visionaria'
            },
            {
                'name': 'Founder + Scale-up',
                'conversation': """
                Nombre: Diego Morales
                Rol: Founder
                Conversación:
                - Fundé esta startup hace 3 años
                - Ahora somos 60 personas, necesitamos escalar
                - El crecimiento se está estancando
                - Busco ventaja competitiva con AI
                """,
                'expected': 'sofia_visionaria'
            },
            {
                'name': 'Director General + Transformación',
                'conversation': """
                Nombre: Patricia López
                Rol: Director General
                Conversación:
                - Dirijo una empresa de servicios profesionales
                - 110 empleados, necesitamos transformación digital urgente
                - La competencia avanza más rápido que nosotros
                - Decisiones estratégicas necesitan más datos
                """,
                'expected': 'sofia_visionaria'
            }
        ]
        
        results = []
        
        for case in test_cases:
            print_info(f"🧪 Probando: {case['name']}")
            
            user_memory = LeadMemory(
                user_id="test_sofia",
                name="Test User",
                role="CEO"
            )
            
            user_memory.add_context_entry(case['conversation'])
            
            insights = await extract_use_case.extract_insights_from_conversation(
                user_memory=user_memory,
                recent_messages=[case['conversation']]
            )
            
            expected = case['expected']
            actual = insights.buyer_persona_match
            
            print_result(expected, actual, 0.0, insights.confidence_score)
            
            is_correct = (expected == actual)
            results.append(is_correct)
        
        success_rate = sum(results) / len(results) * 100
        print_info(f"📊 Tasa de éxito Sofía Visionaria: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        
        return success_rate >= 75.0
        
    except Exception as e:
        print_error(f"Error en test de Sofía Visionaria: {e}")
        return False


async def test_edge_cases_matching():
    """Test 4: Casos extremos y límites del sistema."""
    print_test_header("Casos Extremos y Límites")
    
    try:
        openai_client = OpenAIClient()
        extract_use_case = ExtractUserInfoUseCase(openai_client)
        
        test_cases = [
            {
                'name': 'Información muy limitada',
                'conversation': """
                Nombre: Juan
                Rol: Manager
                Conversación: Hola, trabajo en una empresa.
                """,
                'expected': 'unknown'
            },
            {
                'name': 'Rol no empresarial',
                'conversation': """
                Nombre: Pedro
                Rol: Estudiante
                Conversación: Soy estudiante de marketing, estoy haciendo mi tesis sobre IA.
                """,
                'expected': 'unknown'
            },
            {
                'name': 'Multiple señales mezcladas',
                'conversation': """
                Nombre: Alex Multi
                Rol: Business Manager
                Conversación:
                - Manejo tanto marketing digital como operaciones
                - También hago análisis de datos y reclutamiento
                - Mi empresa tiene de todo: manufactura, agencia, consultoría
                """,
                'expected': 'unknown'  # Demasiado ambiguo
            }
        ]
        
        results = []
        
        for case in test_cases:
            print_info(f"🧪 Probando: {case['name']}")
            
            user_memory = LeadMemory(
                user_id="test_edge",
                name="Test User",
                role="Manager"
            )
            
            user_memory.add_context_entry(case['conversation'])
            
            insights = await extract_use_case.extract_insights_from_conversation(
                user_memory=user_memory,
                recent_messages=[case['conversation']]
            )
            
            expected = case['expected']
            actual = insights.buyer_persona_match
            
            print_result(expected, actual, 0.0, insights.confidence_score)
            
            is_correct = (expected == actual)
            results.append(is_correct)
        
        success_rate = sum(results) / len(results) * 100
        print_info(f"📊 Tasa de éxito Casos Extremos: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        
        return success_rate >= 66.0  # Más permisivo para casos extremos
        
    except Exception as e:
        print_error(f"Error en test de casos extremos: {e}")
        return False


async def run_buyer_persona_matching_tests():
    """Ejecuta todos los tests de buyer persona matching mejorado."""
    print("🚀 INICIANDO TESTS DE BUYER PERSONA MATCHING MEJORADO")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Lucía CopyPro
    lucia_ok = await test_lucia_copypro_matching()
    test_results.append(("Lucía CopyPro Matching", lucia_ok))
    
    # Test 2: Marcos Multitask
    marcos_ok = await test_marcos_multitask_matching()
    test_results.append(("Marcos Multitask Matching", marcos_ok))
    
    # Test 3: Sofía Visionaria
    sofia_ok = await test_sofia_visionaria_matching()
    test_results.append(("Sofía Visionaria Matching", sofia_ok))
    
    # Test 4: Casos extremos
    edge_ok = await test_edge_cases_matching()
    test_results.append(("Casos Extremos", edge_ok))
    
    # Resumen final
    print_test_header("RESUMEN DE RESULTADOS")
    
    all_passed = True
    for test_name, result in test_results:
        if result:
            print_success(f"{test_name}: PASÓ")
        else:
            print_error(f"{test_name}: FALLÓ")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ Buyer persona matching mejorado funcional")
        print("✅ Mayor precisión en detección específica")
        print("✅ Mejor manejo de casos extremos")
        print("✅ Patrones avanzados funcionando correctamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("⚠️  Revisar implementación de matching")
        print("")
        print("🔧 POSIBLES MEJORAS:")
        print("  1. Ajustar thresholds de confianza")
        print("  2. Mejorar keywords específicos")
        print("  3. Balancear peso de categorías")
        print("  4. Refinar prompts de OpenAI")
    
    print("=" * 60)
    return all_passed


async def main():
    """Función principal."""
    try:
        success = await run_buyer_persona_matching_tests()
        
        if success:
            print("\n🚀 BUYER PERSONA MATCHING MEJORADO Y FUNCIONAL")
            return 0
        else:
            print("\n⚠️  BUYER PERSONA MATCHING NECESITA AJUSTES")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido por usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    # Ejecutar tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)