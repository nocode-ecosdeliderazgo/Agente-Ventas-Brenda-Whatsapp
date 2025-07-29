#!/usr/bin/env python3
"""
Script para visualizar los logs de conversación del simulador Brenda.
Muestra las conversaciones guardadas en formato legible.
"""
import os
import json
import sys
from datetime import datetime
from typing import List, Dict, Any

def print_header():
    """Imprime el header del visor de logs"""
    print("\n" + "="*80)
    print("📊 VISOR DE LOGS DE CONVERSACIÓN - BRENDA")
    print("="*80)
    print("📁 Directorio de logs: ./logs/")
    print("📅 Formato: conversation_log_YYYYMMDD.json")
    print("="*80)

def get_log_files() -> List[str]:
    """Obtiene la lista de archivos de log disponibles"""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        print("❌ No existe el directorio de logs. Ejecuta primero el simulador.")
        return []
    
    log_files = []
    for file in os.listdir(logs_dir):
        if file.startswith("conversation_log_") and file.endswith(".json"):
            log_files.append(os.path.join(logs_dir, file))
    
    return sorted(log_files, reverse=True)  # Más recientes primero

def load_conversation_log(log_file: str) -> List[Dict[str, Any]]:
    """Carga un archivo de log de conversación"""
    conversations = []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    conversations.append(json.loads(line))
    except Exception as e:
        print(f"❌ Error cargando log {log_file}: {e}")
    
    return conversations

def format_timestamp(timestamp: str) -> str:
    """Formatea timestamp para mostrar"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%H:%M:%S")
    except:
        return timestamp

def display_conversation(conversation: Dict[str, Any], index: int):
    """Muestra una conversación individual"""
    print(f"\n{'='*60}")
    print(f"💬 CONVERSACIÓN #{conversation.get('conversation_count', index)}")
    print(f"⏰ {format_timestamp(conversation.get('timestamp', ''))}")
    print(f"{'='*60}")
    
    # Mensaje del usuario
    user_msg = conversation.get('user_message', '')
    print(f"👤 USUARIO:")
    print(f"   {user_msg}")
    
    # Respuesta del agente
    agent_msg = conversation.get('agent_response', '')
    print(f"\n🤖 BRENDA:")
    print(f"   {agent_msg}")

def display_log_file(log_file: str):
    """Muestra el contenido de un archivo de log"""
    print(f"\n📁 ARCHIVO: {os.path.basename(log_file)}")
    print(f"📅 FECHA: {os.path.basename(log_file).replace('conversation_log_', '').replace('.json', '')}")
    
    conversations = load_conversation_log(log_file)
    
    if not conversations:
        print("❌ No se encontraron conversaciones en este archivo.")
        return
    
    print(f"💬 Total de conversaciones: {len(conversations)}")
    
    # Mostrar cada conversación
    for i, conversation in enumerate(conversations, 1):
        display_conversation(conversation, i)
    
    print(f"\n{'='*60}")
    print(f"✅ Fin del archivo: {len(conversations)} conversaciones mostradas")

def main():
    """Función principal"""
    print_header()
    
    # Obtener archivos de log
    log_files = get_log_files()
    
    if not log_files:
        print("❌ No se encontraron archivos de log.")
        print("💡 Ejecuta primero: python test_console_simulation.py")
        return
    
    print(f"📁 Archivos de log encontrados: {len(log_files)}")
    
    # Mostrar opciones
    print("\n📋 OPCIONES:")
    print("1. Ver conversación más reciente")
    print("2. Ver todas las conversaciones")
    print("3. Ver conversación específica por fecha")
    print("4. Salir")
    
    while True:
        try:
            choice = input("\n🎯 Selecciona una opción (1-4): ").strip()
            
            if choice == "1":
                # Mostrar archivo más reciente
                if log_files:
                    display_log_file(log_files[0])
                break
                
            elif choice == "2":
                # Mostrar todos los archivos
                for log_file in log_files:
                    display_log_file(log_file)
                    input("\n⏸️  Presiona Enter para continuar...")
                break
                
            elif choice == "3":
                # Mostrar archivo específico
                print("\n📅 Archivos disponibles:")
                for i, log_file in enumerate(log_files, 1):
                    date = os.path.basename(log_file).replace('conversation_log_', '').replace('.json', '')
                    print(f"   {i}. {date}")
                
                try:
                    file_choice = int(input("\n🎯 Selecciona número de archivo: "))
                    if 1 <= file_choice <= len(log_files):
                        display_log_file(log_files[file_choice - 1])
                    else:
                        print("❌ Opción inválida.")
                except ValueError:
                    print("❌ Por favor ingresa un número válido.")
                break
                
            elif choice == "4":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción inválida. Selecciona 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"💥 Error: {e}")

if __name__ == "__main__":
    main() 