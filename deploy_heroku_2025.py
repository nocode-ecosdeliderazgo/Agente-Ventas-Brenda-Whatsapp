#!/usr/bin/env python3
"""
Script para automatizar el despliegue a Heroku 2025
Bot Brenda WhatsApp - Nueva Aplicación
"""
import os
import subprocess
import sys
from pathlib import Path

# Configuración de la aplicación
APP_NAME = "brenda-whatsapp-bot-2025"
HEROKU_GIT_URL = "https://git.heroku.com/brenda-whatsapp-bot-2025.git"

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

def check_heroku_cli():
    """Verifica si Heroku CLI está instalado"""
    try:
        result = subprocess.run("heroku --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Heroku CLI encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Heroku CLI no encontrado")
            return False
    except FileNotFoundError:
        print("❌ Heroku CLI no está instalado")
        return False

def setup_basic_config():
    """Configura las variables básicas de entorno"""
    print("🔧 Configurando variables básicas de entorno...")
    
    basic_configs = [
        ("APP_ENVIRONMENT", "production"),
        ("LOG_LEVEL", "INFO"),
        ("WEBHOOK_VERIFY_SIGNATURE", "false"),
        ("ADVISOR_PHONE_NUMBER", "+52 1 56 1468 6075"),
        ("ADVISOR_NAME", "Especialista en IA"),
        ("ADVISOR_TITLE", "Asesor Comercial")
    ]
    
    for key, value in basic_configs:
        command = f"heroku config:set {key}={value} --app {APP_NAME}"
        result = run_command(command, f"Configurando {key}")
        if result is None:
            print(f"⚠️  No se pudo configurar {key}")

def setup_required_config():
    """Muestra las variables que el usuario debe configurar manualmente"""
    print("\n⚠️  VARIABLES REQUERIDAS - CONFIGURAR MANUALMENTE:")
    print("=" * 60)
    
    required_vars = [
        ("TWILIO_ACCOUNT_SID", "Tu Account SID de Twilio"),
        ("TWILIO_AUTH_TOKEN", "Tu Auth Token de Twilio"),
        ("TWILIO_PHONE_NUMBER", "Tu número de Twilio (ej: +14155238886)"),
        ("OPENAI_API_KEY", "Tu API Key de OpenAI"),
        ("DATABASE_URL", "URL de tu base de datos (opcional)")
    ]
    
    for var_name, description in required_vars:
        print(f"heroku config:set {var_name}=tu_valor --app {APP_NAME}")
        print(f"   # {description}")
        print()

def add_heroku_remote():
    """Agrega el remote de Heroku"""
    print("🔗 Configurando remote de Heroku...")
    
    # Verificar si ya existe el remote
    result = run_command("git remote -v", "Verificando remotes existentes")
    if result and "heroku-2025" in result:
        print("✅ Remote heroku-2025 ya existe")
        return True
    
    # Agregar nuevo remote
    command = f"git remote add heroku-2025 {HEROKU_GIT_URL}"
    result = run_command(command, "Agregando remote de Heroku")
    return result is not None

def commit_changes():
    """Hace commit de los cambios actuales"""
    print("📝 Preparando commit...")
    
    # Agregar todos los archivos
    result = run_command("git add .", "Agregando archivos al staging")
    if result is None:
        return False
    
    # Hacer commit
    commit_message = "Despliegue Bot Brenda WhatsApp 2025 - Versión actualizada con mejoras"
    command = f'git commit -m "{commit_message}"'
    result = run_command(command, "Haciendo commit de cambios")
    return result is not None

def deploy_to_heroku():
    """Despliega la aplicación a Heroku"""
    print("🚀 Desplegando a Heroku...")
    
    command = "git push heroku-2025 main"
    result = run_command(command, "Desplegando aplicación")
    
    if result:
        print("✅ Despliegue completado exitosamente!")
        return True
    else:
        print("❌ Error en el despliegue")
        return False

def show_next_steps():
    """Muestra los próximos pasos"""
    print("\n🎉 ¡DESPLIEGUE COMPLETADO!")
    print("=" * 50)
    print(f"🌍 URL de la aplicación: https://{APP_NAME}-540353a4be47.herokuapp.com/")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Configura las variables de entorno requeridas:")
    print("   (Ver comandos arriba)")
    print("\n2. Configura la URL del webhook en Twilio Console:")
    print(f"   https://{APP_NAME}-540353a4be47.herokuapp.com/webhook/whatsapp")
    print("\n3. Prueba enviando un mensaje desde WhatsApp")
    print("\n4. Monitorea los logs:")
    print(f"   heroku logs --tail --app {APP_NAME}")

def main():
    """Función principal"""
    print("🚀 DESPLIEGUE A HEROKU 2025 - BOT BRENDA WHATSAPP")
    print("=" * 60)
    print(f"🎯 Aplicación: {APP_NAME}")
    print(f"🌍 URL: https://{APP_NAME}-540353a4be47.herokuapp.com/")
    print("=" * 60)
    
    # Verificar Heroku CLI
    if not check_heroku_cli():
        print("❌ Por favor instala Heroku CLI primero:")
        print("   https://devcenter.heroku.com/articles/heroku-cli")
        return
    
    # Configurar variables básicas
    setup_basic_config()
    
    # Mostrar variables requeridas
    setup_required_config()
    
    # Preguntar si continuar
    response = input("\n¿Deseas continuar con el despliegue? (s/n): ").strip().lower()
    if response not in ['s', 'si', 'y', 'yes']:
        print("❌ Despliegue cancelado")
        return
    
    # Agregar remote
    if not add_heroku_remote():
        print("❌ No se pudo configurar el remote de Heroku")
        return
    
    # Hacer commit
    if not commit_changes():
        print("❌ No se pudo hacer commit de los cambios")
        return
    
    # Desplegar
    if deploy_to_heroku():
        show_next_steps()
    else:
        print("❌ Error en el despliegue")

if __name__ == "__main__":
    main() 