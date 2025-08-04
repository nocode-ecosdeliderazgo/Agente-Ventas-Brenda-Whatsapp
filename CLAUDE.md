# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "Brenda" - an intelligent WhatsApp sales bot for "Aprenda y Aplique IA" courses, designed for **PyME leaders** (small and medium enterprise executives). The project implements a complete intelligent conversation system with Clean Architecture, OpenAI integration, buyer persona-based prompts, and specialized templates for business executives.

### 🎯 TARGET AUDIENCE - PyME Leaders (Primary Buyer Personas)

**5 priority buyer personas:**
1. **Lucía CopyPro** - Marketing Digital Manager (Agencies)
2. **Marcos Multitask** - Operations Manager (Manufacturing PyMEs) 
3. **Sofía Visionaria** - CEO/Founder (Professional Services)
4. **Ricardo RH Ágil** - Head of Talent & Learning (Scale-ups)
5. **Daniel Data Innovador** - Senior Innovation/BI Analyst (Corporates)

**Business Focus**: 20-200 employee companies needing AI automation without technical teams.

## ✅ CURRENT STATUS: SISTEMA 100% FUNCIONAL - PURCHASE BONUS SYSTEM WITH BANKING INFO

### **🎉 ÚLTIMA ACTUALIZACIÓN (5 Agosto 2025)**: Sistema completo de bonos de compra con datos bancarios y mejoras de respuestas

**✅ Componentes Completamente Implementados y Validados:**
- **Privacy Flow System** ✅ **COMPLETAMENTE FUNCIONAL** - Flujo GDPR obligatorio
- **Course Announcement System** ✅ **COMPLETAMENTE FUNCIONAL** - Con envío real de PDF e imágenes via ngrok
- **Multimedia File Serving** ✅ **COMPLETAMENTE FUNCIONAL** - Archivos reales desde `resources/course_materials/`
- **🆕 Purchase Bonus System** ✅ **NUEVO - COMPLETAMENTE FUNCIONAL** - Bonos workbook por intención de compra
- **🆕 Banking Integration** ✅ **NUEVO - COMPLETAMENTE FUNCIONAL** - Datos bancarios automáticos en mensajes de compra
- **Anti-Inventos System** ✅ **COMPLETAMENTE FUNCIONAL** - Con fix JSON parser
- **Advanced Personalization** ✅ **COMPLETAMENTE FUNCIONAL** - JSON parsing resuelto
- **Ad Flow System** ✅ **COMPLETAMENTE FUNCIONAL** - Base de datos integrada
- **Role Validation System** ✅ **IMPLEMENTADO Y VALIDADO** - Rechaza roles inválidos
- **Database Integration** ✅ **COMPLETAMENTE FUNCIONAL** - 100% datos dinámicos de BD
- **Intelligent Bonus System** ✅ **COMPLETAMENTE FUNCIONAL** - Bonos contextuales activados
- **Advisor Referral System** ✅ **COMPLETAMENTE FUNCIONAL** - Referencia automática a asesores
- **🆕 FAQ System** ✅ **NUEVO - COMPLETAMENTE FUNCIONAL** - Sistema de preguntas frecuentes integrado

