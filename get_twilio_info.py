#!/usr/bin/env python3
"""
Script para obtener información de la cuenta de Twilio
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

def get_account_info():
    """Obtener información de la cuenta de Twilio"""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("❌ Error: TWILIO_ACCOUNT_SID o TWILIO_AUTH_TOKEN no configurados")
        return
    
    print("🔍 Información de la cuenta de Twilio")
    print("=" * 40)
    
    # Obtener información de la cuenta
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}.json"
    response = requests.get(url, auth=(account_sid, auth_token))
    
    if response.status_code == 200:
        account_info = response.json()
        print(f"📋 Nombre de la cuenta: {account_info.get('friendly_name', 'N/A')}")
        print(f"📋 Estado: {account_info.get('status', 'N/A')}")
        print(f"📋 Tipo: {account_info.get('type', 'N/A')}")
    else:
        print(f"❌ Error obteniendo información de la cuenta: {response.status_code}")
        print(f"📋 Respuesta: {response.text}")
        return
    
    # Obtener números de teléfono
    print("\n📱 Números de teléfono disponibles:")
    print("-" * 40)
    
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/IncomingPhoneNumbers.json"
    response = requests.get(url, auth=(account_sid, auth_token))
    
    if response.status_code == 200:
        numbers = response.json()["incoming_phone_numbers"]
        
        if not numbers:
            print("❌ No hay números de teléfono en esta cuenta")
            print("💡 Para usar WhatsApp Sandbox:")
            print("   1. Ve a Twilio Console → Messaging → Settings → WhatsApp Sandbox")
            print("   2. Copia el número que aparece ahí")
            print("   3. Actualiza TWILIO_PHONE_NUMBER en tu archivo .env")
        else:
            for i, number in enumerate(numbers, 1):
                print(f"{i}. Número: {number.get('phone_number', 'N/A')}")
                print(f"   SID: {number.get('sid', 'N/A')}")
                print(f"   Nombre: {number.get('friendly_name', 'N/A')}")
                print(f"   Estado: {number.get('status', 'N/A')}")
                print()
    else:
        print(f"❌ Error obteniendo números: {response.status_code}")
        print(f"📋 Respuesta: {response.text}")

def main():
    """Función principal"""
    print("🔍 TWILIO ACCOUNT INFO")
    print("=" * 40)
    
    # Cargar variables de entorno
    load_env()
    
    # Obtener información
    get_account_info()
    
    print("\n💡 Próximos pasos:")
    print("1. Copia el número de WhatsApp Sandbox de la lista arriba")
    print("2. Actualiza TWILIO_PHONE_NUMBER en tu archivo .env")
    print("3. Ejecuta: python switch_webhook.py")

if __name__ == "__main__":
    main() 