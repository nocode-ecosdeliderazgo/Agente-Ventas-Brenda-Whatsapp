# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "Brenda" - an intelligent WhatsApp sales bot for "Aprenda y Aplique IA" courses, specifically designed for **PyME leaders** (small and medium enterprise executives). The project has successfully implemented a complete intelligent conversation system with Clean Architecture, OpenAI integration, buyer persona-based prompts, and specialized templates for business executives.

### 🎯 TARGET AUDIENCE - PyME Leaders (Primary Buyer Personas)

The system is optimized for these **5 priority buyer personas**:

1. **Lucía CopyPro** - Marketing Digital Manager (Agencies)
2. **Marcos Multitask** - Operations Manager (Manufacturing PyMEs) 
3. **Sofía Visionaria** - CEO/Founder (Professional Services)
4. **Ricardo RH Ágil** - Head of Talent & Learning (Scale-ups)
5. **Daniel Data Innovador** - Senior Innovation/BI Analyst (Corporates)

**Business Focus**: 20-200 employee companies in services, B2B/B2C sectors needing competitive advantage through AI automation without technical teams.

## Current Architecture Status

### ✅ IMPLEMENTED - Complete Intelligent System with Privacy Flow and Bonus System

The project now features a complete intelligent conversation system with Clean Architecture, mandatory privacy consent flow, **intelligent bonus activation system**, and **real database integration**:

```
app/                           # COMPLETE CLEAN ARCHITECTURE WITH PRIVACY FLOW
├── config.py                  # Centralized configuration (Pydantic Settings)
├── domain/entities/           # Business entities
│   ├── message.py            # Message entities (incoming/outgoing)
│   ├── user.py               # User entities with context
│   └── course.py             # Course entities and models
├── infrastructure/            # Infrastructure layer
│   ├── twilio/client.py      # Specialized Twilio WhatsApp client
│   ├── openai/client.py      # OpenAI GPT-4o-mini integration
│   └── database/             # PostgreSQL database layer
│       ├── client.py         # Async PostgreSQL client with pooling
│       ├── estructura_db.sql # 🆕 Complete database schema
│       ├── elements_url_rows.sql # 🆕 Real multimedia resources data
│       ├── DATABASE_DOCUMENTATION.md # 🆕 Complete database documentation
│       └── repositories/     # Data repositories
│           ├── course_repository.py      # Course data management
│           └── user_memory_repository.py # User memory in PostgreSQL
├── application/usecases/      # Use cases (business logic)
│   ├── send_hello_world.py   # Message sending use case
│   ├── process_incoming_message.py # Intelligent message processing with privacy-first priority
│   ├── privacy_flow_use_case.py # GDPR-compliant mandatory privacy consent workflow
│   ├── manage_user_memory.py # Enhanced memory system with flow state management
│   ├── analyze_message_intent.py # Intent analysis with 17 PyME-specific categories
│   ├── generate_intelligent_response.py # Contextual responses for business executives
│   ├── bonus_activation_use_case.py # 🆕 Intelligent bonus activation system
│   ├── tool_activation_use_case.py # Business tool activation system
│   └── query_course_information.py # Course database queries
├── templates/                 # Message templates
│   └── privacy_flow_templates.py # Professional WhatsApp-optimized privacy messages
└── presentation/api/          # Presentation layer
    └── webhook.py            # FastAPI webhook with privacy-first processing

prompts/                      # 🆕 BUYER PERSONA-OPTIMIZED PROMPTS
└── agent_prompts.py         # Complete PyME-focused prompt system with ROI examples and bonus activation

# 🆕 NEW DOCUMENTATION FILES
SISTEMA_BONOS_INTELIGENTE.md # 🆕 Complete bonus system documentation
GUIA_PRUEBAS_SISTEMA_BONOS.md # 🆕 Step-by-step testing guide
SOLUCION_NO_DISPONIBLE.md    # 🆕 Problem resolution documentation
```

### 🔄 LEGACY SYSTEM (Reference Implementation)

The complete Telegram implementation is preserved in `legacy/` folder:
- `core/` - Main business logic (agents, intent analysis)
- `handlers/` - Webhook and conversation flow handlers  
- `services/` - External integrations (Twilio, OpenAI, database)
- `memory/` - User memory and persistence management
- `prompts/` - Centralized AI prompts and templates
- `config/` - Configuration and environment settings
- `docs/` - Documentation and migration guides

