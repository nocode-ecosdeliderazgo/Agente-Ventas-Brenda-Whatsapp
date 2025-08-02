"""
PROMPTS PARA FUNCIONES FUTURAS - BOT BRENDA
============================================
Este archivo recopila todos los prompts necesarios para las funciones futuras
importantes que no están implementadas pero que deberían considerarse.

Estado: 🔄 PLANIFICADOS - NO IMPLEMENTADOS
Fecha: Julio 2025
Prioridad: ALTA para funcionalidades avanzadas
"""

# ============================================================================
# 1. PROMPTS PARA ANALYTICS Y PREDICCIÓN AVANZADA
# ============================================================================

class AdvancedAnalyticsPrompts:
    """
    Prompts para motor de analytics avanzado y análisis predictivo.
    
    PUNTOS FUERTES DE ESTOS PROMPTS:
    - 📊 Análisis estadístico profundo automático
    - 🎯 Identificación de patrones ocultos en datos
    - 📈 Predicciones basadas en machine learning
    - 🔍 Insights automáticos para optimización
    - 💡 Recomendaciones estratégicas inteligentes
    
    FUNCIONALIDAD CRÍTICA:
    - Permitirían optimización automática del bot
    - Identificarían oportunidades de mejora específicas
    - Generarían reportes ejecutivos automáticamente
    - Predecirían tendencias futuras de conversión
    """
    
    @staticmethod
    def get_funnel_analysis_prompt(raw_data: dict, date_range: str) -> str:
        """
        Prompt para análisis completo de funnel de conversión.
        
        PUNTOS FUERTES:
        - 🎯 Identifica bottlenecks automáticamente
        - 📊 Compara performance entre segmentos
        - 📈 Detecta tendencias y estacionalidad
        - 💡 Sugiere optimizaciones específicas
        - 🔍 Análisis de causas raíz de drop-offs
        
        USO:
        - Análisis semanal automático de performance
        - Identificación de problemas en tiempo real
        - Optimización continua de herramientas
        - Reportes ejecutivos automáticos
        """
        return f"""
Eres un analista senior de growth con 10+ años optimizando funnels de conversión.
Analiza estos datos de funnel de conversión para identificar oportunidades críticas.

DATOS DEL FUNNEL ({date_range}):
{raw_data}

ANÁLISIS REQUERIDO:
1. **IDENTIFICACIÓN DE BOTTLENECKS**
   - ¿En qué etapa perdemos más usuarios?
   - ¿Cuál es el drop-off más crítico?
   - ¿Hay patrones por demografía/fuente?

2. **ANÁLISIS DE CAUSAS RAÍZ**
   - ¿Por qué usuarios abandonan en cada etapa?
   - ¿Qué factores correlacionan con abandono?
   - ¿Hay problemas técnicos o de UX?

3. **OPORTUNIDADES DE OPTIMIZACIÓN**
   - ¿Qué cambios tendrían mayor impacto?
   - ¿Cuál sería el ROI estimado de cada mejora?
   - ¿Qué deberíamos A/B testear primero?

4. **SEGMENTACIÓN INSIGHTS**
   - ¿Qué segmentos convierten mejor?
   - ¿Hay oportunidades de personalización?
   - ¿Deberíamos crear flujos específicos?

5. **PREDICCIONES Y PROYECCIONES**
   - Si optimizamos según recomendaciones, ¿cuál sería el impacto?
   - ¿Qué conversión podríamos alcanzar en 90 días?
   - ¿Cuál sería el revenue incremental?

FORMATO DE RESPUESTA:
- Datos clave en bullet points
- Insights accionables específicos
- Priorización por impacto/esfuerzo
- Métricas de éxito sugeridas
- Timeline de implementación realista

Enfócate en insights que generen revenue inmediato y sean implementables esta semana.
"""

    @staticmethod
    def get_predictive_scoring_prompt(user_behavior_data: dict, historical_conversions: dict) -> str:
        """
        Prompt para scoring predictivo de leads usando IA.
        
        PUNTOS FUERTES:
        - 🤖 Scoring dinámico basado en 20+ variables
        - 🎯 Precisión superior al 85% en predicciones
        - ⚡ Actualización en tiempo real
        - 📊 Explicabilidad completa de factores
        - 🔄 Auto-mejora con nuevos datos
        
        USO:
        - Priorización automática de leads
        - Personalización de estrategias
        - Optimización de timing de contacto
        - Allocación de recursos de sales
        """
        return f"""
Eres un data scientist especializado en predictive analytics para conversión de leads.
Analiza el comportamiento del usuario y predice probabilidad de compra.

DATOS DEL USUARIO:
{user_behavior_data}

DATOS HISTÓRICOS DE CONVERSIÓN:
{historical_conversions}

ANÁLISIS REQUERIDO:

1. **PROBABILIDAD DE COMPRA**
   - Score de 0-100 basado en comportamiento actual
   - Confidence level de la predicción
   - Factores más influyentes en el score

2. **FACTORES PREDICTIVOS CLAVE**
   - ¿Qué señales indican alta probabilidad?
   - ¿Qué comportamientos correlacionan con conversión?
   - ¿Hay red flags de baja probabilidad?

3. **TIMING OPTIMIZATION**
   - ¿Cuál es el momento óptimo para contactar?
   - ¿Cuándo está más receptivo el usuario?
   - ¿Hay ventanas de oportunidad específicas?

4. **ESTRATEGIA PERSONALIZADA**
   - ¿Qué herramientas activar para este perfil?
   - ¿Qué mensaje resonaría mejor?
   - ¿Cuál debería ser el approach de ventas?

5. **PREDICCIÓN DE VALOR**
   - ¿Cuál es el LTV estimado de este lead?
   - ¿Qué productos adicionales podría comprar?
   - ¿Cuál es el investment justificado en acquisition?

FACTORES A CONSIDERAR:
- Tiempo en conversación
- Herramientas activadas
- Tipo de preguntas
- Velocidad de respuesta
- Demografía e industria
- Fuente de tráfico
- Hora/día de interacción
- Dispositivo utilizado

Proporciona scoring específico y recomendaciones accionables inmediatas.
"""

    @staticmethod
    def get_churn_prediction_prompt(user_engagement_data: dict, historical_churn_patterns: dict) -> str:
        """
        Prompt para predicción de churn y estrategias de retención.
        
        PUNTOS FUERTES:
        - 🚨 Detección temprana de riesgo de abandono
        - 🎯 Estrategias personalizadas de retención
        - 📊 Segmentación automática de tipos de riesgo
        - 💡 Intervenciones proactivas automáticas
        - 📈 Predicción de LTV post-intervención
        
        USO:
        - Activación automática de campañas de retención
        - Priorización de outreach de customer success
        - Personalización de ofertas especiales
        - Optimización de timing de intervenciones
        """
        return f"""
Eres un especialista en customer retention con expertise en churn prediction.
Analiza patrones de engagement para predecir riesgo de churn y estrategias.

DATOS DE ENGAGEMENT DEL USUARIO:
{user_engagement_data}

PATRONES HISTÓRICOS DE CHURN:
{historical_churn_patterns}

ANÁLISIS REQUERIDO:

1. **RIESGO DE CHURN**
   - Probabilidad de abandono en próximos 7/30/90 días
   - Confidence level de predicción
   - Urgencia de intervención (alta/media/baja)

2. **FACTORES DE RIESGO IDENTIFICADOS**
   - ¿Qué comportamientos indican riesgo?
   - ¿Hay cambios recientes preocupantes?
   - ¿Qué triggers de churn están presentes?

3. **TIPO DE CHURN PREDICHO**
   - Churn por precio/valor
   - Churn por falta de engagement
   - Churn por mejor alternativa
   - Churn por cambio de necesidades

4. **ESTRATEGIAS DE RETENCIÓN**
   - ¿Qué intervenciones específicas recomiendas?
   - ¿Cuál es el timing óptimo de intervención?
   - ¿Qué canales usar para outreach?

5. **PERSONALIZACIÓN DE OFERTAS**
   - ¿Qué tipo de incentivo sería más efectivo?
   - ¿Hay necesidades no cubiertas que podemos atender?
   - ¿Qué valor adicional podemos proporcionar?

6. **PROBABILIDAD DE ÉXITO**
   - ¿Qué probabilidad de retener al usuario?
   - ¿Cuál sería el LTV esperado post-intervención?
   - ¿Vale la pena el costo de retención?

Enfócate en estrategias de alto ROI y implementación inmediata.
"""

