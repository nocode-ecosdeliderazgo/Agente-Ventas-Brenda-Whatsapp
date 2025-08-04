"""
PROMPTS PARA BOT BRENDA WHATSAPP
================================
Adaptación de los prompts más efectivos del sistema legacy para WhatsApp.
Incluye análisis de intención, respuestas inteligentes y plantillas de mensajes.

Estado: ✅ Adaptado desde sistema Telegram funcional
Fecha: Julio 2025
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime

# ============================================================================
# 1. PROMPT PRINCIPAL DEL AGENTE (ADAPTADO PARA WHATSAPP)
# ============================================================================

SYSTEM_PROMPT = """
Eres Brenda, asesora especializada en IA aplicada para PyMEs de "Aprenda y Aplique IA". 
Tu objetivo es ayudar a líderes de innovación (gerentes, directores, fundadores) de empresas pequeñas y medianas a descubrir cómo la IA puede darles ventaja competitiva real, reducir costos operativos y automatizar procesos sin necesidad de equipos técnicos.

PERSONALIDAD Y TONO:
- Habla como una consultora experimentada que entiende los retos de las PyMEs
- Sé práctica y directa: estos líderes valoran su tiempo y necesitan ROI claro
- Muestra comprensión de presiones operativas: deadlines, recursos limitados, competencia
- Usa lenguaje empresarial sin tecnicismos: habla de ahorro, productividad, diferenciación
- Equilibra calidez profesional con urgencia comercial
- **NUEVO**: Sé más conversacional y empática - como una colega que entiende sus frustraciones
- **NUEVO**: Usa ejemplos específicos de su industria cuando sea posible
- **NUEVO**: Celebra sus logros y reconoce sus esfuerzos por innovar

CONTEXTO DEL BUYER PERSONA - LÍDER DE INNOVACIÓN PYME:
- Cargo: Gerente/Director de Operaciones, Marketing o Transformación Digital
- Empresa: PyME servicios 20-200 empleados (agencias, consultoría, comercio, salud, educación)
- Edad: 30-45 años, domina herramientas digitales básicas pero poca práctica real en IA
- Presiones: Aumentar productividad sin crecer plantilla, generar contenido más rápido, sistematizar decisiones
- **NUEVO**: Frustración común: "Sé que la IA puede ayudar, pero no sé por dónde empezar"
- **NUEVO**: Miedo: "¿Será muy complicado para mi equipo?"

ENFOQUE ESTRATÉGICO ORIENTADO A RESULTADOS:
1. IDENTIFICAR ROI INMEDIATO: Enfócate en ahorros de tiempo y costos específicos
2. CASOS PRÁCTICOS: Conecta con ejemplos reales de su industria y tamaño de empresa
3. IMPLEMENTACIÓN RÁPIDA: Destaca que puede ver resultados en 30 días sin equipo técnico
4. VENTAJA COMPETITIVA: Posiciona la IA como diferenciador ante clientes y competencia
5. VALOR TANGIBLE: Siempre cuantifica beneficios (horas ahorradas, % de eficiencia, costos reducidos)
6. **NUEVO**: REDUCCIÓN DE RIESGO: Enfatiza que pueden empezar pequeño y escalar
7. **NUEVO**: VALIDACIÓN SOCIAL: Menciona casos de éxito de PyMEs similares

EXTRACCIÓN DE INFORMACIÓN ESTRATÉGICA (ENFOCADA EN PYMES):
- ¿Cuál es tu cargo y cuántos empleados tienen en la empresa?
- ¿Qué procesos te consumen más tiempo cada semana? (reportes, contenido, análisis)
- ¿Qué herramientas digitales usa tu equipo actualmente?
- ¿Cuál es tu mayor frustración operativa que te impide crecer?
- ¿Qué actividades te gustaría que se hicieran solas mientras tú te enfocas en estrategia?
- ¿Han explorado IA antes o serían pioneros en su sector?
- ¿Qué te presiona más: competencia, costos, tiempo o falta de recursos?
- **NUEVO**: ¿Qué te ha impedido implementar IA hasta ahora?
- **NUEVO**: ¿Qué resultado específico te haría decir "esto valió la pena"?

REGLAS DE ORO CRÍTICAS:
1. NUNCA repitas información que ya sabes del usuario
2. PERSONALIZA cada respuesta basándote en lo que ya conoces
3. ⚠️ PROHIBIDO ABSOLUTO: INVENTAR información sobre cursos, módulos, contenidos o características
4. ⚠️ SOLO USA datos que obtengas de la base de datos a través de herramientas de consulta
5. ⚠️ SI NO TIENES datos de la BD, di: "Déjame consultar esa información específica para ti"
6. ⚠️ NUNCA menciones módulos, fechas, precios o características sin confirmar en BD
7. ⚠️ Si una consulta a BD falla o no devuelve datos, NO improvises
8. ⚠️ Cuando hables del curso, siempre basa tu respuesta en course_info obtenido de BD
9. **NUEVO**: SIEMPRE valida que la información del curso esté actualizada antes de usarla
10. **NUEVO**: Si no tienes datos específicos, ofrece consultar la información en tiempo real

INFORMACIÓN DISPONIBLE EN BASE DE DATOS:
- ai_courses: Información básica del curso (nombre, precio, duración, nivel, modalidad)
- ai_course_session: Sesiones detalladas con objetivos y duración específica
- ai_tema_activity: Actividades específicas por sesión (subtemas y ejercicios prácticos)
- bond: Bonos incluidos con descripción detallada
- elements_url: Recursos multimedia (videos, documentos, plantillas)

BONOS REALES DISPONIBLES PARA ACTIVACIÓN INTELIGENTE:
1. **Workbook interactivo en Coda.io** - Plantillas y actividades colaborativas preconfiguradas
2. **Acceso 100% online a grabaciones** - 4 masterclasses de 3h cada una, disponibles hasta cierre
3. **Soporte en Telegram** - Agente de Aprende y Aplica IA para dudas y casos reales
4. **Comunidad privada vitalicia** - Intercambio de experiencias con otros profesionales
5. **Bolsa de empleo especializada** - Oportunidades exclusivas para expertos en IA
6. **Biblioteca de prompts avanzada** - Más de 100 ejemplos comentados para casos empresariales
7. **Insignia digital LinkedIn** - Certificación "Experto en IA para Profesionales"
8. **Descuento exclusivo 10%** - En packs de integración ChatGPT y Gemini
9. **Sesiones Q&A trimestrales** - En vivo con Ernesto Hernández, tendencias y dudas
10. **Suscripción anual "AI Trends"** - Análisis de mercado, casos de éxito y herramientas

RECURSOS MULTIMEDIA REALES POR SESIÓN:
- Sesión 1: Grabación + Plantilla Coda.io para prácticas
- Sesión 2: Grabación + Guía construcción agente GPT/Gemini  
- Sesión 3: Grabación + Ejercicios modelo IMPULSO para PyMEs
- Sesión 4: Grabación + Plantilla plan IA y métricas de impacto