### **🔧 Últimas Mejoras Críticas Implementadas (5 Agosto 2025)**
- **✅ Purchase Intent Detection**: IMPLEMENTADO - Detección automática de intención de compra
- **✅ Workbook Bonus Activation**: IMPLEMENTADO - Bonos workbook desde base de datos por compra
- **✅ Banking Information**: IMPLEMENTADO - Datos bancarios automáticos en respuestas de compra
- **✅ Multimedia File Sending**: RESUELTO - Envío real de PDF e imágenes via ngrok
- **✅ Course Information Fix**: RESUELTO - Muestra precio correcto $4500 MXN y información específica
- **✅ Twilio Character Limit**: RESUELTO - Mensajes optimizados bajo 1600 caracteres
- **✅ Processing Priority**: RESUELTO - Course Announcement tiene prioridad sobre Ad Flow
- **✅ Ngrok Integration**: IMPLEMENTADO - URLs públicas para multimedia con fallback automático
- **✅ Concise Specific Responses**: IMPLEMENTADO - Respuestas concisas para consultas específicas con datos de BD
- **🆕 Enhanced FAQ System**: IMPLEMENTADO - 13 FAQs expandidas con información detallada ($2,990 MXN)
- **🆕 Conversational Tone Improvement**: IMPLEMENTADO - Eliminadas frases empáticas repetitivas, tono más dinámico
- **🆕 Greeting Simplification**: IMPLEMENTADO - Eliminado "¡Hola [nombre]!" para evitar duplicaciones
- **🆕 Instructor Inquiry Fix**: IMPLEMENTADO - Preguntas sobre instructores responden correctamente sin fallar
- **🆕 Message Duplication Prevention**: IMPLEMENTADO - Respuestas complejas ya no se duplican
- **🆕 Course Announcement Flag Fix**: IMPLEMENTADO - `course_announcement_sent` solo se marca tras confirmación Twilio

## Current Architecture

```
app/                           # CLEAN ARCHITECTURE
├── config/settings.py         # Pydantic Settings con ngrok_url
├── domain/entities/           # Business entities
│   ├── message.py            # Message entities con multimedia support
│   └── [otros entities]
├── infrastructure/            # Infrastructure layer
│   ├── twilio/client.py      # WhatsApp client con multimedia
│   ├── openai/client.py      # GPT-4o-mini integration
│   └── database/             # PostgreSQL con Supabase
├── application/usecases/      # Business logic
│   ├── process_incoming_message.py # Priority-based message processing
│   ├── privacy_flow_use_case.py # GDPR-compliant workflow
│   ├── course_announcement_use_case.py # ✅ Multimedia course announcements
│   ├── purchase_bonus_use_case.py # 🆕 Purchase intent & workbook bonuses
│   ├── advisor_referral_use_case.py # Intelligent advisor referral
│   └── [otros use cases]
├── templates/                 # WhatsApp-optimized templates
└── presentation/api/webhook.py # FastAPI con StaticFiles para resources/

resources/course_materials/    # ✅ ARCHIVOS MULTIMEDIA REALES
├── experto_ia_profesionales.pdf
└── experto_ia_profesionales.jpg
```

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements-clean.txt

# Configure environment
cp .env.example .env
# Edit .env with credentials including NGROK_URL
```

### Running the System
```bash
# Setup ngrok for multimedia (required for file sending)
ngrok http 8000
# Copy ngrok URL to .env: NGROK_URL=https://your-ngrok-url.ngrok-free.app

# Start webhook server
python run_webhook_server.py

# Test complete system
python test_webhook_simulation.py
```

### Testing Course Announcements with Multimedia
```bash
# Send course codes to test real file sending:
#Experto_IA_GPT_Gemini #ADSIM_05

# Expected results:
# ✅ Price: $4500 MXN (not USD)
# ✅ processing_type: 'course_announcement'
# ✅ Real PDF and image files sent via ngrok URLs
# ✅ Message under 1600 character limit
```

### Development Workflow
```bash
# 1. Basic setup and testing
python test_webhook_simulation.py  # Test complete system
python test_whatsapp_connection.py  # Test basic Twilio connection

# 2. Feature-specific testing
python test_course_announcement_flow.py  # Course announcement system
python test_purchase_bonus_system.py     # Purchase intent and bonus system
python test_buyer_persona_matching_improved.py  # Buyer persona detection

# 3. Running the full system
python run_webhook_server.py      # Production-ready server
python run_webhook_server_debug.py  # Debug mode with detailed logging
python run_development.py         # Development mode with auto-reload
```

### 🆕 Testing Purchase Bonus System
```bash
# Send purchase intent messages to test bonus activation:
"Quiero comprarlo"
"¿Cómo puedo pagar?"
"Ya decidí, me apunto"
"¿Cuánto cuesta?"