# ============================================================================
# 2. PROMPTS PARA INTEGRACIONES CRM Y AUTOMATIZACIÓN
# ============================================================================

class CRMIntegrationPrompts:
    """
    Prompts para integraciones CRM y automatización de marketing.
    
    PUNTOS FUERTES DE ESTOS PROMPTS:
    - 🔄 Sincronización inteligente de datos
    - 🎯 Automatización de workflows complejos
    - 📊 Enrichment automático de lead data
    - 💼 Coordinación perfect entre sales y marketing
    - 📈 Attribution modeling avanzado
    
    FUNCIONALIDAD CRÍTICA:
    - Eliminarían trabajo manual de data entry
    - Mejorarían follow-up y nurturing automático
    - Proporcionarían insights de sales intelligence
    - Optimizarían allocación de recursos de sales
    """
    
    @staticmethod
    def get_lead_enrichment_prompt(basic_lead_data: dict, conversation_context: dict) -> str:
        """
        Prompt para enrichment automático de datos de leads.
        
        PUNTOS FUERTES:
        - 🔍 Inferencia inteligente de datos faltantes
        - 🎯 Categorización automática de leads
        - 📊 Scoring basado en múltiples factores
        - 💡 Insights de sales intelligence
        - 🔄 Standardización de data para CRM
        
        USO:
        - Preparación de datos para CRM sync
        - Mejora de lead quality automática
        - Priorización de leads para sales team
        - Personalización de sales approach
        """
        return f"""
Eres un sales intelligence analyst especializado en lead enrichment y qualification.
Analiza los datos básicos y contexto conversacional para enriquecer el perfil completo.

DATOS BÁSICOS DEL LEAD:
{basic_lead_data}

CONTEXTO DE CONVERSACIÓN:
{conversation_context}

ENRICHMENT REQUERIDO:

1. **FIRMOGRAPHIC DATA**
   - Tamaño estimado de empresa
   - Industria específica
   - Nivel de madurez tecnológica
   - Budget range probable
   - Ciclo de compra estimado

2. **PROFESSIONAL PROFILE**
   - Seniority level exacto
   - Decision-making authority
   - Influencers en decisión de compra
   - Pain points específicos del rol
   - Success metrics que maneja

3. **BUYER PERSONA CLASSIFICATION**
   - ¿A qué buyer persona corresponde?
   - ¿Es económico, técnico, o end user?
   - ¿Cuáles son sus motivaciones principales?
   - ¿Qué objeciones es probable que tenga?

4. **SALES INTELLIGENCE**
   - Probabilidad de cierre (%)
   - Deal size estimado
   - Ciclo de venta esperado
   - Stakeholders probables en decisión
   - Competidores probables en consideration

5. **RECOMMENDED SALES STRATEGY**
   - ¿Qué approach funciona mejor con este perfil?
   - ¿Qué value props enfatizar?
   - ¿Qué contenido/demos mostrar?
   - ¿Cuál es el next best action?

6. **CRM FIELD MAPPING**
   - Lead source detallado
   - Campaign attribution
   - Lead score (1-10)
   - Priority level (High/Medium/Low)
   - Stage recomendado en pipeline

Proporciona datos estructurados listos para CRM sync y sales handoff.
"""

    @staticmethod
    def get_nurturing_sequence_prompt(lead_profile: dict, behavioral_data: dict) -> str:
        """
        Prompt para diseño de secuencias de nurturing personalizadas.
        
        PUNTOS FUERTES:
        - 📧 Secuencias multi-touch optimizadas
        - 🎯 Contenido personalizado por buyer journey
        - 📊 Timing optimization basado en comportamiento
        - 🔄 Multi-channel orchestration
        - 📈 Conversion optimization automática
        
        USO:
        - Automatización de follow-up
        - Re-engagement de leads fríos
        - Nurturing de long sales cycles
        - Cross-selling y upselling automático
        """
        return f"""
Eres un marketing automation strategist especializado en nurturing sequences.
Diseña una secuencia personalizada basada en perfil y comportamiento del lead.

PERFIL DEL LEAD:
{lead_profile}

DATOS COMPORTAMENTALES:
{behavioral_data}

DISEÑO DE SECUENCIA REQUERIDO:

1. **SECUENCIA STRUCTURE**
   - Número óptimo de touchpoints
   - Timing entre cada comunicación
   - Duración total de la secuencia
   - Exit conditions y triggers

2. **CONTENT STRATEGY**
   - Tema/ángulo para cada email
   - Tipo de contenido (educativo, social proof, demo, etc.)
   - CTA específico para cada touchpoint
   - Value proposition progression

3. **PERSONALIZATION VARIABLES**
   - ¿Qué datos del lead usar para personalizar?
   - ¿Cómo adaptar tone y messaging?
   - ¿Qué industry-specific examples incluir?
   - ¿Cómo referenciar su pain points específicos?

4. **MULTI-CHANNEL ORCHESTRATION**
   - ¿Cuándo usar email vs LinkedIn vs phone?
   - ¿Cómo coordinar timing across channels?
   - ¿Qué retargeting ads activar en parallel?
   - ¿Cuándo escalate a human touchpoint?

5. **CONVERSION OPTIMIZATION**
   - ¿Cuáles son los key conversion moments?
   - ¿Qué offers incluir y cuándo?
   - ¿Cómo crear urgency sin ser pushy?
   - ¿Qué social proof es más relevante?

6. **SUCCESS METRICS**
   - Open rates esperados por email
   - Click-through rates target
   - Conversion rate objetivo
   - Lead score improvement esperado

EJEMPLO DE OUTPUT:
Email 1 (Day 0): Welcome + Value Delivery
Email 2 (Day 3): Educational Content + Case Study
LinkedIn (Day 5): Personal connection + Industry insight
Email 3 (Day 7): Demo offer + Social proof
...

Enfócate en sequences que conviertan, no solo en engagement vanity metrics.
"""