### Key Working Components

#### Current Intelligent System with Privacy Flow and Bonus System (Fully Functional)
- **Configuration** (`app/config.py`) - Pydantic-based settings with all API credentials
- **Twilio Client** (`app/infrastructure/twilio/client.py`) - WhatsApp message sending/receiving
- **OpenAI Client** (`app/infrastructure/openai/client.py`) - GPT-4o-mini for intent analysis and responses
- **Database System** (`app/infrastructure/database/`) - Supabase PostgreSQL integration with async client
- **Course Repository** (`app/infrastructure/database/repositories/course_repository.py`) - Course data queries
- **Enhanced Memory System** (`app/application/usecases/manage_user_memory.py`) - Flow state management with privacy workflow support
- **Lead Memory** (`memory/lead_memory.py`) - Enhanced with privacy flow fields and helper methods
- **Privacy Flow** (`app/application/usecases/privacy_flow_use_case.py`) - GDPR-compliant mandatory consent workflow
- **Privacy Templates** (`app/templates/privacy_flow_templates.py`) - Professional WhatsApp-optimized messages without buttons
- **Intent Analysis** (`app/application/usecases/analyze_message_intent.py`) - 17-category PyME-specific intent classification
- **Intelligent Responses** (`app/application/usecases/generate_intelligent_response.py`) - Executive-focused responses with ROI examples
- **🆕 Bonus Activation System** (`app/application/usecases/bonus_activation_use_case.py`) - Intelligent contextual bonus activation
- **🆕 Database Schema** (`app/infrastructure/database/estructura_db.sql`) - Complete PostgreSQL schema with courses and bonuses
- **🆕 Multimedia Resources** (`app/infrastructure/database/elements_url_rows.sql`) - Real video and document URLs per session
- **🆕 Database Documentation** (`app/infrastructure/database/DATABASE_DOCUMENTATION.md`) - Complete database structure documentation
- **Buyer Persona System** (`prompts/agent_prompts.py`) - Complete prompt system optimized for PyME leaders with bonus activation
- **Business Templates** (`prompts/agent_prompts.py:WhatsAppBusinessTemplates`) - ROI-focused message templates
- **Webhook Handler** (`app/presentation/api/webhook.py`) - Privacy-first processing before any other interactions
- **Entities** (`app/domain/entities/`) - Complete domain models for messages, users, and courses

#### Legacy Reference (Complete Implementation)
- **WhatsApp Agent** (`core/whatsapp_agent.py`) - Main conversation processor
- **Webhook Handler** (`handlers/whatsapp_webhook.py`) - Basic webhook receiver  
- **Twilio Service** (`services/twilio_service.py`) - WhatsApp message sending
- **Lead Memory** (`memory/lead_memory.py`) - User context persistence
- **Intent Analyzer** (`core/intent_analyzer.py`) - Message intent classification

## Development Commands

### Environment Setup (Clean Architecture)
```bash
# Install dependencies for new architecture
pip install -r requirements-clean.txt

# Configure environment
cp .env.example .env
# Edit .env with your Twilio credentials (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, etc.)
```

### Running the Current System
```bash
# Test message sending (Hello World)
python test_hello_world_clean.py

# Test intelligent system (OpenAI + memory + intent analysis)
python test_intelligent_system.py

# Test complete system with course database integration
python test_course_integration.py

# Start webhook server (intelligent responses)
python run_webhook_server.py

# In another terminal: expose webhook publicly
ngrok http 8000
# Configure the ngrok URL in Twilio Console
```

### Testing Current Implementation
```bash
# Test basic configuration
python -c "from app.config import settings; print('✅ Config loaded:', settings.twilio_phone_number)"

# Test OpenAI integration
python -c "from app.infrastructure.openai.client import OpenAIClient; print('✅ OpenAI client ready')"

# Test Supabase database connection
python test_supabase_connection.py

# Test complete intelligent system
python test_intelligent_system.py

# Test enhanced memory system with conversation flows
python test_memory_system.py

# Test privacy flow logic (standalone)
python test_integration_logic_only.py

# Test complete privacy flow integration
python test_integrated_privacy_flow.py

# Test buyer persona prompt system
python prompts/agent_prompts.py
```

