# Database Integration Guide

This document describes the PostgreSQL database integration implemented in the WhatsApp bot project.

## Overview

The bot now supports dual-mode operation:
- **JSON Mode**: Local file-based memory (original system)
- **PostgreSQL Mode**: Full database integration with course recommendations
- **Hybrid Mode**: Memory in JSON + course data from PostgreSQL

## Database Structure

### Existing Course Tables (from `app/infrastructure/database/estructura_db.sql`)

```sql
-- Main courses table
ai_courses (
    id_course UUID PRIMARY KEY,
    Name VARCHAR,
    Short_description VARCHAR,
    Long_descrption VARCHAR,  -- Note: Typo in original schema
    session_count SMALLINT,
    Price VARCHAR,
    Currency VARCHAR,
    level VARCHAR,
    modality VARCHAR,
    -- ... other fields
)

-- Course sessions
ai_course_session (
    id_session UUID PRIMARY KEY,
    id_course_fk UUID REFERENCES ai_courses(id_course),
    session_index SMALLINT,
    title VARCHAR,
    objective VARCHAR,
    -- ... other fields
)

-- Session activities  
ai_tema_activity (
    id_activity UUID PRIMARY KEY,
    id_course_fk UUID REFERENCES ai_courses(id_course),
    id_session_fk UUID REFERENCES ai_course_session(id_session),
    item_type TEXT,
    title_item VARCHAR,
    -- ... other fields
)

-- Course bonuses
bond (
    id_bond BIGINT PRIMARY KEY,
    id_courses_fk UUID REFERENCES ai_courses(id_course),
    content TEXT,
    type_bond VARCHAR,
    -- ... other fields
)
```

### New User Memory Table (auto-created)

```sql
-- User memory table (created automatically)
user_memory (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    role VARCHAR(255),
    interests TEXT[],
    pain_points TEXT[],
    lead_score INTEGER DEFAULT 0,
    interaction_count INTEGER DEFAULT 0,
    first_interaction_at TIMESTAMP WITH TIME ZONE,
    last_interaction_at TIMESTAMP WITH TIME ZONE,
    message_history JSONB DEFAULT '[]'::jsonb,
    additional_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## Architecture Components

### 1. Database Client (`app/infrastructure/database/client.py`)
- **Async PostgreSQL client** with connection pooling
- **Connection management** with automatic retries
- **Transaction support** for complex operations
- **Health checking** and error handling

```python
# Example usage
from app.infrastructure.database.client import database_client

await database_client.connect()
results = await database_client.execute_query(
    "SELECT * FROM ai_courses WHERE level = $1", 
    "principiante"
)
```

### 2. Course Repository (`app/infrastructure/database/repositories/course_repository.py`)
- **Course queries** with filtering and search
- **Course recommendations** based on user interests
- **Statistics and analytics** for course catalog
- **WhatsApp-optimized formatting** for course information

Key methods:
- `get_all_courses(filters, limit)` - Filtered course listing
- `search_courses_by_text(search_text)` - Text-based search
- `get_course_complete_info(course_id)` - Complete course details
- `get_recommended_courses(user_interests, user_level)` - Personalized recommendations

### 3. User Memory Repository (`app/infrastructure/database/repositories/user_memory_repository.py`)
- **PostgreSQL-based user memory** (alternative to JSON files)
- **User analytics** and lead scoring
- **Message history** stored as JSONB
- **Migration helpers** from JSON to PostgreSQL

Key methods:
- `save_user_memory(user_memory)` - Upsert user data
- `load_user_memory(user_id)` - Retrieve user context
- `get_high_score_leads(min_score)` - Lead analytics
- `get_user_statistics()` - User engagement metrics

### 4. Course Query Use Case (`app/application/usecases/query_course_information.py`)
- **Business logic** for course queries
- **Recommendation engine** based on user context
- **Search functionality** with keyword matching
- **Course catalog management**

Key methods:
- `search_courses_by_keyword(keyword)` - Smart course search
- `get_recommended_courses(user_interests, user_level)` - Personalized suggestions
- `get_course_catalog_summary()` - Overview statistics
- `format_course_for_chat(course)` - WhatsApp formatting

## Enhanced Intelligence Integration

### Intent-Based Course Recommendations

The intelligent response system now automatically includes course information when relevant:

```python
# Categories that trigger course recommendations
course_relevant_categories = [
    'EXPLORATION',        # User exploring options
    'BUYING_SIGNALS',     # Ready to purchase signals
    'GENERAL_QUESTION',   # General inquiries
    'AUTOMATION_NEED',    # Specific automation needs
    'PROFESSION_CHANGE'   # Career change discussions
]
```

### Dynamic Response Enhancement

When users ask about courses or show buying intent, responses are automatically enhanced with:
- **Relevant course suggestions** from the database
- **Personalized recommendations** based on user interests
- **Course details** formatted for WhatsApp
- **Contextual information** about pricing, duration, level

Example enhanced response:
```
¡Excelente que estés explorando, María! 🎯