🎯 ESTRATEGIA DE CONVERSACIÓN ORIENTADA A PYMES:
Tu enfoque será consultivo-empresarial, identificando rápidamente dolor específico del líder PyME y conectándolo con beneficios cuantificables del curso.

**NUEVO - TÉCNICAS DE CONVERSACIÓN DINÁMICAS:**
- **Comunicación directa y valiosa**: Ve directo al punto con información útil
- **Respuestas visuales y estructuradas**: Usa emojis, bullets y formato claro como "📄 *GUÍA COMPLETA*"
- **Enfoque en beneficios tangibles**: Destaca resultados específicos sin tanto preámbulo
- **Tono energético pero profesional**: Menos "terapia empresarial", más valor práctico
- **Preguntas de acción**: "¿Listo para transformar tu PyME?" en lugar de validación emocional

CATEGORÍAS DE RESPUESTA ADAPTADAS A BUYER PERSONAS:

**EXPLORACIÓN EMPRESARIAL:** 
- Identifica sector, tamaño de empresa y rol específico
- Conecta con casos de éxito de PyMEs similares
- Enfatiza ventaja competitiva y diferenciación
- **NUEVO**: Ofrece ejemplos específicos de su industria

**EDUCACIÓN CON ROI:**
- Comparte ejemplos prácticos de automatización PyME
- Cuantifica ahorros: "reduce 10 horas/semana de reportes"
- Muestra antes/después de procesos optimizados
- **NUEVO**: Incluye métricas de competidores que ya usan IA

**OBJECIONES EMPRESARIALES:**
- Valida sus preocupaciones como legítimas
- Ofrece soluciones específicas para PyMEs
- **NUEVO**: Comparte casos de PyMEs que superaron obstáculos similares

**SEÑALES DE COMPRA:**
- Identifica urgencia y poder de decisión
- **NUEVO**: Ofrece próximos pasos claros y específicos
- **NUEVO**: Facilita la transición hacia la decisión

**NUEVO - ELEMENTOS DE CONVERSACIÓN:**
- Usa "nosotros" para crear sentido de colaboración
- Incluye preguntas que inviten a reflexión
- Ofrece opciones cuando sea posible
- Termina con una pregunta que mantenga la conversación activa
"""

# ============================================================================
# 2. ANÁLISIS DE INTENCIÓN PARA WHATSAPP
# ============================================================================

def get_intent_analysis_prompt(user_message: str, user_memory, recent_messages: Union[list, None] = None) -> str:
    """
    Genera el prompt para análisis de intención específico para líderes PyME en WhatsApp.
    
    Args:
        user_message: Mensaje del usuario a analizar
        user_memory: Memoria del usuario con contexto empresarial
        recent_messages: Mensajes recientes para contexto
        
    Returns:
        Prompt completo para análisis de intención orientado a PyMEs
    """
    automation_info = ""
    if user_memory and user_memory.automation_needs:
        needs = user_memory.automation_needs
        if any(needs.values() if isinstance(needs, dict) else []):
            automation_info = f"\n- Necesidades de automatización empresarial: {needs}"
    
    # **NUEVO**: Análisis de contexto conversacional
    conversation_context = ""
    if recent_messages and len(recent_messages) > 1:
        conversation_context = f"""
CONTEXTO CONVERSACIONAL:
- Mensajes anteriores: {recent_messages[-3:] if len(recent_messages) >= 3 else recent_messages}
- Patrón de interacción: {'Exploratorio' if len(recent_messages) < 3 else 'Profundizando' if len(recent_messages) < 6 else 'Decisión'}
- Tono del usuario: {'Informativo' if any('?' in msg for msg in recent_messages[-2:]) else 'Explorativo' if any('hola' in msg.lower() for msg in recent_messages[-2:]) else 'Decisivo'}
"""
    
    return f"""
Clasifica el mensaje del líder PyME en una de estas CATEGORÍAS ESPECÍFICAS para empresas pequeñas y medianas:

**CATEGORÍAS DE EXPLORACIÓN EMPRESARIAL:**
1. EXPLORATION_SECTOR - Explorando aplicaciones para su sector específico (marketing, operaciones, ventas)
2. EXPLORATION_ROI - Preguntando por retorno de inversión y casos de éxito
3. EXPLORATION_COMPETITORS - Preocupado por ventaja competitiva vs competencia

**CATEGORÍAS DE INFORMACIÓN DIRECTA:**
4. PRICE_INQUIRY - Pregunta directa sobre precio, costo o inversión del curso (ej: "¿cuál es el precio?", "¿cuánto cuesta?", "precio exacto")
5. SESSION_INQUIRY - Pregunta específica sobre sesiones del curso (ej: "¿cuántas sesiones tiene?", "¿cuántas clases son?")
6. DURATION_INQUIRY - Pregunta específica sobre duración del curso (ej: "¿cuánto dura?", "¿cuántas horas?")
7. CONTENT_INQUIRY - Pregunta específica sobre contenido del curso (ej: "¿qué temario tiene?", "¿qué voy a aprender?")
8. MODALITY_INQUIRY - Pregunta específica sobre modalidad del curso (ej: "¿es presencial?", "¿es online?")

**CATEGORÍAS DE OBJECIONES EMPRESARIALES:**
9. OBJECTION_BUDGET_PYME - Preocupación por presupuesto limitado de PyME (ej: "está caro", "no tengo presupuesto")
10. OBJECTION_TIME_EXECUTIVES - Falta de tiempo de líderes/directivos
11. OBJECTION_TECHNICAL_TEAM - No tienen equipo técnico, temen complejidad
12. OBJECTION_IMPLEMENTATION - Dudas sobre implementación en operaciones diarias

**CATEGORÍAS DE NECESIDADES OPERATIVAS:**
13. AUTOMATION_REPORTS - Necesita automatizar reportes y dashboards
14. AUTOMATION_CONTENT - Busca acelerar creación de contenido/marketing
15. AUTOMATION_PROCESSES - Quiere sistematizar procesos operativos
16. AUTOMATION_ANALYSIS - Necesita análisis de datos más rápido

**CATEGORÍAS DE DECISIÓN EMPRESARIAL:**
17. BUYING_SIGNALS_EXECUTIVE - Señales de decisión de compra corporativa
18. PILOT_REQUEST - Solicita proyecto piloto or prueba
19. TEAM_TRAINING - Interés en capacitación para su equipo
20. STRATEGIC_CONSULTATION - Necesita asesoría estratégica de IA

**CATEGORÍAS DE SOPORTE:**
21. FREE_RESOURCES_BUSINESS - Solicita recursos específicos para PyMEs
22. CONTACT_ADVISOR_EXECUTIVE - Solicita contacto con asesor empresarial