### Legacy System Commands (Reference)
```bash
# Legacy testing (if needed for reference)
python -c "from config.twilio_settings import *; print('Legacy config loaded')"
python -c "from services.twilio_service import TwilioService; t=TwilioService(); print('Legacy Twilio ready')"
```

## Migration Status

The project has successfully implemented a complete intelligent conversation system:

### ✅ COMPLETED - PyME-Focused Buyer Persona System

The system now features **specialized prompts and templates** designed specifically for PyME leaders:

#### **Buyer Persona-Optimized Components:**
- **SYSTEM_PROMPT** - Consultive approach for business executives (30-45 years, 8-15 years experience)
- **17 Intent Categories** - Business-specific classifications (ROI exploration, budget concerns, technical team limitations)
- **Executive Templates** - ROI-focused messaging with quantified benefits (hours saved, % efficiency gains)
- **Business Context Extraction** - Company size, sector, operational pain points, automation needs
- **Persona Matching** - Automatic detection and response adaptation based on role and industry

#### **ROI-Focused Messaging Examples:**
- **Lucía CopyPro (Marketing):** "$300 ahorro por campaña → Recuperas inversión en 2 campañas"
- **Marcos Multitask (Operations):** "$2,000 ahorro mensual → ROI del 400% en primer mes" 
- **Sofía Visionaria (CEO):** "$27,600 ahorro anual vs contratar analista → ROI del 1,380% anual"

### ✅ COMPLETED - Intelligent System with Mandatory Privacy Flow
- **Complete Clean Architecture** with clear separation of concerns
- **Mandatory Privacy Consent Flow** - GDPR-compliant first interaction workflow
- **WhatsApp Name Extraction** - Automatic extraction from ProfileName metadata with fallback collection
- **Professional Privacy Messages** - Template-based, WhatsApp-optimized without buttons or inline keyboards
- **User Journey Management** - 5-stage flow: first_contact → privacy_flow → course_selection → sales_agent → converted
- **Enhanced Memory System** - Flow state management with privacy workflow support
- **OpenAI GPT-4o-mini integration** for PyME-focused intent analysis and executive response generation
- **17-category PyME-specific intent classification** (sector exploration, ROI concerns, technical team objections, etc.)
- **Course database integration** - Supabase PostgreSQL queries with course recommendations (optional)
- **Contextual responses** - Enhanced with course information based on user intent
- **Privacy-first webhook system** - Processes privacy before any other interactions
- **Layered fallback system** - Works with/without database, with/without OpenAI
- **Comprehensive testing** - Privacy flow logic, integration, and edge case testing

### ✅ COMPLETED - Advanced Privacy and Personalization Functionality
- **Mandatory privacy workflow** - No interactions allowed before consent acceptance
- **Professional consent messaging** - GDPR-compliant, WhatsApp-optimized templates
- **Intelligent name extraction** - From WhatsApp metadata (ProfileName) with personalized fallback collection
- **User journey orchestration** - State machine managing conversation flow progression
- **Privacy state persistence** - Tracks consent status, flow progress, and user preferences
- **Enhanced user memory system** - Complete user data persistence with privacy workflow support
- **First interaction detection** - Automatic identification of new vs returning users
- **Sales readiness detection** - Intelligent determination when users are ready for sales agent
- **Conversation context generation** - Rich context summaries for AI agents
- **Multi-stage user journey** - 5 distinct stages with automatic transitions
- **Production-ready architecture** - Robust error handling and comprehensive logging

### 🔄 NEXT PHASE - Tool Integration and Advanced Features
- **Course selection system** - Interactive course recommendation and selection based on user interests
- **Sales agent integration** - Enhanced intelligent sales conversations with dynamic course listings
- **Tool registry system** - Framework for the 35+ conversion tools from legacy system
- **Event coordination system** - For automated tool triggers and follow-ups
- **Template engine enhancement** - For dynamic tool-generated content
- **Complete Supabase migration** - Move all memory from JSON to database
- **Advanced analytics** - Privacy consent rates, conversation flow analysis

### 📁 LEGACY REFERENCE - Telegram System
- Complete Telegram bot implementation in `legacy/` folder
- 35+ working conversion tools for lead generation
- Advanced AI conversation system with OpenAI GPT-4o-mini
- PostgreSQL integration with user memory and lead scoring
- Can be used as reference for migrating features to WhatsApp

