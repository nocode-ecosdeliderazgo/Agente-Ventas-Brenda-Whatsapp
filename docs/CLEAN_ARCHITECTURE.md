# Arquitectura Limpia - Bot Brenda WhatsApp

## 🎯 Visión General

Este documento describe la implementación de Clean Architecture para el bot Brenda de WhatsApp, diseñada para ser escalable, mantenible y testeable.

## 🏗️ Principios de Clean Architecture

### Separación de Capas
```
📱 Presentation Layer (FastAPI)
     ↓
🎯 Application Layer (Use Cases)
     ↓  
🏢 Domain Layer (Entities)
     ↓
🔧 Infrastructure Layer (Twilio, DB)
```

### Reglas de Dependencia
- Las capas internas no conocen las externas
- La lógica de negocio está aislada de detalles técnicos
- Los cambios en infraestructura no afectan el dominio

## 📁 Estructura Implementada

### `/app/config.py`
**Propósito**: Configuración centralizada con validación
```python
# Características:
- Pydantic Settings para validación automática
- Variables de entorno tipadas
- Configuración de seguridad y logging
- Separación por ambientes (dev/prod)
```

### `/app/domain/entities/`
**Propósito**: Modelos de negocio puros

#### `message.py`
```python
# Entidades implementadas:
- IncomingMessage: Mensajes recibidos de WhatsApp
- OutgoingMessage: Mensajes a enviar
- MessageType: Enum para tipos de mensaje
- MessageStatus: Estados del mensaje

# Métodos de negocio:
- from_twilio_webhook(): Convierte webhook a entidad
- to_twilio_format(): Prepara para envío
- is_whatsapp(): Validación de plataforma
```

#### `user.py`
```python
# Entidades implementadas:
- User: Usuario con contexto y memoria
- UserStatus: Estados del usuario

# Métodos de negocio:
- display_name: Nombre para mostrar
- is_new_user: Validación de usuario nuevo
- set_memory/get_memory: Gestión de contexto
```

### `/app/infrastructure/twilio/`
**Propósito**: Comunicación con APIs externas

#### `client.py`
```python
# Funcionalidades:
- TwilioWhatsAppClient: Cliente especializado
- Envío de mensajes de texto y multimedia
- Verificación de firmas de webhook
- Manejo robusto de errores
- Logging de todas las operaciones
```

### `/app/application/usecases/`
**Propósito**: Lógica de casos de uso

#### `send_hello_world.py`
```python
# Caso de uso de prueba:
- Envío de mensajes de prueba
- Soporte para WhatsApp y SMS
- Generación de mensajes personalizados
- Logging de resultados
```

#### `process_incoming_message.py`
```python
# Procesamiento principal:
- Recepción de webhooks de Twilio
- Conversión a entidades de dominio
- Generación de respuestas automáticas
- Envío de respuestas
- Logging completo del flujo
```

### `/app/presentation/api/`
**Propósito**: Interfaces externas (API, webhooks)

#### `webhook.py`
```python
# FastAPI webhook:
- Endpoint /webhook/whatsapp para Twilio
- Validación de firmas de webhook
- Procesamiento en background
- Health check endpoint
- Manejo de errores HTTP
```

## 🔄 Flujo de Datos

### Recepción de Mensaje
```
1. WhatsApp → Twilio → POST /webhook/whatsapp
2. Webhook valida firma y extrae datos
3. Background task procesa el mensaje
4. Use case convierte webhook a IncomingMessage
5. Use case genera OutgoingMessage("Hola")
6. Infrastructure envía respuesta via Twilio
7. WhatsApp recibe respuesta
```

### Envío de Mensaje
```
1. Script llama SendHelloWorldUseCase
2. Use case crea OutgoingMessage
3. Infrastructure convierte a formato Twilio
4. Twilio envía a WhatsApp
5. Use case retorna resultado
```

## 🎯 Beneficios Implementados

### ✅ Testabilidad
- Cada capa puede testearse independientemente
- Mocks fáciles de implementar
- Casos de uso aislados

### ✅ Mantenibilidad  
- Código organizado por responsabilidades
- Cambios localizados a una capa
- Fácil identificación de componentes

### ✅ Escalabilidad
- Nuevos casos de uso se agregan fácilmente
- Nuevas integraciones sin afectar lógica de negocio
- Soporte para múltiples interfaces (API, CLI, etc.)

### ✅ Reutilización
- Entidades reutilizables en diferentes contextos
- Use cases independientes de la presentación
- Infrastructure adaptable a diferentes proveedores

## 🚀 Preparación para Expansión

### Casos de Uso Futuros
```python
# Próximos a implementar:
- ProcessMessageWithAI (OpenAI integration)
- ManageUserMemory (context persistence)  
- AnalyzeMessageIntent (intent classification)
- ExecuteConversionTool (35+ tools migration)
```

### Nuevas Entidades
```python
# Entidades planificadas:
- Conversation: Historial de conversación
- Lead: Información de prospecto
- Tool: Herramientas de conversión
- Campaign: Campañas publicitarias
```

### Infrastructure Expansions
```python
# Integraciones futuras:
- OpenAI client (GPT responses)
- Database repository (PostgreSQL)
- Memory service (user context)
- Analytics service (metrics)
```

## 📋 Convenciones de Código

### Naming
- **Entities**: Nombres claros del dominio (`User`, `Message`)
- **Use Cases**: Verbos que describen la acción (`ProcessIncomingMessage`)
- **Infrastructure**: Tecnología + propósito (`TwilioWhatsAppClient`)

### Error Handling
- Excepciones de dominio para reglas de negocio
- Logging estructurado en todas las capas
- Respuestas consistentes con success/error

### Configuration
- Todo configurable via variables de entorno
- Validación automática con Pydantic
- Separación clara dev/staging/production

## 🔍 Comparación con Legacy

| Aspecto | Legacy (Telegram) | Clean Architecture |
|---------|------------------|-------------------|
| **Estructura** | Monolítica por features | Capas por responsabilidad |
| **Dependencies** | Acoplamiento alto | Inversión de dependencias |
| **Testing** | Difícil, requiere mocks complejos | Fácil, cada capa independiente |
| **Configuración** | Variables globales | Pydantic centralizado |
| **Error Handling** | Try/catch disperso | Estrategia consistente |
| **Extensibilidad** | Modificar código existente | Agregar nuevos componentes |

La nueva arquitectura está lista para escalar y recibir todas las funcionalidades avanzadas del sistema legacy de manera organizada y mantenible.