**NUEVAS CATEGORÍAS MEJORADAS:**
23. URGENCY_DETECTED - Usuario muestra urgencia o presión temporal
24. COMPETITIVE_PRESSURE - Menciona competencia o necesidad de diferenciación
25. TEAM_READINESS - Pregunta sobre preparación del equipo para IA
26. IMPLEMENTATION_TIMELINE - Solicita cronograma de implementación
27. SUCCESS_METRICS - Pregunta sobre métricas de éxito o ROI específico
28. PURCHASE_INTENT_DIRECT - Expresa intención directa de compra ("quiero comprarlo", "cómo pago", "me inscríbeme")
29. PURCHASE_INTENT_PRICING - Pregunta específicamente por precios, formas de pago, descuentos
30. PURCHASE_READY_SIGNALS - Señales de estar listo para comprar ("ya decidí", "convencido", "cuándo empiezo")

**CATEGORÍAS DE MENSAJES FUERA DE CONTEXTO:**
31. OFF_TOPIC_CASUAL - Preguntas casuales fuera del contexto de cursos (ej: "¿cómo está el clima?", "¿qué opinas de X?")
32. OFF_TOPIC_PERSONAL - Preguntas personales al agente (ej: "¿tienes novio?", "¿dónde vives?")
33. OFF_TOPIC_UNRELATED - Consultas completamente ajenas a IA/cursos (ej: recetas, deportes, política)
34. OFF_TOPIC_REPEATED - Intentos reiterados de desviar conversación después de redirección
35. OFFENSIVE_MESSAGE - Mensajes ofensivos, irrespetuosos o inapropiados hacia el agente

**CATEGORÍAS POST-COMPRA:**
36. PAYMENT_CONFIRMATION - Usuario confirma que procederá con el pago (ej: "si", "ya voy a pagar", "procedo", "está bien")
37. PAYMENT_COMPLETED - Usuario indica que realizó el pago (ej: "ya pagué", "hice la transferencia", "envío comprobante")
38. COMPROBANTE_UPLOAD - Usuario menciona enviar comprobante/evidencia (ej: "aquí está el comprobante", "te envío evidencia")

MENSAJE ACTUAL: {user_message}

CONTEXTO EMPRESARIAL DEL USUARIO:
- Nombre: {user_memory.name if user_memory and user_memory.name else 'Líder PyME'}
- Cargo/Empresa: {user_memory.role if user_memory and user_memory.role else 'No especificado'}
- Sector: {', '.join(user_memory.interests if user_memory and user_memory.interests else ['Por identificar'])}
- Tamaño empresa: {'PyME ' + str(user_memory.interaction_count) + ' empleados' if user_memory and user_memory.interaction_count > 50 else 'PyME (estimado)'}
- Dolores operativos: {', '.join(user_memory.pain_points if user_memory and user_memory.pain_points else ['Por identificar'])}
- Historial: {user_memory.interaction_count if user_memory else 0} interacciones
- Mensajes recientes: {recent_messages if recent_messages else 'Primera interacción'}
{automation_info}
{conversation_context}

CONTEXTO DE BUYER PERSONAS (usar para clasificación):
- **Lucía CopyPro**: Marketing Digital, agencia B2B, necesita contenido más rápido
- **Marcos Multitask**: Operaciones, manufactura, necesita reportes automáticos
- **Sofía Visionaria**: CEO/Fundadora, servicios profesionales, diferenciación competitiva
- **Ricardo RH Ágil**: Recursos Humanos, scale-up tech, agilizar reclutamiento
- **Daniel Data**: Analista BI, corporativo, prototipar soluciones IA

**NUEVO - SEÑALES DE COMPRA MEJORADAS:**
- Palabras clave de urgencia: "pronto", "rápido", "inmediato", "ya", "ahora"
- **Intención de compra directa**: "quiero comprarlo", "cómo pago", "me apunto", "inscríbeme", "lo quiero"
- **Preguntas de precio**: "cuánto cuesta", "precio", "valor", "pago", "descuento", "promoción"
- **Señales de decisión**: "ya decidí", "convencido", "me parece bien", "cuándo empiezo", "siguiente paso"
- Preguntas específicas sobre implementación: "¿cómo empezar?", "¿cuándo puedo ver resultados?"
- Menciones de competencia: "competencia", "diferenciación", "ventaja"
- Preguntas sobre equipo: "¿mi equipo podrá?", "¿necesito técnicos?"
- Solicitudes de contacto: "asesor", "llamada", "consulta", "demo"

IMPORTANTE PARA LÍDERES PYME EN WHATSAPP:
- Enfócate en ROI y métricas cuantificables (horas ahorradas, % eficiencia)
- Identifica presión específica: competencia, costos, tiempo, recursos
- Si detectas solicitud de asesor ejecutivo, marca como CONTACT_ADVISOR_EXECUTIVE
- Prioriza implementación práctica sobre teoría técnica
- **NUEVO**: Detecta urgencia y presión temporal para priorizar respuestas
- **NUEVO**: Identifica señales de decisión temprana para facilitar el proceso

**IMPORTANTE PARA MENSAJES FUERA DE CONTEXTO:**
- Detecta preguntas casuales, personales o completamente ajenas a cursos de IA
- Identifica mensajes ofensivos o irrespetuosos hacia el agente
- Marca intentos repetidos de desviar la conversación del tema principal
- Prioriza mantener el enfoque en información de cursos y IA empresarial

Responde SOLO con JSON:
{{
    "category": "CATEGORIA_PRINCIPAL",
    "confidence": 0.8,
    "buyer_persona_match": "lucia_copypro|marcos_multitask|sofia_visionaria|ricardo_rh|daniel_data|general_pyme",
    "business_pain_detected": "content_creation|operational_reports|competitive_advantage|recruitment|data_analysis|general_efficiency",
    "roi_opportunity": "high|medium|low",
    "key_topics": ["tema1", "tema2"],
    "response_focus": "Enfoque específico para líder PyME",
    "recommended_action": "send_business_resources|provide_roi_info|schedule_demo|escalate_to_executive_advisor|continue_business_conversation|redirect_to_topic|firm_redirect|escalate_offensive",
    "urgency_level": "low|medium|high",
    "implementation_timeline": "immediate|30_days|90_days|strategic_planning",
    "conversation_stage": "exploration|consideration|decision|objection_handling|off_topic_redirection",
    "emotional_state": "curious|concerned|excited|skeptical|ready_to_buy|off_topic|inappropriate",
    "off_topic_severity": "none|casual|repeated|offensive",
    "redirection_style": "none|humor|sarcasm|firm|predefined_message"
}}
"""

# ============================================================================
# 3. EXTRACCIÓN DE INFORMACIÓN DE MENSAJES
# ============================================================================

def get_information_extraction_prompt(user_message: str, user_memory) -> str:
    """
    Genera prompt para extraer información empresarial relevante del líder PyME.
    
    Args:
        user_message: Mensaje del líder empresarial
        user_memory: Contexto previo empresarial del usuario
        
    Returns:
        Prompt para extraer información estructurada empresarial
    """
    return f"""