## Important Implementation Notes

### WhatsApp vs Telegram Differences
- WhatsApp requires pre-approved templates for outbound messages to new users
- No inline buttons - use simple text responses and menus
- Multimedia support is more limited than Telegram
- Webhook must be publicly accessible (use ngrok for development)

### Environment Variables Required
```env
# Twilio WhatsApp Integration
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token  
TWILIO_PHONE_NUMBER=your_whatsapp_number

# OpenAI Intelligence
OPENAI_API_KEY=your_openai_key

# Supabase Database (Optional - system works without it)
DATABASE_URL=postgresql://postgres.your_ref:your_password@aws-0-us-east-2.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://your_ref.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Application Settings
APP_ENVIRONMENT=development
LOG_LEVEL=INFO
WEBHOOK_VERIFY_SIGNATURE=true
```

### Security Features Implemented
- **Webhook signature verification** - Validates requests from Twilio
- **Environment variable protection** - All secrets in .env file
- **Parameterized database queries** - Protection against SQL injection
- **Input validation** - Pydantic models validate all data
- **Error boundary isolation** - Failures don't crash the system

## Supabase Integration

The system now includes full Supabase PostgreSQL integration for scalable database operations:

### Supabase Configuration

#### **Environment Variables**
```env
# Supabase Database Connection
DATABASE_URL=postgresql://postgres.your_ref:your_password@aws-0-us-east-2.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://your_ref.supabase.co  
SUPABASE_KEY=your_supabase_anon_key
```

#### **Database Client** (`app/infrastructure/database/client.py`)
- **Async Connection Pool** - Optimized for high-performance concurrent operations
- **Health Check System** - Real-time database connectivity monitoring
- **Transaction Support** - ACID compliance for complex operations
- **Error Handling** - Robust fallback and retry mechanisms
- **Query Logging** - Detailed debugging and performance monitoring

### Supabase Testing

#### **Comprehensive Test Suite** (`test_supabase_connection.py`)
The system includes a complete test suite for Supabase functionality:

1. **Basic Connection Test** - Verifies database connectivity
2. **Health Check Test** - Monitors database status
3. **Query Execution Test** - PostgreSQL version, current time, database info
4. **Supabase Features Test** - Extensions (uuid-ossp, pgcrypto, etc.), timezone config
5. **Course System Test** - Verifies course and user memory tables
6. **Connection Pooling Test** - Tests concurrent connections and performance

#### **Running Supabase Tests**
```bash
# Complete Supabase functionality test
python test_supabase_connection.py

# Expected output:
# ✅ ÉXITO: Conexión establecida con Supabase
# ✅ ÉXITO: Health check OK  
# ✅ Versión de PostgreSQL: PostgreSQL 15.x...
# ✅ Encontradas X tablas de usuario
# 🎉 ¡TODAS LAS PRUEBAS PASARON! Supabase está funcionando correctamente.
```

### Database Architecture

#### **Tables and Schema**
- **`courses`** - Course catalog with pricing and descriptions
- **`user_memory`** - User conversation state and preferences (future implementation)
- **Extensions** - uuid-ossp, pgcrypto for advanced functionality
- **Indexing** - Optimized queries for conversation flows

#### **Migration Strategy**
- **Phase 1** ✅ - Database client and testing infrastructure
- **Phase 2** 🔄 - User memory migration from JSON to Supabase
- **Phase 3** 🔄 - Course data integration and management
- **Phase 4** 🔄 - Analytics and conversation flow tracking

### Performance Features

- **Connection Pooling** - 1-10 concurrent connections with automatic scaling
- **Query Optimization** - JIT disabled for simple queries, optimal performance
- **Async Operations** - Non-blocking database operations
- **Transaction Management** - Atomic operations for data consistency
- **Error Recovery** - Graceful degradation when database unavailable

## Privacy Flow Architecture

The system implements a mandatory privacy consent workflow that executes before any other interactions:

### Privacy Flow Components

