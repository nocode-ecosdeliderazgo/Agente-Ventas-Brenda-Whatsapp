# Bot de Ventas Inteligente (Brenda) - WhatsApp (Twilio)

## 🎯 Objetivo
Migrar y modernizar el bot de ventas "Brenda" para operar 100% sobre WhatsApp usando Twilio, con arquitectura modular, escalable y lista para producción.

## 🚀 Estado Actual del Proyecto

### ✅ COMPLETADO - Arquitectura Limpia Funcional
- **Configuración robusta** con Pydantic Settings
- **Webhook funcional** que recibe mensajes de WhatsApp
- **Respuesta automática** "Hola" a cualquier mensaje
- **Separación de responsabilidades** con Clean Architecture
- **Logging estructurado** y manejo de errores
- **Verificación de firmas** de webhook para seguridad

### 🔄 EN DESARROLLO - Componentes Legacy (Referencia)
- Motor de IA conversacional (OpenAI GPT-4o-mini)
- Sistema de memoria persistente por usuario
- 35+ herramientas de conversión (recursos, demos, bonos, cierre, etc.)
- Activación inteligente de herramientas según intención
- Base de datos PostgreSQL (async)
- Flujos de conversación: Ads, cursos, contacto, FAQ
- Lead scoring y seguimiento
- Validación anti-alucinación

## 🏗️ Arquitectura Implementada

### Nueva Estructura (Clean Architecture)
```
app/                           # ✅ NUEVA ARQUITECTURA LIMPIA
├── config.py                  # ✅ Configuración centralizada (Pydantic)
├── domain/entities/           # ✅ Entidades de negocio
│   ├── message.py            # ✅ Mensajes (entrantes/salientes)
│   └── user.py               # ✅ Usuarios y contexto
├── infrastructure/twilio/     # ✅ Capa de infraestructura
│   └── client.py             # ✅ Cliente Twilio especializado
├── application/usecases/      # ✅ Casos de uso
│   ├── send_hello_world.py   # ✅ Envío de mensajes
│   └── process_incoming_message.py # ✅ Procesamiento entrantes
└── presentation/api/          # ✅ Capa de presentación
    └── webhook.py            # ✅ Webhook FastAPI
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
3. **Respuesta automática** - Responde "Hola" a cualquier mensaje
4. **Arquitectura escalable** - Clean Architecture implementada

### Próximos Pasos (🔄)
1. **Análisis de intención** - Procesar contenido de mensajes
2. **Integración OpenAI** - Respuestas inteligentes
3. **Sistema de memoria** - Contexto de usuarios
4. **Migración de herramientas** - 35+ herramientas de conversión

## 🏗️ Migración a WhatsApp (Twilio)
- ✅ Toda la lógica de envío/recepción via Twilio implementada
- ✅ Webhook funcional para mensajes entrantes
- ✅ Respuesta automática básica funcionando
- ✅ Arquitectura limpia lista para escalar
- 🔄 Pendiente: Migración de lógica avanzada desde `legacy/`

---

> **Nota:** El sistema legacy en `legacy/` contiene la implementación completa y funcional del bot Telegram. Se usa como referencia para migrar funcionalidades a la nueva arquitectura WhatsApp.