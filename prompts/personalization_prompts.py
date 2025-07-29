"""
Personalization Prompts for Buyer Persona-Based Responses

This module contains specialized prompts for generating personalized responses
based on detected buyer personas and user context.
"""

from typing import Dict, Any, Optional

# Base system prompt for personalized responses
PERSONALIZATION_SYSTEM_PROMPT = """
Eres Brenda, asesora especializada en IA aplicada para PyMEs de "Aprenda y Aplique IA". 
Tu especialidad es adaptar tu comunicación al perfil específico de cada líder empresarial,
hablando su idioma y enfocándote en sus necesidades específicas.

PRINCIPIOS DE PERSONALIZACIÓN:
1. Adapta tu lenguaje al nivel profesional y técnico del usuario
2. Enfócate en los pain points específicos de su buyer persona
3. Usa ejemplos relevantes a su industria y rol
4. Ajusta el nivel de detalle según su poder de decisión
5. Considera el tamaño de su empresa para los ejemplos de ROI

REGLAS DE COMUNICACIÓN:
- Mantén siempre un tono profesional pero cálido
- Usa ejemplos cuantificados específicos para su perfil
- Evita jerga técnica excesiva a menos que sea apropiada
- Personaliza los beneficios según su rol y responsabilidades
"""

# Buyer Persona Specific Prompts
BUYER_PERSONA_PROMPTS = {
    'lucia_copypro': {
        'context': """
PERFIL DEL USUARIO - LUCÍA COPYPRO (Marketing Digital Manager):
- Edad: 28-35 años, 5-8 años experiencia en marketing digital
- Empresa: Agencia de marketing o empresa con equipo marketing (20-100 empleados)
- Responsabilidades: Campañas, contenido, leads, ROI de marketing
- Pain Points: Crear contenido consistente, optimizar campañas, generar leads de calidad
        """,
        'communication_style': 'creativo_roi_enfocado',
        'language_level': 'intermedio_negocios',
        'key_benefits': [
            'Automatización de contenido para redes sociales',
            'Optimización de campañas con IA',
            'Análisis predictivo de audiencias',
            'Generación automática de copys'
        ],
        'roi_examples': [
            '80% menos tiempo creando contenido = 16 horas semanales ahorradas',
            '45% mejor CTR en campañas automatizadas',
            '$300 ahorro por campaña → Recuperas inversión en 2 campañas'
        ]
    },
    
    'marcos_multitask': {
        'context': """
PERFIL DEL USUARIO - MARCOS MULTITASK (Operations Manager):
- Edad: 32-42 años, 8-12 años experiencia operativa
- Empresa: Manufactura o servicios PyME (50-200 empleados)
- Responsabilidades: Eficiencia operativa, procesos, costos, calidad
- Pain Points: Procesos manuales, ineficiencias, control de costos
        """,
        'communication_style': 'eficiencia_operacional',
        'language_level': 'practico_resultados',
        'key_benefits': [
            'Automatización de procesos operativos',
            'Optimización de inventarios',
            'Análisis predictivo de demanda',
            'Control de calidad automatizado'
        ],
        'roi_examples': [
            '30% reducción en tiempo de procesos manuales',
            '25% menos errores operativos',
            '$2,000 ahorro mensual → ROI del 400% en primer mes'
        ]
    },
    
    'sofia_visionaria': {
        'context': """
PERFIL DEL USUARIO - SOFÍA VISIONARIA (CEO/Founder):
- Edad: 35-45 años, 10-15 años experiencia empresarial
- Empresa: CEO/Founder de servicios profesionales (30-150 empleados)
- Responsabilidades: Estrategia, crecimiento, competitividad, innovación
- Pain Points: Competencia, escalabilidad, innovación, toma de decisiones estratégicas
        """,
        'communication_style': 'estrategico_ejecutivo',
        'language_level': 'ejecutivo_visionario',
        'key_benefits': [
            'Ventaja competitiva través de IA',
            'Escalabilidad sin crecimiento exponencial de costos',
            'Toma de decisiones basada en datos',
            'Innovación en modelo de negocio'
        ],
        'roi_examples': [
            '40% más productividad sin contratar más personal',
            '60% mejor toma de decisiones con insights de IA',
            '$27,600 ahorro anual vs contratar analista → ROI del 1,380% anual'
        ]
    },
    
    'ricardo_rh_agil': {
        'context': """
PERFIL DEL USUARIO - RICARDO RH ÁGIL (Head of Talent & Learning):
- Edad: 30-40 años, 6-10 años experiencia en RRHH
- Empresa: Scale-up o empresa en crecimiento (100-300 empleados)
- Responsabilidades: Desarrollo de talento, capacitación, productividad del equipo
- Pain Points: Capacitación escalable, retención de talento, desarrollo de skills
        """,
        'communication_style': 'desarrollo_personas',
        'language_level': 'profesional_humano',
        'key_benefits': [
            'Capacitación personalizada y escalable',
            'Desarrollo de competencias en IA',
            'Retención de talento through upskilling',
            'Evaluación automática de progreso'
        ],
        'roi_examples': [
            '70% más eficiencia en capacitaciones',
            '85% mayor retención post-upskilling',
            '$15,000 ahorro anual vs capacitación externa'
        ]
    },
    
    'daniel_data_innovador': {
        'context': """
PERFIL DEL USUARIO - DANIEL DATA INNOVADOR (Senior Innovation/BI Analyst):
- Edad: 28-38 años, 5-10 años experiencia en datos/innovación
- Empresa: Corporate o empresa tech-forward (200+ empleados)
- Responsabilidades: Business Intelligence, innovación, análisis avanzado
- Pain Points: Herramientas limitadas, análisis manual, implementación de innovación
        """,
        'communication_style': 'tecnico_analitico',
        'language_level': 'avanzado_tecnico',
        'key_benefits': [
            'Herramientas avanzadas de IA aplicada',
            'Automatización de análisis complejos',
            'Implementación práctica de ML',
            'Pipeline de innovación estructurado'
        ],
        'roi_examples': [
            '90% menos tiempo en análisis repetitivos',
            '3x más insights accionables por semana',
            '$45,000 ahorro anual en herramientas vs suite BI enterprise'
        ]
    }
}

