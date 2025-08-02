#!/usr/bin/env python3
"""
Script para automatizar el despliegue a Heroku
"""
import os
import subprocess
import sys
from pathlib import Path

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

def create_heroku_app(app_name):
    """Crea una nueva aplicación en Heroku"""
    print(f"🚀 Creando aplicación Heroku: {app_name}")
    
    # Verificar si la app ya existe
    result = run_command(f"heroku apps:info --app {app_name}", "Verificando si la app existe")
    if result is not None:
        print(f"✅ La aplicación {app_name} ya existe")
        return True
    
    # Crear nueva app
    result = run_command(f"heroku create {app_name}", "Creando nueva aplicación")
    return result is not None

def setup_environment_variables(app_name):
    """Configura las variables de entorno en Heroku"""
    print("🔧 Configurando variables de entorno...")
    
    # Variables requeridas
    env_vars = {
        "APP_ENVIRONMENT": "production",
        "OPENAI_API_KEY": "REQUIRED",  # El usuario debe configurar esto
        "TWILIO_ACCOUNT_SID": "REQUIRED",
        "TWILIO_AUTH_TOKEN": "REQUIRED", 
        "TWILIO_PHONE_NUMBER": "REQUIRED",
        "DATABASE_URL": "REQUIRED"
    }
    
    for key, value in env_vars.items():
        if value == "REQUIRED":
            print(f"⚠️  IMPORTANTE: Debes configurar {key} manualmente:")
            print(f"   heroku config:set {key}=tu_valor --app {app_name}")
        else:
            run_command(f"heroku config:set {key}={value} --app {app_name}", f"Configurando {key}")

def deploy_to_heroku(app_name):
    """Despliega la aplicación a Heroku"""
    print(f"🚀 Desplegando a Heroku: {app_name}")
    
    # Agregar Heroku como remote
    run_command("git remote add heroku https://git.heroku.com/{app_name}.git", "Agregando remote de Heroku")
    
    # Push a Heroku
    result = run_command(f"git push heroku main", "Desplegando aplicación")
    
    if result:
        print("✅ Despliegue completado exitosamente!")
        print(f"🌍 URL de la aplicación: https://{app_name}.herokuapp.com")
        return True
    else:
        print("❌ Error en el despliegue")
        return False

def main():
    """Función principal"""
    print("🚀 DESPLIEGUE A HEROKU - BOT BRENDA WHATSAPP")
    print("=" * 50)
    
    # Verificar Heroku CLI
    if not check_heroku_cli():
        print("❌ Por favor instala Heroku CLI primero:")
        print("   https://devcenter.heroku.com/articles/heroku-cli")
        return
    
    # Solicitar nombre de la app
    app_name = input("📝 Ingresa el nombre para tu app Heroku (o presiona Enter para auto-generar): ").strip()
    
    if not app_name:
        app_name = "brenda-whatsapp-bot"
    
    print(f"🎯 Usando nombre de app: {app_name}")
    
    # Crear app
    if not create_heroku_app(app_name):
        print("❌ No se pudo crear la aplicación")
        return
    
    # Configurar variables de entorno
    setup_environment_variables(app_name)
    
    # Desplegar
    if deploy_to_heroku(app_name):
        print("\n🎉 ¡DESPLIEGUE COMPLETADO!")
        print(f"🌍 URL: https://{app_name}.herokuapp.com")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Configura las variables de entorno requeridas:")
        print(f"   heroku config:set OPENAI_API_KEY=tu_api_key --app {app_name}")
        print(f"   heroku config:set TWILIO_ACCOUNT_SID=tu_sid --app {app_name}")
        print(f"   heroku config:set TWILIO_AUTH_TOKEN=tu_token --app {app_name}")
        print(f"   heroku config:set TWILIO_PHONE_NUMBER=tu_numero --app {app_name}")
        print(f"   heroku config:set DATABASE_URL=tu_url_db --app {app_name}")
        print("2. Configura la URL del webhook en Twilio Console:")
        print(f"   https://{app_name}.herokuapp.com/webhook")
        print("3. Prueba enviando un mensaje desde WhatsApp")
    else:
        print("❌ Error en el despliegue")

if __name__ == "__main__":
    main() 