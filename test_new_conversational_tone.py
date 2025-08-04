#!/usr/bin/env python3
"""
Test del nuevo tono conversacional mejorado.
Compara respuestas anteriores vs nuevas para verificar mejoras.
"""

import asyncio
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prompts.agent_prompts import WhatsAppBusinessTemplates
from app.infrastructure.faq.faq_knowledge_provider import FAQKnowledgeProvider


def print_test_header(test_name: str):
    """Imprime header del test."""
    print(f"\n{'='*70}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*70}")


def print_comparison(old_style: str, new_style: str, test_name: str):
    """Compara estilos antiguo vs nuevo."""
    print(f"\n📊 COMPARACIÓN - {test_name}")
    print(f"\n❌ ESTILO ANTERIOR (Aburrido):")
    print(f"   {old_style[:100]}...")
    print(f"\n✅ ESTILO NUEVO (Dinámico):")
    print(f"   {new_style[:100]}...")
    
    # Verificar mejoras
    improvements = []
    if "🚀" in new_style or "💰" in new_style or "📊" in new_style:
        improvements.append("✅ Usa emojis y formato visual")
    if "Entiendo" not in new_style:
        improvements.append("✅ Eliminó frases empáticas repetitivas")
    if "*" in new_style and "*" in new_style:
        improvements.append("✅ Usa formato destacado con asteriscos")
    if "¿" in new_style and len([c for c in new_style if c == "?"]) <= 1:
        improvements.append("✅ Pregunta directa sin sobreexplicar")
    
    if improvements:
        print(f"\n🎯 MEJORAS DETECTADAS:")
        for improvement in improvements:
            print(f"   {improvement}")
    else:
        print(f"\n⚠️  NO SE DETECTARON MEJORAS SIGNIFICATIVAS")


async def test_urgency_response():
    """Test de respuesta a urgencia."""
    print_test_header("RESPUESTA A URGENCIA")
    
    # Estilo anterior simulado
    old_style = "Entiendo perfectamente que sientes la presión de la competencia. Es una situación que muchos líderes PyME están enfrentando. La buena noticia es que con IA puedes ver resultados..."
    
    # Nuevo estilo
    new_style = WhatsAppBusinessTemplates.urgency_detected_response("Carlos", "competition")
    
    print_comparison(old_style, new_style, "Detección de Urgencia")
    print(f"\n📝 RESPUESTA COMPLETA NUEVA:\n{new_style}")


async def test_team_readiness():
    """Test de preocupación sobre equipo."""
    print_test_header("PREOCUPACIÓN SOBRE EQUIPO")
    
    # Estilo anterior simulado
    old_style = "Es una excelente pregunta sobre tu equipo. Te entiendo perfectamente. La buena noticia es que nuestro curso está diseñado específicamente..."
    
    # Nuevo estilo
    new_style = WhatsAppBusinessTemplates.team_readiness_concern("María", "pequeño")
    
    print_comparison(old_style, new_style, "Preocupación de Equipo")
    print(f"\n📝 RESPUESTA COMPLETA NUEVA:\n{new_style}")


async def test_business_resources():
    """Test de oferta de recursos."""
    print_test_header("OFERTA DE RECURSOS EMPRESARIALES")
    
    # Estilo anterior simulado
    old_style = "Entiendo que como Director de Marketing, necesitas recursos prácticos para implementar IA en tu empresa en tecnología. Te puedo ofrecer..."
    
    # Nuevo estilo
    new_style = WhatsAppBusinessTemplates.business_resources_offer("Roberto", "Director de Marketing", "tecnología")
    
    print_comparison(old_style, new_style, "Recursos Empresariales")
    print(f"\n📝 RESPUESTA COMPLETA NUEVA:\n{new_style}")


