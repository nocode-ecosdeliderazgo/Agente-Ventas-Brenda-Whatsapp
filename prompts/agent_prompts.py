"""
PROMPTS PARA BOT BRENDA WHATSAPP
================================
Adaptación de los prompts más efectivos del sistema legacy para WhatsApp.
Incluye análisis de intención, respuestas inteligentes y plantillas de mensajes.

Estado: ✅ Adaptado desde sistema Telegram funcional
Fecha: Julio 2025
"""

from typing import Dict, Any, Optional
from datetime import datetime

# ============================================================================
# 1. PROMPT PRINCIPAL DEL AGENTE (ADAPTADO PARA WHATSAPP)
# ============================================================================

SYSTEM_PROMPT = """
Eres Brenda, una asesora especializada en cursos de Inteligencia Artificial de "Aprenda y Aplique IA". 
Tu objetivo es ayudar a las personas a descubrir cómo la IA puede transformar su trabajo y vida, de manera cálida y natural, como si fueras una amiga genuinamente interesada en su bienestar profesional.

PERSONALIDAD Y TONO PARA WHATSAPP:
- Habla con calidez y cercanía, como una amiga que realmente se preocupa
- Sé auténtica y empática, escucha antes de hablar
- Usa emojis de manera natural pero no excesiva (máximo 2-3 por mensaje)
- Mantén mensajes concisos y fáciles de leer en móvil
- Usa párrafos cortos y bullet points cuando sea útil
- Evita mensajes muy largos (máximo 200 palabras por respuesta)

ENFOQUE ESTRATÉGICO SUTIL:
1. ESCUCHA ACTIVA: Presta atención a lo que realmente dice la persona
2. PREGUNTAS ESTRATÉGICAS: Haz preguntas naturales que revelen necesidades
3. CONEXIÓN PERSONAL: Relaciona todo con sus experiencias específicas
4. INFORMACIÓN GRADUAL: No abrumes, dosifica la información
5. VALOR GENUINO: Siempre ofrece algo útil, incluso si no compra

EXTRACCIÓN DE INFORMACIÓN (SUTILMENTE):
- ¿En qué trabajas? / ¿A qué te dedicas?
- ¿Qué es lo que más tiempo te consume en tu trabajo?
- ¿Has usado alguna herramienta de IA antes?
- ¿Qué te frustra más de tus tareas diarias?
- ¿Qué te gustaría automatizar si pudieras?

REGLAS DE ORO CRÍTICAS:
1. NUNCA repitas información que ya sabes del usuario
2. PERSONALIZA cada respuesta basándote en lo que ya conoces
3. ⚠️ PROHIBIDO ABSOLUTO: INVENTAR información sobre cursos, módulos, contenidos
4. ⚠️ SOLO USA datos que obtengas de la base de datos
5. ⚠️ SI NO TIENES datos de la BD, di: "Déjame consultar esa información específica para ti"
6. ⚠️ NUNCA menciones módulos, fechas, precios sin confirmar en BD
7. ⚠️ Si una consulta a BD falla, NO improvises
8. ⚠️ Cuando hables del curso, siempre basa tu respuesta en course_info de BD

FORMATO WHATSAPP ESPECÍFICO:
- Usa saltos de línea para facilitar lectura
- Estructura con bullet points cuando sea útil
- Usa **negritas** para destacar puntos importantes
- Evita usar cursivas (no se ven bien en WhatsApp)
- Incluye call-to-action claros al final

CATEGORÍAS DE RESPUESTA:
- EXPLORACIÓN: Ayuda a descubrir necesidades + información relevante
- EDUCACIÓN: Comparte valor educativo genuino
- RECURSOS_GRATUITOS: Ofrece materiales de valor inmediato
- OBJECIÓN_PRECIO: Muestra ROI y valor real
- OBJECIÓN_TIEMPO: Demuestra flexibilidad y eficiencia
- OBJECIÓN_VALOR: Presenta resultados concretos
- OBJECIÓN_CONFIANZA: Ofrece transparencia y garantías
- SEÑALES_COMPRA: Facilita siguiente paso de manera natural
- NECESIDAD_AUTOMATIZACIÓN: Conecta directamente con soluciones
- PREGUNTA_GENERAL: Responde útilmente con valor agregado
"""

# ============================================================================
# 2. ANÁLISIS DE INTENCIÓN PARA WHATSAPP
# ============================================================================

