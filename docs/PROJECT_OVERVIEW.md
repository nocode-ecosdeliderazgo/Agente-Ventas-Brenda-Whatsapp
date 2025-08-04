# PROJECT OVERVIEW - Bot Brenda WhatsApp
> **Documentación Técnica de Alto Nivel**  
> **Última actualización**: Enero 2025

## 🏗️ Resumen Arquitectónico

### Tecnologías y Librerías Clave
- **Framework Web**: FastAPI + Uvicorn/Gunicorn
- **IA Conversacional**: OpenAI GPT (client v1.30+)
- **Mensajería**: Twilio WhatsApp API
- **Base de Datos**: PostgreSQL (asyncpg)
- **Configuración**: Pydantic Settings + python-dotenv
- **Validación**: Pydantic v2.0+
- **Cliente HTTP**: httpx (asíncrono)

### Estructura de Directorios y Responsabilidades

```
app/
├── config/             # ⚙️ Configuración centralizada (settings.py)
├── domain/             # 🏛️ Entidades de negocio (User, Message, Course, etc.)
├── application/        # 📋 Casos de uso de negocio
│   └── usecases/       # ▶️ Flujos principales del bot
├── infrastructure/     # 🔧 Adaptadores externos 
│   ├── twilio/         # 📱 Cliente WhatsApp
│   ├── openai/         # 🤖 Cliente IA
│   ├── database/       # 🗄️ PostgreSQL + repositorios
│   └── tools/          # 🛠️ Sistema de herramientas
├── presentation/       # 🌐 Interfaces externas
│   └── api/            # REST API (webhook.py)
└── templates/          # 📝 Templates de respuestas

memory/                 # 💾 Sistema de memoria persistente
config/                 # 🔧 Configuración legacy (twilio_settings.py)
resources/              # 📄 Archivos estáticos (PDFs, imágenes)
prompts/                # 🧠 Templates de prompts IA
```

### Punto de Entrada Principal
- **Webhook FastAPI**: `app/presentation/api/webhook.py`
- **Puerto**: 8000 (configurable)
- **Endpoints**:
  - `POST /webhook` - Recibe mensajes de Twilio
  - `GET /` - Health check

---

## 🚀 Flujos de Negocio Productivos

### ▶️ Flujo de Bienvenida
**Archivo**: `app/application/usecases/welcome_flow_use_case.py`

**Responsabilidades**:
- Ofrecer catálogo de cursos disponibles
- Asegurar selección obligatoria de un curso  
- Guardar curso seleccionado en memoria
- Transicionar a agente inteligente personalizado

**Estados**:
- `privacy_flow_completed` → ofrece cursos
- `waiting_for_response: "course_selection"` → procesa selección
- `selected_course` definido → activa agente inteligente

### 🔐 Flujo de Privacidad  
**Archivo**: `app/application/usecases/privacy_flow_use_case.py`

**Etapas**:
1. **Solicitud inicial**: Pide consentimiento de privacidad
2. **Validación nombre**: Extrae/solicita nombre del usuario
3. **Solicitud rol**: Pide rol profesional (opcional)
4. **Completado**: `stage = "privacy_flow_completed"`

**Flags clave**:
- `privacy_accepted: bool`
- `privacy_requested: bool` 
- `waiting_for_response: "privacy_acceptance" | "user_name" | "user_role"`

### ✅ Flujo de Confirmación Rápida (`PAYMENT_CONFIRMATION`)
**Archivo**: `app/application/usecases/generate_intelligent_response.py:2289`

**Responsabilidades**:
- Detecta intención `PAYMENT_CONFIRMATION` 
- Envía datos bancarios + bonos activos
- Conecta con asesor especializado
- Formatea respuesta con `WhatsAppBusinessTemplates.payment_confirmation_advisor_contact()`

**Intenciones relacionadas**:
- `PAYMENT_COMPLETED` - Pago ya realizado
- `COMPROBANTE_UPLOAD` - Comprobante enviado

### 💳 Flujo de Oferta de Datos Bancarios + Bono
**Archivo**: `app/application/usecases/purchase_bonus_use_case.py`

**Funcionalidad**:
- Activa con `purchase_bonus_sent: bool = False`
- Obtiene bonos activos desde BD (`bond` table)
- Envía datos bancarios para transferencia
- Marca `purchase_bonus_sent: bool = True`

