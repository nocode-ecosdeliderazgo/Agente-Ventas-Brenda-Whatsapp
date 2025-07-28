# GUÍA DEL SISTEMA DE PROMPTS EMPRESARIALES - BOT BRENDA

**Versión:** 2.0 - PyME Optimized  
**Fecha:** Julio 2025  
**Archivo:** `prompts/agent_prompts.py`

---

## 🎯 OVERVIEW DEL SISTEMA

El sistema de prompts ha sido completamente rediseñado para optimizar conversaciones con **líderes de PyMEs** (empresas de 20-200 empleados). Incluye detección automática de buyer personas, ejemplos ROI cuantificados, y mensajes ejecutivos especializados.

### Características Principales:
- **17 categorías de intención** específicas para PyMEs
- **5 buyer personas** priorizados con ejemplos ROI
- **Templates ejecutivos** con beneficios cuantificados
- **Extracción de contexto empresarial** automática
- **Compatibilidad completa** con sistema existente

---

## 📚 COMPONENTES PRINCIPALES

### 1. SYSTEM_PROMPT Ejecutivo

**Ubicación:** `prompts/agent_prompts.py:18-110`

**Características:**
- **Personalidad:** Consultora especializada en IA para PyMEs
- **Tono:** Práctica, directa, enfocada en ROI
- **Audiencia:** Líderes 30-45 años, empresas 20-200 empleados
- **Sectores:** Agencias, consultoría, manufactura, salud, educación

**Uso:**
```python
from prompts.agent_prompts import SYSTEM_PROMPT

# El SYSTEM_PROMPT se usa automáticamente en todas las respuestas
# Está optimizado para líderes PyME con enfoque consultivo
```

**Contexto Incluido:**
```python
CONTEXTO DEL BUYER PERSONA - LÍDER DE INNOVACIÓN PYME:
- Cargo: Gerente/Director de Operaciones, Marketing o Transformación Digital
- Empresa: PyME servicios 20-200 empleados
- Presiones: Aumentar productividad sin crecer plantilla, generar contenido más rápido
```

### 2. Análisis de Intención PyME (17 Categorías)

**Función:** `get_intent_analysis_prompt(user_message, user_memory, recent_messages)`  
**Ubicación:** `prompts/agent_prompts.py:116-202`

#### Categorías Empresariales:

**🏢 EXPLORACIÓN EMPRESARIAL:**
- `EXPLORATION_SECTOR` - Aplicaciones para sector específico
- `EXPLORATION_ROI` - Retorno de inversión y casos de éxito  
- `EXPLORATION_COMPETITORS` - Ventaja competitiva vs competencia

**💰 OBJECIONES EMPRESARIALES:**
- `OBJECTION_BUDGET_PYME` - Presupuesto limitado PyME
- `OBJECTION_TIME_EXECUTIVES` - Falta tiempo líderes/directivos
- `OBJECTION_TECHNICAL_TEAM` - Sin equipo técnico, temen complejidad
- `OBJECTION_IMPLEMENTATION` - Dudas implementación operaciones

**⚙️ NECESIDADES OPERATIVAS:**
- `AUTOMATION_REPORTS` - Automatizar reportes y dashboards
- `AUTOMATION_CONTENT` - Acelerar creación contenido/marketing
- `AUTOMATION_PROCESSES` - Sistematizar procesos operativos
- `AUTOMATION_ANALYSIS` - Análisis de datos más rápido

**🎯 DECISIÓN EMPRESARIAL:**
- `BUYING_SIGNALS_EXECUTIVE` - Señales decisión corporativa
- `PILOT_REQUEST` - Solicita proyecto piloto
- `TEAM_TRAINING` - Capacitación para equipo
- `STRATEGIC_CONSULTATION` - Asesoría estratégica IA

**📞 SOPORTE:**
- `FREE_RESOURCES_BUSINESS` - Recursos específicos PyMEs
- `CONTACT_ADVISOR_EXECUTIVE` - Contacto asesor empresarial

