# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "Brenda" - an intelligent WhatsApp sales bot for "Aprenda y Aplique IA" courses, migrated from Telegram to WhatsApp using Twilio. The project has successfully implemented a complete intelligent conversation system with Clean Architecture, OpenAI integration, PostgreSQL database support, and contextual course recommendations.

## Current Architecture Status

### ✅ IMPLEMENTED - Complete Intelligent System with Database Integration

The project now features a complete intelligent conversation system with Clean Architecture:

```
app/                           # COMPLETE CLEAN ARCHITECTURE
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
│       └── repositories/     # Data repositories
│           ├── course_repository.py      # Course data management
│           └── user_memory_repository.py # User memory in PostgreSQL
├── application/usecases/      # Use cases (business logic)
│   ├── send_hello_world.py   # Message sending use case
│   ├── process_incoming_message.py # Intelligent message processing
│   ├── manage_user_memory.py # Dual memory system (JSON + PostgreSQL)
│   ├── analyze_message_intent.py # Intent analysis with OpenAI
│   ├── generate_intelligent_response.py # Contextual responses
│   └── query_course_information.py # Course database queries
└── presentation/api/          # Presentation layer
    └── webhook.py            # FastAPI webhook with intelligence
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

#### Current Intelligent System (Fully Functional)
- **Configuration** (`app/config.py`) - Pydantic-based settings with all API credentials
- **Twilio Client** (`app/infrastructure/twilio/client.py`) - WhatsApp message sending/receiving
- **OpenAI Client** (`app/infrastructure/openai/client.py`) - GPT-4o-mini for intent analysis and responses
- **Database System** (`app/infrastructure/database/`) - PostgreSQL integration with async client
- **Course Repository** (`app/infrastructure/database/repositories/course_repository.py`) - Course data queries
- **Memory System** (`app/application/usecases/manage_user_memory.py`) - Dual JSON + PostgreSQL memory
- **Intent Analysis** (`app/application/usecases/analyze_message_intent.py`) - 11-category intent classification
- **Intelligent Responses** (`app/application/usecases/generate_intelligent_response.py`) - Contextual + course-enhanced responses
- **Webhook Handler** (`app/presentation/api/webhook.py`) - FastAPI with full intelligence + fallback layers
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

# Test database connection (optional)
python -c "from app.infrastructure.database.client import database_client; print('✅ Database client ready')"

# Test complete intelligent system
python test_intelligent_system.py
```

### Legacy System Commands (Reference)
```bash
# Legacy testing (if needed for reference)
python -c "from config.twilio_settings import *; print('Legacy config loaded')"
python -c "from services.twilio_service import TwilioService; t=TwilioService(); print('Legacy Twilio ready')"
```

## Migration Status

The project has successfully implemented a complete intelligent conversation system:

### ✅ COMPLETED - Intelligent System with Database Integration
- **Complete Clean Architecture** with clear separation of concerns
- **OpenAI GPT-4o-mini integration** for intent analysis and response generation
- **11-category intent classification** (exploration, buying signals, objections, etc.)
- **Dual memory system** - JSON local files + optional PostgreSQL integration
- **Course database integration** - PostgreSQL queries with course recommendations
- **Contextual responses** - Enhanced with course information based on user intent
- **Layered fallback system** - Works with/without database, with/without OpenAI
- **Robust webhook system** with signature verification and background processing
- **Comprehensive testing** - Scripts for basic, intelligent, and database integration testing

### ✅ COMPLETED - Advanced Functionality 
- **Intelligent message processing** - Understands user intent and context
- **Personalized responses** - Based on user memory, interests, and detected intent
- **Course recommendations** - Dynamic course suggestions from PostgreSQL database
- **User memory persistence** - Tracks names, roles, interests, pain points, and lead scoring
- **Multi-number support** with individual user contexts
- **Production-ready architecture** with proper error handling and logging

### 🔄 NEXT PHASE - Tool Integration Preparation
- **Conversation state management** - For complex multi-step flows
- **Tool registry system** - Framework for the 35+ conversion tools
- **Complete PostgreSQL migration** - Move all memory from JSON to database
- **Event system** - For tool coordination and automated triggers
- **Template engine enhancement** - For dynamic tool-generated content

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

# PostgreSQL Database (Optional - system works without it)
DATABASE_URL=postgresql://user:password@localhost:5432/database_name

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

## Legacy System Reference

The `legacy/` folder contains the complete, functional Telegram implementation with:
- 35+ working conversion tools
- Advanced AI conversation system
- Full PostgreSQL integration  
- Memory and lead scoring systems

Refer to `legacy/CLAUDE.md` for the complete Telegram implementation details. Use this as reference when adapting features for WhatsApp.

## Current Development Status

The WhatsApp bot now has a complete intelligent conversation system ready for production use:

### ✅ FULLY IMPLEMENTED - Intelligent Conversation System
1. **Reliable webhook message processing** - Handles all incoming WhatsApp messages
2. **Intelligent response generation** - OpenAI-powered with 11 intent categories
3. **Memory persistence** - Dual system (JSON + optional PostgreSQL)
4. **Course database integration** - Dynamic course recommendations from PostgreSQL
5. **Contextual conversations** - Remembers user info and adapts responses
6. **Production-ready architecture** - Clean Architecture with proper error handling

### 🔄 READY FOR NEXT PHASE - Tool Integration
The foundation is solid and ready for migrating the 35+ conversion tools from the legacy system. Before starting tool migration, consider implementing:

1. **Conversation state management** - For multi-step tool flows
2. **Tool registry framework** - Centralized tool activation and management
3. **Enhanced template system** - For dynamic tool-generated content
4. **Event coordination system** - For automated tool triggers and follow-ups

### 📋 Available Documentation
- **`CLAUDE.md`** - This comprehensive development guide
- **`README.md`** - Project overview and quick start
- **`TESTING_CLEAN_ARCHITECTURE.md`** - Testing the new architecture
- **`WEBHOOK_SETUP.md`** - Webhook configuration guide
- **`docs/DEVELOPMENT_PROGRESS.md`** - Detailed development progress
- **`docs/CLEAN_ARCHITECTURE.md`** - Architecture decisions and patterns

### 🧪 Testing Scripts Available
- **`test_hello_world_clean.py`** - Basic message sending test
- **`test_intelligent_system.py`** - Complete intelligent system test
- **`test_course_integration.py`** - Database integration test with course queries