# Response templates by communication approach
COMMUNICATION_APPROACHES = {
    'creative_roi_focused': {
        'greeting_style': 'energético y orientado a resultados',
        'example_intro': 'Imagina poder crear',
        'benefit_focus': 'creatividad + eficiencia',
        'closing_style': 'call-to-action creativo'
    },
    'efficiency_operational': {
        'greeting_style': 'directo y orientado a soluciones',
        'example_intro': 'Podrías optimizar',
        'benefit_focus': 'eficiencia + ahorro de costos',
        'closing_style': 'próximos pasos concretos'
    },
    'strategic_executive': {
        'greeting_style': 'visionario y estratégico',
        'example_intro': 'Tu empresa podría liderar',
        'benefit_focus': 'ventaja competitiva + escalabilidad',
        'closing_style': 'visión de futuro'
    },
    'people_development': {
        'greeting_style': 'enfocado en personas y crecimiento',
        'example_intro': 'Tu equipo podría desarrollar',
        'benefit_focus': 'desarrollo de talento + retención',
        'closing_style': 'impacto en las personas'
    },
    'technical_analytical': {
        'greeting_style': 'técnico y orientado a datos',
        'example_intro': 'Podrías implementar',
        'benefit_focus': 'capacidades técnicas + análisis avanzado',
        'closing_style': 'especificaciones técnicas'
    },
    'general_business': {
        'greeting_style': 'profesional y adaptable',
        'example_intro': 'Tu negocio podría beneficiarse',
        'benefit_focus': 'mejora general del negocio',
        'closing_style': 'valor agregado'
    }
}

