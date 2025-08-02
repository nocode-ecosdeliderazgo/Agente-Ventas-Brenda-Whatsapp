#!/usr/bin/env python3
"""
Script para verificar y corregir credenciales de Twilio
"""
import os
import requests
from pathlib import Path

def load_env():
    """Cargar variables de entorno"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value.strip('"')

def check_credentials():
    """Verificar las credenciales actuales"""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    print("🔍 Verificando credenciales actuales")
    print("=" * 40)
    print(f"📋 Account SID: {account_sid}")
    print(f"📋 Auth Token: {auth_token[:10]}..." if auth_token else "❌ No configurado")
    
    if not account_sid or not auth_token:
        print("❌ Credenciales incompletas")
        return False
    
    # Verificar si es un Account SID válido
    if account_sid.startswith("SK"):
        print("⚠️  Detectado Subaccount Key (SK) en lugar de Account SID (AC)")
        print("💡 Para subcuentas, necesitas usar el Account SID principal")
        return False
    elif not account_sid.startswith("AC"):
        print("❌ Account SID no tiene formato válido (debe empezar con AC)")
        return False
    
    # Probar las credenciales
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}.json"
    response = requests.get(url, auth=(account_sid, auth_token))
    
    if response.status_code == 200:
        print("✅ Credenciales válidas")
        return True
    else:
        print(f"❌ Error con las credenciales: {response.status_code}")
        print(f"📋 Respuesta: {response.text}")
        return False

def get_whatsapp_sandbox_info():
    """Obtener información del WhatsApp Sandbox"""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        return
    
    print("\n📱 Información del WhatsApp Sandbox")
    print("=" * 40)
    
    # Obtener números de teléfono
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/IncomingPhoneNumbers.json"
    response = requests.get(url, auth=(account_sid, auth_token))
    
    if response.status_code == 200:
        numbers = response.json()["incoming_phone_numbers"]
        
        if not numbers:
            print("❌ No hay números de teléfono en esta cuenta")
            print("💡 Para configurar WhatsApp Sandbox:")
            print("   1. Ve a Twilio Console → Messaging → Settings → WhatsApp Sandbox")
            print("   2. Sigue las instrucciones para activar el sandbox")
            print("   3. Copia el número que aparece ahí")
        else:
            print("📱 Números disponibles:")
            for i, number in enumerate(numbers, 1):
                print(f"{i}. {number.get('phone_number', 'N/A')}")
                print(f"   Nombre: {number.get('friendly_name', 'N/A')}")
                print(f"   SID: {number.get('sid', 'N/A')}")
                print()
    else:
        print(f"❌ Error obteniendo números: {response.status_code}")

def main():
    """Función principal"""
    print("🔧 TWILIO CREDENTIALS FIXER")
    print("=" * 40)
    
    # Cargar variables de entorno
    load_env()
    
    # Verificar credenciales
    if check_credentials():
        get_whatsapp_sandbox_info()
    else:
        print("\n💡 Para corregir las credenciales:")
        print("1. Ve a https://console.twilio.com/")
        print("2. Selecciona tu cuenta principal (no subcuenta)")
        print("3. Ve a Settings → API Keys & Tokens")
        print("4. Copia el Account SID (empieza con AC)")
        print("5. Copia el Auth Token")
        print("6. Actualiza tu archivo .env con estos valores")
        print("\n📝 Formato del .env:")
        print("TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("TWILIO_PHONE_NUMBER=+14155238886  # Actualizar con tu número")

if __name__ == "__main__":
    main() 