#### Privacy Flow Use Case (`app/application/usecases/privacy_flow_use_case.py`)
```python
class PrivacyFlowUseCase:
    async def handle_privacy_flow(self, user_id: str, incoming_message: IncomingMessage):
        """Orchestrates the complete privacy consent flow"""
        
    def should_handle_privacy_flow(self, user_memory: LeadMemory) -> bool:
        """Determines if privacy flow should be activated"""
        
    async def _initiate_privacy_flow(self, user_id: str, incoming_message: IncomingMessage):
        """Initiates privacy consent request with WhatsApp name extraction"""
        
    async def _handle_privacy_response(self, user_id: str, incoming_message: IncomingMessage):
        """Processes privacy acceptance/rejection responses"""
        
    async def _handle_name_response(self, user_id: str, incoming_message: IncomingMessage):
        """Processes user name collection after privacy acceptance"""
```

#### Privacy Templates (`app/templates/privacy_flow_templates.py`)
- **WhatsApp-optimized messaging** - No buttons, professional text-based responses
- **GDPR-compliant consent** - Clear data processing explanation
- **Name extraction** - Automatic ProfileName extraction with fallback collection
- **Response validation** - Intelligent acceptance/rejection detection
- **Professional messaging** - Personalized, friendly, and compliant

#### Enhanced Memory System (`memory/lead_memory.py`)
```python
@dataclass
class LeadMemory:
    # Privacy flow management
    privacy_accepted: bool = False
    privacy_requested: bool = False
    current_flow: str = "none"  # none, privacy, course_selection, sales_conversation
    flow_step: int = 0
    waiting_for_response: str = ""  # privacy_acceptance, user_name
    
    # Helper methods for privacy flow
    def is_first_interaction(self) -> bool
    def needs_privacy_flow(self) -> bool
    def is_ready_for_sales_agent(self) -> bool
```

### Privacy Flow Sequence

1. **First Interaction Detection** - Automatic identification of new users
2. **WhatsApp Name Extraction** - Extract ProfileName from Twilio webhook metadata
3. **Privacy Consent Request** - Professional GDPR-compliant message
4. **Response Processing** - Intelligent acceptance/rejection detection
5. **Name Collection** - Personalized name request after acceptance
6. **Flow Completion** - Transition to sales agent ready state

### Privacy Flow Testing

The system includes comprehensive privacy flow testing:
- **`test_integration_logic_only.py`** - Complete logic validation without external dependencies
- **`test_integrated_privacy_flow.py`** - Full integration test with webhook simulation
- **Edge case handling** - User rejection, unclear responses, invalid names

## Enhanced Memory System Architecture

The memory system has been enhanced with privacy flow management for robust conversation state tracking:

### Memory Structure (`memory/lead_memory.py`)
```python
@dataclass
class LeadMemory:
    # Basic user info
    user_id: str
    name: str
    role: str
    
    # Conversation flow management
    stage: str  # first_contact, privacy_flow, course_selection, sales_agent, converted
    current_flow: str  # none, privacy, course_selection, sales_conversation
    flow_step: int  # current step within flow
    waiting_for_response: str  # expected response type
    
    # Privacy and interaction tracking
    privacy_accepted: bool
    privacy_requested: bool
    interaction_count: int
    
    # User interests and behavior
    interests: List[str]
    pain_points: List[str]
    buying_signals: List[str]
    lead_score: int
    
    # Helper methods for flow detection
    def is_first_interaction(self) -> bool
    def needs_privacy_flow(self) -> bool
    def is_ready_for_sales_agent(self) -> bool
    def get_conversation_context(self) -> str
```

### Flow Management Use Cases (`app/application/usecases/manage_user_memory.py`)
- `start_privacy_flow()` - Initiates privacy acceptance workflow
- `accept_privacy()` - Marks privacy as accepted and transitions to course selection
- `start_sales_agent_flow()` - Activates intelligent sales conversation
- `update_user_role()` - Updates user profession/role
- `update_user_name()` - Updates user's preferred name after privacy acceptance
- `set_waiting_for_response()` - Sets expected response type
- `advance_flow_step()` - Moves to next step in current flow

### Webhook Processing Priority (`app/application/usecases/process_incoming_message.py`)
The webhook processes messages with the following priority:

1. **PRIORITY 1: Privacy Flow** - Mandatory privacy consent before any other interactions
   ```python
   if self.privacy_flow_use_case.should_handle_privacy_flow(user_memory):
       privacy_result = await self.privacy_flow_use_case.handle_privacy_flow(user_id, incoming_message)
       return privacy_result  # Exit early if in privacy flow
   ```

