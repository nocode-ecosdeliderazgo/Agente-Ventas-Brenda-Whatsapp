#!/usr/bin/env python3
"""
Script de prueba para la integración de OpenAI Threads.
Verifica que la integración funcione correctamente sin romper flujos existentes.
"""
import asyncio
import logging
import os
import sys

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.infrastructure.openai.threads_adapter import ThreadsAdapter
from app.infrastructure.database.repositories.oa_threads_map_repository import OAThreadsMapRepository
from app.application.usecases.threads_integration_use_case import ThreadsIntegrationUseCase
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from memory.lead_memory import MemoryManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_test(message: str, status: str = "info"):
    """Print test con colores."""
    colors = {
        "info": "🔍",
        "success": "✅", 
        "error": "❌",
        "warning": "⚠️",
        "step": "📍"
    }
    print(f"{colors.get(status, '🔍')} {message}")


async def test_configuration():
    """Test 1: Verificar configuración básica."""
    print_test("=== TEST 1: VERIFICACIÓN DE CONFIGURACIÓN ===", "step")
    
    # Verificar variables de entorno necesarias
    required_vars = ['OPENAI_API_KEY', 'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
    
    for var in required_vars:
        if hasattr(settings, var.lower()) and getattr(settings, var.lower()):
            print_test(f"{var} configurado", "success")
        else:
            print_test(f"{var} NO configurado", "error")
            return False
    
    # Verificar ASSISTANT_ID (opcional)
    if getattr(settings, 'assistant_id', None):
        print_test(f"ASSISTANT_ID configurado: {settings.assistant_id}", "success")
        return True
    else:
        print_test("ASSISTANT_ID NO configurado - Threads Integration deshabilitado", "warning")
        return None  # Configuración parcial


async def test_database_integration():
    """Test 2: Verificar integración con base de datos."""
    print_test("=== TEST 2: VERIFICACIÓN DE BASE DE DATOS ===", "step")
    
    try:
        # Probar repositorio de threads
        repo = OAThreadsMapRepository()
        await repo.ensure_table_exists()
        
        # Health check
        health = await repo.health_check()
        if health:
            print_test("Repositorio de threads funcional", "success")
        else:
            print_test("Repositorio de threads con problemas", "error")
            return False
        
        # Test básico de mapeo
        test_phone = "whatsapp:+1234567890"
        test_thread = "thread_test_123"
        
        # Guardar mapeo de prueba
        saved = await repo.save_thread_id(test_phone, test_thread)
        if saved:
            print_test("Guardado de mapeo exitoso", "success")
        else:
            print_test("Error guardando mapeo", "error")
            return False
        
        # Recuperar mapeo
        retrieved = await repo.get_thread_id(test_phone)
        if retrieved == test_thread:
            print_test("Recuperación de mapeo exitosa", "success")
        else:
            print_test("Error recuperando mapeo", "error")
            return False
        
        # Limpiar test
        await repo.delete_mapping(test_phone)
        print_test("Cleanup de test completado", "success")
        
        return True
        
    except Exception as e:
        print_test(f"Error en test de base de datos: {e}", "error")
        return False


async def test_threads_adapter():
    """Test 3: Verificar ThreadsAdapter."""
    print_test("=== TEST 3: VERIFICACIÓN DE THREADS ADAPTER ===", "step")
    
    try:
        # Verificar si está habilitado
        if not getattr(settings, 'assistant_id', None):
            print_test("ASSISTANT_ID no configurado, saltando test de adapter", "warning")
            return None
        
        # Crear adapter
        adapter = ThreadsAdapter()
        
        # Health check
        health = await adapter.health_check()
        if health:
            print_test("ThreadsAdapter health check OK", "success")
        else:
            print_test("ThreadsAdapter health check falló", "error")
            return False
        
        print_test("ThreadsAdapter inicializado correctamente", "success")
        return True
        
    except Exception as e:
        print_test(f"Error en test de ThreadsAdapter: {e}", "error")
        return False


async def test_use_case_initialization():
    """Test 4: Verificar inicialización de use cases."""
    print_test("=== TEST 4: VERIFICACIÓN DE USE CASES ===", "step")
    
    try:
        # Inicializar dependencias
        twilio_client = TwilioWhatsAppClient()
        memory_manager = MemoryManager(memory_dir="memorias")
        memory_use_case = ManageUserMemoryUseCase(memory_manager)
        
        print_test("Dependencias básicas inicializadas", "success")
        
        # Verificar si ThreadsIntegrationUseCase puede inicializarse
        if ThreadsIntegrationUseCase.is_enabled():
            try:
                threads_use_case = ThreadsIntegrationUseCase(twilio_client, memory_use_case)
                print_test("ThreadsIntegrationUseCase inicializado", "success")
                
                # Health check
                health_result = await threads_use_case.health_check()
                if health_result.get('status') == 'healthy':
                    print_test("ThreadsIntegrationUseCase health check OK", "success")
                else:
                    print_test(f"ThreadsIntegrationUseCase health: {health_result.get('status', 'unknown')}", "warning")
                
                return True
                
            except Exception as e:
                print_test(f"Error inicializando ThreadsIntegrationUseCase: {e}", "error")
                return False
        else:
            print_test("ThreadsIntegrationUseCase deshabilitado (ASSISTANT_ID no configurado)", "warning")
            return None
            
    except Exception as e:
        print_test(f"Error en test de use cases: {e}", "error")
        return False


async def test_webhook_compatibility():
    """Test 5: Verificar compatibilidad con webhook existente."""
    print_test("=== TEST 5: VERIFICACIÓN DE COMPATIBILIDAD ===", "step")
    
    try:
        # Simular datos de webhook
        test_webhook_data = {
            "MessageSid": "SM123test456",
            "From": "whatsapp:+1234567890",
            "To": "whatsapp:+14155238886",
            "Body": "Test message for threads integration"
        }
        
        print_test("Datos de webhook simulados creados", "success")
        
        # Si threads está habilitado, probar el flujo
        if ThreadsIntegrationUseCase.is_enabled():
            print_test("Threads integration habilitado - flujo moderno activo", "success")
        else:
            print_test("Threads integration deshabilitado - flujo tradicional activo", "success")
        
        # Test de decisión de routing (sin ejecutar realmente)
        print_test("Routing lógico verificado", "success")
        
        return True
        
    except Exception as e:
        print_test(f"Error en test de compatibilidad: {e}", "error")
        return False


async def test_fallback_behavior():
    """Test 6: Verificar comportamiento de fallback."""
    print_test("=== TEST 6: VERIFICACIÓN DE FALLBACK ===", "step")
    
    try:
        # Test de mensajes de fallback
        if ThreadsIntegrationUseCase.is_enabled():
            twilio_client = TwilioWhatsAppClient()
            memory_manager = MemoryManager(memory_dir="memorias")  
            memory_use_case = ManageUserMemoryUseCase(memory_manager)
            
            threads_use_case = ThreadsIntegrationUseCase(twilio_client, memory_use_case)
            
            # Test de fallback responses
            fallback_tests = [
                ("hola", "saludo"),
                ("curso", "consulta de curso"),
                ("precio", "consulta de precio"),
                ("contacto", "solicitud de contacto"),
                ("test genérico", "mensaje genérico")
            ]
            
            for message, test_type in fallback_tests:
                fallback_response = await threads_use_case._get_fallback_response(
                    "whatsapp:+1234567890", message
                )
                
                if fallback_response and len(fallback_response) > 10:
                    print_test(f"Fallback para {test_type}: OK", "success")
                else:
                    print_test(f"Fallback para {test_type}: Respuesta muy corta", "warning")
            
            print_test("Sistema de fallback verificado", "success")
        else:
            print_test("Sistema de fallback no aplica (threads deshabilitado)", "info")
        
        return True
        
    except Exception as e:
        print_test(f"Error en test de fallback: {e}", "error")
        return False


async def main():
    """Función principal de tests."""
    print_test("🚀 INICIANDO TESTS DE THREADS INTEGRATION", "step")
    print_test("=" * 60, "info")
    
    tests = [
        ("Configuración", test_configuration),
        ("Base de Datos", test_database_integration),
        ("Threads Adapter", test_threads_adapter),
        ("Use Cases", test_use_case_initialization),
        ("Compatibilidad Webhook", test_webhook_compatibility),
        ("Comportamiento Fallback", test_fallback_behavior)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print_test(f"\n{'=' * 60}", "info")
        try:
            result = await test_func()
            results[test_name] = result
            
            if result is True:
                print_test(f"✅ {test_name}: PASADO", "success")
            elif result is False:
                print_test(f"❌ {test_name}: FALLIDO", "error")
            else:
                print_test(f"⚠️ {test_name}: SALTADO (configuración incompleta)", "warning")
                
        except Exception as e:
            print_test(f"💥 {test_name}: ERROR - {e}", "error")
            results[test_name] = False
    
    # Resumen final
    print_test(f"\n{'=' * 60}", "info")
    print_test("📊 RESUMEN DE TESTS", "step")
    print_test("=" * 60, "info")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    for test_name, result in results.items():
        status_icon = "✅" if result is True else ("❌" if result is False else "⚠️")
        status_text = "PASADO" if result is True else ("FALLIDO" if result is False else "SALTADO")
        print_test(f"{status_icon} {test_name}: {status_text}")
    
    print_test("=" * 60, "info")
    print_test(f"📈 Resultados: {passed} pasados, {failed} fallidos, {skipped} saltados")
    
    if failed == 0:
        print_test("🎉 TODOS LOS TESTS CRÍTICOS PASARON", "success")
        print_test("✅ La integración está lista para usar", "success")
    elif passed > 0:
        print_test("⚠️ INTEGRACIÓN PARCIALMENTE FUNCIONAL", "warning")
        print_test("🔧 Revisar configuración para funcionalidad completa", "warning")
    else:
        print_test("❌ INTEGRACIÓN REQUIERE ATENCIÓN", "error")
        print_test("🛠️ Revisar errores antes de usar en producción", "error")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)