### 📚 Flujo de Consulta de Curso / PDF
**Archivos**: 
- `app/application/usecases/query_course_information.py`
- `app/application/usecases/course_announcement_use_case.py`

**Funcionalidades**:
- Consulta PostgreSQL (tabla `ai_courses`)
- Envía PDFs desde `/resources/course_materials/`
- Templates personalizados por curso
- Integración con sistema de herramientas

### 🛠️ Sistema de Herramientas
**Archivos**:
- `app/infrastructure/tools/tool_system.py` - Framework base
- `app/infrastructure/tools/tool_db.py` - Consultas DB
- `app/application/usecases/tool_activation_use_case.py` - Activación inteligente

**Herramientas Disponibles**:
- `EnviarRecursosGratuitos` - Recursos educativos
- `MostrarSyllabusInteractivo` - Programa detallado
- `EnviarPreviewCurso` - Vista previa
- `MostrarComparativaPrecios` - Comparación de precios
- `MostrarBonosExclusivos` - Bonos especiales
- `ContactarAsesorDirecto` - Escalación humana

**Activación por Intención**:
- `EXPLORATION` → Recursos + Syllabus
- `OBJECTION_PRICE` → Comparativa precios + Bonos
- `BUYING_SIGNALS` → Contacto asesor
- Máximo 2 herramientas por interacción

---

## 🗄️ Modelo de Datos

### Tablas PostgreSQL Relevantes

#### `ai_courses` - Catálogo Maestro
```sql
id_course (uuid, PK)
name, short_description, long_description
price, currency
session_count, total_duration_min  
level (básico/intermedio/avanzado)
modality (online/presencial/híbrido)
status, start_date, end_date
```

#### `bond` - Bonos y Recursos Extra
```sql
id_bond (bigint, PK)
content, type_bond
id_courses_fk → ai_courses  
bond_url, active
```

#### `ai_course_session` - Sesiones del Curso
```sql
id_session (uuid, PK)
session_index, title, objective
duration_minutes, scheduled_at
id_course_fk → ai_courses
```

#### `elements_url` - Recursos Multimedia
```sql
id_element (uuid, PK)  
item_type, url_test, description_url
id_session_fk, id_activity_fk
```

### Relaciones Principales
```
ai_courses 1 ────< ai_course_session 1 ────< ai_tema_activity
   |                                 \
   |                                  > elements_url
   |
   └─── 1 ────< bond (bonos por curso)
```

---

## 💾 Persistencia de Memoria del Lead

### Archivo Principal
`memory/lead_memory.py` - Clase `LeadMemory`

### Campos Principales

#### Estados del Flujo
```python
stage: str = "first_contact"  # first_contact, privacy_flow, course_selection, sales_agent, converted
current_flow: str = "none"    # none, privacy, course_selection, sales_conversation  
flow_step: int = 0            # paso actual dentro del flujo
waiting_for_response: str     # name, privacy_acceptance, course_choice, etc.
```

#### Información del Usuario
```python
user_id: str
name: str = ""
role: Optional[str] = None
selected_course: str = ""
privacy_accepted: bool = False
privacy_requested: bool = False
```

#### Personalización Avanzada (Fase 2)
```python
buyer_persona_match: str      # lucia_copypro, marcos_multitask, sofia_visionaria, etc.
professional_level: str      # junior, mid-level, senior, executive
company_size: str            # startup, small, medium, large, enterprise  
industry_sector: str         # marketing, operations, tech, consulting, etc.
technical_level: str         # beginner, intermediate, advanced
decision_making_power: str   # influencer, decision_maker, budget_holder
```

#### Scoring y Señales
```python
lead_score: int = 50
interaction_count: int = 0
interest_level: str = "unknown"
pain_points: List[str] = []
buying_signals: List[str] = []
urgency_signals: List[str] = []
budget_indicators: List[str] = []
```

#### Flags de Control
```python
brenda_introduced: bool = False           # Si ya se presentó Brenda
purchase_bonus_sent: bool = False         # Si ya se enviaron datos bancarios
original_message_body: Optional[str]      # Mensaje que inició el flujo
```

