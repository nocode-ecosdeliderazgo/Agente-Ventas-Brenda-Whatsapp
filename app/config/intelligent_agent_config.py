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
    
    "certification": {
        "keywords": ["certificado", "badge", "diploma", "acreditación", "reconocimiento", "título", "validación"],
        "answer": (
            "🎓 **CERTIFICADO OFICIAL:**\n\n"
            "✅ Recibes certificado digital \"Experto en IA para Profesionales\" con código único de validación\n"
            "✅ Evaluación práctica: proyecto integrador + diseño de workflow (90 minutos)\n"
            "✅ Requisitos: 75% asistencia + 70% calificación mínima\n"
            "✅ Reconocido por empresas, válido para CV y LinkedIn\n"
            "✅ Badge digital para perfil profesional\n\n"
            "Este certificado te posiciona como líder en innovación digital y te diferencia en el mercado laboral."
        )
    },
    
    "tools_platforms": {
        "keywords": ["herramientas", "plataformas", "Coda.io", "APIs", "SDKs", "software", "tecnología", "qué usaremos"],
        "answer": (
            "🛠️ **HERRAMIENTAS Y PLATAFORMAS QUE DOMINARÁS:**\n\n"
            "**IA Generativa:**\n"
            "• ChatGPT Plus (configuración avanzada)\n"
            "• Google Gemini Advanced\n"
            "• Custom GPTs personalizados\n"
            "• Custom Gems especializados\n\n"
            "**Plataformas de Productividad:**\n"
            "• Coda.io para reportes automatizados\n"
            "• Zapier para flujos de trabajo\n"
            "• Make.com para automatizaciones\n\n"
            "**APIs y Integraciones:**\n"
            "• OpenAI API para desarrollos custom\n"
            "• Google AI Studio\n"
            "• Integraciones con CRM/ERP existentes\n\n"
            "**Todas las herramientas incluyen plantillas listas para usar en tu empresa.**"
        )
    },
    
    "course_sessions": {
        "keywords": ["sesiones", "clases", "horarios", "programa", "temario", "cronograma", "objetivos"],
        "answer": (
            "📚 **PROGRAMA DETALLADO - 4 SESIONES INTENSIVAS:**\n\n"
            "**Sesión 1: Fundamentos y Configuración (3h)**\n"
            "• Panorama IA para PyMEs\n"
            "• Configuración ChatGPT + Gemini\n"
            "• Primeros prompts efectivos\n"
            "• Casos de uso inmediatos\n\n"
            "**Sesión 2: Prompting Avanzado (3h)**\n"
            "• Framework IMPULSO\n"
            "• Plantillas reutilizables\n"
            "• Integración con datos empresariales\n\n"
            "**Sesión 3: Customización y Agentes (3h)**\n"
            "• Custom GPTs operativos\n"
            "• Custom Gems especializados\n"
            "• Flujos automatizados\n\n"
            "**Sesión 4: Implementación y ROI (3h)**\n"
            "• Metodología de implementación\n"
            "• KPIs SMART y medición\n"
            "• Proyecto final con ROI proyectado\n\n"
            "**Modalidad:** 100% online en vivo, Martes y Jueves 6-9 PM (México)"
        )
    },
    
    "investment_pricing": {
        "keywords": ["precio", "costo", "inversión", "pago", "cuánto cuesta", "valor", "descuento"],
        "answer": (
            "💰 **INVERSIÓN Y FORMAS DE PAGO:**\n\n"
            "**Inversión Total: $2,990 MXN**\n"
            "*(Valor real del programa: $8,500 MXN)*\n\n"
            "**Opciones de Pago:**\n"
            "1️⃣ **Pago único:** $2,990 MXN - ¡Acceso inmediato!\n"
            "2️⃣ **2 pagos:** $1,495 MXN c/u - Sin intereses\n"
            "3️⃣ **Descuento grupal:** 10% OFF para equipos 3+ personas\n\n"
            "**BONOS POR INSCRIPCIÓN:**\n"
            "🎁 Sesión 1:1 personalizada (valor $1,500)\n"
            "🎁 Kit plantillas avanzadas (valor $800)\n"
            "🎁 Comunidad VIP 1 año (valor $1,200)\n\n"
            "**Garantía:** 100% satisfacción o reembolso completo"
        )
    },
    
    "included_materials": {
        "keywords": ["incluye", "materiales", "recursos", "PDF", "grabaciones", "plantillas", "qué recibo"],
        "answer": (
            "📦 **TODO LO QUE INCLUYE TU INVERSIÓN:**\n\n"
            "**📄 Recursos Descargables:**\n"
            "• PDF Ejecutivo \"Guía IA para PyMEs\" (120+ páginas)\n"
            "• 50+ plantillas de prompts empresariales\n"
            "• Checklist implementación 30 días\n"
            "• Templates Custom GPTs pre-configurados\n\n"
            "**🎥 Acceso Digital:**\n"
            "• Grabaciones HD de las 4 sesiones (6 meses)\n"
            "• 2 Sesiones Q&A adicionales en vivo\n"
            "• Comunidad privada Discord\n"
            "• Updates mensuales con nuevas técnicas\n\n"
            "**🤝 Soporte Incluido:**\n"
            "• Acompañamiento durante implementación\n"
            "• Revisión personalizada proyecto final\n"
            "• Certificado con validación LinkedIn"
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