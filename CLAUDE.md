# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "Brenda" - an intelligent WhatsApp sales bot for "Aprenda y Aplique IA" courses, migrated from Telegram to WhatsApp using Twilio. The project is currently implementing a Clean Architecture approach with a functional webhook system that responds automatically to WhatsApp messages.

## Current Architecture Status

### ✅ IMPLEMENTED - Clean Architecture (Current Working System)

The project now uses Clean Architecture with clear separation of concerns:

```
app/                           # NEW CLEAN ARCHITECTURE
├── config.py                  # Centralized configuration (Pydantic Settings)
├── domain/entities/           # Business entities
│   ├── message.py            # Message entities (incoming/outgoing)
│   └── user.py               # User entities with context
├── infrastructure/twilio/     # Infrastructure layer
│   └── client.py             # Specialized Twilio WhatsApp client
├── application/usecases/      # Use cases (business logic)
│   ├── send_hello_world.py   # Message sending use case
│   └── process_incoming_message.py # Incoming message processing
└── presentation/api/          # Presentation layer
    └── webhook.py            # FastAPI webhook handler
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

#### Current Clean Architecture (Functional)
- **Configuration** (`app/config.py`) - Pydantic-based settings with all API credentials
- **Twilio Client** (`app/infrastructure/twilio/client.py`) - WhatsApp message sending/receiving
- **Webhook Handler** (`app/presentation/api/webhook.py`) - FastAPI endpoint for Twilio webhooks
- **Message Processing** (`app/application/usecases/process_incoming_message.py`) - Auto-response logic
- **Entities** (`app/domain/entities/`) - Clean domain models for messages and users

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

# Start webhook server (auto-response "Hola")
python run_webhook_server.py

# In another terminal: expose webhook publicly
ngrok http 8000
# Configure the ngrok URL in Twilio Console
```

### Testing Current Implementation
```bash
# Test configuration
python -c "from app.config import settings; print('✅ Config loaded:', settings.twilio_phone_number)"

# Test Twilio client
python -c "from app.infrastructure.twilio.client import TwilioWhatsAppClient; print('✅ Twilio client ready')"
```

### Legacy System Commands (Reference)
```bash
# Legacy testing (if needed for reference)
python -c "from config.twilio_settings import *; print('Legacy config loaded')"
python -c "from services.twilio_service import TwilioService; t=TwilioService(); print('Legacy Twilio ready')"
```

## Migration Status

The project has successfully completed the foundational Clean Architecture implementation:

### ✅ COMPLETED - Clean Architecture Foundation
- **Robust configuration** with Pydantic Settings and environment validation
- **Functional webhook system** that receives WhatsApp messages via Twilio
- **Automatic "Hola" response** to any incoming WhatsApp message
- **Complete separation of concerns** following Clean Architecture principles
- **Structured logging** and comprehensive error handling
- **Webhook signature verification** for security
- **FastAPI-based presentation layer** with background processing

### ✅ COMPLETED - Basic Functionality 
- **Message sending** working (tested with hello world script)
- **Message receiving** working (webhook processes incoming messages)
- **Auto-response** working (responds "Hola" to any message)
- **Multi-number support** (any phone number can message the bot)

### 🔄 NEXT PHASE - Advanced Features
- **Message intent analysis** (understand what users are asking)
- **OpenAI integration** (intelligent responses instead of "Hola")
- **User memory system** (remember conversation context)
- **Migration of 35+ conversion tools** from legacy system

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
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token  
TWILIO_PHONE_NUMBER=your_whatsapp_number
OPENAI_API_KEY=your_openai_key
DATABASE_URL=your_postgresql_url
```

### Security Considerations
- Webhook authentication not yet implemented - needs Twilio signature validation
- Environment variables should never be committed
- All database queries should use parameterized statements

## Legacy System Reference

The `legacy/` folder contains the complete, functional Telegram implementation with:
- 35+ working conversion tools
- Advanced AI conversation system
- Full PostgreSQL integration  
- Memory and lead scoring systems

Refer to `legacy/CLAUDE.md` for the complete Telegram implementation details. Use this as reference when adapting features for WhatsApp.

## Current Development Priority

Focus on completing the basic WhatsApp conversation flow before adapting advanced features. The immediate goal is to establish:

1. Reliable webhook message processing
2. Basic agent response generation
3. Memory persistence integration
4. Simple conversation flows

Once the foundation is solid, gradually migrate the sophisticated tools and AI capabilities from the legacy system.