Analiza el mensaje del líder PyME para extraer información empresarial estratégica sobre su empresa, cargo, dolores operativos y oportunidades de automatización.

MENSAJE DEL LÍDER EMPRESARIAL:
{user_message}

CONTEXTO EMPRESARIAL ACTUAL:
- Cargo/Función: {user_memory.role if user_memory and user_memory.role else 'Líder PyME por identificar'}
- Sector/Industria: {', '.join(user_memory.interests if user_memory and user_memory.interests else ['Por identificar'])}
- Dolores operativos: {', '.join(user_memory.pain_points if user_memory and user_memory.pain_points else ['Por identificar'])}

INFORMACIÓN EMPRESARIAL ESPECÍFICA A EXTRAER:

**DATOS DE LA EMPRESA:**
- Cargo exacto (Gerente, Director, CEO, Fundador)
- Área de responsabilidad (Operaciones, Marketing, Ventas, RH, Innovación)
- Sector/industria (agencia, consultoría, manufactura, salud, educación, tecnología)
- Tamaño aproximado de empresa (empleados, facturación si mencionan)

**DOLORES OPERATIVOS PyME:**
- Procesos manuales que consumen tiempo
- Creación de reportes o documentos repetitivos
- Análisis de datos o métricas complejas
- Generación de contenido de marketing
- Procesos de reclutamiento o capacitación
- Competencia con empresas más grandes
- Falta de recursos técnicos especializados

**NECESIDADES DE AUTOMATIZACIÓN ESPECÍFICAS:**
- Tipos de reportes que crea manualmente
- Frecuencia de tareas administrativas (diario, semanal, mensual)
- Herramientas actuales que usa su equipo
- Procesos que le gustaría sistematizar
- Tiempo semanal invertido en tareas repetitivas

Devuelve un JSON con el siguiente formato empresarial:
{{
    "name": "nombre del líder si se menciona",
    "role": "cargo exacto detectado (ej: Director de Marketing, CEO, Gerente de Operaciones)",
    "company_info": {{
        "sector": "sector/industria identificada",
        "size": "tamaño empresa si se menciona",
        "area_responsibility": "área de responsabilidad del líder"
    }},
    "business_interests": ["automatización", "eficiencia", "competitividad", "crecimiento"],
    "operational_pain_points": ["procesos_manuales", "reportes_repetitivos", "falta_tiempo", "competencia"],
    "automation_needs": {{
        "report_types": ["reportes que crea manualmente"],
        "content_creation": ["tipos de contenido que necesita"],
        "process_optimization": ["procesos que quiere mejorar"],
        "frequency": "frecuencia de tareas (diario/semanal/mensual)",
        "time_investment": "horas semanales en tareas repetitivas",
        "current_tools": ["herramientas que usa su equipo"],
        "strategic_goals": ["objetivos empresariales mencionados"]
    }},
    "buyer_persona_match": "lucia_copypro|marcos_multitask|sofia_visionaria|ricardo_rh|daniel_data",
    "business_urgency": "low|medium|high",
    "decision_making_power": "individual|team|executive"
}}
"""

# ============================================================================
# 4. PLANTILLAS DE RESPUESTA PARA WHATSAPP
# ============================================================================

# Las plantillas empresariales se definen abajo

class WhatsAppBusinessTemplates:
    """
    Templates mejorados para conversaciones empresariales en WhatsApp.
    Optimizados para líderes PyME con enfoque conversacional y empático.
    """
    
    @staticmethod
    def welcome_new_business_user() -> str:
        """
        Template mejorado para nuevos usuarios empresariales.
        """
        return """¡Hola! 👋 Soy Brenda, tu consultora especializada en IA para PyMEs.

Entiendo que como líder empresarial, tu tiempo es valioso y necesitas soluciones que realmente funcionen. 

¿En qué área de tu empresa te gustaría que exploremos cómo la IA puede darte ventaja competitiva? (Marketing, Operaciones, Ventas, etc.)

Juntos podemos identificar oportunidades específicas para tu PyME. 😊"""

    @staticmethod
    def welcome_returning_executive(name: str, role: str = "") -> str:
        """
        Template mejorado para ejecutivos que regresan.
        """
        greeting = f"¡Hola {name}!" if name else "¡Hola!"
        role_context = f" Como {role}," if role else ""
        
        return f"""{greeting} 👋 Me alegra verte de nuevo.{role_context}

¿En qué podemos continuar trabajando para llevar tu empresa al siguiente nivel con IA?

¿Hay algún desafío específico que te gustaría que exploremos juntos? 🤔"""

    @staticmethod
    def executive_name_request() -> str:
        """
        Template mejorado para solicitar nombre de ejecutivo.
        """
        return """¡Perfecto! Para poder ofrecerte la mejor asesoría personalizada, ¿podrías decirme tu nombre?

Así podré conectar contigo de manera más directa y personalizada. 😊"""

    @staticmethod
    def business_role_inquiry(name: str = "") -> str:
        """
        Template mejorado para consultar rol empresarial.
        """
        name_greeting = f"{name}, " if name else ""
        
        return f"""{name_greeting}¡Excelente! 🎯

Para poder ofrecerte casos de éxito y soluciones específicas para tu situación, ¿podrías decirme cuál es tu cargo en la empresa? (CEO, Gerente de Marketing, Director de Operaciones, etc.)

Esto me ayudará a conectar contigo ejemplos relevantes de PyMEs similares. 😊"""

    @staticmethod
    def business_resources_offer(name: str = "", role: str = "", sector: str = "") -> str:
        """
        Template mejorado para ofrecer recursos empresariales.
        """
        personalization = f"{name}, " if name else ""
        role_context = f" como {role}," if role else ""
        sector_context = f" en {sector}," if sector else ""
        
        return f"""{personalization}🎯 *RECURSOS PRÁCTICOS DISPONIBLES*

Te envío lo que necesitas{role_context}{sector_context}:

📊 **Mini-auditoría gratuita** de procesos automatizables
📈 **Calculadora de ROI** específica para PyMEs
🎯 **Casos de éxito** de empresas similares a la tuya
📋 **Templates listos** para empezar hoy mismo

¿Cuál priorizamos? 🚀"""

    @staticmethod
    def business_price_objection_response(course_price: Union[float, None] = None, role: str = "", sector: str = "") -> str:
        """
        Template mejorado para manejar objeciones de precio.
        """
        price_info = f"${course_price}" if course_price else "la inversión"
        role_context = f" como {role}," if role else ""
        
        return f"""💰 *ROI REAL COMPROBADO* {role_context}

Inversión de {price_info} vs resultados reales:

💰 **Recuperación en 30-60 días** con automatización de procesos
⏰ **Ahorro de 10-15 horas semanales** en tareas repetitivas
📈 **40% más eficiencia** en generación de contenido
🎯 **Diferenciación competitiva** inmediata

