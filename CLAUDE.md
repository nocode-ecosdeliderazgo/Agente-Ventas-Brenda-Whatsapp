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

## ✅ CURRENT STATUS: SISTEMA 100% FUNCIONAL - MULTIMEDIA COURSE ANNOUNCEMENTS WORKING

### **🎉 ÚLTIMA ACTUALIZACIÓN (1 Agosto 2025)**: Sistema de anuncios con archivos multimedia completamente funcional

**✅ Componentes Completamente Implementados y Validados:**
- **Privacy Flow System** ✅ **COMPLETAMENTE FUNCIONAL** - Flujo GDPR obligatorio
- **Course Announcement System** ✅ **COMPLETAMENTE FUNCIONAL** - Con envío real de PDF e imágenes via ngrok
- **Multimedia File Serving** ✅ **NUEVO - COMPLETAMENTE FUNCIONAL** - Archivos reales desde `resources/course_materials/`
- **Anti-Inventos System** ✅ **COMPLETAMENTE FUNCIONAL** - Con fix JSON parser
- **Advanced Personalization** ✅ **COMPLETAMENTE FUNCIONAL** - JSON parsing resuelto
- **Ad Flow System** ✅ **COMPLETAMENTE FUNCIONAL** - Base de datos integrada
- **Role Validation System** ✅ **IMPLEMENTADO Y VALIDADO** - Rechaza roles inválidos
- **Database Integration** ✅ **COMPLETAMENTE FUNCIONAL** - 100% datos dinámicos de BD
- **Intelligent Bonus System** ✅ **COMPLETAMENTE FUNCIONAL** - Bonos contextuales activados
- **Advisor Referral System** ✅ **COMPLETAMENTE FUNCIONAL** - Referencia automática a asesores

### **🔧 Últimas Mejoras Críticas Implementadas (1 Agosto 2025)**
- **✅ Multimedia File Sending**: RESUELTO - Envío real de PDF e imágenes via ngrok
- **✅ Course Information Fix**: RESUELTO - Muestra precio correcto $4500 MXN y información específica
- **✅ Twilio Character Limit**: RESUELTO - Mensajes optimizados bajo 1600 caracteres
- **✅ Processing Priority**: RESUELTO - Course Announcement tiene prioridad sobre Ad Flow
- **✅ Ngrok Integration**: IMPLEMENTADO - URLs públicas para multimedia con fallback automático

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

## Environment Variables Required

```env
# Twilio WhatsApp Integration
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token  
TWILIO_PHONE_NUMBER=your_whatsapp_number

# OpenAI Intelligence
OPENAI_API_KEY=your_openai_key

# Database (Optional)
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=your_supabase_key

# ✅ Ngrok for Multimedia (REQUIRED for file sending)
NGROK_URL=https://your-ngrok-url.ngrok-free.app

# Application Settings
APP_ENVIRONMENT=development
LOG_LEVEL=INFO

# Advisor Configuration
ADVISOR_PHONE_NUMBER=+5215614686075
ADVISOR_NAME=Especialista en IA
```

## Message Processing Priority System

The system processes messages with the following priority:

1. **PRIORIDAD 1**: Privacy Flow (mandatory GDPR consent)
2. **PRIORIDAD 1.5**: Course Announcements (#Experto_IA_GPT_Gemini, #ADSIM_05, etc.)
3. **PRIORIDAD 1.6**: Ad Flow (hashtag-based campaigns) 
4. **PRIORIDAD 1.7**: Welcome Flow (generic messages)
5. **PRIORIDAD 1.8**: Advisor Referral (contact requests)
6. **PRIORIDAD 2**: Intelligent Responses (OpenAI-powered)
7. **Fallback**: Basic context-aware responses

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

## Production Readiness

### ✅ Ready for Production
- **Core System**: 100% functional and validated
- **Database Integration**: Complete with fallback systems
- **Error Handling**: Comprehensive with graceful degradation
- **Security**: GDPR compliance and input validation
- **Performance**: Optimized message handling under Twilio limits
- **Multimedia Support**: Real file sending with ngrok integration

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

### Ngrok Requirements
- **Development**: Ngrok required for multimedia file testing
- **Production**: Replace with permanent domain solution
- **Fallback**: System works with text-only if multimedia unavailable

### Message Processing
- Privacy flow is mandatory and always executes first
- Course announcements have priority over ad flow
- All flows include comprehensive error handling
- System maintains conversation context across interactions

## Legacy Reference

The `legacy/` folder contains the complete Telegram implementation with 35+ conversion tools. Use as reference for migrating additional features to WhatsApp.

---

**Current Status**: ✅ **PRODUCTION READY** - Complete multimedia course announcement system functional
**Last Updated**: August 1, 2025
**Version**: 2.0 - Multimedia Course Announcements