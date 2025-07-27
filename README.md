# Bot de Ventas Inteligente (Brenda) - WhatsApp (Twilio)

## 🎯 Objetivo
Migrar y modernizar el bot de ventas "Brenda" para operar 100% sobre WhatsApp usando Twilio, con arquitectura modular, escalable y lista para producción.

## 🚀 Estado Actual del Proyecto

### ✅ COMPLETADO - Sistema Inteligente con Base de Datos
- **Configuración robusta** con Pydantic Settings
- **Webhook funcional** que recibe mensajes de WhatsApp
- **Sistema de memoria dual** - JSON local + PostgreSQL opcional
- **Base de datos de cursos** - consulta inteligente de información de cursos
- **Análisis de intención** con OpenAI GPT-4o-mini
- **Respuestas contextualizadas** con información específica de cursos
- **Arquitectura escalable** con Clean Architecture
- **Logging estructurado** y manejo de errores
- **Verificación de firmas** de webhook para seguridad
- **Fallback en capas** - funciona sin PostgreSQL y/o sin OpenAI

### 🔄 PRÓXIMO - Componentes Legacy (Referencia)
- 35+ herramientas de conversión (recursos, demos, bonos, cierre, etc.)
- Activación inteligente de herramientas según intención
- Base de datos PostgreSQL (async)
- Flujos de conversación: Ads, cursos, contacto, FAQ
- Lead scoring avanzado y seguimiento automático
- Validación anti-alucinación

## 🏗️ Arquitectura Implementada

### Nueva Estructura (Clean Architecture)
```
app/                           # ✅ NUEVA ARQUITECTURA LIMPIA
├── config.py                  # ✅ Configuración centralizada (Pydantic)
├── domain/entities/           # ✅ Entidades de negocio
│   ├── message.py            # ✅ Mensajes (entrantes/salientes)
│   └── user.py               # ✅ Usuarios y contexto
├── infrastructure/            # ✅ Capa de infraestructura
│   ├── twilio/client.py      # ✅ Cliente Twilio especializado
│   ├── openai/client.py      # ✅ Cliente OpenAI GPT-4o-mini
│   └── database/             # ✅ Sistema de base de datos
│       ├── client.py         # ✅ Cliente PostgreSQL asíncrono
│       └── repositories/     # ✅ Repositorios de datos
│           ├── course_repository.py      # ✅ Gestión de cursos
│           └── user_memory_repository.py # ✅ Memoria de usuarios
├── application/usecases/      # ✅ Casos de uso
│   ├── send_hello_world.py   # ✅ Envío de mensajes
│   ├── process_incoming_message.py # ✅ Procesamiento inteligente
│   ├── manage_user_memory.py # ✅ Gestión de memoria de usuario
│   ├── analyze_message_intent.py # ✅ Análisis de intención con IA
│   ├── generate_intelligent_response.py # ✅ Respuestas inteligentes
│   └── query_course_information.py # ✅ Consulta de información de cursos
└── presentation/api/          # ✅ Capa de presentación
    └── webhook.py            # ✅ Webhook FastAPI con IA
```

### Estructura Legacy (Referencia)
- `core/`         → Lógica principal, agentes, servicios
- `handlers/`     → Flujos conversacionales
- `services/`     → Integraciones externas (Twilio, OpenAI, BD)
- `memory/`       → Gestión de memoria y persistencia
- `prompts/`      → Prompts y plantillas centralizadas
- `config/`       → Configuración y variables de entorno
- `docs/`         → Documentación y roadmap
- `legacy/`       → Código Telegram completo y funcional

## 🚀 Inicio Rápido

### 1. Configuración Básica
```bash
# Instalar dependencias
pip install -r requirements-clean.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Twilio
```

### 2. Probar Envío de Mensajes (Hola Mundo)
```bash
python test_hello_world_clean.py
```

### 3. Ejecutar Webhook (Respuesta Automática)
```bash
# Terminal 1: Servidor webhook
python run_webhook_server.py

# Terminal 2: Exponer webhook públicamente
ngrok http 8000

# Configurar webhook en Twilio Console con la URL de ngrok
```

## 📚 Documentación Disponible

### Guías de Uso
- **`WEBHOOK_SETUP.md`** - Configuración completa del webhook
- **`TESTING_CLEAN_ARCHITECTURE.md`** - Testing de la nueva arquitectura
- **`CLAUDE.md`** - Guía completa para desarrollo con Claude Code

### Documentación Legacy
- **`docs/ROADMAP.md`** - Estado de migración y próximos pasos
- **`docs/WHATSAPP_MIGRATION.md`** - Guía técnica de migración
- **`legacy/CLAUDE.md`** - Documentación del sistema Telegram original

### Scripts de Prueba
- **`test_hello_world_clean.py`** - Prueba de envío con nueva arquitectura
- **`run_webhook_server.py`** - Servidor webhook con instrucciones
- **`legacy/hola_mundo_twilo.py`** - Primera prueba funcional (referencia)

## 🔄 Flujo de Desarrollo Actual

### Funcionando Ahora (✅)
1. **Envío de mensajes** - Script de prueba funcional
2. **Webhook de recepción** - Recibe mensajes de WhatsApp
3. **Sistema de memoria dual** - JSON local + PostgreSQL opcional
4. **Base de datos de cursos** - Consulta inteligente de información de cursos con filtros
5. **Análisis de intención** - Clasificación inteligente con OpenAI GPT-4o-mini
6. **Respuestas contextualizadas** - Con información específica de cursos según la intención
7. **Arquitectura escalable** - Clean Architecture con separación de responsabilidades
8. **Fallback en capas** - Funciona sin PostgreSQL y/o sin OpenAI

### Próximos Pasos (🔄)
1. **Herramientas de conversión** - Migrar 35+ herramientas desde sistema legacy
2. **Memoria PostgreSQL** - Migrar completamente desde JSON a PostgreSQL para escalabilidad
3. **Flujos avanzados** - Implementar flujos de ads, cursos, contacto y FAQ
4. **Lead scoring avanzado** - Sistema de puntuación y seguimiento automático en BD

## 🏗️ Migración a WhatsApp (Twilio)
- ✅ Toda la lógica de envío/recepción via Twilio implementada
- ✅ Webhook funcional para mensajes entrantes
- ✅ Sistema de memoria dual (JSON + PostgreSQL opcional)
- ✅ Base de datos de cursos con consultas inteligentes
- ✅ Análisis de intención con OpenAI GPT-4o-mini
- ✅ Respuestas contextualizadas con información de cursos
- ✅ Arquitectura escalable lista para producción
- 🔄 Pendiente: Migración completa de herramientas específicas desde `legacy/`

## 🧪 Scripts de Prueba

### Pruebas del Sistema Completo
- **`test_intelligent_system.py`** - Prueba sistema inteligente básico (OpenAI + memoria)
- **`test_course_integration.py`** - Prueba integración completa con base de datos de cursos

---

> **Nota:** El sistema legacy en `legacy/` contiene la implementación completa y funcional del bot Telegram. Se usa como referencia para migrar funcionalidades a la nueva arquitectura WhatsApp.