def get_personalized_system_prompt(user_context: Dict[str, Any]) -> str:
    """
    Generates a personalized system prompt based on user context.
    
    Args:
        user_context: User context with buyer persona and profile information
        
    Returns:
        Personalized system prompt for AI generation
    """
    
    buyer_persona = user_context.get('user_profile', {}).get('buyer_persona', 'unknown')
    professional_level = user_context.get('user_profile', {}).get('professional_level', 'unknown')
    company_size = user_context.get('user_profile', {}).get('company_size', 'unknown')
    
    # Get buyer persona specific context
    persona_info = BUYER_PERSONA_PROMPTS.get(buyer_persona, {})
    
    # Build personalized prompt
    personalized_prompt = f"""
{PERSONALIZATION_SYSTEM_PROMPT}

{persona_info.get('context', 'USUARIO GENERAL')}

ESTILO DE COMUNICACIÓN PERSONALIZADO:
- Enfoque: {persona_info.get('communication_style', 'profesional_general')}
- Nivel de lenguaje: {persona_info.get('language_level', 'intermedio_negocios')}
- Tamaño de empresa: {company_size}
- Nivel profesional: {professional_level}

BENEFICIOS CLAVE PARA ESTE PERFIL:
{chr(10).join([f"• {benefit}" for benefit in persona_info.get('key_benefits', ['Beneficios generales de IA'])])}

EJEMPLOS DE ROI ESPECÍFICOS:
{chr(10).join([f"• {example}" for example in persona_info.get('roi_examples', ['ROI positivo comprobado'])])}

INSTRUCCIONES ESPECÍFICAS:
1. Usa el contexto del usuario para personalizar completamente tu respuesta
2. Enfócate en los pain points específicos de su buyer persona
3. Proporciona ejemplos cuantificados relevantes a su industria
4. Adapta el nivel de detalle técnico según su perfil
5. Mantén el enfoque en valor empresarial y ROI
"""
    
    return personalized_prompt

def get_personalized_response_prompt(
    user_message: str,
    user_context: Dict[str, Any],
    conversation_intent: str = "general"
) -> str:
    """
    Generates a personalized response prompt for specific user message.
    
    Args:
        user_message: The user's message
        user_context: Complete user context
        conversation_intent: Detected conversation intent
        
    Returns:
        Personalized response prompt
    """
    
    buyer_persona = user_context.get('user_profile', {}).get('buyer_persona', 'unknown')
    pain_points = user_context.get('interests_and_needs', {}).get('pain_points', [])
    automation_needs = user_context.get('interests_and_needs', {}).get('automation_needs', {})
    urgency_signals = user_context.get('communication_context', {}).get('urgency_signals', [])
    
    response_prompt = f"""
MENSAJE DEL USUARIO: "{user_message}"

CONTEXTO PERSONALIZADO:
- Buyer Persona: {buyer_persona}
- Pain Points identificados: {', '.join(pain_points[:3]) if pain_points else 'Por identificar'}
- Necesidades de automatización: {str(automation_needs)[:100] if automation_needs else 'Por explorar'}
- Señales de urgencia: {', '.join(urgency_signals) if urgency_signals else 'Ninguna'}
- Intención de conversación: {conversation_intent}

INSTRUCCIONES PARA LA RESPUESTA:
1. Personaliza completamente basándote en el buyer persona {buyer_persona}
2. Aborda directamente los pain points mencionados
3. Usa ejemplos específicos para su industria y rol
4. Si hay señales de urgencia, ajusta el tono apropiadamente
5. Proporciona valor inmediato en tu respuesta
6. Incluye call-to-action relevante a su nivel de decisión

OBJETIVO: Generar una respuesta que demuestre comprensión profunda de su negocio y necesidades específicas.
"""
    
    return response_prompt

def get_buyer_persona_examples(buyer_persona: str) -> Dict[str, Any]:
    """
    Returns specific examples and context for a buyer persona.
    
    Args:
        buyer_persona: The buyer persona identifier
        
    Returns:
        Dictionary with examples and context
    """
    return BUYER_PERSONA_PROMPTS.get(buyer_persona, {
        'context': 'Usuario empresarial general',
        'key_benefits': ['Beneficios generales de IA aplicada'],
        'roi_examples': ['ROI positivo comprobado']
    })

def get_communication_approach_info(approach: str) -> Dict[str, str]:
    """
    Returns communication approach information.
    
    Args:
        approach: The communication approach identifier
        
    Returns:
        Dictionary with approach information
    """
    return COMMUNICATION_APPROACHES.get(approach, COMMUNICATION_APPROACHES['general_business'])