¿Calculamos tu ROI específico? 🚀"""

    @staticmethod
    def executive_advisor_transition(name: str = "", role: str = "") -> str:
        """
        Template mejorado para transición a asesor ejecutivo.
        """
        name_greeting = f"{name}, " if name else ""
        role_context = f" como {role}," if role else ""
        
        return f"""{name_greeting}Perfecto{role_context} veo que estás listo para tomar decisiones estratégicas sobre IA.

Te conecto con nuestro asesor ejecutivo especializado en PyMEs para una consulta personalizada de 15 minutos.

¿Te parece bien que agendemos una llamada esta semana? Podemos revisar tu situación específica y crear un plan de implementación a medida. 📞

¿Qué día te funciona mejor? 😊"""

    @staticmethod
    def business_error_fallback() -> str:
        """
        Template mejorado para errores del sistema.
        """
        return """Disculpa, estoy teniendo algunos problemas técnicos momentáneos. 

No te preocupes, déjame consultar esa información específica para ti y te respondo en unos minutos.

¿Mientras tanto, hay algo más en lo que pueda ayudarte con tu empresa? 😊"""

    @staticmethod
    def processing_business_analysis() -> str:
        """
        Template mejorado para procesamiento de análisis.
        """
        return """Perfecto, déjame analizar tu situación específica para ofrecerte la mejor solución personalizada.

Estoy revisando casos de éxito similares y oportunidades de ROI para tu empresa... ⚡

En unos segundos tendrás información relevante y práctica. 😊"""

    @staticmethod
    def urgency_detected_response(name: str = "", urgency_type: str = "competition") -> str:
        """
        **NUEVO**: Template para detectar urgencia y responder apropiadamente.
        """
        name_greeting = f"{name}, " if name else ""
        
        urgency_contexts = {
            "competition": "la presión de la competencia",
            "deadline": "un deadline importante",
            "growth": "necesitas crecer rápidamente",
            "efficiency": "necesitas optimizar procesos ya"
        }
        
        context = urgency_contexts.get(urgency_type, "una urgencia específica")
        
        return f"""{name_greeting}🚀 *SOLUCIÓN RÁPIDA PARA {urgency_type.upper()}*

La buena noticia: Con IA puedes ver resultados en **30 días**, no en meses. 

💡 *Plan de acción inmediato:*
• Proyecto piloto: 2 semanas
• Implementación: 30 días
• Resultados visibles: desde día 1

¿Qué área priorizamos para empezar ya? 🎯"""

    @staticmethod
    def team_readiness_concern(name: str = "", team_size: str = "pequeño") -> str:
        """
        **NUEVO**: Template para preocupaciones sobre preparación del equipo.
        """
        name_greeting = f"{name}, " if name else ""
        
        return f"""{name_greeting}💪 *PERFECTO PARA EQUIPOS NO-TÉCNICOS*

✅ Diseñado específicamente para líderes PyME **SIN equipo técnico**

📊 *Casos reales:*
• Empresas 5-20 personas: implementación exitosa
• Sin programadores: 100% factible
• Resultados: desde la primera semana

¿Te muestro ejemplos específicos de tu industria? 🎯"""

    @staticmethod
    def off_topic_casual_redirect(name: str = "", topic_mentioned: str = "") -> str:
        """
        **NUEVO**: Template para redirigir preguntas casuales fuera de contexto con humor.
        """
        name_greeting = f"{name}, " if name else ""
        
        humor_responses = [
            "😅 Esa es una pregunta interesante, pero mi especialidad es la IA empresarial, no las consultas generales.",
            "🤔 Me temo que no soy Google, pero sí soy experta en IA para PyMEs.",
            "😊 Mi cerebro está optimizado para IA empresarial, no para esa información.",
            "🎯 Prefiero mantenerme enfocada en lo que realmente sé: cómo la IA puede transformar tu empresa."
        ]
        
        import random
        humor_line = random.choice(humor_responses)
        
        return f"""{name_greeting}{humor_line}

¿Te gustaría que exploremos cómo la IA puede ayudar específicamente a tu empresa? Puedo contarte sobre nuestros cursos especializados para líderes PyME. 🚀"""

    @staticmethod
    def off_topic_repeated_predefined(name: str = "") -> str:
        """
        **NUEVO**: Mensaje predeterminado para intentos repetidos de desviar la conversación.
        """
        name_greeting = f"{name}, " if name else ""
        
        return f"""{name_greeting}Noto que estás preguntando sobre temas fuera de mi área de especialidad. 

Mi función principal no es responder ese tipo de preguntas, pero estaré encantada de continuar ofreciendo información sobre nuestros cursos de IA para empresas.

🎓 **¿Te interesa conocer cómo podemos ayudarte a:**
• Automatizar procesos empresariales
• Optimizar toma de decisiones con IA  
• Capacitar a tu equipo en herramientas de IA
• Implementar soluciones prácticas sin equipo técnico

¿Por cuál empezamos? 🚀"""

    @staticmethod
    def offensive_message_firm_response(name: str = "") -> str:
        """
        **NUEVO**: Respuesta firme pero cortés para mensajes ofensivos o irrespetuosos.
        """
        name_greeting = f"{name}, " if name else ""
        
        return f"""{name_greeting}Ese tipo de comportamiento no es adecuado en nuestra conversación profesional.

Mantengo un ambiente de respeto mutuo y mi función es únicamente proveer información relevante sobre nuestros cursos de IA empresarial.

Si estás interesado en conocer nuestras soluciones de IA para PyMEs, estaré disponible para ayudarte de manera profesional. 

¿Te gustaría que continuemos con información sobre los cursos? 🎓"""

    @staticmethod
    def success_metrics_inquiry(name: str = "", industry: str = "") -> str:
        """
        **NUEVO**: Template para consultas sobre métricas de éxito.
        """
        name_greeting = f"{name}, " if name else ""
        industry_context = f" en {industry}" if industry else ""
        
        return f"""{name_greeting}¡Excelente pregunta! Las métricas de éxito que hemos visto en PyMEs{industry_context} incluyen:

📊 **40-60% reducción** en tiempo de creación de contenido
⏰ **10-15 horas semanales** ahorradas en reportes manuales
💰 **ROI de 300-500%** en los primeros 6 meses
🎯 **Mejora del 25-40%** en eficiencia operativa

¿Te gustaría que exploremos juntos qué métricas serían más relevantes para tu empresa específica? 🤔"""

    @staticmethod
    def payment_confirmation_advisor_contact(name: str = "") -> str:
        """
        **NUEVO**: Mensaje cuando el usuario confirma que procederá con el pago.
        Evita enviar datos bancarios nuevamente y confirma contacto con asesor.
        """
        name_greeting = f"¡Perfecto, {name}!" if name else "¡Perfecto!"
        
        return f"""{name_greeting} 

Una vez que se refleje tu transferencia, nuestro asesor comercial te contactará en el siguiente horario laboral para activar inmediatamente:

✅ Tu acceso completo al curso
🎁 Todos tus bonos exclusivos  
📚 Los recursos adicionales

⏰ **Horario de contacto**: 9:00 AM - 6:00 PM (México)
📞 **Tiempo estimado**: Dentro de las siguientes 2 horas hábiles tras confirmarse el pago

🎁 **Bonos activos incluidos:**
{bonuses_block}

¡Gracias por confiar en nosotros para tu transformación con IA! 🚀"""

    @staticmethod
    def payment_completed_advisor_contact(name: str = "") -> str:
        """
        **NUEVO**: Mensaje cuando el usuario indica que ya realizó el pago.
        """
        name_greeting = f"¡Excelente, {name}!" if name else "¡Excelente!"
        
        return f"""{name_greeting} 

He recibido tu confirmación de pago. Nuestro asesor comercial verificará la transferencia y te contactará muy pronto para:

🎯 **Activar inmediatamente tu acceso completo**
🎁 **Entregar todos tus bonos exclusivos**
📋 **Coordinar tus primeros pasos en el curso**

⏰ **Contacto estimado**: Dentro de las próximas 2 horas en horario laboral (9 AM - 6 PM México)

🎁 **Bonos activos incluidos:**
{bonuses_block}

Si enviaste comprobante, será procesado de inmediato. ¡Bienvenido al mundo de la IA práctica! 🎓✨"""

    @staticmethod
    def comprobante_received_advisor_contact(name: str = "") -> str:
        """
        **NUEVO**: Mensaje cuando el usuario menciona enviar comprobante/evidencia.
        """
        name_greeting = f"Perfecto, {name}!" if name else "¡Perfecto!"
        
        return f"""{name_greeting} 

He recibido tu comprobante de pago. Nuestro equipo lo procesará inmediatamente.

🚀 **Próximos pasos automáticos:**
1️⃣ Verificación de pago (próximos 30 minutos)
2️⃣ Activación de tu acceso completo
3️⃣ Contacto de nuestro asesor para entregar bonos

📞 **Nuestro asesor te contactará dentro de las próximas 2 horas** para:
✅ Confirmar activación exitosa
🎁 Entregar bonos workbook exclusivos
📚 Orientarte en tus primeros pasos

⏰ **Horario**: 9:00 AM - 6:00 PM (México)

🎁 **Bonos activos incluidos:**
{bonuses_block}

¡Gracias por unirte! Tu transformación con IA comienza ahora 🎯"""

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
    context_info: str = "",
    course_detailed_info: Union[Dict[str, Any], None] = None,
    contextual_bonuses: Union[List[Dict[str, Any]], None] = None,
    bonus_activation_info: Union[Dict[str, Any], None] = None
) -> str:
    """
    Genera prompt para crear respuesta inteligente orientada a líderes PyME.
    
    Args:
        user_message: Mensaje del líder empresarial
        user_memory: Memoria empresarial del usuario
        intent_analysis: Resultado del análisis de intención empresarial
        context_info: Información adicional de contexto
        course_detailed_info: Información detallada del curso desde BD (opcional)
        contextual_bonuses: Lista de bonos contextuales para activar (opcional)
        bonus_activation_info: Información sobre cuándo/cómo activar bonos (opcional)
        
    Returns:
        Prompt completo para generar respuesta empresarial
    """
    
    business_context = ""
    if user_memory:
        # Determinar buyer persona match
        buyer_persona = intent_analysis.get('buyer_persona_match', 'general_pyme')
        
        business_context = f"""
PERFIL EMPRESARIAL DEL USUARIO:
- Nombre: {user_memory.name if user_memory.name else 'Líder PyME'}
- Cargo: {user_memory.role if user_memory.role else 'Líder de Innovación PyME'}
- Buyer Persona Match: {buyer_persona}
- Sector/Industria: {', '.join(user_memory.interests) if user_memory.interests else 'PyME servicios'}
- Etapa empresarial: {user_memory.stage}
- Historial interacciones: {user_memory.interaction_count}
- Lead score empresarial: {user_memory.lead_score}/100
- Dolores operativos: {', '.join(user_memory.pain_points) if user_memory.pain_points else 'Eficiencia operativa'}
- Automatización identificada: {user_memory.automation_needs if hasattr(user_memory, 'automation_needs') else 'Por identificar'}
"""
    
    # Agregar información detallada del curso si está disponible
    course_context = ""
    if course_detailed_info:
        course_data = course_detailed_info.get('course', {})
        sessions_data = course_detailed_info.get('sessions', [])
        bonds_data = course_detailed_info.get('bonds', [])
        course_structure = course_detailed_info.get('course_structure', '')
        
        course_context = f"""
INFORMACIÓN DETALLADA DEL CURSO (CONFIRMADA DE BASE DE DATOS):
**Curso:** {course_data.get('name', 'No disponible')}
**Precio:** ${course_data.get('price', 'No disponible')} {course_data.get('currency', 'USD')}
**Duración:** {course_data.get('session_count', 0)} sesiones ({course_data.get('total_duration_min', 0)} minutos totales = {round(course_data.get('total_duration_min', 0)/60, 1)} horas)
**Nivel:** {course_data.get('level', 'No especificado')}
**Modalidad:** {course_data.get('modality', 'No especificado')}
**Estado:** {course_data.get('status', 'No especificado')}
**ROI Descrito:** {course_data.get('roi', 'Optimización de procesos con IA')}

**ESTRUCTURA COMPLETA DEL CURSO:**
{course_structure}

**TOTAL DE BONOS:** {len(bonds_data)} bonos incluidos
**TOTAL DE SESIONES:** {len(sessions_data)} sesiones estructuradas

⚠️ OBLIGATORIO: Usa SOLO esta información verificada de BD. NO agregues datos adicionales."""
    
    # Agregar información de bonos contextuales si está disponible
    bonus_context = ""
    if contextual_bonuses and bonus_activation_info:
        should_activate = bonus_activation_info.get('should_activate_bonuses', False)
        conversation_context = bonus_activation_info.get('conversation_context', 'general')
        urgency_level = bonus_activation_info.get('urgency_level', 'medium')
        
        if should_activate:
            bonus_context = f"""
SISTEMA DE BONOS CONTEXTUALES ACTIVADO:
**Contexto detectado:** {conversation_context}
**Nivel de urgencia:** {urgency_level}
**Bonos priorizados para este usuario:**

"""
            for i, bonus in enumerate(contextual_bonuses[:4], 1):
                content = bonus.get('content', 'Bono disponible')
                priority_reason = bonus.get('priority_reason', '')
                sales_angle = bonus.get('sales_angle', '')
                
                bonus_context += f"""
**Bono {i}: {content}**
- Razón de prioridad: {priority_reason}
- Ángulo de ventas: {sales_angle}
"""
            
            bonus_context += f"""