**Respuesta JSON:**
```json
{
    "category": "AUTOMATION_REPORTS",
    "buyer_persona_match": "marcos_multitask",
    "business_pain_detected": "operational_reports",
    "roi_opportunity": "high",
    "implementation_timeline": "30_days",
    "recommended_action": "provide_roi_info"
}
```

### 3. Extracción de Información Empresarial

**Función:** `get_information_extraction_prompt(user_message, user_memory)`  
**Ubicación:** `prompts/agent_prompts.py:208-278`

**Información Extraída:**
```json
{
    "name": "nombre del líder si se menciona",
    "role": "cargo exacto (ej: Director de Marketing, CEO)",
    "company_info": {
        "sector": "agencia|consultoría|manufactura|salud|educación",
        "size": "tamaño empresa si se menciona",
        "area_responsibility": "área de responsabilidad del líder"
    },
    "automation_needs": {
        "report_types": ["reportes que crea manualmente"],
        "content_creation": ["tipos de contenido que necesita"],
        "process_optimization": ["procesos que quiere mejorar"],
        "time_investment": "horas semanales en tareas repetitivas",
        "strategic_goals": ["objetivos empresariales mencionados"]
    },
    "buyer_persona_match": "lucia_copypro|marcos_multitask|sofia_visionaria",
    "business_urgency": "low|medium|high",
    "decision_making_power": "individual|team|executive"
}
```

### 4. Templates Empresariales (WhatsAppBusinessTemplates)

**Clase:** `WhatsAppBusinessTemplates`  
**Ubicación:** `prompts/agent_prompts.py:287-427`

#### **Mensajes de Bienvenida:**

```python
# Bienvenida ejecutiva con beneficios cuantificados
WhatsAppBusinessTemplates.welcome_new_business_user()
# Retorna mensaje con: automatizar procesos, reducir 10+ horas, ventaja en 30 días

# Bienvenida para ejecutivos que regresan
WhatsAppBusinessTemplates.welcome_returning_executive(name, role)
# Mensaje personalizado con seguimiento de implementación
```

#### **Recursos Empresariales:**

```python
# Recursos específicos para PyMEs
WhatsAppBusinessTemplates.business_resources_offer(name, role, sector)
# Incluye: calculadora ROI, kit automatización, casos sector, guía 30 días
```

#### **Manejo de Objeciones con ROI:**

```python
# Respuesta a objeciones de precio con ejemplos ROI específicos
WhatsAppBusinessTemplates.business_price_objection_response(
    course_price=497, 
    role="Director de Marketing", 
    sector="agencia"
)
```

**Ejemplos ROI por Buyer Persona:**
- **Lucía CopyPro (Marketing):** $300 ahorro por campaña → 2 campañas recupera inversión
- **Marcos Multitask (Operaciones):** $2,000 ahorro mensual → ROI 400% primer mes
- **Sofía Visionaria (CEO):** $27,600 ahorro anual → ROI 1,380% anual

#### **Contacto Asesor Ejecutivo:**

```python
# Transición a asesor especializado en PyMEs
WhatsAppBusinessTemplates.executive_advisor_transition(name, role)
# Ofrece: análisis procesos, plan implementación, casos éxito similares
```

### 5. Generación de Respuestas Ejecutivas

**Función:** `get_response_generation_prompt(user_message, user_memory, intent_analysis, context_info)`  
**Ubicación:** `prompts/agent_prompts.py:479-547`

**Características:**
- **Enfoque consultivo empresarial** especializado en PyMEs
- **Lenguaje ejecutivo** - ROI, eficiencia, competitividad
- **Beneficios cuantificados** - horas ahorradas, % mejoras
- **Ejemplos sector-específicos** - casos éxito similares
- **Mensajes 150-250 palabras** - ejecutivos necesitan más contexto
- **Call-to-action empresarial** - demo, auditoría, consulta

