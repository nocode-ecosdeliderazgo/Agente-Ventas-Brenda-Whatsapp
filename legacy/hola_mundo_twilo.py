"""
Script para enviar "Hola Mundo" usando Twilio
=============================================
Este script usa la API REST de Twilio para enviar un mensaje SMS/WhatsApp
al número: +52 1 55 7224 6258
"""

from twilio.rest import Client
import os
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN DE TWILIO
# ============================================================================

# Credenciales de Twilio (debes obtenerlas de tu cuenta de Twilio)
# Puedes obtenerlas en: https://console.twilio.com/
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '') 
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')  # Tu número de Twilio

# Número de destino (el que proporcionaste)
NUMERO_DESTINO = '+5215572246258'  # Formato internacional

def enviar_hola_mundo():
    """
    Envía un mensaje "Hola Mundo" usando Twilio REST API.
    
    Returns:
        dict: Resultado del envío con información del mensaje
    """
    try:
        # Inicializar cliente de Twilio
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Mensaje a enviar
        mensaje = f"¡Hola Mundo! 🌟\n\nEste es un mensaje de prueba enviado desde Python usando Twilio.\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        
        print(f"📱 Enviando mensaje a: {NUMERO_DESTINO}")
        print(f"📄 Mensaje: {mensaje}")
        print(f"📞 Desde número: {TWILIO_PHONE_NUMBER}")
        print("-" * 50)
        
        # Enviar mensaje SMS
        message = client.messages.create(
            body=mensaje,
            from_=TWILIO_PHONE_NUMBER,
            to=NUMERO_DESTINO
        )
        
        resultado = {
            'success': True,
            'message_sid': message.sid,
            'status': message.status,
            'direction': message.direction,
            'from_number': message.from_,
            'to_number': message.to,
            'date_created': message.date_created,
            'price': message.price,
            'uri': message.uri
        }
        
        print("✅ ¡Mensaje enviado exitosamente!")
        print(f"📋 SID del mensaje: {message.sid}")
        print(f"📊 Estado: {message.status}")
        print(f"💰 Precio: {message.price}")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def enviar_hola_mundo_whatsapp():
    """
    Envía un mensaje "Hola Mundo" por WhatsApp usando Twilio.
    
    Nota: Requiere que tengas configurado WhatsApp Business API con Twilio
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        mensaje = f"¡Hola Mundo desde WhatsApp! 🚀\n\nEste mensaje fue enviado usando la API de Twilio para WhatsApp.\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        
        print(f"📱 Enviando WhatsApp a: {NUMERO_DESTINO}")
        print(f"📄 Mensaje: {mensaje}")
        print("-" * 50)
        
        # Para WhatsApp, usar el formato whatsapp:+numero
        message = client.messages.create(
            body=mensaje,
            from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',  # Tu número de WhatsApp Business
            to=f'whatsapp:{NUMERO_DESTINO}'
        )
        
        print("✅ ¡Mensaje de WhatsApp enviado exitosamente!")
        print(f"📋 SID del mensaje: {message.sid}")
        print(f"📊 Estado: {message.status}")
        
        return {
            'success': True,
            'message_sid': message.sid,
            'status': message.status,
            'platform': 'whatsapp'
        }
        
    except Exception as e:
        print(f"❌ Error al enviar WhatsApp: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'platform': 'whatsapp'
        }

def verificar_configuracion():
    """
    Verifica que las credenciales de Twilio estén configuradas.
    """
    print("🔧 Verificando configuración de Twilio...")
    
    if TWILIO_ACCOUNT_SID == 'tu_account_sid_aqui':
        print("⚠️  ATENCIÓN: Necesitas configurar tu TWILIO_ACCOUNT_SID")
        return False
    
    if TWILIO_AUTH_TOKEN == 'tu_auth_token_aqui':
        print("⚠️  ATENCIÓN: Necesitas configurar tu TWILIO_AUTH_TOKEN")
        return False
        
    if TWILIO_PHONE_NUMBER == '+1234567890':
        print("⚠️  ATENCIÓN: Necesitas configurar tu TWILIO_PHONE_NUMBER")
        return False
    
    print("✅ Configuración básica completa")
    return True

if __name__ == "__main__":
    print("🚀 SCRIPT DE ENVÍO - HOLA MUNDO CON TWILIO")
    print("=" * 50)
    
    # Verificar configuración
    if not verificar_configuracion():
        print("\n📝 INSTRUCCIONES PARA CONFIGURAR:")
        print("1. Crea una cuenta en Twilio: https://console.twilio.com/")
        print("2. Obtén tu Account SID y Auth Token")
        print("3. Compra un número de teléfono en Twilio")
        print("4. Configura las variables de entorno o edita el script:")
        print("   - TWILIO_ACCOUNT_SID")
        print("   - TWILIO_AUTH_TOKEN") 
        print("   - TWILIO_PHONE_NUMBER")
        print("\n💡 Puedes usar variables de entorno o editar directamente el código")
        exit(1)
    
    # Menú de opciones
    print("\n📱 ¿Qué tipo de mensaje quieres enviar?")
    print("1. SMS (recomendado para pruebas)")
    print("2. WhatsApp (requiere WhatsApp Business API)")
    
    opcion = input("\nSelecciona una opción (1 o 2): ").strip()
    
    if opcion == "1":
        print("\n📨 Enviando SMS...")
        resultado = enviar_hola_mundo()
    elif opcion == "2":
        print("\n📱 Enviando WhatsApp...")
        resultado = enviar_hola_mundo_whatsapp()
    else:
        print("❌ Opción inválida")
        exit(1)
    
    # Mostrar resultado final
    if resultado['success']:
        print(f"\n🎉 ¡ÉXITO! Mensaje enviado al {NUMERO_DESTINO}")
        print(f"📋 ID del mensaje: {resultado['message_sid']}")
    else:
        print(f"\n💥 Error: {resultado['error']}")
        print("\n🔍 Posibles causas:")
        print("- Credenciales incorrectas")
        print("- Número de Twilio no verificado")
        print("- Saldo insuficiente en cuenta Twilio")
        print("- Número de destino en formato incorrecto") 