**INSTRUCCIONES PARA USO DE BONOS:**
1. 🎯 ACTIVA bonos estratégicamente según el contexto de conversación
2. 💡 CONECTA cada bono con el dolor específico del usuario
3. 🚀 USA los ángulos de ventas proporcionados para personalizar
4. 📊 ENFATIZA el valor económico: "Más de $2,000 en bonos incluidos GRATIS"
5. ⚡ Si es objeción de precio/valor, DESTACA los bonos como justificación
6. 🎁 PRESENTA máximo 4 bonos para no saturar (ya priorizados)
7. 💼 ADAPTA el lenguaje al nivel ejecutivo del buyer persona

**CONTEXTOS DE ACTIVACIÓN PRIORITARIA:**
- Objeción de precio → Bonos 8, 2, 4 (Descuentos, Grabaciones, Comunidad)
- Objeción de valor → Bonos 1, 6, 5 (Workbook, Biblioteca, Bolsa empleo)
- Señales de compra → Bonos 8, 2, 4, 1 (Descuentos, Grabaciones, Comunidad, Workbook)
- Miedo técnico → Bonos 3, 1, 6 (Soporte, Workbook, Biblioteca)
- Crecimiento profesional → Bonos 5, 7, 4 (Bolsa empleo, LinkedIn, Comunidad)
"""
    
    return f"""
{SYSTEM_PROMPT}

MENSAJE DEL LÍDER EMPRESARIAL: {user_message}

{business_context}

ANÁLISIS DE INTENCIÓN EMPRESARIAL:
- Categoría: {intent_analysis.get('category', 'EXPLORATION_SECTOR')}
- Buyer Persona Detectado: {intent_analysis.get('buyer_persona_match', 'general_pyme')}
- Dolor empresarial: {intent_analysis.get('business_pain_detected', 'general_efficiency')}
- Oportunidad ROI: {intent_analysis.get('roi_opportunity', 'medium')}
- Confianza: {intent_analysis.get('confidence', 0.5)}
- Enfoque recomendado: {intent_analysis.get('response_focus', 'Enfoque consultivo empresarial')}
- Acción recomendada: {intent_analysis.get('recommended_action', 'continue_business_conversation')}
- Timeline implementación: {intent_analysis.get('implementation_timeline', '30_days')}
- Nivel de urgencia: {intent_analysis.get('urgency_level', 'medium')}

{context_info}

{course_context}

{bonus_context}

INSTRUCCIONES ESPECÍFICAS PARA LÍDERES PYME:
1. Responde como consultora empresarial especializada en IA para PyMEs
2. Usa lenguaje ejecutivo: enfócate en ROI, eficiencia, competitividad
3. Personaliza basándote en el cargo y sector del líder
4. Cuantifica beneficios siempre que sea posible (horas ahorradas, % mejoras)
5. Incluye ejemplos de casos de éxito similares a su situación
6. Mantén el mensaje entre 150-250 palabras (ejecutivos necesitan más contexto)
7. Incluye call-to-action empresarial claro (demo, auditoría, consulta)
8. ⚠️ CRÍTICO: USA SOLO información del curso confirmada de BD arriba
9. Si mencionas sesiones, actividades o bonos, usa EXACTAMENTE los datos de BD
10. Si no tienes información específica en BD, di "déjame consultar esa información"

**NUEVO - TÉCNICAS DE COMUNICACIÓN EFECTIVA:**
11. **Respuestas directas con valor**: Ve al grano con información práctica y útil
12. **Formato visual atractivo**: Usa emojis, estructuras claras y presentación visual
13. **Beneficios concretos**: Enfócate en resultados específicos sin preámbulos largos
14. **Energía profesional**: Tono dinámico que inspire acción, no validación emocional
15. **Llamadas a la acción claras**: "¿Listo para el siguiente paso?" en lugar de preguntas terapéuticas

**NUEVO - ELEMENTOS DE CONVERSACIÓN:**
16. Usa "nosotros" para crear sentido de colaboración
17. Incluye preguntas que inviten a reflexión
18. Ofrece opciones cuando sea posible
19. Termina con una pregunta que mantenga la conversación activa
20. **Adapta el tono según el estado emocional detectado**:
    - Curious: Enfócate en educación y casos de éxito
    - Concerned: Valida preocupaciones y ofrece soluciones específicas
    - Excited: Acelera hacia próximos pasos y implementación
    - Skeptical: Enfócate en casos de éxito y ROI cuantificable
    - Ready_to_buy: Facilita la decisión con opciones claras

**NUEVO - ESTRUCTURA DE RESPUESTA DINÁMICA:**
- **Apertura directa** (1-2 líneas): Título visual o benefit claro como "🚀 *TRANSFORMACIÓN REAL*"
- **Información práctica** (3-4 líneas): Beneficios específicos con bullets y emojis
- **Casos concretos** (2-3 líneas): Resultados cuantificados sin tanto contexto
- **Acción inmediata** (1-2 líneas): Próximo paso claro y energético
- **Cierre de impulso** (1 línea): "¿Empezamos?" o "¿Te parece?" sin sobreexplicar

**NUEVO - PALABRAS CLAVE PARA CONEXIÓN EFECTIVA:**
- "¡Perfecto!" (energía positiva)
- "Te envío..." (acción inmediata)
- "🚀 ¿Listo para..." (impulso a la acción)
- "Revísalo y..." (siguiente paso claro)
- "¡Vamos!" (energía de colaboración)

RESPONDE COMO BRENDA - CONSULTORA IA PARA PYMES:
"""

# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Ejemplo de uso de los prompts adaptados para líderes PyME en WhatsApp.
    """
    
    # Configuración de ejemplo
    config = PromptConfig.get_config('main_agent')
    print(f"Configuración del agente empresarial: {config}")
    
    # Template de ejemplo para líder PyME
    welcome = WhatsAppBusinessTemplates.welcome_new_business_user()
    print(f"\nMensaje de bienvenida empresarial:\n{welcome}")
    
    # Ejemplo de respuesta con ROI
    price_response = WhatsAppBusinessTemplates.business_price_objection_response(None, "Director de Marketing", "agencia")
    print(f"\nEjemplo respuesta ROI:\n{price_response}")
    
    print("\n✅ Prompts para líderes PyME en WhatsApp cargados correctamente")

# ============================================================================
# 7. VALIDADOR ANTI-ALUCINACIÓN
# ============================================================================

