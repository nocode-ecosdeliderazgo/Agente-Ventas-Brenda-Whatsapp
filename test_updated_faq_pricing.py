#!/usr/bin/env python3
"""
Test rápido para verificar que la información de precios FAQ esté actualizada correctamente.
"""

import asyncio
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.faq.faq_processor import FAQProcessor
from app.infrastructure.faq.faq_knowledge_provider import FAQKnowledgeProvider


async def test_updated_pricing():
    """Test para verificar precios actualizados."""
    print("🧪 VERIFICANDO INFORMACIÓN DE PRECIOS ACTUALIZADA")
    print("=" * 60)
    
    # Test 1: FAQ Processor
    print("\n1. FAQ PROCESSOR - Información Base:")
    processor = FAQProcessor()
    
    # Buscar FAQ de precio
    precio_faq = None
    for faq in processor.faq_database:
        if faq['category'] == 'precio':
            precio_faq = faq
            break
    
    if precio_faq:
        print(f"   ✅ Pregunta: {precio_faq['question']}")
        print(f"   💰 Respuesta: {precio_faq['answer']}")
        
        # Verificar datos específicos
        if "$2,990 MXN" in precio_faq['answer']:
            print("   ✅ Precio correcto: $2,990 MXN")
        else:
            print("   ❌ Precio no actualizado")
            
        if "2 exhibiciones sin interés" in precio_faq['answer']:
            print("   ✅ Modalidad de pago correcta")
        else:
            print("   ❌ Modalidad de pago no actualizada")
            
        if "10% por inscripción grupal" in precio_faq['answer']:
            print("   ✅ Descuento grupal incluido")
        else:
            print("   ❌ Descuento grupal no incluido")
    else:
        print("   ❌ FAQ de precio no encontrada")
    
    # Test 2: FAQ Knowledge Provider
    print("\n2. FAQ KNOWLEDGE PROVIDER - Contexto Inteligente:")
    provider = FAQKnowledgeProvider()
    
    user_context = {
        'name': 'Carlos',
        'user_role': 'CEO',
        'company_size': 'mediana',
        'industry': 'tecnología'
    }
    
    faq_context = await provider.get_faq_context_for_intelligence(
        "¿Cuánto cuesta el curso?", user_context
    )
    
    if faq_context['is_faq'] and faq_context['category'] == 'precio':
        print("   ✅ FAQ de precio detectada")
        ai_context = faq_context['context_for_ai']
        print(f"   📝 Contexto AI: {len(ai_context)} caracteres")
        
        # Verificar información en contexto AI
        if "$2,990 MXN" in ai_context:
            print("   ✅ Precio correcto en contexto AI")
        else:
            print("   ❌ Precio no actualizado en contexto AI")
            
        if "2 exhibiciones sin interés" in ai_context:
            print("   ✅ Modalidad de pago en contexto AI")
        else:
            print("   ❌ Modalidad no actualizada en contexto AI")
            
        if "10% por inscripción grupal" in ai_context:
            print("   ✅ Descuento grupal en contexto AI")
        else:
            print("   ❌ Descuento no incluido en contexto AI")
    else:
        print("   ❌ FAQ de precio no detectada en Knowledge Provider")
    
    # Test 3: Consistencia entre ambos sistemas
    print("\n3. VERIFICACIÓN DE CONSISTENCIA:")
    if precio_faq and faq_context['is_faq']:
        base_answer = precio_faq['answer']
        ai_context = faq_context['context_for_ai']
        
        # Verificar elementos clave en ambos
        elementos_clave = ["$2,990 MXN", "2 exhibiciones", "10%", "grupal"]
        consistente = True
        
        for elemento in elementos_clave:
            en_base = elemento in base_answer
            en_contexto = elemento in ai_context
            
            if en_base and en_contexto:
                print(f"   ✅ '{elemento}' consistente en ambos sistemas")
            elif en_base and not en_contexto:
                print(f"   ⚠️  '{elemento}' solo en FAQ base, falta en contexto AI")
                consistente = False
            elif not en_base and en_contexto:
                print(f"   ⚠️  '{elemento}' solo en contexto AI, falta en FAQ base")
                consistente = False
            else:
                print(f"   ❌ '{elemento}' falta en ambos sistemas")
                consistente = False
        
        if consistente:
            print("\n🎉 SISTEMAS CONSISTENTES - Información actualizada correctamente")
        else:
            print("\n⚠️  REVISAR INCONSISTENCIAS entre sistemas")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")


if __name__ == "__main__":
    asyncio.run(test_updated_pricing())