# Expected results:
# ✅ Purchase intent detected automatically
# ✅ Workbook bonus activated from database
# ✅ Banking details included in response
# ✅ Personalized ROI message by buyer persona
# ✅ Lead score increased significantly
# ✅ High-priority purchase signal recorded
```

### 🆕 Testing Concise Specific Response System
```bash
# Test specific inquiry responses with database integration:

# Price inquiries
"¿Cuál es el precio del curso?"
"¿Cuánto cuesta?"
"¿Qué precio tiene?"

# Session inquiries
"¿Cuántas sesiones tiene el curso?"
"¿Cuántas clases son?"
"¿Qué sesiones incluye?"

# Duration inquiries
"¿Cuánto dura el curso?"
"¿Cuántas horas son?"
"¿Qué duración tiene?"

# Content inquiries
"¿Qué temario tiene?"
"¿Qué voy a aprender?"
"¿Cuál es el contenido?"

# Modality inquiries
"¿Es presencial u online?"
"¿Qué modalidad tiene?"
"¿Cómo es el formato?"

# Expected results:
# ✅ Concise response with only requested info
# ✅ Real data from PostgreSQL database
# ✅ Course name + specific info + follow-up question
# ✅ No hardcoded or invented information
# ✅ Proper categorization: SESSION_INQUIRY, PRICE_INQUIRY, etc.
```

## Environment Variables Required

```env
# === CORE CREDENTIALS (REQUIRED) ===
TWILIO_ACCOUNT_SID=your_twilio_sid       # From Twilio Console
TWILIO_AUTH_TOKEN=your_twilio_token      # From Twilio Console
TWILIO_PHONE_NUMBER=+14155238886         # Your Twilio WhatsApp number
OPENAI_API_KEY=sk-proj-...               # From OpenAI API keys

# === MULTIMEDIA SUPPORT (REQUIRED for file sending) ===
NGROK_URL=https://your-ngrok-url.ngrok-free.app  # From ngrok http 8000

# === DATABASE (OPTIONAL - system works without it) ===
DATABASE_URL=postgresql://username:password@host:port/database
SUPABASE_URL=https://your-ref.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# === APPLICATION SETTINGS ===
APP_ENVIRONMENT=development              # development|production
LOG_LEVEL=INFO                          # DEBUG|INFO|WARNING|ERROR
WEBHOOK_VERIFY_SIGNATURE=true          # Enable/disable signature verification

# === ADVISOR CONFIGURATION ===
ADVISOR_PHONE_NUMBER=+5215614686075     # Phone for advisor referrals
ADVISOR_NAME=Especialista en IA         # Advisor display name
```

## Message Processing Priority System

The system processes messages with the following priority:

1. **PRIORIDAD 1**: Privacy Flow (mandatory GDPR consent)
2. **PRIORIDAD 1.5**: Course Announcements (#Experto_IA_GPT_Gemini, #ADSIM_05, etc.)
3. **PRIORIDAD 1.6**: Ad Flow (hashtag-based campaigns) 
4. **PRIORIDAD 1.7**: Welcome Flow (generic messages)
5. **PRIORIDAD 1.8**: Advisor Referral (contact requests)
6. **PRIORIDAD 2**: Intelligent Responses (OpenAI-powered)
   - **✅ Enhanced Intelligent FAQ Handling**: Natural FAQ responses (13 expanded FAQs) with improved conversational tone
   - **✅ Concise Specific Responses**: Direct answers for price/session/duration inquiries from database
   - **✅ Purchase Intent Detection**: Automatic bonus activation on purchase signals
   - **✅ Workbook Bonus Activation**: Database-driven bonus offering
7. **FAQ Fallback**: Direct FAQ flow if intelligent agent fails
8. **Fallback**: Basic context-aware responses

## Course Announcement System

### Supported Course Codes
- `#Experto_IA_GPT_Gemini` - Experto en IA para Profesionales ($4500 MXN)
- `#ADSIM_05` - Same course, different campaign code
- `#CursoIA1`, `#CursoIA2`, `#CursoIA3` - Mock courses for testing