async def test_price_objection():
    """Test de objeción de precio."""
    print_test_header("MANEJO DE OBJECIÓN DE PRECIO")
    
    # Estilo anterior simulado
    old_style = "Como CEO, entiendo perfectamente tu preocupación por $2,990. Es una decisión importante para tu empresa. Te comparto el ROI real que hemos visto..."
    
    # Nuevo estilo
    new_style = WhatsAppBusinessTemplates.business_price_objection_response(2990, "CEO", "consultoría")
    
    print_comparison(old_style, new_style, "Objeción de Precio")
    print(f"\n📝 RESPUESTA COMPLETA NUEVA:\n{new_style}")


async def test_faq_context_improvement():
    """Test de contexto FAQ mejorado."""
    print_test_header("CONTEXTO FAQ CON NUEVO TONO")
    
    provider = FAQKnowledgeProvider()
    
    user_context = {
        'name': 'Ana',
        'user_role': 'Gerente de Marketing',
        'company_size': 'mediana',
        'industry': 'servicios'
    }
    
    # Test con FAQ de precio
    faq_context = await provider.get_faq_context_for_intelligence(
        "¿Cuánto cuesta el curso?", user_context
    )
    
    if faq_context['is_faq']:
        ai_context = faq_context['context_for_ai']
        
        # Verificar que el contexto no tenga frases empáticas repetitivas
        problematic_phrases = ["Entiendo tu", "Es normal que", "Muchos líderes como tú"]
        
        print(f"\n📝 CONTEXTO AI GENERADO:")
        print(f"   Categoría: {faq_context['category']}")
        print(f"   Longitud: {len(ai_context)} caracteres")
        
        # Verificar mejoras
        has_problems = any(phrase in ai_context for phrase in problematic_phrases)
        
        if has_problems:
            print(f"\n⚠️  CONTEXTO AÚN CONTIENE FRASES EMPÁTICAS PROBLEMÁTICAS")
        else:
            print(f"\n✅ CONTEXTO LIMPIO - Sin frases empáticas repetitivas")
        
        # Mostrar extracto
        print(f"\n📋 EXTRACTO DEL CONTEXTO:")
        print(f"   {ai_context[:200]}...")
    else:
        print(f"\n❌ FAQ no detectada para test de contexto")


async def main():
    """Función principal."""
    print("🚀 INICIANDO TESTS DEL NUEVO TONO CONVERSACIONAL")
    print("=" * 70)
    
    # Test 1: Respuesta a urgencia
    await test_urgency_response()
    
    # Test 2: Preocupación sobre equipo
    await test_team_readiness()
    
    # Test 3: Recursos empresariales
    await test_business_resources()
    
    # Test 4: Objeción de precio
    await test_price_objection()
    
    # Test 5: Contexto FAQ mejorado
    await test_faq_context_improvement()
    
    # Resumen final
    print(f"\n{'='*70}")
    print("🎉 EVALUACIÓN DEL NUEVO TONO CONVERSACIONAL")
    print(f"{'='*70}")
    
    print(f"\n✅ CAMBIOS IMPLEMENTADOS:")
    print("• Eliminadas frases empáticas repetitivas como 'Entiendo tu frustración'")
    print("• Agregado formato visual con emojis y asteriscos")
    print("• Respuestas más directas y orientadas a acción")
    print("• Títulos llamativos como '🚀 *SOLUCIÓN RÁPIDA*'")
    print("• Preguntas de cierre más energéticas: '¿Empezamos?' vs '¿Te parece bien?'")
    
    print(f"\n🎯 MEJORAS ESPERADAS EN CONVERSACIONES:")
    print("• Menos 'terapia empresarial', más valor práctico")
    print("• Respuestas que parecen más a plantillas atractivas")
    print("• Tono energético pero profesional")
    print("• Enfoque en beneficios tangibles sin tanto preámbulo")
    
    print(f"\n🔄 PRÓXIMOS PASOS:")
    print("• Probar en conversaciones reales")
    print("• Ajustar según feedback del usuario")
    print("• Mantener compatibilidad para merge con otro desarrollador")
    
    print(f"\n✅ SISTEMA LISTO PARA PRUEBAS EN CONVERSACIONES REALES")


if __name__ == "__main__":
    asyncio.run(main())