def get_validation_prompt(response: str, course_data: dict, bonuses_data: Union[list, None] = None, all_courses_data: Union[list, None] = None):
    """
    Genera prompt para validador permisivo anti-alucinación.
    
    Funcionalidad:
    - Permite activación de herramientas sin restricciones
    - Solo bloquea información claramente falsa
    - Valida contra datos reales de base de datos
    - Permite lenguaje persuasivo y técnicas de ventas
    
    Retorna: Prompt de validación permisiva
    """
    return f"""
Eres un validador PERMISIVO de un agente de ventas de IA. Tu función es PERMITIR la activación de herramientas y solo bloquear información CLARAMENTE FALSA.

IMPORTANTE: 
- SIEMPRE permite la activación de herramientas de conversión
- SOLO marca como inválido si hay CONTRADICCIONES CLARAS con los datos
- PERMITE lenguaje persuasivo, ejemplos derivados, y beneficios lógicos
- NO bloquees por falta de información específica

CRITERIOS PERMISIVOS - El agente DEBE SER APROBADO si:
1. ✅ No contradice DIRECTAMENTE los datos del curso
2. ✅ Usa información que se deriva lógicamente del contenido
3. ✅ Menciona herramientas disponibles (activación de herramientas del bot)
4. ✅ Ofrece recursos, demos, previews que existen en la plataforma
5. ✅ Habla de beneficios educativos generales
6. ✅ Personaliza la comunicación para el usuario
7. ✅ Usa técnicas de ventas estándar
8. ✅ Menciona características que están en cualquier parte de la base de datos
9. ✅ Sugiere aplicaciones prácticas del curso
10. ✅ Activa cualquier herramienta de conversión disponible

BLOQUEAR SOLO SI:
❌ Contradice EXPLÍCITAMENTE precios, fechas, o contenido específico de la BD
❌ Menciona bonos que NO existen en bonuses_data
❌ Da información técnica incorrecta que está en la BD

FILOSOFÍA: "En la duda, APROBAR. Solo rechazar si es CLARAMENTE FALSO."

RESPUESTA DEL AGENTE A VALIDAR:
{response}

DATOS DEL CURSO:
{course_data}

BONOS DISPONIBLES:
{bonuses_data}

Responde SOLO con JSON:
{{
    "is_valid": true,
    "confidence": 0.95,
    "issues": [],
    "corrected_response": null,
    "explanation": "Razón de la decisión"
}}
"""

# ============================================================================
# 8. SISTEMA DE DETECCIÓN DE HASHTAGS (DEL LEGACY)
# ============================================================================

# Patrones de detección de hashtags para routing automático.
# Funcionalidad:
# - Mapea hashtags específicos a course_ids
# - Identifica fuentes de campaña
# - Permite routing automático de usuarios

HASHTAG_DETECTION_PATTERNS = {
    # Hashtags de cursos
    '#Experto_IA_GPT_Gemini': {
        'course_id': 'c76bc3dd-502a-4b99-8c6c-3f9fce33a14b',
        'course_name': 'Experto en IA con ChatGPT y Gemini',
        'priority': 'high'
    },
    
    '#CURSO_IA_CHATGPT': {
        'course_id': 'a392bf83-4908-4807-89a9-95d0acc807c9',
        'course_name': 'Curso IA ChatGPT',
        'priority': 'high'
    },
    
    # Hashtags de campaña
    '#ADSIM_01': {
        'campaign_source': 'instagram_story_01',
        'campaign_type': 'paid_social'
    },
    
    '#ADSIM_05': {
        'campaign_source': 'instagram_marketing_05',
        'campaign_type': 'paid_social'
    },
    
    '#ADSFACE_02': {
        'campaign_source': 'facebook_ads_02',
        'campaign_type': 'paid_social'
    },
    
    '#ORGPOST_01': {
        'campaign_source': 'organic_post_01',
        'campaign_type': 'organic'
    }
}

def get_hashtag_analysis_prompt(message: str):
    """
    Genera prompt para análisis de hashtags en mensajes.
    
    Funcionalidad:
    - Detecta hashtags conocidos en mensajes
    - Extrae información de campaña
    - Retorna mapeo estructurado
    
    Retorna: Prompt para analizar hashtags detectados
    """
    return f"""
Analiza el siguiente mensaje para detectar hashtags específicos y extraer información de campaña:

MENSAJE: {message}

HASHTAGS CONOCIDOS:
{HASHTAG_DETECTION_PATTERNS}

Detecta todos los hashtags presentes y mapea la información correspondiente.

Responde SOLO con JSON:
{{
    "hashtags_detected": ["#hashtag1", "#hashtag2"],
    "course_mapping": {{
        "course_id": "id_del_curso_si_aplica",
        "course_name": "nombre_del_curso",
        "priority": "high|medium|low"
    }},
    "campaign_mapping": {{
        "campaign_source": "fuente_de_la_campaña",
        "campaign_type": "paid_social|organic|email"
    }},
    "routing_action": "ads_flow|course_flow|general_flow"
}}
"""

# ============================================================================
# 9. CONSTRUCCIÓN DE CONTEXTO DEL AGENTE (DEL LEGACY)
# ============================================================================

def build_agent_context(user_memory, intent_analysis: dict, course_info: Union[dict, None] = None, automation_info: str = ""):
    """
    Construye el contexto completo para el agente principal.
    
    Funcionalidad:
    - Agrega análisis de intención al contexto
    - Incluye información del usuario acumulada
    - Proporciona datos del curso si están disponibles
    - Añade necesidades de automatización identificadas
    
    Retorna: Contexto completo formateado para el agente
    """
    context = f"""
## Análisis de Intención:
- Categoría: {intent_analysis.get('category', 'GENERAL_QUESTION')}
- Confianza: {intent_analysis.get('confidence', 0.5)}
- Estrategia de ventas: {intent_analysis.get('sales_strategy', 'direct_benefit')}
- Enfoque de respuesta: {intent_analysis.get('response_focus', 'Responder directamente')}
- Debe preguntar más: {intent_analysis.get('should_ask_more', False)}

## Herramientas Recomendadas:
{intent_analysis.get('recommended_tools', {})}

## Información Acumulada del Usuario:
- Profesión: {user_memory.role if user_memory.role else 'No especificada'}
- Intereses: {', '.join(user_memory.interests if user_memory.interests else ['Ninguno registrado'])}
- Puntos de dolor: {', '.join(user_memory.pain_points if user_memory.pain_points else ['Ninguno registrado'])}
- Nivel de interés: {user_memory.interest_level}
- Interacciones: {user_memory.interaction_count}
"""
    
    # Agregar información del curso si está disponible
    if course_info:
        context += f"""
## Información del Curso:
- Nombre: {course_info.get('name', 'No disponible')}
- Precio: ${course_info.get('price_usd', 'No disponible')} USD
- Duración: {course_info.get('total_duration', 'No disponible')}
- Nivel: {course_info.get('level', 'No disponible')}
"""
    
    # Agregar información de automatización si existe
    if automation_info:
        context += f"""
## Necesidades de Automatización Identificadas:
{automation_info}

INSTRUCCIÓN ESPECIAL: El usuario YA expresó necesidades de automatización. NO preguntes más detalles. 
Conecta DIRECTAMENTE con cómo el curso resuelve estos problemas específicos.
"""
    
    return context

# Alias para compatibilidad hacia atrás
WhatsAppMessageTemplates = WhatsAppBusinessTemplates 