### Complete Flow
1. **Code Detection** - Automatic detection in messages
2. **Course Info Retrieval** - From database or mock data
3. **Personalized Message** - ROI-focused, under 1600 chars
4. **Real File Sending** - PDF and image via ngrok URLs
5. **Fallback Handling** - Text messages if multimedia fails

## Multimedia File System

### File Structure
```
resources/course_materials/
├── experto_ia_profesionales.pdf    # Course guide
└── experto_ia_profesionales.jpg    # Course infographic
```

### Ngrok Configuration
1. **Run ngrok**: `ngrok http 8000`
2. **Copy URL**: Update `NGROK_URL` in `.env`
3. **Test Access**: Verify files accessible at ngrok URL
4. **Automatic Fallback**: System uses text messages if ngrok unavailable

## Key Features

### Anti-Inventos System
Validates AI responses to prevent hallucinations using:
- Pattern risk detection
- Database verification
- Confidence scoring
- Safe response generation

### Buyer Persona System
- Automatic persona detection
- ROI-focused messaging
- Role-specific communication styles
- Professional context extraction

### Privacy Flow
- Mandatory GDPR consent
- WhatsApp name extraction
- Professional messaging
- Flow state management

### Advisor Referral
- Intelligent request detection
- Urgency level assessment
- Professional handoff messages
- Context preservation

### 🆕 Purchase Bonus System
**Automatic purchase intent detection** triggers workbook bonus activation:
- **Intent Categories**: PURCHASE_INTENT_DIRECT, PURCHASE_INTENT_PRICING, PURCHASE_READY_SIGNALS
- **Keywords**: "quiero comprarlo", "cómo pago", "me apunto", "ya decidí", "cuánto cuesta"
- **Workbook Bonuses**: Database-driven Coda.io templates and guides
- **Banking Information**: Automatic inclusion of company banking details
- **Personalization**: ROI-focused messages by buyer persona
- **Memory Update**: High-priority lead scoring and purchase signal tracking

**Banking Details Included:**
- Razón Social: Aprende y Aplica AI S.A. de C.V.
- Banco: BBVA
- Cuenta CLABE: 012345678901234567
- RFC: AAI210307DEF
- Uso de CFDI: GO3-Gastos en general

### 🆕 Concise Specific Response System
**Intelligent detection of specific inquiries** triggers concise, database-driven responses:

#### Supported Inquiry Types
- **PRICE_INQUIRY**: Direct price questions → Shows course name + price + follow-up question
- **SESSION_INQUIRY**: Session count questions → Shows course name + session info + follow-up question  
- **DURATION_INQUIRY**: Duration questions → Shows course name + time duration + follow-up question
- **CONTENT_INQUIRY**: Content/curriculum questions → Shows course name + content overview + follow-up question
- **MODALITY_INQUIRY**: Format questions → Shows course name + modality info + follow-up question

#### Detection Methods
1. **OpenAI Categorization**: Automatically categorizes specific inquiry types
2. **Keyword Detection**: Fallback detection using Spanish keywords
3. **Smart Mapping**: Maps categories to specific response types

#### Example Responses
```
# Price Inquiry: "¿cuál es el precio del curso?"
🎓 **Experto en IA para Profesionales**
💰 **Precio**: $4,500 MXN

¿Te gustaría conocer más detalles del curso?

# Session Inquiry: "¿cuántas sesiones tiene?"
🎓 **Experto en IA para Profesionales**  
📅 **Sesiones**: 8 sesiones (12 horas)

¿Te gustaría conocer el contenido de las sesiones?
```

