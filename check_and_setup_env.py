#!/usr/bin/env python3
"""
Script para verificar y configurar variables de entorno en Heroku
Bot Brenda WhatsApp 2025
"""
import subprocess
import json
import sys

# Configuración de la aplicación
APP_NAME = "brenda-whatsapp-bot-2025"

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Stderr: {e.stderr}")
        return None

def get_current_config():
    """Obtiene la configuración actual de Heroku"""
    print("📋 Verificando configuración actual...")
    
    command = f"heroku config --app {APP_NAME} --json"
    result = run_command(command, "Obteniendo configuración actual")
    
    if result:
        try:
            config = json.loads(result)
            return config
        except json.JSONDecodeError:
            print("❌ Error al parsear la configuración JSON")
            return {}
    return {}

def check_required_variables():
    """Define las variables requeridas y sus valores por defecto"""
    return {
        # Variables requeridas (sin valor por defecto)
        "required": [
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN", 
            "TWILIO_PHONE_NUMBER",
            "OPENAI_API_KEY"
        ],
        
        # Variables con valores por defecto
        "with_defaults": {
            "APP_ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO",
            "WEBHOOK_VERIFY_SIGNATURE": "false",
            "ADVISOR_PHONE_NUMBER": "+52 1 56 1468 6075",
            "ADVISOR_NAME": "Especialista en IA",
            "ADVISOR_TITLE": "Asesor Comercial",
            "ALLOWED_WEBHOOK_IPS": "*"
        },
        
        # Variables opcionales
        "optional": [
            "DATABASE_URL",
            "NGROK_URL"
        ]
    }

def analyze_configuration(current_config, required_vars):
    """Analiza la configuración actual y determina qué falta"""
    print("\n🔍 ANALIZANDO CONFIGURACIÓN ACTUAL")
    print("=" * 50)
    
    missing_required = []
    missing_defaults = []
    configured_vars = []
    
    # Verificar variables requeridas
    for var in required_vars["required"]:
        if var in current_config:
            configured_vars.append(f"✅ {var}")
        else:
            missing_required.append(var)
            print(f"❌ FALTA: {var} (REQUERIDA)")
    
    # Verificar variables con valores por defecto
    for var, default_value in required_vars["with_defaults"].items():
        if var in current_config:
            configured_vars.append(f"✅ {var} = {current_config[var]}")
        else:
            missing_defaults.append((var, default_value))
            print(f"⚠️  FALTA: {var} (se configurará con valor por defecto)")
    
    # Mostrar variables opcionales configuradas
    for var in required_vars["optional"]:
        if var in current_config:
            configured_vars.append(f"✅ {var} = {current_config[var]}")
    
    # Mostrar variables configuradas
    if configured_vars:
        print(f"\n✅ VARIABLES CONFIGURADAS ({len(configured_vars)}):")
        for var in configured_vars:
            print(f"   {var}")
    
    return missing_required, missing_defaults

def setup_missing_variables(missing_defaults):
    """Configura las variables que faltan con valores por defecto"""
    if not missing_defaults:
        print("\n✅ Todas las variables con valores por defecto ya están configuradas")
        return True
    
    print(f"\n🔧 CONFIGURANDO {len(missing_defaults)} VARIABLES FALTANTES")
    print("=" * 50)
    
    success_count = 0
    for var, default_value in missing_defaults:
        command = f"heroku config:set {var}={default_value} --app {APP_NAME}"
        result = run_command(command, f"Configurando {var}")
        if result:
            success_count += 1
            print(f"   ✅ {var} = {default_value}")
        else:
            print(f"   ❌ Error configurando {var}")
    
    print(f"\n📊 Resultado: {success_count}/{len(missing_defaults)} variables configuradas")
    return success_count == len(missing_defaults)

def show_required_setup(missing_required):
    """Muestra las variables que el usuario debe configurar manualmente"""
    if not missing_required:
        print("\n🎉 ¡TODAS LAS VARIABLES REQUERIDAS ESTÁN CONFIGURADAS!")
        return
    
    print(f"\n⚠️  VARIABLES REQUERIDAS FALTANTES ({len(missing_required)})")
    print("=" * 60)
    print("Debes configurar estas variables manualmente con tus credenciales:")
    print()
    
    for var in missing_required:
        if var == "TWILIO_ACCOUNT_SID":
            print(f"heroku config:set {var}=tu_account_sid --app {APP_NAME}")
            print("   # Obtén desde: https://console.twilio.com/")
        elif var == "TWILIO_AUTH_TOKEN":
            print(f"heroku config:set {var}=tu_auth_token --app {APP_NAME}")
            print("   # Obtén desde: https://console.twilio.com/")
        elif var == "TWILIO_PHONE_NUMBER":
            print(f"heroku config:set {var}=tu_numero_twilio --app {APP_NAME}")
            print("   # Ejemplo: +14155238886")
        elif var == "OPENAI_API_KEY":
            print(f"heroku config:set {var}=tu_openai_api_key --app {APP_NAME}")
            print("   # Obtén desde: https://platform.openai.com/api-keys")
        print()

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN DE VARIABLES DE ENTORNO - BOT BRENDA WHATSAPP 2025")
    print("=" * 70)
    print(f"🎯 Aplicación: {APP_NAME}")
    print("=" * 70)
    
    # Obtener configuración actual
    current_config = get_current_config()
    
    # Definir variables requeridas
    required_vars = check_required_variables()
    
    # Analizar configuración
    missing_required, missing_defaults = analyze_configuration(current_config, required_vars)
    
    # Configurar variables con valores por defecto
    if missing_defaults:
        response = input(f"\n¿Deseas configurar las {len(missing_defaults)} variables faltantes con valores por defecto? (s/n): ").strip().lower()
        if response in ['s', 'si', 'y', 'yes']:
            setup_missing_variables(missing_defaults)
        else:
            print("❌ Configuración automática cancelada")
    
    # Mostrar variables requeridas faltantes
    show_required_setup(missing_required)
    
    # Resumen final
    print("\n📊 RESUMEN FINAL")
    print("=" * 30)
    print(f"✅ Variables configuradas: {len(current_config)}")
    print(f"❌ Variables requeridas faltantes: {len(missing_required)}")
    print(f"⚠️  Variables con valores por defecto faltantes: {len(missing_defaults)}")
    
    if not missing_required and not missing_defaults:
        print("\n🎉 ¡CONFIGURACIÓN COMPLETA!")
        print("La aplicación está lista para ser desplegada.")
    else:
        print("\n⚠️  CONFIGURACIÓN INCOMPLETA")
        print("Completa las variables faltantes antes de desplegar.")

if __name__ == "__main__":
    main() 