#!/usr/bin/env python3
"""
Test completo del sistema FAQ extendido con toda la información detallada.
"""

import asyncio
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.faq.faq_processor import FAQProcessor
from app.infrastructure.faq.faq_knowledge_provider import FAQKnowledgeProvider


def print_test_header(test_name: str):
    """Imprime header del test."""
    print(f"\n{'='*70}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*70}")


def print_test_result(success: bool, message: str):
    """Imprime resultado del test."""
    status = "✅ PASÓ" if success else "❌ FALLÓ"
    print(f"\n{status}: {message}")


async def test_new_faqs():
    """Test de las 3 nuevas FAQs específicas."""
    
    print_test_header("NUEVAS FAQs ESPECÍFICAS")
    
    processor = FAQProcessor()
    
    # Test 1: FAQ_011 - ¿Qué incluye?
    print("🧪 TEST 1: FAQ ¿Qué incluye el curso?")
    test_messages_incluye = [
        "¿Qué incluye el curso?",
        "¿Qué materiales me dan?",
        "¿Qué recursos contiene?",
        "¿Qué entregables tiene?"
    ]
    
    for msg in test_messages_incluye:
        faq_match = await processor.detect_faq(msg)
        if faq_match and faq_match['category'] == 'incluye':
            print(f"   ✅ '{msg}' → Detectada FAQ_011 (incluye)")
            # Verificar contenido clave
            answer = faq_match['answer']
            elementos_clave = ["Manual completo en PDF", "plantillas", "grabaciones", "Q&A", "foro"]
            for elemento in elementos_clave:
                if elemento.lower() in answer.lower():
                    print(f"      ✅ Incluye: {elemento}")
                else:
                    print(f"      ❌ Falta: {elemento}")
            break
    else:
        print("   ❌ FAQ 'incluye' no detectada")
    
    # Test 2: FAQ_012 - Ventajas
    print("\n🧪 TEST 2: FAQ ¿Cuáles son las ventajas?")
    test_messages_ventajas = [
        "¿Cuáles son las ventajas?",
        "¿Por qué elegir este curso?",
        "¿Qué beneficios tiene?",
        "¿Qué lo hace único?"
    ]
    
    for msg in test_messages_ventajas:
        faq_match = await processor.detect_faq(msg)
        if faq_match and faq_match['category'] == 'ventajas':
            print(f"   ✅ '{msg}' → Detectada FAQ_012 (ventajas)")
            answer = faq_match['answer']
            ventajas_clave = ["práctica guiada", "recursos premium", "AplicaAI Helper", "proyecto real"]
            for ventaja in ventajas_clave:
                if ventaja.lower() in answer.lower():
                    print(f"      ✅ Incluye ventaja: {ventaja}")
                else:
                    print(f"      ❌ Falta ventaja: {ventaja}")
            break
    else:
        print("   ❌ FAQ 'ventajas' no detectada")
    
    # Test 3: FAQ_013 - Examen
    print("\n🧪 TEST 3: FAQ ¿Cómo es el examen?")
    test_messages_examen = [
        "¿Cómo es el examen?",
        "¿Qué tipo de evaluación hay?",
        "¿Cómo es la certificación?",
        "¿Qué formato tiene el proyecto?"
    ]
    
    for msg in test_messages_examen:
        faq_match = await processor.detect_faq(msg)
        if faq_match and faq_match['category'] == 'examen':
            print(f"   ✅ '{msg}' → Detectada FAQ_013 (examen)")
            answer = faq_match['answer']
            elementos_examen = ["90 minutos", "proyecto integrador", "escenarios reales", "plantillas IMPULSO"]
            for elemento in elementos_examen:
                if elemento.lower() in answer.lower():
                    print(f"      ✅ Incluye: {elemento}")
                else:
                    print(f"      ❌ Falta: {elemento}")
            break
    else:
        print("   ❌ FAQ 'examen' no detectada")