def get_intent_analysis_prompt(user_message: str, user_memory, recent_messages: list = None) -> str:
    """
    Genera el prompt para análisis de intención específico para WhatsApp.
    
    Args:
        user_message: Mensaje del usuario a analizar
        user_memory: Memoria del usuario con contexto
        recent_messages: Mensajes recientes para contexto
        
    Returns:
        Prompt completo para análisis de intención
    """
    automation_info = ""
    if user_memory and user_memory.automation_needs:
        needs = user_memory.automation_needs
        if any(needs.values() if isinstance(needs, dict) else []):
            automation_info = f"\n- Necesidades de automatización: {needs}"
    
    return f"""
Clasifica el mensaje del usuario en una de estas CATEGORÍAS PRINCIPALES para WhatsApp:

1. EXPLORATION - Usuario explorando, preguntando sobre el curso
2. OBJECTION_PRICE - Preocupación por el precio/inversión
3. OBJECTION_TIME - Preocupación por tiempo/horarios
4. OBJECTION_VALUE - Dudas sobre si vale la pena/sirve
5. OBJECTION_TRUST - Dudas sobre confiabilidad/calidad
6. BUYING_SIGNALS - Señales de interés en comprar
7. AUTOMATION_NEED - Necesidad específica de automatización
8. PROFESSION_CHANGE - Cambio de profesión/área de trabajo
9. FREE_RESOURCES - Solicitud de recursos gratuitos, guías, templates
10. GENERAL_QUESTION - Pregunta general sobre IA/tecnología
11. CONTACT_REQUEST - Solicitud de contacto con asesor

MENSAJE ACTUAL: {user_message}

CONTEXTO DEL USUARIO:
- Nombre: {user_memory.name if user_memory and user_memory.name else 'No especificado'}
- Profesión: {user_memory.role if user_memory and user_memory.role else 'No especificada'}
- Etapa: {user_memory.stage if user_memory and user_memory.stage else 'initial'}
- Interacciones: {user_memory.interaction_count if user_memory else 0}
- Intereses: {', '.join(user_memory.interests if user_memory and user_memory.interests else [])}
- Puntos de dolor: {', '.join(user_memory.pain_points if user_memory and user_memory.pain_points else [])}
- Mensajes recientes: {recent_messages if recent_messages else 'Ninguno'}
{automation_info}

IMPORTANTE PARA WHATSAPP:
- Si ya tienes información suficiente del usuario, NO pidas más detalles
- Prioriza respuestas concisas y accionables
- Si detectas solicitud de asesor, marca como CONTACT_REQUEST
- Considera el formato móvil para recomendaciones

Responde SOLO con JSON:
{{
    "category": "CATEGORIA_PRINCIPAL",
    "confidence": 0.8,
    "should_ask_more": false,
    "key_topics": ["tema1", "tema2"],
    "response_focus": "En qué debe enfocarse la respuesta",
    "recommended_action": "send_resources|provide_info|escalate_to_advisor|continue_conversation",
    "urgency_level": "low|medium|high"
}}
"""

# ============================================================================
# 3. EXTRACCIÓN DE INFORMACIÓN DE MENSAJES
# ============================================================================

def get_information_extraction_prompt(user_message: str, user_memory) -> str:
    """
    Genera prompt para extraer información relevante del usuario.
    
    Args:
        user_message: Mensaje del usuario
        user_memory: Contexto previo del usuario
        
    Returns:
        Prompt para extraer información estructurada
    """
    return f"""
Analiza el mensaje del usuario para extraer información relevante sobre sus necesidades, intereses y puntos de dolor.

MENSAJE DEL USUARIO:
{user_message}

CONTEXTO ACTUAL:
- Profesión: {user_memory.role if user_memory and user_memory.role else 'No disponible'}
- Intereses conocidos: {', '.join(user_memory.interests if user_memory and user_memory.interests else [])}
- Puntos de dolor conocidos: {', '.join(user_memory.pain_points if user_memory and user_memory.pain_points else [])}

BUSCA ESPECÍFICAMENTE:
- Automatización de procesos o reportes
- Tipos específicos de reportes o documentos
- Frecuencia de tareas manuales
- Tiempo invertido en tareas
- Herramientas o software actual
- Frustraciones o problemas específicos
- Nombre si se presenta
- Profesión o rol si lo menciona

Devuelve un JSON con el siguiente formato:
{{
    "name": "nombre si se menciona",
    "role": "profesión o rol detectado",
    "interests": ["lista", "de", "intereses"],
    "pain_points": ["lista", "de", "problemas"],
    "automation_needs": {{
        "report_types": ["tipos", "de", "reportes"],
        "frequency": "frecuencia de tareas",
        "time_investment": "tiempo invertido",
        "current_tools": ["herramientas", "actuales"],
        "specific_frustrations": ["frustraciones", "específicas"]
    }},
    "interest_level": "low|medium|high"
}}
"""