**Instrucciones Específicas:**
```python
INSTRUCCIONES ESPECÍFICAS PARA LÍDERES PYME:
1. Responde como consultora empresarial especializada en IA para PyMEs
2. Usa lenguaje ejecutivo: enfócate en ROI, eficiencia, competitividad
3. Personaliza basándote en el cargo y sector del líder
4. Cuantifica beneficios siempre que sea posible (horas ahorradas, % mejoras)
5. Incluye ejemplos de casos de éxito similares a su situación
6. Mantén el mensaje entre 150-250 palabras (ejecutivos necesitan más contexto)
7. Incluye call-to-action empresarial claro (demo, auditoría, consulta)
8. NO inventes datos técnicos - usa solo información confirmada de BD
```

---

## 🚀 GUÍA DE USO PRÁCTICA

### Inicialización Básica

```python
from prompts.agent_prompts import (
    SYSTEM_PROMPT,
    get_intent_analysis_prompt,
    get_information_extraction_prompt,
    WhatsAppBusinessTemplates,
    get_response_generation_prompt
)

# Compatibilidad hacia atrás mantenida
from prompts.agent_prompts import WhatsAppMessageTemplates  # Alias automático
```

### Flujo Típico de Conversación PyME

#### 1. **Análisis de Intención Empresarial**

```python
# Analizar mensaje de líder PyME
intent_prompt = get_intent_analysis_prompt(
    user_message="Necesito automatizar los reportes semanales de mi agencia",
    user_memory=user_memory,
    recent_messages=[]
)

# OpenAI retornará:
{
    "category": "AUTOMATION_REPORTS",
    "buyer_persona_match": "lucia_copypro",
    "business_pain_detected": "operational_reports", 
    "roi_opportunity": "high",
    "implementation_timeline": "30_days"
}
```

#### 2. **Extracción de Contexto Empresarial**

```python
# Extraer información empresarial específica
extraction_prompt = get_information_extraction_prompt(
    user_message="Soy María, Directora de Marketing de una agencia digital de 45 empleados",
    user_memory=user_memory
)

# OpenAI retornará:
{
    "name": "María",
    "role": "Directora de Marketing",
    "company_info": {
        "sector": "agencia digital",
        "size": "45 empleados",
        "area_responsibility": "Marketing"
    },
    "buyer_persona_match": "lucia_copypro"
}
```

#### 3. **Generación de Respuesta Ejecutiva**

```python
# Generar respuesta especializada para PyME  
response_prompt = get_response_generation_prompt(
    user_message="¿Cuánto cuesta el curso?",
    user_memory=user_memory,
    intent_analysis=intent_analysis,
    context_info="Course price: $497 USD"
)

# Respuesta incluirá ROI específico para su buyer persona
```

#### 4. **Templates Específicos por Situación**

```python
# Bienvenida ejecutiva
welcome = WhatsAppBusinessTemplates.welcome_new_business_user()

# Recursos empresariales específicos  
resources = WhatsAppBusinessTemplates.business_resources_offer(
    name="María",
    role="Directora de Marketing", 
    sector="agencia digital"
)

# Manejo objeción precio con ROI
price_response = WhatsAppBusinessTemplates.business_price_objection_response(
    course_price=497,
    role="Directora de Marketing",
    sector="agencia"
)
# Incluirá ejemplo Lucía CopyPro: $300 ahorro por campaña

# Contacto asesor ejecutivo
advisor = WhatsAppBusinessTemplates.executive_advisor_transition(
    name="María",
    role="Directora de Marketing"
)
```

---

## 🎯 BUYER PERSONAS Y ADAPTACIÓN

### Detección Automática de Buyer Persona

El sistema detecta automáticamente el buyer persona basado en:
- **Cargo mencionado** (Director, Gerente, CEO, etc.)
- **Sector/industria** (agencia, manufactura, consultoría, etc.)
- **Dolores expresados** (reportes manuales, contenido lento, etc.)
- **Tamaño empresa** (empleados mencionados)

### Adaptación Automática de Mensajes

