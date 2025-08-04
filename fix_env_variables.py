#!/usr/bin/env python3
"""
Script para configurar las variables de entorno que fallaron
Bot Brenda WhatsApp 2025
"""
import subprocess

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

def fix_variables_with_spaces():
    """Configura las variables que tienen espacios en sus valores"""
    print("🔧 CONFIGURANDO VARIABLES CON ESPACIOS")
    print("=" * 50)
    
    # Variables que necesitan comillas por tener espacios
    variables_to_fix = [
        ("ADVISOR_PHONE_NUMBER", "+52 1 56 1468 6075"),
        ("ADVISOR_NAME", "Especialista en IA"),
        ("ADVISOR_TITLE", "Asesor Comercial")
    ]
    
    success_count = 0
    for var, value in variables_to_fix:
        # Usar comillas dobles para valores con espacios
        command = f'heroku config:set {var}="{value}" --app {APP_NAME}'
        result = run_command(command, f"Configurando {var}")
        if result:
            success_count += 1
            print(f"   ✅ {var} = {value}")
        else:
            print(f"   ❌ Error configurando {var}")
    
    print(f"\n📊 Resultado: {success_count}/{len(variables_to_fix)} variables configuradas")
    return success_count == len(variables_to_fix)

def show_current_status():
    """Muestra el estado actual de las variables"""
    print("\n📋 ESTADO ACTUAL DE LAS VARIABLES")
    print("=" * 50)
    
    # Variables que deberían estar configuradas
    expected_vars = [
        "APP_ENVIRONMENT",
        "LOG_LEVEL", 
        "WEBHOOK_VERIFY_SIGNATURE",
        "ADVISOR_PHONE_NUMBER",
        "ADVISOR_NAME",
        "ADVISOR_TITLE",
        "ALLOWED_WEBHOOK_IPS"
    ]
    
    for var in expected_vars:
        command = f"heroku config:get {var} --app {APP_NAME}"
        result = run_command(command, f"Verificando {var}")
        if result:
            print(f"✅ {var} = {result.strip()}")
        else:
            print(f"❌ {var} = NO CONFIGURADA")

def main():
    """Función principal"""
    print("🔧 CORRECCIÓN DE VARIABLES DE ENTORNO - BOT BRENDA WHATSAPP 2025")
    print("=" * 70)
    print(f"🎯 Aplicación: {APP_NAME}")
    print("=" * 70)
    
    # Configurar variables con espacios
    fix_variables_with_spaces()
    
    # Mostrar estado actual
    show_current_status()
    
    print("\n📋 RESUMEN DE VARIABLES REQUERIDAS")
    print("=" * 50)
    print("Las siguientes variables deben configurarse manualmente:")
    print()
    print("heroku config:set TWILIO_ACCOUNT_SID=tu_account_sid --app brenda-whatsapp-bot-2025")
    print("heroku config:set TWILIO_AUTH_TOKEN=tu_auth_token --app brenda-whatsapp-bot-2025")
    print("heroku config:set TWILIO_PHONE_NUMBER=tu_numero_twilio --app brenda-whatsapp-bot-2025")
    print("heroku config:set OPENAI_API_KEY=tu_openai_api_key --app brenda-whatsapp-bot-2025")
    print()
    print("Opcional:")
    print("heroku config:set DATABASE_URL=tu_database_url --app brenda-whatsapp-bot-2025")

if __name__ == "__main__":
    main() 