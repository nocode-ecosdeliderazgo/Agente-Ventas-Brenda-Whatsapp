# Testing - Arquitectura Limpia

## 🎯 Objetivo
Probar que la nueva arquitectura limpia funciona correctamente enviando mensajes "Hola Mundo" via Twilio.

## 🏗️ Arquitectura Implementada

```
app/
├── config.py                              # ✅ Configuración con Pydantic
├── domain/entities/                       # ✅ Entidades de negocio
│   ├── message.py                         # ✅ Mensajes entrantes/salientes
│   └── user.py                            # ✅ Usuarios y contexto
├── infrastructure/twilio/                 # ✅ Capa de infraestructura
│   └── client.py                          # ✅ Cliente Twilio especializado
└── application/usecases/                  # ✅ Casos de uso
    └── send_hello_world.py                # ✅ Envío de mensajes de prueba
```

## 🚀 Prueba Rápida

### 1. Instalar dependencias:
```bash
pip install -r requirements-clean.txt
```

### 2. Configurar credenciales:
```bash
cp .env.example .env
# Editar .env con tus credenciales de Twilio
```

### 3. Ejecutar prueba:
```bash
python test_hello_world_clean.py
```

## 📱 Comparación con Legacy

| Aspecto | Legacy (`legacy/hola_mundo_twilo.py`) | Nueva Arquitectura |
|---------|--------------------------------------|-------------------|
| **Configuración** | Variables globales | Pydantic Settings |
| **Estructura** | Script monolítico | Clean Architecture |
| **Manejo errores** | Try/catch básico | Logging estructurado |
| **Reutilización** | Código duplicado | Casos de uso reutilizables |
| **Testing** | Difícil de testear | Fácil testing unitario |
| **Escalabilidad** | Limitada | Preparada para crecer |

## 🎛️ Configuración Disponible

En `.env`:
```env
# Credenciales Twilio
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token  
TWILIO_PHONE_NUMBER=+14155238886

# Configuración de app
APP_ENVIRONMENT=development
LOG_LEVEL=INFO
WEBHOOK_VERIFY_SIGNATURE=true
```

## 📊 Casos de Uso Implementados

### `SendHelloWorldUseCase`
- ✅ Envío de WhatsApp
- ✅ Envío de SMS  
- ✅ Manejo de errores
- ✅ Logging estructurado
- ✅ Validación de datos

## 🔍 Próximos Pasos

Una vez que esta prueba funcione:

1. **Webhook Handler** - Recibir mensajes entrantes
2. **Procesamiento IA** - Integrar OpenAI para respuestas
3. **Sistema de Memoria** - Contexto de usuarios
4. **Herramientas de Conversión** - Migrar las 35+ herramientas
5. **Testing Automatizado** - Suite de pruebas completa

## 🐛 Debugging

Si algo no funciona:

1. **Verificar configuración**: El script mostrará errores específicos
2. **Revisar logs**: Configurados automáticamente según `LOG_LEVEL`
3. **Validar credenciales**: Probar primero con el script legacy
4. **Comprobar saldo**: Twilio requiere saldo para envíos

## 💡 Beneficios de esta Arquitectura

- **Separación de responsabilidades**: Cada componente tiene una función clara
- **Testeable**: Cada capa puede probarse independientemente  
- **Escalable**: Fácil agregar nuevas funcionalidades
- **Mantenible**: Código organizado y documentado
- **Reutilizable**: Casos de uso que se pueden usar en diferentes contextos