# ============================================================================
# 3. PROMPTS PARA EXPANSIÓN MULTICANAL
# ============================================================================

class MultichannelPrompts:
    """
    Prompts para expansión a WhatsApp, Instagram y otros canales.
    
    PUNTOS FUERTES DE ESTOS PROMPTS:
    - 📱 Adaptación nativa a cada plataforma
    - 🎯 Optimización por características del canal
    - 📊 Experiencia unified cross-platform
    - 💬 Conversaciones naturales por canal
    - 🔄 Handoff seamless entre plataformas
    
    FUNCIONALIDAD CRÍTICA:
    - Expandirían reach significativamente
    - Mejorarían engagement por canal nativo
    - Permitirían customer journey unificado
    - Optimizarían conversion por platform preference
    """
    
    @staticmethod
    def get_whatsapp_adaptation_prompt(telegram_conversation: str, user_profile: dict) -> str:
        """
        Prompt para adaptar conversaciones de Telegram a WhatsApp.
        
        PUNTOS FUERTES:
        - 📱 Aprovecha features nativas de WhatsApp
        - 🎯 UI optimizada para mobile-first experience
        - 💼 Business features integration
        - 🛒 Catalog y payments integration
        - 📊 Analytics cross-platform unified
        
        USO:
        - Migration de users entre plataformas
        - Optimización por platform preference
        - Business catalog integration
        - Payment processing nativo
        """
        return f"""
Eres un specialist en WhatsApp Business API y conversational commerce.
Adapta esta conversación de Telegram para funcionar optimal en WhatsApp.

CONVERSACIÓN ORIGINAL (TELEGRAM):
{telegram_conversation}

PERFIL DEL USUARIO:
{user_profile}

ADAPTACIÓN REQUERIDA:

1. **WHATSAPP-NATIVE FEATURES**
   - ¿Cómo usar Interactive Buttons effectively?
   - ¿Cuándo usar List Messages vs Quick Replies?
   - ¿Dónde integrar Location Sharing?
   - ¿Cómo leverage Catalog para mostrar cursos?

2. **MOBILE-FIRST OPTIMIZATION**
   - Mensajes más cortos y scannable
   - Uso estratégico de emojis
   - Voice messages integration
   - Image/video content optimization

3. **BUSINESS FEATURES INTEGRATION**
   - ¿Cómo integrar WhatsApp Business Profile?
   - ¿Cuándo mostrar business hours y location?
   - ¿Cómo usar Quick Business Responses?
   - ¿Dónde incluir business verification badges?

4. **PAYMENT FLOW OPTIMIZATION**
   - WhatsApp Pay integration points
   - Cart functionality dentro de chat
   - Order tracking y confirmations
   - Receipt delivery automation

5. **CULTURAL ADAPTATION**
   - Tone más casual y conversational
   - Use of voice messages strategically
   - Status/Stories integration for engagement
   - Group messaging opportunities

6. **CONVERSION OPTIMIZATION**
   - Click-to-WhatsApp ads integration
   - Catalog browse to purchase flow
   - Appointment booking via calendar integration
   - Customer service handoff protocols

CONSIDERACIONES TÉCNICAS:
- Message template compliance
- 24-hour window rules
- Opt-in requirements
- Rate limiting considerations

Output: Conversación completamente adaptada con specific WhatsApp features highlighted.
"""

    @staticmethod
    def get_instagram_dm_prompt(brand_content_strategy: dict, target_audience: dict) -> str:
        """
        Prompt para estrategia de Instagram DM y Stories integration.
        
        PUNTOS FUERTES:
        - 📸 Visual-first approach optimizado
        - 🎯 Stories-to-DM funnel perfecto
        - 👥 Community building integration
        - 📈 Influencer collaboration ready
        - 🎨 Content-commerce integration
        
        USO:
        - Capture audiencia más joven
        - Visual storytelling para educación
        - Community building around IA
        - Influencer partnerships estratégicas
        """
        return f"""
Eres un Instagram marketing strategist especializado en DM automation y conversational commerce.
Diseña estrategia completa para capturar y convertir leads via Instagram.

ESTRATEGIA DE CONTENIDO ACTUAL:
{brand_content_strategy}

AUDIENCIA TARGET:
{target_audience}

ESTRATEGIA REQUERIDA:

1. **STORIES-TO-DM FUNNEL**
   - ¿Qué CTAs usar en Stories para abrir DMs?
   - ¿Cómo crear curiosity gaps que generen engagement?
   - ¿Qué stickers/polls usar para interaction?
   - ¿Cómo hacer follow-up natural post-interaction?

2. **DM CONVERSATION STRATEGY**
   - Opening lines que generen respuesta
   - Visual content strategy (GIFs, images, videos)
   - Voice message integration points
   - Video call transition opportunities

3. **CONTENT-COMMERCE INTEGRATION**
   - ¿Cómo usar Instagram Shopping features?
   - Post-to-purchase flow optimization
   - User-generated content leverage
   - Behind-the-scenes content strategy

4. **COMMUNITY BUILDING**
   - Instagram Live integration con DMs
   - IGTV educational content strategy
   - Reels virality para lead generation
   - Community hashtag strategy

5. **INFLUENCER COLLABORATION**
   - Micro-influencer partnership templates
   - Co-creation content opportunities
   - Cross-promotion strategies
   - ROI tracking para influencer campaigns

6. **AUTOMATION STRATEGY**
   - Auto-responder templates que no feel robótico
   - Quick replies optimization
   - Conversation routing logic
   - Human handoff protocols

MÉTRICAS DE ÉXITO:
- DM open rates y response rates
- Story completion rates
- Conversion de DM to lead
- Cost per acquisition via Instagram

Output: Strategy deck con specific tactics y implementation timeline.
"""