2. **PRIORITY 2: Intelligent Response** - OpenAI-powered responses (after privacy acceptance)
3. **PRIORITY 3: Basic Fallback** - Simple context-aware responses

### Memory Testing
The system includes comprehensive testing via `test_memory_system.py`:
- First interaction detection
- Privacy flow management
- User information persistence
- PyME business context extraction
- Buyer persona matching and ROI calculation
- Sales agent readiness assessment
- JSON persistence and recovery
- Backward compatibility validation

## Buyer Persona System Architecture

The system now implements a sophisticated buyer persona detection and response system optimized for PyME leaders:

### Buyer Persona Components (`prompts/agent_prompts.py`)

#### **1. Executive-Focused SYSTEM_PROMPT**
```python
SYSTEM_PROMPT = """
Eres Brenda, asesora especializada en IA aplicada para PyMEs de "Aprenda y Aplique IA". 
Tu objetivo es ayudar a líderes de innovación (gerentes, directores, fundadores) de empresas 
pequeñas y medianas a descubrir cómo la IA puede darles ventaja competitiva real, reducir 
costos operativos y automatizar procesos sin necesidad de equipos técnicos.

CONTEXTO DEL BUYER PERSONA - LÍDER DE INNOVACIÓN PYME:
- Cargo: Gerente/Director de Operaciones, Marketing o Transformación Digital
- Empresa: PyME servicios 20-200 empleados (agencias, consultoría, comercio, salud, educación)
- Edad: 30-45 años, domina herramientas digitales básicas pero poca práctica real en IA
- Presiones: Aumentar productividad sin crecer plantilla, generar contenido más rápido, sistematizar decisiones
"""
```

#### **2. 17-Category PyME Intent Classification**
- **EXPLORATION_SECTOR** - Aplicaciones para sector específico
- **EXPLORATION_ROI** - Retorno de inversión y casos de éxito
- **OBJECTION_BUDGET_PYME** - Preocupación por presupuesto limitado
- **OBJECTION_TECHNICAL_TEAM** - Sin equipo técnico, temen complejidad
- **AUTOMATION_REPORTS** - Automatizar reportes y dashboards
- **AUTOMATION_CONTENT** - Acelerar creación de contenido/marketing
- **BUYING_SIGNALS_EXECUTIVE** - Señales de decisión corporativa
- **PILOT_REQUEST** - Solicita proyecto piloto
- **TEAM_TRAINING** - Capacitación para equipo
- **STRATEGIC_CONSULTATION** - Asesoría estratégica de IA

#### **3. Business Context Extraction**
```python
# Extrae información empresarial específica:
{
    "company_info": {
        "sector": "sector/industria identificada",
        "size": "tamaño empresa",
        "area_responsibility": "área de responsabilidad del líder"
    },
    "automation_needs": {
        "report_types": ["reportes que crea manualmente"],
        "content_creation": ["tipos de contenido que necesita"],
        "process_optimization": ["procesos que quiere mejorar"],
        "strategic_goals": ["objetivos empresariales mencionados"]
    },
    "buyer_persona_match": "lucia_copypro|marcos_multitask|sofia_visionaria|ricardo_rh|daniel_data"
}
```

#### **4. ROI-Focused WhatsApp Templates**
```python
class WhatsAppBusinessTemplates:
    def business_price_objection_response(course_price, role, sector):
        # Ejemplos específicos por buyer persona:
        # Lucía CopyPro: $300 ahorro por campaña
        # Marcos Multitask: $2,000 ahorro mensual  
        # Sofía Visionaria: $27,600 ahorro anual
```

### Buyer Persona Usage

#### **Activating Buyer Persona Detection:**
```python
from prompts.agent_prompts import get_intent_analysis_prompt, WhatsAppBusinessTemplates

# El sistema automáticamente detecta y clasifica por buyer persona
intent_analysis = await analyze_message_intent(user_message, user_memory)
# Retorna: buyer_persona_match, business_pain_detected, roi_opportunity

# Las plantillas se adaptan automáticamente
response = WhatsAppBusinessTemplates.business_price_objection_response(
    course_price=497, 
    role="Director de Marketing", 
    sector="agencia"
)
```

## Legacy System Reference

The `legacy/` folder contains the complete, functional Telegram implementation with:
- 35+ working conversion tools
- Advanced AI conversation system
- Full Supabase PostgreSQL integration  
- Memory and lead scoring systems

