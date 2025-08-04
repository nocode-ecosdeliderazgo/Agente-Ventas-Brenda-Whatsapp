# PROJECT OVERVIEW - BOT BRENDA WHATSAPP AGENT

> **Estado:** Sistema operativo con arquitectura Clean Architecture  
> **Última actualización:** Enero 2025  
> **Responsable:** Israel - Equipo de Desarrollo  

---

## 📋 RESUMEN ARQUITECTÓNICO

### 🛠️ Tecnologías y Librerías Clave

**Framework Principal:**
- **FastAPI** - API web asíncrona para webhooks
- **Uvicorn/Gunicorn** - Servidor ASGI para producción
- **Pydantic** - Validación de datos y configuración

**Integraciones Externas:**
- **Twilio WhatsApp** - Comunicación por WhatsApp
- **OpenAI GPT** - Motor de inteligencia artificial
- **PostgreSQL** - Base de datos principal (Supabase)
- **AsyncPG** - Cliente PostgreSQL asíncrono

**Infraestructura:**
- **Heroku** - Plataforma de despliegue
- **Ngrok** - Túneles para desarrollo local
- **JSON** - Persistencia local de memoria de leads

### 🏗️ Estructura de Directorios

```
app/
├── config/               # ⚙️ Configuración (settings.py, campaign_config.py)
├── domain/entities/      # 🎯 Entidades de negocio (User, Course, Message, etc.)
├── application/usecases/ # 📋 Casos de uso (22 archivos de lógica de negocio)
├── infrastructure/      # 🔧 Integraciones externas
│   ├── database/        # 💾 PostgreSQL repositories y client
│   ├── twilio/          # 📱 Cliente WhatsApp
│   ├── openai/          # 🤖 Cliente OpenAI
│   ├── tools/           # 🛠️ Sistema de herramientas de conversión
│   └── faq/             # ❓ Sistema de FAQ inteligente
└── presentation/api/    # 🌐 Webhook FastAPI

memory/                  # 🧠 Sistema de memoria persistente
config/                  # ⚙️ Configuración legacy
resources/               # 📁 Archivos estáticos (PDFs, imágenes)
legacy/                  # 📦 Código heredado (funciones operativas)
```

---

## 🔄 FLUJOS DE NEGOCIO PRODUCTIVOS

### ▶️ Flujo de Bienvenida
**Archivo:** `app/application/usecases/welcome_flow_use_case.py`

**Responsabilidades:**
- Activar después de completar flujo de privacidad
- Ofrecer catálogo de cursos desde PostgreSQL
- Procesar selección inteligente (número, nombre, nivel)
- Guardar curso seleccionado en memoria del lead
- Preparar para agente inteligente

**Estados manejados:**
- `privacy_flow_completed` → `course_selection` → `ready_for_sales_agent`

### 💳 Flujo de Oferta de Datos Bancarios + Bono
**Archivos:** 
- `app/application/usecases/purchase_bonus_use_case.py`
- `app/application/usecases/bonus_activation_use_case.py`

**Activación:** Intención de compra detectada (confianza ≥ 0.7)
- `PURCHASE_INTENT_DIRECT`
- `PURCHASE_INTENT_PRICING` 
- `PURCHASE_READY_SIGNALS`
- `BUYING_SIGNALS_EXECUTIVE`

**Flujo:**
1. Detectar intención de compra por análisis de IA
2. Obtener bonos workbook desde BD (tabla `bond`)
3. Seleccionar bono relevante según buyer persona
4. Generar mensaje con datos bancarios:
   - **Razón Social:** Aprende y Aplica AI S.A. de C.V.
   - **Banco:** BBVA
   - **CLABE:** 012345678901234567
   - **RFC:** AAI210307DEF
   - **CFDI:** GO3-Gastos en general

### ✅ Flujo de Confirmación Rápida (PAYMENT_CONFIRMATION)
**Estado:** No encontrado sistema específico - **⚠️ Punto crítico**

**Nota:** Buscar implementación en código heredado o crear caso de uso.

### 📚 Flujo de Consulta de Curso / PDF
**Archivo:** `app/application/usecases/query_course_information.py`