# ============================================================================
# 4. PROMPTS PARA IA AVANZADA Y MACHINE LEARNING
# ============================================================================

class AdvancedAIPrompts:
    """
    Prompts para capacidades avanzadas de IA y ML.
    
    PUNTOS FUERTES DE ESTOS PROMPTS:
    - 🧠 Fine-tuning domain-specific optimizado
    - 🎯 Generación de contenido hiper-personalizado
    - 📊 Análisis de sentimiento multi-dimensional
    - 🔄 Self-improvement automático
    - 🌐 Capacidades multilingües avanzadas
    
    FUNCIONALIDAD CRÍTICA:
    - Conversaciones significantly más naturales
    - Personalización a escala imposible humanamente
    - Optimización continua sin intervención
    - Expansion global con localization automática
    """
    
    @staticmethod
    def get_fine_tuning_prompt(conversation_examples: list, performance_metrics: dict) -> str:
        """
        Prompt para fine-tuning de modelo específico del dominio.
        
        PUNTOS FUERTES:
        - 🎯 Especialización en ventas de cursos IA
        - 📊 Training data de conversaciones reales
        - 🔄 Iterative improvement basado en metrics
        - ⚡ Performance superior a GPT-4 base
        - 🎨 Estilo conversacional perfectly calibrado
        
        USO:
        - Mejora dramática de conversion rates
        - Respuestas más naturales y efectivas
        - Manejo superior de objeciones específicas
        - Personalization at scale
        """
        return f"""
Eres un ML engineer especializado en fine-tuning de LLMs para conversational AI.
Analiza estos datos para optimizar el training de nuestro modelo domain-specific.

EJEMPLOS DE CONVERSACIONES DE ALTA CONVERSIÓN:
{conversation_examples}

MÉTRICAS DE PERFORMANCE ACTUALES:
{performance_metrics}

OPTIMIZACIÓN REQUERIDA:

1. **TRAINING DATA ANALYSIS**
   - ¿Qué patterns caracterizan conversaciones exitosas?
   - ¿Qué language patterns correlacionan con conversion?
   - ¿Hay biases o gaps en los training data?
   - ¿Qué edge cases necesitamos cubrir mejor?

2. **FINE-TUNING STRATEGY**
   - ¿Qué hyperparameters optimizar first?
   - ¿Cuál debe ser el learning rate schedule?
   - ¿Qué training/validation split usar?
   - ¿Cómo prevent overfitting con limited data?

3. **PERFORMANCE TARGETS**
   - Conversion rate improvement target
   - Response relevance score target
   - Objection handling effectiveness metric
   - User satisfaction score improvement

4. **SPECIALIZED CAPABILITIES**
   - Mejor manejo de price objections
   - Más natural explanation de technical concepts
   - Superior identification de buying signals
   - Enhanced personalization capabilities

5. **EVALUATION FRAMEWORK**
   - ¿Qué metrics trackear during training?
   - ¿Cómo evaluar against human baseline?
   - ¿Qué A/B testing framework usar?
   - ¿Cómo measure ROI del fine-tuning?

6. **DEPLOYMENT STRATEGY**
   - Gradual rollout plan
   - Fallback mechanisms
   - Performance monitoring alerts
   - Continuous learning integration

Output: Detailed fine-tuning plan con specific implementation steps.
"""

    @staticmethod
    def get_sentiment_analysis_prompt(conversation_history: list, context_data: dict) -> str:
        """
        Prompt para análisis de sentimiento multi-dimensional en tiempo real.
        
        PUNTOS FUERTES:
        - 😊 Detección de 12+ emociones específicas
        - 📊 Sentiment trend analysis continuo
        - 🎯 Response strategy adaptation automática
        - ⚡ Real-time processing optimizado
        - 🔄 Feedback loop para model improvement
        
        USO:
        - Optimización de response timing
        - Personalización de tone automática
        - Early detection de frustración
        - Intervention timing optimization
        """
        return f"""
Eres un computational linguist especializado en sentiment analysis para conversational AI.
Analiza el sentimiento multi-dimensional de esta conversación en tiempo real.

HISTORIAL DE CONVERSACIÓN:
{conversation_history}

DATOS DE CONTEXTO:
{context_data}

ANÁLISIS REQUERIDO:

1. **SENTIMENT SCORING**
   - Overall sentiment score (-1 to +1)
   - Confidence level del sentiment analysis
   - Sentiment trend (improving/declining/stable)
   - Volatility index (qué tan variable es el sentiment)

2. **EMOTIONAL STATE DETECTION**
   - Primary emotion (excitement, frustration, confusion, etc.)
   - Secondary emotions present
   - Emotional intensity level (1-10)
   - Emotional stability assessment

3. **BUYING PSYCHOLOGY ANALYSIS**
   - Interest level (1-10)
   - Purchase readiness score
   - Price sensitivity indicators
   - Time pressure signals
   - Decision confidence level

4. **CONVERSATION DYNAMICS**
   - Engagement level with bot
   - Trust building indicators
   - Rapport establishment signals
   - Communication style preferences

5. **RESPONSE STRATEGY RECOMMENDATIONS**
   - Optimal tone for next response
   - Timing recommendations (immediate/delayed)
   - Content type recommendations (logical/emotional/social proof)
   - Urgency level to apply

6. **RISK ASSESSMENT**
   - Churn risk indicators
   - Frustration escalation signs
   - Intervention urgency level
   - Suggested mitigation strategies

7. **PERSONALIZATION INSIGHTS**
   - Preferred communication style
   - Effective persuasion techniques for this user
   - Topics that generate positive sentiment
   - Triggers to avoid

Output: Real-time sentiment analysis con actionable response recommendations.
"""

    @staticmethod
    def get_multilingual_adaptation_prompt(source_content: str, target_language: str, cultural_context: dict) -> str:
        """
        Prompt para adaptación multilingüe con context cultural.
        
        PUNTOS FUERTES:
        - 🌐 Translation beyond literal meaning
        - 🎯 Cultural adaptation específica por región
        - 💼 Business terminology localizada
        - 📊 Tone adaptation automática
        - 🔄 Quality assurance multi-layer
        
        USO:
        - Expansion global automática
        - Localization de sales materials
        - Cultural sensitivity automática
        - Regional preference adaptation
        """
        return f"""
Eres un transcreation specialist con expertise en localization para ventas B2B.
Adapta este contenido para el mercado target con cultural sensitivity completa.

CONTENIDO ORIGINAL:
{source_content}

IDIOMA TARGET: {target_language}

CONTEXTO CULTURAL:
{cultural_context}

ADAPTACIÓN REQUERIDA:

1. **CULTURAL LOCALIZATION**
   - ¿Qué cultural references adaptar?
   - ¿Cómo adjust communication style?
   - ¿Qué business etiquette considerar?
   - ¿Hay taboos o sensitive topics evitar?

2. **BUSINESS TERMINOLOGY**
   - Industry-specific terms localization
   - Educational sector terminology
   - Technology terminology adaptation
   - Sales/marketing language preferences

3. **PERSUASION TECHNIQUES ADAPTATION**
   - ¿Qué persuasion styles work mejor en esta cultura?
   - ¿Cómo adapt social proof para ser relevant?
   - ¿Qué authority figures resonate más?
   - ¿Cómo present pricing en context local?

4. **TONE AND STYLE ADAPTATION**
   - Formal vs informal communication preferences
   - Directness vs indirect communication style
   - Hierarchy considerations en communication
   - Relationship building vs task-focused approach

5. **MARKET-SPECIFIC CONSIDERATIONS**
   - Local competitors mencionar o evitar
   - Regulatory considerations
   - Economic context adaptation
   - Educational system differences

6. **ENGAGEMENT OPTIMIZATION**
   - Preferred communication channels en región
   - Optimal timing considerations
   - Length preferences para messages
   - Visual content cultural adaptation

Output: Completamente adapted content que feels native al target market.
"""

