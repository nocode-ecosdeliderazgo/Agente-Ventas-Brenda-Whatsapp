#!/usr/bin/env python3
"""
Script para configurar WhatsApp Sandbox y actualizar el .env
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

def update_env_file(new_phone_number):
    """Actualizar el archivo .env con el nuevo número"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        return False
    
    # Leer el archivo actual
    with open(env_file, "r") as f:
        lines = f.readlines()
    
    # Buscar y actualizar la línea TWILIO_PHONE_NUMBER
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("TWILIO_PHONE_NUMBER="):
            lines[i] = f"TWILIO_PHONE_NUMBER={new_phone_number}\n"
            updated = True
            break
    
    if not updated:
        # Si no existe, agregar después de las credenciales de Twilio
        for i, line in enumerate(lines):
            if line.startswith("TWILIO_AUTH_TOKEN="):
                lines.insert(i + 1, f"TWILIO_PHONE_NUMBER={new_phone_number}\n")
                break
    
    # Escribir el archivo actualizado
    with open(env_file, "w") as f:
        f.writelines(lines)
    
    print(f"✅ Archivo .env actualizado con el número: {new_phone_number}")
    return True

def test_whatsapp_number(phone_number):
    """Probar si el número de WhatsApp está configurado correctamente"""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("❌ Credenciales de Twilio no configuradas")
        return False
    
    # Buscar el número en la cuenta
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/IncomingPhoneNumbers.json"
    response = requests.get(url, auth=(account_sid, auth_token))
    
    if response.status_code == 200:
        numbers = response.json()["incoming_phone_numbers"]
        
        for number in numbers:
            if phone_number in number.get("phone_number", ""):
                print(f"✅ Número encontrado: {number.get('phone_number')}")
                print(f"📋 SID: {number.get('sid')}")
                print(f"📋 Estado: {number.get('status')}")
                return True
        
        print(f"❌ Número {phone_number} no encontrado en tu cuenta")
        return False
    else:
        print(f"❌ Error verificando números: {response.status_code}")
        return False

def main():
    """Función principal"""
    print("📱 WHATSAPP SANDBOX SETUP")
    print("=" * 40)
    
    # Cargar variables de entorno
    load_env()
    
    print("💡 Para configurar WhatsApp Sandbox:")
    print("1. Ve a https://console.twilio.com/")
    print("2. Selecciona tu subcuenta")
    print("3. Ve a Messaging → Settings → WhatsApp Sandbox")
    print("4. Configura el sandbox y copia el número")
    print()
    
    # Solicitar el número
    current_number = os.getenv("TWILIO_PHONE_NUMBER", "")
    print(f"📋 Número actual en .env: {current_number}")
    
    new_number = input("\n📱 Ingresa el número de WhatsApp Sandbox (ej: +14155238886): ").strip()
    
    if not new_number:
        print("❌ No se ingresó ningún número")
        return
    
    # Normalizar el número (quitar espacios, guiones, etc.)
    new_number = new_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    print(f"\n🔍 Verificando número: {new_number}")
    
    # Probar el número
    if test_whatsapp_number(new_number):
        # Actualizar el archivo .env
        if update_env_file(new_number):
            print("\n🎉 ¡Configuración completada!")
            print("💡 Ahora puedes ejecutar: python switch_webhook.py")
        else:
            print("❌ Error actualizando el archivo .env")
    else:
        print("\n❌ El número no está configurado en tu cuenta")
        print("💡 Asegúrate de:")
        print("   1. Haber configurado el WhatsApp Sandbox en Twilio Console")
        print("   2. Usar el número correcto de tu sandbox")
        print("   3. Tener permisos en la subcuenta")

if __name__ == "__main__":
    main() 