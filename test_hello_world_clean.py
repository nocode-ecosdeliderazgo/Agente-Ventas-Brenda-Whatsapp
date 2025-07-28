#!/usr/bin/env python3
"""
Script de prueba "Hola Mundo" usando la nueva arquitectura limpia.
=================================================================

Este script demuestra cómo enviar mensajes usando la arquitectura Clean Architecture
que hemos implementado, con separación clara de responsabilidades.

Uso:
    python test_hello_world_clean.py

Asegúrate de tener configurado tu archivo .env con las credenciales de Twilio.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.application.usecases.send_hello_world import SendHelloWorldUseCase

# Configurar logging
logging.basicConfig(
    level=settings.get_log_level(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verificar_configuracion() -> bool:
    """
    Verifica que la configuración esté completa.
    
    Returns:
        True si la configuración es válida
    """
    print("🔧 Verificando configuración...")
    
    try:
        # Intentar acceder a la configuración
        _ = settings.twilio_account_sid
        _ = settings.twilio_auth_token
        _ = settings.twilio_phone_number
        
        if not settings.twilio_account_sid or settings.twilio_account_sid == "your_twilio_account_sid_here":
            print("❌ TWILIO_ACCOUNT_SID no configurado")
            return False
            
        if not settings.twilio_auth_token or settings.twilio_auth_token == "your_twilio_auth_token_here":
            print("❌ TWILIO_AUTH_TOKEN no configurado")
            return False
            
        if not settings.twilio_phone_number or settings.twilio_phone_number == "your_twilio_phone_number_here":
            print("❌ TWILIO_PHONE_NUMBER no configurado")
            return False
            
        print("✅ Configuración válida")
        print(f"📱 Número Twilio: {settings.twilio_phone_number}")
        print(f"🌍 Entorno: {settings.app_environment}")
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        print("\n📝 INSTRUCCIONES:")
        print("1. Copia .env.example a .env")
        print("2. Configura tus credenciales de Twilio en .env")
        print("3. Ejecuta este script nuevamente")
        return False


async def enviar_hola_mundo(numero_destino: str, platform: str = "whatsapp"):
    """
    Envía un mensaje "Hola Mundo" usando la nueva arquitectura.
    
    Args:
        numero_destino: Número de teléfono destino
        platform: Plataforma de envío ("whatsapp" o "sms")
    """
    try:
        print(f"\n🚀 Iniciando envío via {platform.upper()}...")
        print(f"📱 Destino: {numero_destino}")
        print("-" * 50)
        
        # Crear instancias siguiendo la arquitectura
        twilio_client = TwilioWhatsAppClient()
        hello_world_use_case = SendHelloWorldUseCase(twilio_client)
        
        # Ejecutar caso de uso
        resultado = await hello_world_use_case.execute(numero_destino, platform)
        
        # Mostrar resultado
        if resultado['success']:
            print("✅ ¡MENSAJE ENVIADO EXITOSAMENTE!")
            print(f"📋 SID: {resultado['message_sid']}")
            print(f"📊 Estado: {resultado['status']}")
            print(f"📅 Timestamp: {resultado['timestamp']}")
            print(f"🏗️ Caso de uso: {resultado['use_case']}")
            
            if platform == "whatsapp":
                print(f"\n💬 El mensaje fue enviado a WhatsApp del número {numero_destino}")
            else:
                print(f"\n📨 El mensaje SMS fue enviado al número {numero_destino}")
                
        else:
            print("❌ ERROR AL ENVIAR MENSAJE")
            print(f"🔍 Error: {resultado['error']}")
            print("\n🛠️ Posibles soluciones:")
            print("- Verifica las credenciales de Twilio")
            print("- Asegúrate de tener saldo en tu cuenta Twilio")
            print("- Verifica que el número esté en formato internacional")
            if platform == "whatsapp":
                print("- Confirma que tienes WhatsApp Business API habilitado")
        
        return resultado
        
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        return {'success': False, 'error': str(e)}


def mostrar_menu():
    """Muestra el menú de opciones."""
    print("\n" + "=" * 60)
    print("🤖 BOT BRENDA - PRUEBA HOLA MUNDO (ARQUITECTURA LIMPIA)")
    print("=" * 60)
    print("\n📱 ¿Qué tipo de mensaje quieres enviar?")
    print("1. WhatsApp (recomendado)")
    print("2. SMS")
    print("3. Ambos (WhatsApp + SMS)")
    print("0. Salir")


async def main():
    """Función principal del script."""
    print("🚀 INICIANDO PRUEBA DE ARQUITECTURA LIMPIA")
    print("=" * 50)
    
    # Verificar configuración
    if not verificar_configuracion():
        return
    
    # Número de destino (el que usabas en el legacy)
    NUMERO_DESTINO = '+5215572246258'
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSelecciona una opción (0-3): ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
                
            elif opcion == "1":
                print("\n📱 Enviando WhatsApp...")
                await enviar_hola_mundo(NUMERO_DESTINO, "whatsapp")
                
            elif opcion == "2":
                print("\n📨 Enviando SMS...")
                await enviar_hola_mundo(NUMERO_DESTINO, "sms")
                
            elif opcion == "3":
                print("\n📱📨 Enviando ambos...")
                print("\n1. Enviando WhatsApp...")
                resultado_wa = await enviar_hola_mundo(NUMERO_DESTINO, "whatsapp")
                
                print("\n2. Enviando SMS...")
                resultado_sms = await enviar_hola_mundo(NUMERO_DESTINO, "sms")
                
                print(f"\n📊 RESUMEN:")
                print(f"WhatsApp: {'✅' if resultado_wa['success'] else '❌'}")
                print(f"SMS: {'✅' if resultado_sms['success'] else '❌'}")
                
            else:
                print("❌ Opción inválida. Intenta de nuevo.")
                
            input("\n📝 Presiona Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n💥 Error: {e}")
            input("📝 Presiona Enter para continuar...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Script interrumpido por el usuario")
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        sys.exit(1)