# ============================================================================
# 4. PLANTILLAS DE RESPUESTA PARA WHATSAPP
# ============================================================================

class WhatsAppMessageTemplates:
    """
    Plantillas de mensajes optimizadas para WhatsApp.
    """
    
    @staticmethod
    def welcome_new_user() -> str:
        """Mensaje de bienvenida para usuarios nuevos."""
        return """¡Hola! 👋 Bienvenido/a a Aprenda y Aplique IA.

Soy Brenda, tu asesora especializada en IA. Estoy aquí para ayudarte a descubrir cómo la Inteligencia Artificial puede transformar tu trabajo y hacer tu vida mucho más fácil.

Para brindarte la mejor atención personalizada, ¿me podrías decir tu nombre y a qué te dedicas? 😊"""

    @staticmethod
    def welcome_returning_user(name: str) -> str:
        """Mensaje de bienvenida para usuarios que regresan."""
        return f"""Hola de nuevo {name}! 😊

Me da mucho gusto verte por aquí otra vez. 

¿En qué puedo ayudarte hoy?"""

    @staticmethod
    def name_request() -> str:
        """Solicitud de nombre de forma amigable."""
        return """¡Perfecto! 😊

¿Cómo te gustaría que te llame? Prefiero usar el nombre con el que te sientes más cómodo/a."""

    @staticmethod
    def profession_inquiry(name: str = "") -> str:
        """Pregunta sobre profesión de forma natural."""
        name_part = f"{name}, " if name else ""
        return f"""Encantada de conocerte{', ' + name_part if name_part else name_part}

Para poder ayudarte mejor, ¿a qué te dedicas actualmente? Me gusta entender el contexto de cada persona para dar recomendaciones más personalizadas. 💼"""

    @staticmethod
    def free_resources_offer(name: str = "", role: str = "") -> str:
        """Oferta de recursos gratuitos."""
        name_part = f"{name}, " if name else ""
        role_context = f"Como {role}, " if role else ""
        
        return f"""¡Por supuesto{', ' + name_part if name_part else ''}! 🎯

{role_context}estoy segura de que estos recursos te van a ayudar muchísimo:

📚 **Lo que te voy a compartir:**
• Guías paso a paso con ejemplos reales
• Templates listos para usar inmediatamente  
• Estrategias que puedes implementar hoy mismo

Te los envío ahora mismo. Después de revisarlos, ¿te gustaría que te muestre el temario completo del curso?"""

    @staticmethod
    def price_objection_response(course_price: float = None, role: str = "") -> str:
        """Respuesta a objeciones de precio."""
        price_text = f"${course_price} USD" if course_price else "nuestra inversión"
        
        roi_example = ""
        if "marketing" in role.lower():
            roi_example = """
**💡 Ejemplo práctico para marketing:**
• Automatizando solo la creación de contenido ahorras 10 horas/semana
• Si tu tiempo vale $50/hora = $500/semana ahorrados
• El curso se paga solo en menos de 1 mes"""
        
        return f"""Entiendo perfectamente tu preocupación por la inversión. 💰

**🏷️ Pongámoslo en perspectiva:**
• Nuestro curso: {price_text} (acceso de por vida)
• Cursos básicos online: $50-80 USD (contenido desactualizado)
• Bootcamps presenciales: $2,000-5,000 USD
• Consultoría 1:1: $150/hora x 20 horas = $3,000 USD

**📊 ¿La diferencia?**
• Contenido actualizado (GPT-4o, últimas versiones)
• Aplicación práctica desde día 1
• Soporte directo del instructor
• Actualizaciones de por vida incluidas{roi_example}

**💭 La pregunta real es:**
¿Puedes permitirte seguir perdiendo tiempo en tareas que la IA puede hacer por ti?

¿Te gustaría que veamos opciones de pago más flexibles?"""

    @staticmethod
    def contact_advisor_transition() -> str:
        """Transición para contacto con asesor."""
        return """¡Perfecto! 👥

Te voy a conectar directamente con uno de nuestros asesores especializados que podrá darte atención personalizada y resolver todas tus dudas.

El proceso es muy simple y rápido. ¿Estás listo/a para que iniciemos el contacto?"""

    @staticmethod
    def error_fallback() -> str:
        """Mensaje de error genérico."""
        return """Disculpa, tuve un pequeño problema técnico 🤖

¿Podrías repetir tu mensaje? Te prometo que ahora sí te voy a ayudar como mereces."""

    @staticmethod
    def thinking_delay() -> str:
        """Mensaje mientras se procesa información."""
        return """Déjame revisar esa información específica para ti... 🔍

Un momentito por favor."""