#### Key Benefits
- **Always Database-Driven**: Real data from PostgreSQL, never hardcoded
- **Concise Format**: Only shows requested information + course name + follow-up
- **Maintains Context**: Preserves conversation flow and buyer persona detection
- **No Information Invention**: Prevents AI hallucination with specific data

## Testing Scripts

### Core System Tests
- `test_webhook_simulation.py` - ⭐ **Complete system test with multimedia**
- `test_supabase_connection.py` - Database connectivity
- `test_course_integration.py` - Course system integration
- `test_memory_system.py` - User memory and personalization

### Specialized Tests
- `test_anti_inventos_system.py` - Anti-hallucination validation
- `test_personalization_system.py` - Buyer persona detection
- `test_course_announcement_flow.py` - Course code processing
- `test_purchase_bonus_system.py` - 🆕 Purchase intent & workbook bonus activation
- `test_faq_flow_integration.py` - 🆕 FAQ system integration and detection
- `test_intelligent_faq_system.py` - 🆕 Intelligent FAQ with knowledge provider and fallback

## Production Readiness

### ✅ Ready for Production
- **Core System**: 100% functional and validated
- **Database Integration**: Complete with fallback systems
- **Error Handling**: Comprehensive with graceful degradation
- **Security**: GDPR compliance and input validation
- **Performance**: Optimized message handling under Twilio limits
- **Multimedia Support**: Real file sending with ngrok integration
- **🆕 Purchase Flow**: Complete purchase intent detection with bonus activation
- **🆕 Banking Integration**: Automatic banking details in purchase responses
- **🆕 Intelligent FAQ System**: Dual-layer FAQ handling with intelligent responses and robust fallback

### 🔄 Future Enhancements
- Custom domain for multimedia (replace ngrok)
- Advanced analytics and metrics
- Extended tool registry system
- Additional course integrations

## Important Notes

### WhatsApp Limitations
- 1600 character limit per message (handled)
- Multimedia requires public URLs (ngrok solution implemented)
- No inline buttons (text-based interactions only)

### Ngrok Requirements & Troubleshooting
- **Development**: Ngrok required for multimedia file testing
- **Production**: Replace with permanent domain solution
- **Fallback**: System works with text-only if multimedia unavailable

**Common Issues:**
- If files don't send: Check NGROK_URL in .env matches current ngrok session
- If webhook fails: Verify ngrok tunnel is active and Twilio webhook URL is updated
- If slow responses: Check OpenAI API limits and database connection

### Message Processing
- Privacy flow is mandatory and always executes first
- Course announcements have priority over ad flow
- All flows include comprehensive error handling
- System maintains conversation context across interactions

## Architecture Notes for Development

### Clean Architecture Implementation
- **Domain Layer** (`app/domain/`): Business entities and core logic
- **Application Layer** (`app/application/usecases/`): Business use cases and workflows
- **Infrastructure Layer** (`app/infrastructure/`): External service integrations (Twilio, OpenAI, Database)
- **Presentation Layer** (`app/presentation/`): API endpoints and webhook handlers

### Key Design Patterns
- **Use Case Pattern**: Each business operation is encapsulated in a use case class
- **Repository Pattern**: Database access abstracted through repository interfaces
- **Template Pattern**: Message templates separated from business logic
- **Strategy Pattern**: Different response generation strategies based on context

### Testing Strategy
- **Integration Tests**: `test_webhook_simulation.py` tests complete message flows
- **Unit Tests**: Individual use case testing with mocked dependencies
- **Feature Tests**: Specific functionality like course announcements and purchase flow

## Legacy Reference

The `legacy/` folder contains the complete Telegram implementation with 35+ conversion tools. Use as reference for migrating additional features to WhatsApp.

---

**Current Status**: ✅ **PRODUCTION READY** - Enhanced FAQ system + Improved conversational tone + Concise specific responses
**Last Updated**: August 5, 2025
**Version**: 2.4 - Response Fixes and Greeting Simplification