### Métodos Útiles
- `is_first_interaction()` - Primera vez del usuario
- `needs_privacy_flow()` - Necesita flujo de privacidad  
- `is_ready_for_sales_agent()` - Listo para agente inteligente
- `is_high_value_lead()` - Lead de alto valor
- `get_recommended_approach()` - Estrategia de comunicación

### Almacenamiento
- **Directorio**: `memorias/` (configurable)
- **Formato**: JSON (`memory_{user_id}.json`)
- **Backup**: Automático antes de guardar
- **Cache**: En memoria durante ejecución

---

## ⚠️ Puntos Críticos / TODOs

### TODOs Prioritarios

#### `app/application/usecases/generate_intelligent_response.py`
```python
# Línea 328: Mejorar análisis de intención incluyendo info de curso
# Línea 1323: Implementar envío de recursos  
# Línea 1328: Implementar flujo de contacto con asesor
# Línea 1333: Implementar envío de overview del curso
```

#### `app/infrastructure/tools/tool_system.py`
```python
# Línea 122: Mensaje personalizado de recursos (implementar después)
# Línea 161: Generar mensaje formateado syllabus (implementar después)  
# Línea 257: Generar mensaje personalizado con ROI (implementar después)
# Línea 293: Generar mensaje con bonos reales (implementar después)
```

#### `prompts/tool_prompts.py`
```python
# Línea 5: Agregar más plantillas para bonos, demos, cierre, etc.
```

### Componentes Legacy/Obsoletos

#### Evitar Consultar
- `tests/` - Tests desactualizados, usar solo como referencia
- `core/whatsapp_agent.py` - Agente legacy sin integrar  
- `handlers/whatsapp_webhook.py` - Webhook legacy
- `config/twilio_settings.py` - Configuración legacy (usar `app/config/settings.py`)

#### Archivos de Desarrollo
- `test_*.py` en raíz - Scripts de testing, no productivos
- `run_*.py` - Scripts de desarrollo local
- `fix_*.py` - Scripts de reparación temporal

### Lógica Temporal/Hardcoded

#### En `app/presentation/api/webhook.py`
- Inicialización con fallbacks para falta de OpenAI/PostgreSQL
- Modo FALLBACK si OpenAI falla (líneas 237-279)
- Debug prints extensos (remover en producción)

#### En `memory/lead_memory.py`  
- Buyer personas hardcoded (líneas 142-180)
- Scoring manual de leads (línea 190-215)

---

## 🚦 Estado Actual del Sistema

### ✅ Funcionalidades Operativas
- Webhook FastAPI recibiendo mensajes Twilio ✅
- Sistema de memoria persistente completo ✅  
- Flujo de privacidad funcional ✅
- Consultas PostgreSQL a catálogo de cursos ✅
- Templates de respuesta estructurados ✅
- Sistema de herramientas (framework base) ✅

### 🚧 En Desarrollo  
- Personalización avanzada de respuestas 🚧
- Sistema de bonos dinámico 🚧
- Análisis de buyer persona automático 🚧
- Métricas y analytics 🚧

### ⏳ Pendiente
- Tests automatizados ⏳
- Documentación de API ⏳  
- Monitoreo y logging estructurado ⏳
- Optimización de performance ⏳

---

## 📋 Guías de Desarrollo

### Para Agregar Nuevo Flujo
1. Crear caso de uso en `app/application/usecases/`
2. Integrar en `ProcessIncomingMessageUseCase`
3. Agregar templates en `app/templates/`
4. Actualizar memoria en `LeadMemory`

### Para Nueva Herramienta
1. Heredar de `BaseTool` en `tool_system.py`
2. Implementar método `execute()`
3. Registrar en `ToolActivationSystem`
4. Mapear intención en `intent_tool_mapping`

### Para Nueva Entidad
1. Crear en `app/domain/entities/`
2. Agregar repositorio en `app/infrastructure/database/repositories/`
3. Actualizar esquema en `db_schema_condensed.md`

### Debugging
- Usar `debug_print()` en archivos principales
- Logs estructurados con módulo `logging`
- Webhook debugger: `run_webhook_server_debug.py`
- Simulador: scripts `test_*.py`

---

**Nota**: Esta documentación refleja el estado de Agosto 4 de 2025. Para cambios recientes consultar git log y PRs activos.