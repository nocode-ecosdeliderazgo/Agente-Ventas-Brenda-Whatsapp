#!/usr/bin/env python3
"""
Script para actualizar la URL del webhook en el código.
"""
import os
import re

def update_webhook_url(new_url: str):
    """Actualiza la URL del webhook en el código"""
    print(f"🔄 Actualizando URL del webhook a: {new_url}")
    
    # Asegurar que la URL termine con /
    if not new_url.endswith('/'):
        new_url = new_url + '/'
    
    # Archivo a actualizar
    file_path = 'app/presentation/api/webhook.py'
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar y reemplazar la URL anterior
            old_pattern = r'url_for_validation = "https://cute-kind-dog\.ngrok-free\.app/"'
            new_pattern = f'url_for_validation = "{new_url}"'
            
            new_content = re.sub(old_pattern, new_pattern, content)
            
            if content != new_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Actualizado: {file_path}")
                print(f"   URL anterior: https://cute-kind-dog.ngrok-free.app/")
                print(f"   URL nueva: {new_url}")
            else:
                print(f"ℹ️ Sin cambios: {file_path}")
                
        except Exception as e:
            print(f"❌ Error actualizando {file_path}: {e}")
    else:
        print(f"⚠️ Archivo no encontrado: {file_path}")

def main():
    """Función principal"""
    print("🔄 ACTUALIZADOR DE URL WEBHOOK")
    print("=" * 40)
    
    # Solicitar la nueva URL
    new_url = input("🌐 Ingresa la nueva URL del webhook (ej: https://tu-tunnel.ngrok.io): ").strip()
    
    if not new_url:
        print("❌ No se ingresó ninguna URL")
        return
    
    # Actualizar la URL
    update_webhook_url(new_url)
    
    print(f"\n📋 PRÓXIMOS PASOS:")
    print(f"1. Asegúrate de que la URL en Twilio Console sea: {new_url}webhook")
    print(f"2. Reinicia el servidor webhook")
    print(f"3. Prueba enviando un mensaje de WhatsApp")

if __name__ == "__main__":
    main() 