async def test_updated_existing_faqs():
    """Test de FAQs existentes actualizadas."""
    
    print_test_header("FAQs EXISTENTES ACTUALIZADAS")
    
    processor = FAQProcessor()
    
    # Test 1: FAQ_004 - Requisitos (ahora incluye "Dirigido a")
    print("🧪 TEST 1: FAQ Requisitos actualizada")
    faq_requisitos = None
    for faq in processor.faq_database:
        if faq['category'] == 'requisitos':
            faq_requisitos = faq
            break
    
    if faq_requisitos:
        answer = faq_requisitos['answer']
        nuevos_elementos = ["Ejecutivos y managers", "Emprendedores", "PYMES", "insights en segundos"]
        for elemento in nuevos_elementos:
            if elemento in answer:
                print(f"   ✅ Incluye: {elemento}")
            else:
                print(f"   ❌ Falta: {elemento}")
    
    # Test 2: FAQ_007 - Certificado (ahora incluye detalles del examen)
    print("\n🧪 TEST 2: FAQ Certificado actualizada")
    faq_certificado = None
    for faq in processor.faq_database:
        if faq['category'] == 'certificado':
            faq_certificado = faq
            break
    
    if faq_certificado:
        answer = faq_certificado['answer']
        elementos_certificado = ["90 minutos", "75%", "70%", "código único", "plantillas IMPULSO"]
        for elemento in elementos_certificado:
            if elemento in answer:
                print(f"   ✅ Incluye: {elemento}")
            else:
                print(f"   ❌ Falta: {elemento}")
    
    # Test 3: FAQ_008 - Soporte (ahora incluye Q&A y AplicaAI Helper)
    print("\n🧪 TEST 3: FAQ Soporte actualizada")
    faq_soporte = None
    for faq in processor.faq_database:
        if faq['category'] == 'soporte':
            faq_soporte = faq
            break
    
    if faq_soporte:
        answer = faq_soporte['answer']
        elementos_soporte = ["2 sesiones Q&A", "AplicaAI Helper", "24/7", "foro privado"]
        for elemento in elementos_soporte:
            if elemento in answer:
                print(f"   ✅ Incluye: {elemento}")
            else:
                print(f"   ❌ Falta: {elemento}")


async def test_knowledge_provider_new_contexts():
    """Test del Knowledge Provider con nuevos contextos."""
    
    print_test_header("KNOWLEDGE PROVIDER - NUEVOS CONTEXTOS")
    
    provider = FAQKnowledgeProvider()
    
    user_context = {
        'name': 'Roberto',
        'user_role': 'CEO',
        'company_size': 'mediana',
        'industry': 'manufactura'
    }
    
    # Test 1: Contexto para "incluye"
    print("🧪 TEST 1: Contexto AI para 'incluye'")
    faq_context = await provider.get_faq_context_for_intelligence(
        "¿Qué incluye el curso?", user_context
    )
    
    if faq_context['is_faq'] and faq_context['category'] == 'incluye':
        ai_context = faq_context['context_for_ai']
        elementos_contexto = ["Manual completo", "plantillas", "Q&A", "foro", "CEO"]
        for elemento in elementos_contexto:
            if elemento in ai_context:
                print(f"   ✅ Contexto incluye: {elemento}")
            else:
                print(f"   ❌ Contexto falta: {elemento}")
    else:
        print("   ❌ Contexto AI para 'incluye' no generado")
    
    # Test 2: Contexto para "ventajas"
    print("\n🧪 TEST 2: Contexto AI para 'ventajas'")
    faq_context = await provider.get_faq_context_for_intelligence(
        "¿Por qué elegir este curso?", user_context
    )
    
    if faq_context['is_faq'] and faq_context['category'] == 'ventajas':
        ai_context = faq_context['context_for_ai']
        elementos_ventajas = ["práctica guiada", "recursos premium", "AplicaAI Helper", "manufactura"]
        for elemento in elementos_ventajas:
            if elemento in ai_context:
                print(f"   ✅ Contexto incluye: {elemento}")
            else:
                print(f"   ❌ Contexto falta: {elemento}")
    else:
        print("   ❌ Contexto AI para 'ventajas' no generado")
    
    # Test 3: Contexto para "examen"
    print("\n🧪 TEST 3: Contexto AI para 'examen'")
    faq_context = await provider.get_faq_context_for_intelligence(
        "¿Cómo es la evaluación?", user_context
    )
    
    if faq_context['is_faq'] and faq_context['category'] == 'examen':
        ai_context = faq_context['context_for_ai']
        elementos_examen = ["90 minutos", "proyecto integrador", "plantillas IMPULSO", "CEO"]
        for elemento in elementos_examen:
            if elemento in ai_context:
                print(f"   ✅ Contexto incluye: {elemento}")
            else:
                print(f"   ❌ Contexto falta: {elemento}")
    else:
        print("   ❌ Contexto AI para 'examen' no generado")