Te muestro nuestros cursos más populares:

**1. 📚 Automatización con IA para Marketing
📝 Aprende a automatizar campañas y análisis de datos
📊 Nivel: intermedio | 💻 Modalidad: online | 🗓️ Sesiones: 8
💰 Precio: $299 USD**

**2. 📚 IA para Creación de Contenido
📝 Domina las herramientas de IA para contenido digital
📊 Nivel: principiante | 💻 Modalidad: híbrido | 🗓️ Sesiones: 6
💰 Precio: $199 USD**

¿Alguno de estos cursos te llama la atención?
```

## Configuration and Setup

### Environment Variables

```env
# Required for Twilio and OpenAI
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_whatsapp_number
OPENAI_API_KEY=your_openai_key

# Optional - system works without database
DATABASE_URL=postgresql://user:password@localhost:5432/database_name
```

### Fallback Behavior

The system is designed with robust fallback:

1. **Full System**: OpenAI + PostgreSQL + Course recommendations
2. **AI Only**: OpenAI + JSON memory (no course database)
3. **Basic Mode**: Template responses only (no AI, no database)

### Dependencies

```bash
# Added to requirements-clean.txt
asyncpg>=0.28.0  # PostgreSQL async client
```

## Testing

### Database Integration Test
```bash
# Test complete system with database
python test_course_integration.py
```

This script tests:
- Database connection
- Course queries and recommendations
- Enhanced conversation flow
- Fallback behavior when database unavailable

### Manual Testing Commands

```bash
# Test database connection
python -c "
from app.infrastructure.database.client import database_client
import asyncio
asyncio.run(database_client.connect())
print('Database connected')
"

# Test course queries
python -c "
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
import asyncio

async def test():
    query_use_case = QueryCourseInformationUseCase()
    await query_use_case.initialize()
    courses = await query_use_case.search_courses_by_keyword('IA')
    print(f'Found {len(courses)} courses')

asyncio.run(test())
"
```

## Migration Notes

### From JSON to PostgreSQL Memory

Currently, the system uses both:
- **JSON files** for backward compatibility
- **PostgreSQL** for advanced features

Future migration path:
1. **Phase 1**: Dual mode (current)
2. **Phase 2**: Gradual PostgreSQL migration
3. **Phase 3**: Full PostgreSQL with JSON backup

### Course Data Requirements

For optimal performance, ensure your `ai_courses` table contains:
- **Courses with clear names and descriptions**
- **Appropriate level categorization** (principiante, intermedio, avanzado)
- **Modality information** (online, presencial, híbrido)
- **Price and currency data**

## Security Considerations

### Database Security
- **Parameterized queries** prevent SQL injection
- **Connection pooling** with timeout management
- **Error boundary isolation** prevents system crashes
- **Input validation** through Pydantic models

### Data Privacy
- **User memory encryption** can be added
- **GDPR compliance** through user data deletion methods
- **Audit logging** for data access patterns

## Performance Optimization

### Database Performance
- **Connection pooling** reduces connection overhead
- **Async operations** prevent blocking
- **Query optimization** with proper indexing
- **Fallback caching** for reliability

### Recommended Indexes
```sql
-- Indexes for optimal performance
CREATE INDEX idx_ai_courses_level ON ai_courses(level);
CREATE INDEX idx_ai_courses_modality ON ai_courses(modality);
CREATE INDEX idx_ai_courses_name_search ON ai_courses USING gin(to_tsvector('spanish', Name));
CREATE INDEX idx_user_memory_lead_score ON user_memory(lead_score);
CREATE INDEX idx_user_memory_last_interaction ON user_memory(last_interaction_at);
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check DATABASE_URL format
   - Verify PostgreSQL is running
   - Test network connectivity

2. **Course Recommendations Empty**
   - Verify ai_courses table has data
   - Check course data formatting
   - Review user interests extraction

3. **Memory Not Persisting**
   - Check database write permissions
   - Verify user_memory table creation
   - Review error logs for transaction failures

### Debug Commands

```bash
# Check database health
python -c "
from app.infrastructure.database.client import database_client
import asyncio
print('Health check:', asyncio.run(database_client.health_check()))
"

# Verify course data
python -c "
from app.infrastructure.database.repositories.course_repository import CourseRepository
import asyncio

async def check():
    repo = CourseRepository()
    stats = await repo.get_course_statistics()
    print('Course stats:', stats)

asyncio.run(check())
"
```