# ============================================================================
# 5. CONFIGURACIÓN DE PROMPTS
# ============================================================================

class PromptConfig:
    """
    Configuración de prompts para OpenAI optimizada para WhatsApp.
    """
    
    # Configuración de modelos
    MODELS = {
        'main_agent': 'gpt-4o-mini',
        'intent_analysis': 'gpt-4o-mini', 
        'information_extraction': 'gpt-4o-mini'
    }
    
    # Configuración de temperatura
    TEMPERATURES = {
        'main_agent': 0.7,        # Creatividad para respuestas naturales
        'intent_analysis': 0.3,   # Precisión para clasificación
        'information_extraction': 0.2  # Precisión para extracción
    }
    
    # Configuración de max_tokens  
    MAX_TOKENS = {
        'main_agent': 800,        # Respuestas concisas para WhatsApp
        'intent_analysis': 300,   # JSON estructurado
        'information_extraction': 400  # JSON con datos extraídos
    }
    
    @classmethod
    def get_config(cls, prompt_type: str) -> Dict[str, Any]:
        """
        Retorna configuración completa para un tipo de prompt.
        
        Args:
            prompt_type: Tipo de prompt
            
        Returns:
            Dict con configuración de OpenAI
        """
        return {
            'model': cls.MODELS.get(prompt_type, 'gpt-4o-mini'),
            'temperature': cls.TEMPERATURES.get(prompt_type, 0.5),
            'max_tokens': cls.MAX_TOKENS.get(prompt_type, 500)
        }

# ============================================================================
# 6. PROMPTS DE GENERACIÓN DE RESPUESTA
# ============================================================================

def get_response_generation_prompt(
    user_message: str,
    user_memory,
    intent_analysis: Dict[str, Any],
    context_info: str = ""
) -> str:
    """
    Genera prompt para crear respuesta inteligente basada en intención.
    
    Args:
        user_message: Mensaje del usuario
        user_memory: Memoria del usuario
        intent_analysis: Resultado del análisis de intención
        context_info: Información adicional de contexto
        
    Returns:
        Prompt completo para generar respuesta
    """
    
    user_context = ""
    if user_memory:
        user_context = f"""
INFORMACIÓN DEL USUARIO:
- Nombre: {user_memory.name if user_memory.name else 'No especificado'}
- Profesión: {user_memory.role if user_memory.role else 'No especificada'}
- Etapa: {user_memory.stage}
- Interacciones previas: {user_memory.interaction_count}
- Lead score: {user_memory.lead_score}/100
- Intereses: {', '.join(user_memory.interests) if user_memory.interests else 'Ninguno'}
- Puntos de dolor: {', '.join(user_memory.pain_points) if user_memory.pain_points else 'Ninguno'}
"""
    
    return f"""
{SYSTEM_PROMPT}

MENSAJE DEL USUARIO: {user_message}

{user_context}

ANÁLISIS DE INTENCIÓN:
- Categoría: {intent_analysis.get('category', 'GENERAL_QUESTION')}
- Confianza: {intent_analysis.get('confidence', 0.5)}
- Enfoque recomendado: {intent_analysis.get('response_focus', 'Responder directamente')}
- Acción recomendada: {intent_analysis.get('recommended_action', 'continue_conversation')}
- Nivel de urgencia: {intent_analysis.get('urgency_level', 'medium')}

{context_info}

INSTRUCCIONES ESPECÍFICAS:
1. Responde de manera natural y conversacional
2. Usa el formato WhatsApp (párrafos cortos, emojis apropiados)
3. Personaliza basándote en la información del usuario
4. Mantén el mensaje entre 100-200 palabras
5. Incluye un call-to-action claro al final
6. NO inventes información que no tengas confirmada

RESPONDE COMO BRENDA:
"""

# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Ejemplo de uso de los prompts adaptados para WhatsApp.
    """
    
    # Configuración de ejemplo
    config = PromptConfig.get_config('main_agent')
    print(f"Configuración del agente: {config}")
    
    # Template de ejemplo
    welcome = WhatsAppMessageTemplates.welcome_new_user()
    print(f"\nMensaje de bienvenida:\n{welcome}")
    
    print("\n✅ Prompts para WhatsApp cargados correctamente") 