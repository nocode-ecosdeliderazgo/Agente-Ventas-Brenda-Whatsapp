# app/config/intelligent_agent_config.py

# This file centralizes all hardcoded information for the intelligent agent
# to use during the emergency deployment phase.
# The goal is to replace this with a proper database connection later.

COURSE_CONTEXT = {
    "marketing_digital": {
        "title": "TRANSFORMACIÓN REAL PARA TU ÁREA DE MARKETING DIGITAL",
        "intro": "Gael, entiendo que en marketing digital, la eficiencia es clave para destacar en un mercado tan competitivo.\nAplicar inteligencia artificial en tu área puede ser un cambio de juego.\nAquí hay algunas formas en que nuestro curso puede ayudarte:",
        "talking_points": [
            {
                "title": "Automatización de reportes",
                "body": "Imagina reducir el tiempo que dedicas a crear reportes manualmente. Con IA, puedes generar informes automáticos que te ahorran hasta 10 horas a la semana."
            },
            {
                "title": "Optimización de contenido",
                "body": "La IA puede ayudarte a generar contenido de calidad de forma más rápida, lo que significa que puedes enfocarte en estrategias más creativas y menos en tareas rutinarias."
            },
            {
                "title": "Análisis de datos",
                "body": "Con herramientas de IA, podrás analizar el comportamiento de tus clientes de manera más efectiva, lo que te permitirá ajustar tus campañas en tiempo real y maximizar el ROI."
            }
        ],
        "case_study": "Casos como el de una de una agencia de marketing que implementó IA vieron un aumento del 30% en su eficiencia operativa y una reducción significativa en costos de producción de contenido.",
        "next_step": "💡 **¿Listo para ver cómo esto puede aplicarse específicamente a tu equipo?** Podemos agendar una consulta para explorar tus necesidades y cómo la IA puede ser parte de tu estrategia.",
        "closing_prompt": "¿Qué te parece? ¡Vamos a dar el siguiente paso hacia la innovación! ✨"
    }
}

FAQ_CONTEXT = {
    "team_readiness": {
        "keywords": ["enseñar", "enseñe", "capacitado", "instructor", "profesor", "quien da el curso", "Ernesto", "Ale"],
        "answer": (
            "El curso es impartido por dos expertos con perfiles complementarios que garantizan una formación integral:\n\n"
            "👨‍🏫 **Ernesto H. Martínez** - *\"El Pastor Cibernético\"*\n"
            "Es Ingeniero en Sistemas con más de 15 años de experiencia en transformación digital. Ha implementado más de 200 proyectos de automatización e IA y es consultor certificado en Google Cloud AI y Microsoft AI. Él aporta la visión estratégica y técnica.\n\n"
            "👩‍🎨 **Ale Rodríguez Escobar** - *\"La Arquitecta Audiovisual\"*\n"
            "Es Maestra en Diseño Multimedia y experta en comunicación visual y experiencia de usuario. Ha optimizado más de 50 proyectos de contenido digital con IA, especializándose en prompting creativo y storytelling. Ella aporta la visión práctica y creativa."
        )
    },
    "advisor_contact": {
        "keywords": ["asesor", "contacto", "persona", "humano", "ayuda", "llamar", "telefono"],
        "answer": (
            "¡Excelente, {user_name}! Como experto en Marketing Digital, entiendo que tienes necesidades específicas de IA. He enviado tu solicitud a nuestro Asesor Comercial especializado en trabajar con profesionales en tu área.\n\n"
            "🤝 *Un asesor se contactará contigo muy pronto* para ayudarte de manera personalizada sobre IA.\n\n"
            "🕒 *Tiempo estimado de contacto*: Dentro de las próximas 2 horas en horario laboral (9 AM - 6 PM, México).\n\n"
            "El Asesor Comercial podrá ofrecerte:\n"
            "✅ Análisis personalizado de tu caso como Marketing Digital\n"
            "✅ Recomendaciones específicas para tu industria\n"
            "✅ Propuesta de implementación de IA en tu área\n"
            "✅ Precios corporativos y facilidades de pago\n\n"
            "Mientras esperamos su contacto, ¿hay algo más en lo que pueda ayudarte? 🤔"
        )
    }
}

# Combine all contexts into a single dictionary for easy access
INTELLIGENT_AGENT_CONFIG = {
    "courses": COURSE_CONTEXT,
    "faq": FAQ_CONTEXT
}

def get_agent_config():
    """
    Función para obtener la configuración del agente inteligente.
    Permite importar la configuración desde otros archivos.
    
    Returns:
        dict: Diccionario con toda la configuración del agente
    """
    return INTELLIGENT_AGENT_CONFIG