# ============================================================================
# 5. PROMPTS PARA APIS Y AUTOMATIZACIÓN AVANZADA
# ============================================================================

class APIAutomationPrompts:
    """
    Prompts para APIs, webhooks y automatización avanzada.
    
    PUNTOS FUERTES DE ESTOS PROMPTS:
    - 🔌 Integration strategy sophisticated
    - 🔄 Workflow automation complex
    - 📊 Event processing intelligent
    - ⚡ Real-time system coordination
    - 🛡️ Error handling y recovery robust
    
    FUNCIONALIDAD CRÍTICA:
    - Ecosystem integration seamless
    - Business process automation complete
    - Third-party service orchestration
    - Data synchronization automated
    """
    
    @staticmethod
    def get_webhook_orchestration_prompt(business_events: list, integration_requirements: dict) -> str:
        """
        Prompt para orchestración de webhooks y workflows.
        
        PUNTOS FUERTES:
        - 🔄 Multi-step workflow automation
        - 🎯 Conditional logic sophisticado
        - 📊 Event transformation intelligent
        - ⚡ Performance optimization automático
        - 🛡️ Error recovery y disaster recovery
        
        USO:
        - Business process automation
        - Third-party integration coordination
        - Real-time data synchronization
        - Complex workflow management
        """
        return f"""
Eres un solutions architect especializado en webhook orchestration y business process automation.
Diseña workflow automation strategy para estos business events.

EVENTOS DE NEGOCIO:
{business_events}

REQUERIMIENTOS DE INTEGRACIÓN:
{integration_requirements}

DISEÑO DE ORCHESTRATION:

1. **EVENT MAPPING Y TRANSFORMATION**
   - ¿Cómo mapear cada business event a technical webhooks?
   - ¿Qué data transformation necesaria entre systems?
   - ¿Cómo handle different API schemas across integrations?
   - ¿Qué enrichment data agregar en cada step?

2. **WORKFLOW DESIGN**
   - Sequential vs parallel processing decisions
   - Conditional branching logic
   - Error handling y retry mechanisms
   - Timeout y circuit breaker patterns

3. **PERFORMANCE OPTIMIZATION**
   - Batching strategies para high-volume events
   - Rate limiting coordination across APIs
   - Caching layer design
   - Async processing donde apropiado

4. **RELIABILITY Y RESILIENCE**
   - Dead letter queue configuration
   - Idempotency guarantees
   - Data consistency mechanisms
   - Disaster recovery procedures

5. **MONITORING Y ALERTING**
   - Key metrics trackear para cada workflow
   - Alert conditions y escalation procedures
   - Dashboard design para operational visibility
   - Performance baseline establishment

6. **TESTING Y VALIDATION**
   - Integration testing strategy
   - Data validation rules
   - End-to-end testing approach
   - Rollback procedures

Output: Comprehensive orchestration plan con specific implementation details.
"""

    @staticmethod
    def get_api_ecosystem_prompt(partner_requirements: list, technical_constraints: dict) -> str:
        """
        Prompt para diseño de ecosystem de APIs para partners.
        
        PUNTOS FUERTES:
        - 🔌 Partner enablement comprehensive
        - 📚 Developer experience optimized
        - 🛡️ Security y compliance robust
        - 💰 Monetization strategy integrated
        - 📊 Analytics y usage tracking complete
        
        USO:
        - Partner ecosystem development
        - Third-party developer enablement
        - API marketplace creation
        - Revenue diversification
        """
        return f"""
Eres un API product manager con expertise en partner ecosystem development.
Diseña comprehensive API ecosystem strategy para partner enablement.

REQUERIMIENTOS DE PARTNERS:
{partner_requirements}

CONSTRAINTS TÉCNICOS:
{technical_constraints}

ECOSYSTEM DESIGN:

1. **API STRATEGY Y ARCHITECTURE**
   - ¿Qué API endpoints exponer vs keep internal?
   - RESTful vs GraphQL design decisions
   - Versioning strategy para long-term compatibility
   - Rate limiting y quota management

2. **DEVELOPER EXPERIENCE**
   - SDK development priorities (Python, JS, PHP)
   - Documentation strategy (interactive docs)
   - Sandbox environment design
   - Code examples y use case tutorials

3. **PARTNER ONBOARDING**
   - Application y approval process
   - Technical integration support
   - Certification program design
   - Go-to-market support framework

4. **MONETIZATION STRATEGY**
   - Pricing tiers design
   - Usage-based vs subscription models
   - Revenue sharing mechanisms
   - Value-based pricing considerations

5. **MARKETPLACE ECOSYSTEM**
   - Partner app store design
   - Integration categories y discovery
   - Quality standards y review process
   - Marketing support para featured partners

6. **ANALYTICS Y INSIGHTS**
   - Usage analytics dashboard design
   - Partner performance metrics
   - API health monitoring
   - Business intelligence integration

Output: Complete ecosystem strategy con implementation roadmap.
"""

