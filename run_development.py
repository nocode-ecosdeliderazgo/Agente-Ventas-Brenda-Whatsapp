#!/usr/bin/env python3
"""
Script para ejecutar el bot en modo desarrollo local
Usa variables de entorno locales sin afectar producción
"""
import os
import sys
from pathlib import Path

# Cargar variables de entorno locales
def load_local_env():
    """Carga variables de entorno desde .env.local"""
    env_file = Path(".env.local")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value.strip('"')
        print("✅ Variables de entorno locales cargadas")
    else:
        print("⚠️ Archivo .env.local no encontrado, usando variables del sistema")

if __name__ == "__main__":
    print("🚀 BRENDA WHATSAPP BOT - MODO DESARROLLO")
    print("=" * 50)
    
    # Cargar variables locales
    load_local_env()
    
    # Verificar variables críticas
    required_vars = [
        "OPENAI_API_KEY",
        "TWILIO_ACCOUNT_SID", 
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "DATABASE_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables faltantes: {missing_vars}")
        print("Por favor, configura las variables en .env.local")
        sys.exit(1)
    
    print("✅ Todas las variables configuradas")
    print("🎯 Iniciando simulation en modo desarrollo...")
    print("📝 NOTA: Este es el modo de desarrollo, NO afecta producción")
    print("=" * 50)
    
    # Ejecutar simulation
    try:
        from test_webhook_simulation import main
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Desarrollo terminado por el usuario")
    except Exception as e:
        print(f"❌ Error en desarrollo: {e}")
        sys.exit(1) 