```python
# El sistema adapta automáticamente los mensajes ROI:

if buyer_persona == "lucia_copypro":
    roi_example = "$300 ahorro por campaña → 2 campañas recupera inversión"
elif buyer_persona == "marcos_multitask": 
    roi_example = "$2,000 ahorro mensual → ROI 400% primer mes"
elif buyer_persona == "sofia_visionaria":
    roi_example = "$27,600 ahorro anual → ROI 1,380% anual"
```

### Mensajes Sector-Específicos

- **Agencias:** Enfoque en automatización de contenido y campañas
- **Manufactura:** Optimización de reportes operativos y dashboards
- **Consultoría:** Diferenciación competitiva y eficiencia de procesos
- **Scale-ups Tech:** Automatización de reclutamiento y capacitación
- **Corporativos:** Prototipado rápido y demostración de valor

---

## 🔧 CONFIGURACIÓN Y PERSONALIZACIÓN

### Configuración OpenAI Optimizada

```python
class PromptConfig:
    MODELS = {
        'main_agent': 'gpt-4o-mini',           # Respuestas ejecutivas
        'intent_analysis': 'gpt-4o-mini',     # Clasificación PyME
        'information_extraction': 'gpt-4o-mini' # Extracción empresarial
    }
    
    TEMPERATURES = {
        'main_agent': 0.7,        # Creatividad para ejecutivos
        'intent_analysis': 0.3,   # Precisión clasificación
        'information_extraction': 0.2  # Precisión extracción
    }
    
    MAX_TOKENS = {
        'main_agent': 800,        # Respuestas ejecutivas más largas
        'intent_analysis': 300,   # JSON estructurado
        'information_extraction': 400  # Datos empresariales
    }
```

### Personalización por Sector

Para personalizar respuestas por sector específico:

1. **Agregar nuevos sectores** en la extracción de información
2. **Crear ejemplos ROI** específicos para el sector
3. **Adaptar lenguaje** a la terminología del sector
4. **Incluir casos de éxito** reales del sector

---

## ✅ VALIDACIÓN Y TESTING

### Testing del Sistema

```bash
# Test completo del sistema de prompts
python prompts/agent_prompts.py

# Salida esperada:
# ✅ Configuración del agente empresarial cargada
# ✅ Template de bienvenida empresarial funcionando
# ✅ Ejemplo respuesta ROI generado correctamente
# ✅ Prompts para líderes PyME cargados correctamente
```

### Validación de Componentes

```python
# Verificar imports
from prompts.agent_prompts import (
    SYSTEM_PROMPT,
    get_intent_analysis_prompt, 
    WhatsAppBusinessTemplates,
    WhatsAppMessageTemplates  # Alias funcionando
)

# Verificar configuración
config = PromptConfig.get_config('main_agent')
print(f"Modelo: {config['model']}, Temp: {config['temperature']}")

# Verificar templates
welcome = WhatsAppBusinessTemplates.welcome_new_business_user()
assert "PyMEs" in welcome
assert "consultora especializada" in welcome
```

---

## 🎊 RESULTADO FINAL

### Sistema Completamente Funcional

- ✅ **17 categorías PyME-específicas** vs 11 genéricas anteriores
- ✅ **5 buyer personas** con ejemplos ROI cuantificados
- ✅ **Templates ejecutivos** con beneficios específicos por sector
- ✅ **Compatibilidad total** - todas las funciones existentes preservadas
- ✅ **Testing verificado** - sistema completo validado
- ✅ **Documentación completa** - guías de uso y ejemplos prácticos

### Próximos Pasos

1. **A/B testing** de mensajes ROI por buyer persona
2. **Métricas de conversión** específicas por perfil
3. **Base de datos** con casos éxito reales por sector
4. **Templates personalizados** adicionales por industria

---

**El sistema de prompts está ahora completamente optimizado para líderes PyME con ejemplos ROI cuantificados, lenguaje ejecutivo, y adaptación automática por buyer persona.**