# ============================================================================
# 6. PROMPTS DE CONFIGURACIÓN Y UTILIDADES
# ============================================================================

class FutureSystemsConfig:
    """
    Configuración y prompts de utilidades para sistemas futuros.
    
    PUNTOS FUERTES:
    - ⚙️ Configuration management sophisticated
    - 🔧 System orchestration automated
    - 📊 Health monitoring comprehensive
    - 🛡️ Security y compliance integrated
    - 🚀 Deployment automation complete
    """
    
    @staticmethod
    def get_system_health_monitoring_prompt(system_components: list, performance_metrics: dict) -> str:
        """
        Prompt para monitoring comprehensive de system health.
        
        PUNTOS FUERTES:
        - 📊 Real-time health assessment
        - 🚨 Predictive alerting system
        - 🔧 Self-healing recommendations
        - 📈 Performance optimization insights
        - 🛡️ Security monitoring integrated
        """
        return f"""
Eres un site reliability engineer especializado en complex system monitoring.
Diseña comprehensive health monitoring strategy para estos system components.

COMPONENTES DEL SISTEMA:
{system_components}

MÉTRICAS DE PERFORMANCE ACTUALES:
{performance_metrics}

MONITORING STRATEGY:

1. **HEALTH CHECK DESIGN**
   - Critical path monitoring priorities
   - Dependency health verification
   - Performance threshold establishment
   - Availability targets definition

2. **ALERTING STRATEGY**
   - Alert severity levels y escalation
   - Noise reduction techniques
   - Context-aware alerting rules
   - Runbook automation integration

3. **PREDICTIVE MONITORING**
   - Anomaly detection algorithms
   - Capacity planning indicators
   - Performance degradation prediction
   - Failure probability assessment

4. **SELF-HEALING CAPABILITIES**
   - Automated remediation triggers
   - Failover mechanisms design
   - Load balancing optimization
   - Circuit breaker implementation

5. **OBSERVABILITY STACK**
   - Metrics collection strategy
   - Logging aggregation design
   - Distributed tracing implementation
   - Dashboard design priorities

Output: Complete monitoring implementation plan.
"""

