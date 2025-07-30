#!/usr/bin/env python3
"""
Script de prueba simple para verificar que el sistema funciona correctamente.
"""
import os
import sys
import asyncio

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.database.client import DatabaseClient
from memory.lead_memory import MemoryManager

async def test_basic_system():
    """Prueba básica del sistema"""
    print("🧪 PRUEBA BÁSICA DEL SISTEMA BRENDA")
    print("="*50)
    
    try:
        # 1. Verificar configuración
        print("1. ✅ Verificando configuración...")
        print(f"   OpenAI API Key: {'✅' if settings.openai_api_key else '❌'}")
        print(f"   Database URL: {'✅' if settings.database_url else '❌'}")
        
        # 2. Probar cliente OpenAI
        print("\n2. 🤖 Probando cliente OpenAI...")
        openai_client = OpenAIClient()
        print("   ✅ Cliente OpenAI inicializado")
        
        # 3. Probar base de datos
        print("\n3. 🗄️ Probando base de datos...")
        db_client = DatabaseClient()
        await db_client.connect()
        print("   ✅ Base de datos conectada")
        
        # 4. Probar memoria
        print("\n4. 💾 Probando sistema de memoria...")
        memory_manager = MemoryManager(memory_dir="memorias")
        print("   ✅ Sistema de memoria inicializado")
        
        # 5. Prueba de memoria
        test_user_id = "test_user_001"
        memory = memory_manager.get_user_memory(test_user_id)
        memory.add_interaction("Hola", "¡Hola! ¿Cómo estás?")
        print(f"   ✅ Memoria guardada para usuario {test_user_id}")
        
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("✅ El sistema está listo para usar")
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        return False
    
    return True

async def main():
    """Función principal"""
    success = await test_basic_system()
    
    if success:
        print("\n🚀 Puedes ejecutar el simulador completo con:")
        print("   python test_webhook_simulation.py")
    else:
        print("\n🔧 Revisa la configuración antes de continuar")

if __name__ == "__main__":
    asyncio.run(main()) 