**Capacidades:**
- Búsqueda por palabra clave en PostgreSQL
- Obtener detalles completos con sesiones y bonos
- Formateo para WhatsApp con límites de contenido
- Recursos multimedia desde tabla `elements_url`

**Métodos clave:**
- `search_courses_by_keyword()` - Búsqueda textual
- `get_course_detailed_content()` - Información completa para prompts
- `format_detailed_course_for_chat()` - Formato WhatsApp optimizado

### 🛠️ Herramientas (Sistema de Conversión)
**Archivo:** `app/infrastructure/tools/tool_system.py`

**Herramientas Disponibles:**
1. **`enviar_recursos_gratuitos`** - PDFs y materiales gratuitos
2. **`mostrar_syllabus_interactivo`** - Temario completo del curso  
3. **`enviar_preview_curso`** - Videos de muestra
4. **`mostrar_comparativa_precios`** - Análisis ROI vs mercado
5. **`mostrar_bonos_exclusivos`** - Bonos por tiempo limitado
6. **`contactar_asesor_directo`** - **⚡ CRÍTICO** - Transferencia a humano

**Activación por Intención:**
```python
intent_tool_mapping = {
    'EXPLORATION': ['mostrar_syllabus_interactivo', 'enviar_preview_curso'],
    'FREE_RESOURCES': ['enviar_recursos_gratuitos'],
    'OBJECTION_PRICE': ['mostrar_comparativa_precios'],
    'CONTACT_REQUEST': ['contactar_asesor_directo']  # CRÍTICO
}
```

---

## 💾 MODELO DE DATOS

### 🗄️ Tablas PostgreSQL Relevantes

**`ai_courses`** - Catálogo de cursos
```sql
- id_course (UUID)           - Identificador único
- name (VARCHAR)             - Nombre del curso
- short_description          - Descripción breve
- price/currency             - Precio y moneda
- level                      - Nivel (Básico, Intermedio, Avanzado)
- session_count              - Número de sesiones
- modality                   - Modalidad (online, presencial)
- status                     - Estado (active, inactive)
```

**`bond`** - Bonos y materiales
```sql
- id_bond (BIGINT)           - ID auto-generado
- content (TEXT)             - Descripción del bono
- type_bond (VARCHAR)        - Tipo de bono
- id_courses_fk (UUID)       - Relación con curso
- emisor (VARCHAR)           - Emisor del bono
```

**`ai_course_session`** - Sesiones del curso
```sql
- id_session (UUID)          - Identificador único
- title (VARCHAR)            - Título de la sesión
- duration_minutes           - Duración en minutos
- session_index              - Orden de la sesión
- id_course_fk (UUID)        - Relación con curso
```

**`elements_url`** - Recursos multimedia
```sql
- id_element (UUID)          - Identificador único
- url_test (VARCHAR)         - URL del recurso
- description_url            - Descripción del recurso
- item_type                  - Tipo de recurso
- id_session_fk (UUID)       - Relación con sesión
```

### 🔗 Relaciones Principales
```
ai_courses (1) ←→ (N) bond
ai_courses (1) ←→ (N) ai_course_session  
ai_course_session (1) ←→ (N) elements_url
```

---

## 🧠 PERSISTENCIA DE MEMORIA DEL LEAD

### 📁 Ubicación
**Archivo:** `memory/lead_memory.py`  
**Directorio:** `memorias/` (archivos JSON por usuario)

### 🏷️ Flags de Estado Principales

**Estados del Usuario:**
```python
stage: str = "first_contact"  # first_contact → privacy_flow → course_selection → sales_agent → converted
privacy_accepted: bool = False
privacy_requested: bool = False  
brenda_introduced: bool = False
selected_course: str = ""        # Código del curso seleccionado
```

**Control de Flujo:**
```python
current_flow: str = "none"       # none, privacy, course_selection, sales_conversation
flow_step: int = 0               # Paso actual dentro del flujo
waiting_for_response: str = ""   # name, privacy_acceptance, course_choice, etc.
```

**Personalización Avanzada (Buyer Personas):**
```python
buyer_persona_match: str = "unknown"        # lucia_copypro, marcos_multitask, sofia_visionaria, etc.
professional_level: str = "unknown"         # junior, mid-level, senior, executive
company_size: str = "unknown"               # startup, small, medium, large, enterprise  
decision_making_power: str = "unknown"      # influencer, decision_maker, budget_holder
response_style_preference: str = "business" # business, technical, casual, executive
```

