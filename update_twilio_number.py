#!/usr/bin/env python3
"""
Script para actualizar el número de Twilio en la configuración.
"""
import os
import re

def update_twilio_number(new_number: str):
    """Actualiza el número de Twilio en los archivos de configuración"""
    print(f"🔄 Actualizando número de Twilio a: {new_number}")
    
    # Asegurar que el número tenga el formato correcto
    if not new_number.startswith('+'):
        new_number = '+' + new_number
    
    # Archivos a actualizar
    files_to_update = [
        'config/twilio_settings.py',
        'test_integrated_privacy_flow.py',
        'test_privacy_flow.py',
        'test_memory_system.py',
        'test_integration_logic_only.py'
    ]
    
    updated_files = []
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar y reemplazar el número anterior
                old_pattern = r'\+14155238886'
                new_content = re.sub(old_pattern, new_number, content)
                
                if content != new_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updated_files.append(file_path)
                    print(f"✅ Actualizado: {file_path}")
                else:
                    print(f"ℹ️ Sin cambios: {file_path}")
                    
            except Exception as e:
                print(f"❌ Error actualizando {file_path}: {e}")
        else:
            print(f"⚠️ Archivo no encontrado: {file_path}")
    
    print(f"\n📊 Resumen:")
    print(f"   Archivos actualizados: {len(updated_files)}")
    print(f"   Nuevo número: {new_number}")
    
    if updated_files:
        print(f"\n✅ ¡Número de Twilio actualizado exitosamente!")
        print(f"🔧 Recuerda actualizar también:")
        print(f"   1. La URL del webhook en Twilio Console")
        print(f"   2. Las variables de entorno en tu .env")
    else:
        print(f"\n⚠️ No se encontraron archivos para actualizar")

def main():
    """Función principal"""
    print("🔄 ACTUALIZADOR DE NÚMERO TWILIO")
    print("=" * 40)
    
    # Solicitar el nuevo número
    new_number = input("📱 Ingresa el nuevo número de Twilio (ej: 14155238886): ").strip()
    
    if not new_number:
        print("❌ No se ingresó ningún número")
        return
    
    # Actualizar el número
    update_twilio_number(new_number)

if __name__ == "__main__":
    main() 