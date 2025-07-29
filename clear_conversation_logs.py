#!/usr/bin/env python3
"""
Script para limpiar los logs de conversación del simulador Brenda.
Permite eliminar logs antiguos o todos los logs.
"""
import os
import sys
from datetime import datetime

def print_header():
    """Imprime el header del limpiador de logs"""
    print("\n" + "="*80)
    print("🗑️  LIMPIADOR DE LOGS DE CONVERSACIÓN - BRENDA")
    print("="*80)
    print("📁 Directorio de logs: ./logs/")
    print("⚠️  ATENCIÓN: Esta acción eliminará archivos permanentemente")
    print("="*80)

def get_log_files():
    """Obtiene la lista de archivos de log disponibles"""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        print("❌ No existe el directorio de logs.")
        return []
    
    log_files = []
    for file in os.listdir(logs_dir):
        if file.startswith("conversation_log_") and file.endswith(".json"):
            log_files.append(os.path.join(logs_dir, file))
    
    return sorted(log_files, reverse=True)

def display_log_files(log_files):
    """Muestra los archivos de log disponibles"""
    if not log_files:
        print("❌ No se encontraron archivos de log para eliminar.")
        return
    
    print(f"\n📁 Archivos de log encontrados ({len(log_files)}):")
    for i, log_file in enumerate(log_files, 1):
        file_size = os.path.getsize(log_file)
        file_date = os.path.basename(log_file).replace('conversation_log_', '').replace('.json', '')
        print(f"   {i}. {os.path.basename(log_file)} ({file_size} bytes) - {file_date}")

def delete_log_files(log_files, indices):
    """Elimina los archivos de log especificados"""
    deleted_count = 0
    for index in indices:
        if 1 <= index <= len(log_files):
            try:
                os.remove(log_files[index - 1])
                print(f"✅ Eliminado: {os.path.basename(log_files[index - 1])}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error eliminando {os.path.basename(log_files[index - 1])}: {e}")
        else:
            print(f"❌ Índice inválido: {index}")
    
    return deleted_count

def main():
    """Función principal"""
    print_header()
    
    # Obtener archivos de log
    log_files = get_log_files()
    
    if not log_files:
        print("💡 No hay logs para limpiar. Ejecuta primero el simulador para generar logs.")
        return
    
    # Mostrar archivos disponibles
    display_log_files(log_files)
    
    # Mostrar opciones
    print("\n📋 OPCIONES:")
    print("1. Eliminar archivo específico")
    print("2. Eliminar archivos antiguos (más de 7 días)")
    print("3. Eliminar todos los logs")
    print("4. Salir sin eliminar")
    
    while True:
        try:
            choice = input("\n🎯 Selecciona una opción (1-4): ").strip()
            
            if choice == "1":
                # Eliminar archivo específico
                try:
                    file_choice = int(input("\n🎯 Selecciona número de archivo a eliminar: "))
                    if 1 <= file_choice <= len(log_files):
                        confirm = input(f"⚠️  ¿Estás seguro de eliminar {os.path.basename(log_files[file_choice - 1])}? (s/N): ")
                        if confirm.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                            deleted = delete_log_files(log_files, [file_choice])
                            print(f"\n✅ Eliminados {deleted} archivos.")
                        else:
                            print("❌ Operación cancelada.")
                    else:
                        print("❌ Opción inválida.")
                except ValueError:
                    print("❌ Por favor ingresa un número válido.")
                break
                
            elif choice == "2":
                # Eliminar archivos antiguos
                from datetime import timedelta
                cutoff_date = datetime.now() - timedelta(days=7)
                old_files = []
                
                for i, log_file in enumerate(log_files, 1):
                    file_date_str = os.path.basename(log_file).replace('conversation_log_', '').replace('.json', '')
                    try:
                        file_date = datetime.strptime(file_date_str, '%Y%m%d')
                        if file_date < cutoff_date:
                            old_files.append(i)
                    except:
                        pass
                
                if old_files:
                    print(f"\n📅 Archivos antiguos encontrados ({len(old_files)}):")
                    for i in old_files:
                        print(f"   {i}. {os.path.basename(log_files[i-1])}")
                    
                    confirm = input(f"\n⚠️  ¿Eliminar {len(old_files)} archivos antiguos? (s/N): ")
                    if confirm.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                        deleted = delete_log_files(log_files, old_files)
                        print(f"\n✅ Eliminados {deleted} archivos antiguos.")
                    else:
                        print("❌ Operación cancelada.")
                else:
                    print("✅ No se encontraron archivos antiguos para eliminar.")
                break
                
            elif choice == "3":
                # Eliminar todos los logs
                confirm = input(f"\n⚠️  ¿Eliminar TODOS los {len(log_files)} archivos de log? (s/N): ")
                if confirm.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                    all_indices = list(range(1, len(log_files) + 1))
                    deleted = delete_log_files(log_files, all_indices)
                    print(f"\n✅ Eliminados {deleted} archivos.")
                else:
                    print("❌ Operación cancelada.")
                break
                
            elif choice == "4":
                print("👋 Operación cancelada. Los logs se mantienen intactos.")
                break
                
            else:
                print("❌ Opción inválida. Selecciona 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Operación cancelada.")
            break
        except Exception as e:
            print(f"💥 Error: {e}")

if __name__ == "__main__":
    main() 