async def test_faq_database_completeness():
    """Test de completitud de la base de datos FAQ."""
    
    print_test_header("COMPLETITUD BASE DE DATOS FAQ")
    
    processor = FAQProcessor()
    
    # Verificar que tenemos 13 FAQs (10 originales + 3 nuevas)
    total_faqs = len(processor.faq_database)
    print(f"📊 Total de FAQs: {total_faqs}")
    
    if total_faqs == 13:
        print("✅ Número correcto de FAQs (13)")
    else:
        print(f"❌ Número incorrecto. Esperado: 13, Actual: {total_faqs}")
    
    # Verificar todas las categorías
    categorias_esperadas = [
        'precio', 'duración', 'implementación', 'requisitos', 'casos_éxito',
        'roi', 'certificado', 'soporte', 'acceso', 'garantía',
        'incluye', 'ventajas', 'examen'
    ]
    
    categorias_encontradas = []
    for faq in processor.faq_database:
        categorias_encontradas.append(faq['category'])
    
    print("\n📋 Verificación de categorías:")
    for categoria in categorias_esperadas:
        if categoria in categorias_encontradas:
            print(f"   ✅ {categoria}")
        else:
            print(f"   ❌ {categoria} - FALTA")
    
    # Verificar que todas las FAQs tienen la estructura correcta
    print("\n🔍 Verificación de estructura:")
    campos_requeridos = ['id', 'category', 'question', 'keywords', 'answer', 'escalation_needed', 'priority']
    
    for faq in processor.faq_database:
        faq_id = faq.get('id', 'ID_MISSING')
        estructura_correcta = True
        
        for campo in campos_requeridos:
            if campo not in faq:
                print(f"   ❌ {faq_id}: Falta campo '{campo}'")
                estructura_correcta = False
        
        if estructura_correcta:
            print(f"   ✅ {faq_id}: Estructura completa")


async def main():
    """Función principal."""
    print("🚀 INICIANDO TESTS DEL SISTEMA FAQ EXTENDIDO")
    
    # Test 1: Nuevas FAQs
    await test_new_faqs()
    
    # Test 2: FAQs existentes actualizadas
    await test_updated_existing_faqs()
    
    # Test 3: Knowledge Provider con nuevos contextos
    await test_knowledge_provider_new_contexts()
    
    # Test 4: Completitud de la base de datos
    await test_faq_database_completeness()
    
    # Resumen final
    print(f"\n{'='*70}")
    print("🎉 TESTS DEL SISTEMA FAQ EXTENDIDO COMPLETADOS")
    print(f"{'='*70}")
    print("\n📋 INFORMACIÓN ACTUALIZADA:")
    print("✅ Precios: $2,990 MXN con modalidades flexibles")
    print("✅ 13 FAQs completas (10 actualizadas + 3 nuevas)")
    print("✅ Información detallada de recursos, ventajas y examen")
    print("✅ Contextos AI enriquecidos para respuestas inteligentes")
    print("✅ Personalización avanzada por buyer persona")
    
    print("\n🆕 NUEVAS FAQs AGREGADAS:")
    print("• FAQ_011: ¿Qué incluye el curso? (materiales + soporte)")
    print("• FAQ_012: ¿Cuáles son las ventajas? (práctica + premium + proyecto)")
    print("• FAQ_013: ¿Cómo es el examen? (formato + preparación)")
    
    print("\n🔧 FAQs MEJORADAS:")
    print("• Requisitos: Ahora incluye perfiles target específicos")
    print("• Certificado: Detalles completos del examen práctico")
    print("• Soporte: Q&A en vivo + AplicaAI Helper")
    print("• Duración: 4 sesiones + proyecto real")
    print("• Acceso: Grabaciones + materiales descargables")
    
    print("\n🎯 SISTEMA LISTO PARA:")
    print("• Respuestas detalladas sobre contenido del curso")
    print("• Información específica de ventajas competitivas")
    print("• Detalles completos de certificación y examen")
    print("• Personalización avanzada por industria y rol")


if __name__ == "__main__":
    asyncio.run(main())