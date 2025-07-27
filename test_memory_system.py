#!/usr/bin/env python3
"""
Script para probar el sistema de memoria del bot Brenda.
"""
import os
import sys
import logging
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory.lead_memory import MemoryManager, LeadMemory
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.domain.entities.message import IncomingMessage, MessageType

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_memory_system():
    """Prueba completa del sistema de memoria."""
    print("🧠 Iniciando pruebas del sistema de memoria...")
    
    # 1. Crear manager de memoria
    print("\n1️⃣ Creando MemoryManager...")
    memory_manager = MemoryManager(memory_dir="test_memorias")
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    print("✅ MemoryManager creado")
    
    # 2. Probar obtención de memoria nueva
    print("\n2️⃣ Probando obtención de memoria nueva...")
    test_user_id = "1234567890"
    user_memory = memory_use_case.get_user_memory(test_user_id)
    print(f"✅ Memoria obtenida: user_id={user_memory.user_id}, stage={user_memory.stage}")
    
    # 3. Probar actualización de nombre
    print("\n3️⃣ Probando actualización de nombre...")
    user_memory = memory_use_case.update_user_name(test_user_id, "María González")
    print(f"✅ Nombre actualizado: {user_memory.name}")
    
    # 4. Probar actualización de etapa
    print("\n4️⃣ Probando actualización de etapa...")
    user_memory = memory_use_case.update_user_stage(test_user_id, "engaged")
    print(f"✅ Etapa actualizada: {user_memory.stage}")
    
    # 5. Probar agregación de interés
    print("\n5️⃣ Probando agregación de interés...")
    user_memory = memory_use_case.add_user_interest(test_user_id, "automatización")
    print(f"✅ Interés agregado: {user_memory.interests}")
    
    # 6. Probar actualización de lead score
    print("\n6️⃣ Probando actualización de lead score...")
    user_memory = memory_use_case.update_lead_score(test_user_id, 10, "Mostró interés en automatización")
    print(f"✅ Lead score actualizado: {user_memory.lead_score}")
    
    # 7. Crear mensaje simulado para probar actualización con mensaje
    print("\n7️⃣ Probando actualización con mensaje...")
    mock_message = IncomingMessage(
        message_sid="TEST123",
        from_number="+1234567890",
        to_number="+14155238886",
        body="Hola, me interesa el curso de IA",
        message_type=MessageType.TEXT,
        timestamp=datetime.now(),
        raw_data={"From": "whatsapp:+1234567890"}
    )
    
    extracted_info = {
        "pain_points": ["falta de automatización"],
        "buying_signals": ["interés expresado"],
        "interest_level": "medium"
    }
    
    user_memory = memory_use_case.update_user_memory(
        test_user_id, 
        mock_message, 
        extracted_info
    )
    print(f"✅ Memoria actualizada con mensaje:")
    print(f"   - Interacciones: {user_memory.interaction_count}")
    print(f"   - Mensajes en historial: {len(user_memory.message_history)}")
    print(f"   - Pain points: {user_memory.pain_points}")
    print(f"   - Buying signals: {user_memory.buying_signals}")
    print(f"   - Interest level: {user_memory.interest_level}")
    
    # 8. Probar persistencia - obtener memoria desde archivo
    print("\n8️⃣ Probando persistencia...")
    # Limpiar cache para forzar carga desde archivo
    memory_manager.leads_cache.clear()
    
    # Obtener memoria nuevamente (debería cargar desde JSON)
    reloaded_memory = memory_use_case.get_user_memory(test_user_id)
    print(f"✅ Memoria recargada desde archivo:")
    print(f"   - Nombre: {reloaded_memory.name}")
    print(f"   - Etapa: {reloaded_memory.stage}")
    print(f"   - Interacciones: {reloaded_memory.interaction_count}")
    print(f"   - Lead score: {reloaded_memory.lead_score}")
    
    # 9. Verificar archivo JSON creado
    print("\n9️⃣ Verificando archivo JSON...")
    json_file = f"test_memorias/memory_{test_user_id}.json"
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            import json
            data = json.load(f)
        print(f"✅ Archivo JSON creado exitosamente:")
        print(f"   - Archivo: {json_file}")
        print(f"   - Tamaño: {len(json.dumps(data, indent=2))} caracteres")
        print(f"   - Keys: {list(data.keys())}")
    else:
        print(f"❌ Archivo JSON no encontrado: {json_file}")
    
    print("\n🎉 ¡Todas las pruebas del sistema de memoria completadas exitosamente!")
    print(f"📁 Los archivos de prueba están en: test_memorias/")

def cleanup_test_files():
    """Limpia archivos de prueba."""
    import shutil
    test_dir = "test_memorias"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"🧹 Archivos de prueba eliminados: {test_dir}/")

if __name__ == "__main__":
    try:
        test_memory_system()
        
        # Preguntar si limpiar archivos de prueba
        response = input("\n¿Eliminar archivos de prueba? (y/N): ").lower().strip()
        if response == 'y':
            cleanup_test_files()
        else:
            print("📁 Archivos de prueba conservados en test_memorias/")
            
    except Exception as e:
        print(f"💥 Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)