Refer to `legacy/CLAUDE.md` for the complete Telegram implementation details. Use this as reference when adapting features for WhatsApp.

## Current Development Status

The WhatsApp bot now has a complete intelligent conversation system ready for production use:

### ✅ FULLY IMPLEMENTED - Intelligent Conversation System with Complete Privacy Flow and Bonus System
1. **Privacy-first webhook processing** - Mandatory privacy consent before any other interactions
2. **GDPR-compliant consent workflow** - Professional privacy acceptance with WhatsApp-optimized messages
3. **WhatsApp name extraction** - Automatic extraction from ProfileName metadata with personalized fallback
4. **🆕 Complete user information collection** - Name and role/cargo collection with validation
5. **Intelligent response generation** - OpenAI-powered with 11 intent categories (after privacy acceptance)
6. **Enhanced memory persistence** - Robust JSON-based system with privacy flow state tracking
7. **User journey management** - 5-stage automatic flow detection and management
8. **First interaction detection** - Smart identification of new vs returning users
9. **Privacy flow orchestration** - Complete structured privacy acceptance workflow
10. **Sales readiness assessment** - Intelligent determination of when users are ready for sales
11. **Contextual conversations** - Rich memory-based personalized responses by user role
12. **Production-ready architecture** - Clean Architecture with comprehensive error handling
13. **🆕 Role-based personalization** - Responses adapted to user's professional role
14. **🆕 Intelligent bonus activation system** - Contextual bonus presentation based on user role and conversation
15. **🆕 Real database integration** - Supabase PostgreSQL with course data, bonuses, and multimedia resources
16. **🆕 SOLUCIÓN DEFINITIVA AL PROBLEMA DE FIRMA INVÁLIDA** - Webhook funcionando perfectamente sin errores de autenticación
17. **🆕 Sistema de bonos inteligente** - Activación contextual de bonos basada en rol y conversación

### 🔄 READY FOR NEXT PHASE - Tool Integration with Supabase
The foundation is solid with Supabase integration and ready for migrating the 35+ conversion tools from the legacy system. Before starting tool migration, consider implementing:

1. **Conversation state management** - For multi-step tool flows stored in Supabase
2. **Tool registry framework** - Centralized tool activation and management with database persistence
3. **Enhanced template system** - For dynamic tool-generated content
4. **Event coordination system** - For automated tool triggers and follow-ups with database logging

### 📋 Available Documentation

#### **Core Documentation**
- **`CLAUDE.md`** - This comprehensive development guide (UPDATED with buyer personas, bonus system, and signature fix)
- **`README.md`** - Project overview with PyME focus and ROI examples
- **`BUYER_PERSONAS_ADAPTATION.md`** - Complete PyME buyer persona system documentation
- **`PROMPTS_SYSTEM_GUIDE.md`** - Detailed guide for using business-optimized prompts
- **`SOLUCION_NO_DISPONIBLE.md`** - Complete documentation of the "No disponible" problem solution
- **`app/infrastructure/database/DATABASE_DOCUMENTATION.md`** - Complete database structure and bonus system documentation
- **`SISTEMA_BONOS_INTELIGENTE.md`** - Complete bonus system documentation
- **`GUIA_PRUEBAS_SISTEMA_BONOS.md`** - Step-by-step testing guide for bonus system

#### **Technical Documentation** 
- **`TESTING_CLEAN_ARCHITECTURE.md`** - Testing the new architecture
- **`WEBHOOK_SETUP.md`** - Webhook configuration guide
- **`docs/DEVELOPMENT_PROGRESS.md`** - Detailed development progress
- **`docs/CLEAN_ARCHITECTURE.md`** - Architecture decisions and patterns

### 🧪 Testing Scripts Available
- **`test_hello_world_clean.py`** - Basic message sending test
- **`test_intelligent_system.py`** - Complete intelligent system test
- **`test_memory_system.py`** - Enhanced memory system and conversation flow test
- **`test_integration_logic_only.py`** - Privacy flow logic validation (no external dependencies)
- **`test_integrated_privacy_flow.py`** - Complete privacy flow integration test with webhook simulation
- **`test_course_integration.py`** - Database integration test with course queries
- **`test_supabase_connection.py`** - Comprehensive Supabase connection and functionality test