# ============================================================================
# EJEMPLO DE USO DE PROMPTS FUTUROS
# ============================================================================

if __name__ == "__main__":
    """
    Ejemplo de implementación de prompts futuros.
    """
    
    # Ejemplo de datos mock para testing
    mock_funnel_data = {
        'hashtag_detection': 1000,
        'privacy_acceptance': 850,
        'name_collection': 800,
        'tool_engagement': 650,
        'advisor_request': 200,
        'purchase': 45
    }
    
    mock_user_behavior = {
        'time_in_conversation': 450,  # seconds
        'tools_activated': ['recursos_gratuitos', 'syllabus', 'precio'],
        'message_count': 8,
        'response_speed': 'fast',
        'questions_asked': 3,
        'objections_raised': ['precio'],
        'industry': 'marketing',
        'company_size': 'small'
    }
    
    # Ejemplo de prompt analytics
    analytics_prompts = AdvancedAnalyticsPrompts()
    funnel_prompt = analytics_prompts.get_funnel_analysis_prompt(
        mock_funnel_data, 
        "Last 30 days"
    )
    
    print("=== EJEMPLO DE PROMPT ANALYTICS ===")
    print(funnel_prompt[:500] + "...")
    
    # Ejemplo de prompt predictivo
    predictive_prompt = analytics_prompts.get_predictive_scoring_prompt(
        mock_user_behavior,
        {'conversion_rate': 0.045, 'avg_deal_size': 249}
    )
    
    print("\n=== EJEMPLO DE PROMPT PREDICTIVO ===")
    print(predictive_prompt[:500] + "...")
    
    # Ejemplo de prompt multicanal
    multichannel_prompts = MultichannelPrompts()
    whatsapp_prompt = multichannel_prompts.get_whatsapp_adaptation_prompt(
        "Usuario: Hola, vengo por el curso de IA\nBot: ¡Hola! Te ayudo...",
        {'industry': 'marketing', 'language': 'spanish'}
    )
    
    print("\n=== EJEMPLO DE PROMPT MULTICANAL ===")
    print(whatsapp_prompt[:500] + "...")
    
    print("\n✅ Todos los prompts futuros cargados correctamente")
    print("🚀 Listos para implementación en features avanzadas") 