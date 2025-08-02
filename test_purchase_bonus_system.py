#!/usr/bin/env python3
"""
Test del sistema de bonos por intención de compra.
Prueba la detección de intención de compra y activación automática de bonos workbook.
"""
import asyncio
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from app.application.usecases.purchase_bonus_use_case import PurchaseBonusUseCase
from memory.lead_memory import LeadMemory, MemoryManager
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase


async def test_purchase_intent_detection():
    """Test detección de intención de compra."""
    print("🧪 TESTING: Purchase Intent Detection")
    print("=" * 50)
    
    purchase_bonus_use_case = PurchaseBonusUseCase()
    
    # Test cases para intención de compra
    test_cases = [
        {
            'name': 'Intención directa de compra',
            'intent_analysis': {
                'category': 'PURCHASE_INTENT_DIRECT',
                'confidence': 0.9,
                'buying_signals_detected': ['quiero comprarlo', 'cómo pago']
            },
            'should_activate': True
        },
        {
            'name': 'Pregunta de precio',
            'intent_analysis': {
                'category': 'PURCHASE_INTENT_PRICING',
                'confidence': 0.8,
                'buying_signals_detected': ['cuánto cuesta', 'precio']
            },
            'should_activate': True
        },
        {
            'name': 'Señales de estar listo',
            'intent_analysis': {
                'category': 'PURCHASE_READY_SIGNALS',
                'confidence': 0.85,
                'buying_signals_detected': ['ya decidí', 'cuándo empiezo']
            },
            'should_activate': True
        },
        {
            'name': 'Múltiples señales de compra',
            'intent_analysis': {
                'category': 'GENERAL_INQUIRY',
                'confidence': 0.6,
                'buying_signals_detected': ['me interesa', 'quiero más información', 'cómo empiezo']
            },
            'should_activate': True  # Por múltiples señales
        },
        {
            'name': 'No intención de compra',
            'intent_analysis': {
                'category': 'GENERAL_INQUIRY',
                'confidence': 0.7,
                'buying_signals_detected': []
            },
            'should_activate': False
        },
        {
            'name': 'Confianza baja',
            'intent_analysis': {
                'category': 'PURCHASE_INTENT_DIRECT',
                'confidence': 0.5,  # Bajo threshold
                'buying_signals_detected': ['tal vez']
            },
            'should_activate': False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Categoría: {test_case['intent_analysis']['category']}")
        print(f"   Confianza: {test_case['intent_analysis']['confidence']}")
        print(f"   Señales: {test_case['intent_analysis']['buying_signals_detected']}")
        
        should_activate = purchase_bonus_use_case.should_activate_purchase_bonus(test_case['intent_analysis'])
        expected = test_case['should_activate']
        
        if should_activate == expected:
            print(f"   ✅ PASS - {'Activaría bonos' if should_activate else 'No activaría bonos'}")
        else:
            print(f"   ❌ FAIL - Esperado: {expected}, Obtenido: {should_activate}")
    
    print("\n" + "=" * 50)


async def test_workbook_bonuses():
    """Test obtención de bonos workbook."""
    print("🧪 TESTING: Workbook Bonuses Retrieval")
    print("=" * 50)
    
    purchase_bonus_use_case = PurchaseBonusUseCase()
    
    # Test obtención de bonos
    workbook_bonuses = await purchase_bonus_use_case.get_workbook_bonuses()
    
    print(f"📚 Bonos workbook encontrados: {len(workbook_bonuses)}")
    
    for i, bonus in enumerate(workbook_bonuses, 1):
        print(f"\n{i}. {bonus['title']}")
        print(f"   ID: {bonus['id']}")
        print(f"   Descripción: {bonus['description']}")
        print(f"   URL: {bonus['url']}")
        print(f"   Tipo: {bonus['type']}")
        print(f"   Sesión: {bonus['session']}")
    
    if workbook_bonuses:
        print("\n✅ Bonos workbook cargados correctamente")
    else:
        print("\n❌ No se encontraron bonos workbook")
    
    print("\n" + "=" * 50)


async def test_purchase_bonus_message():
    """Test generación de mensaje de bono por compra."""
    print("🧪 TESTING: Purchase Bonus Message Generation")  
    print("=" * 50)
    
    # Crear memoria de usuario de prueba
    user_memory = LeadMemory()
    user_memory.user_id = "test_user_001" 
    user_memory.name = "Juan Pérez"
    user_memory.role = "Director de Marketing"
    user_memory.buyer_persona_match = "lucia_copypro"
    user_memory.interaction_count = 5
    user_memory.lead_score = 75
    
    # Análisis de intención de compra
    intent_analysis = {
        'category': 'PURCHASE_INTENT_DIRECT',
        'confidence': 0.9,
        'buying_signals_detected': ['quiero comprarlo', 'cómo pago'],
        'buyer_persona_match': 'lucia_copypro'
    }
    
    purchase_bonus_use_case = PurchaseBonusUseCase()
    
    # Generar mensaje de bono
    bonus_message = await purchase_bonus_use_case.generate_purchase_bonus_message(
        user_memory, intent_analysis
    )
    
    print("📝 MENSAJE DE BONO GENERADO:")
    print("-" * 30)
    print(bonus_message)
    print("-" * 30)
    
    # Verificar elementos clave
    checks = [
        ("Personalización con nombre", "Juan" in bonus_message),
        ("Menciona bono especial", "BONO" in bonus_message.upper()),
        ("Incluye URL de workbook", "https://coda.io" in bonus_message),
        ("Call-to-action presente", "inscripción" in bonus_message.lower() or "proceso" in bonus_message.lower()),
        ("ROI específico por persona", "campaña" in bonus_message.lower())  # Para lucia_copypro
    ]
    
    print("\n🔍 VERIFICACIONES:")
    for check_name, check_result in checks:
        status = "✅ PASS" if check_result else "❌ FAIL"
        print(f"   {status} - {check_name}")
    
    print("\n" + "=" * 50)


async def test_memory_update():
    """Test actualización de memoria con intención de compra."""
    print("🧪 TESTING: Memory Update with Purchase Intent")
    print("=" * 50)
    
    # Configurar sistema de memoria
    memory_manager = MemoryManager()
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    purchase_bonus_use_case = PurchaseBonusUseCase(memory_use_case=memory_use_case)
    
    user_id = "test_user_002"
    
    # Crear memoria inicial
    initial_memory = memory_use_case.get_user_memory(user_id)
    initial_memory.name = "María González"
    initial_memory.role = "CEO"
    initial_score = initial_memory.lead_score
    initial_signals = len(initial_memory.buying_signals)
    
    print(f"👤 Usuario: {initial_memory.name}")
    print(f"📊 Score inicial: {initial_score}")
    print(f"🎯 Señales iniciales: {initial_signals}")
    
    # Análisis de intención de compra
    intent_analysis = {
        'category': 'PURCHASE_READY_SIGNALS',
        'confidence': 0.85,
        'buying_signals_detected': ['ya decidí', 'cuándo empiezo']
    }
    
    # Actualizar memoria
    await purchase_bonus_use_case.update_user_memory_with_purchase_intent(
        user_id, intent_analysis
    )
    
    # Verificar cambios
    updated_memory = memory_use_case.get_user_memory(user_id)
    final_score = updated_memory.lead_score
    final_signals = len(updated_memory.buying_signals)
    
    print(f"\n📈 DESPUÉS DE ACTUALIZACIÓN:")
    print(f"📊 Score final: {final_score} (cambio: +{final_score - initial_score})")
    print(f"🎯 Señales finales: {final_signals} (cambio: +{final_signals - initial_signals})")
    print(f"🔥 Interest level: {updated_memory.interest_level}")
    
    # Verificar historial
    if updated_memory.message_history:
        latest_entry = updated_memory.message_history[-1]
        print(f"\n📝 Última entrada del historial:")
        print(f"   Acción: {latest_entry.get('action')}")
        print(f"   Categoría: {latest_entry.get('category')}")
        print(f"   Confianza: {latest_entry.get('confidence')}")
    
    # Limpiar memoria de prueba
    memory_manager.clear_user_memory(user_id)
    
    print(f"\n✅ Memoria actualizada correctamente")
    print("\n" + "=" * 50)


async def main():
    """Ejecutar todas las pruebas."""
    print("🚀 INICIANDO TESTS DEL SISTEMA DE BONOS POR COMPRA")
    print("=" * 60)
    
    try:
        await test_purchase_intent_detection()
        await test_workbook_bonuses()
        await test_purchase_bonus_message()
        await test_memory_update()
        
        print("\n🎉 ¡TODOS LOS TESTS COMPLETADOS!")
        
    except Exception as e:
        print(f"\n❌ ERROR EN TESTS: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())