**Scoring y Análisis:**
```python
lead_score: int = 50             # Puntuación del lead (0-100)
interest_level: str = "unknown"  # Nivel de interés detectado
interaction_count: int = 0       # Número de interacciones
```

### 💡 Métodos de Estado Críticos
```python
def needs_privacy_flow() -> bool         # Verificar si necesita privacidad
def is_ready_for_sales_agent() -> bool   # Listo para agente inteligente
def is_high_value_lead() -> bool         # Lead de alto valor
def get_conversation_priority_score()    # Puntuación de prioridad (0-100)
```

---

## ⚠️ PUNTOS CRÍTICOS / TODOS

### 🔧 TODOs en Código
```python
# app/infrastructure/tools/tool_system.py
TODO: Implementar mensajes personalizados en herramientas (líneas 122, 161, 209)
TODO: Generar mensaje personalizado con ROI (línea 257)

# app/application/usecases/tool_activation_use_case.py  
TODO: Integrar con DatabaseService real (línea 222)
TODO: Integrar con ResourceService real (línea 224)
TODO: Integrar con ContactFlowHandler real (línea 226)

# app/application/usecases/generate_intelligent_response.py
TODO: Mejorar análisis de intención para incluir info de curso (línea 339)
TODO: Implementar envío de recursos (línea 1384)
TODO: Implementar flujo de contacto con asesor (línea 1389)
```

### 🚨 Áreas de Riesgo

**1. Flujo de Confirmación de Pagos**
- **Estado:** No encontrado sistema específico para `PAYMENT_CONFIRMATION`
- **Riesgo:** Leads que confirman pago pueden no tener flujo automatizado
- **Acción:** Verificar código heredado o implementar caso de uso

**2. Servicios Mock en Producción**
- **Ubicación:** `app/infrastructure/tools/tool_system.py`
- **Riesgo:** Usando `MockResourceService` y `MockDatabaseService`
- **Acción:** Implementar servicios reales

**3. Sistema de Herramientas Incompleto**
- **Estado:** Estructura base implementada, mensajes en desarrollo
- **Riesgo:** Herramientas devuelven respuestas genéricas
- **Acción:** Completar personalización de mensajes

### 📂 Archivos Obsoletos (NO CONSULTAR)

**Tests Desactualizados:**
- `test_*.py` - Solo para referencia, no usar para desarrollo
- `legacy/` - Código heredado, solo para migración

**Documentación Antigua:**
- `docs/legacy/` - Documentación desactualizada
- Archivos `.md` en `/docs/` - Verificar fecha antes de usar

---

## 🚀 CONFIGURACIÓN DE DESPLIEGUE

### 🔧 Heroku
**Archivo:** `Procfile`
```bash
web: gunicorn app.presentation.api.webhook:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### 🌐 Webhook Endpoints
- **POST /webhook** - Receptor principal de mensajes Twilio
- **POST /** - Alias para webhook
- **GET /** - Health check

### ⚙️ Variables de Entorno Críticas
```bash
TWILIO_ACCOUNT_SID=<twilio_sid>
TWILIO_AUTH_TOKEN=<twilio_token>  
TWILIO_PHONE_NUMBER=<numero_whatsapp>
OPENAI_API_KEY=<openai_key>
DATABASE_URL=<postgresql_url>
```

---

## 🎯 ORDEN DE PRIORIDAD PARA DESARROLLO

**🔴 Crítico (P0):**
1. Implementar flujo de confirmación de pagos
2. Completar mensajes personalizados en herramientas
3. Reemplazar servicios mock por implementaciones reales

**🟡 Alto (P1):**
4. Mejorar análisis de intención con contexto de curso
5. Implementar flujo de contacto con asesor humano
6. Optimizar sistema de scoring de leads

**🟢 Medio (P2):**
7. Expandir sistema de buyer personas
8. Agregar métricas de conversión
9. Implementar sistema de A/B testing

---

*Archivo generado automáticamente el 2025-01-27*  
*Para actualizaciones, contactar al equipo de desarrollo*