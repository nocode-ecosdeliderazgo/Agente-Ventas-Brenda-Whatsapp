# Configuración del Webhook - Bot Brenda

## 🎯 Objetivo
Configurar el webhook para que Twilio envíe mensajes entrantes de WhatsApp a nuestro bot y reciba respuestas automáticas "Hola".

## 🚀 Pasos para configurar

### 1. Ejecutar el servidor webhook
```bash
# Instalar dependencias si no lo has hecho
pip install -r requirements-clean.txt

# Ejecutar servidor
python run_webhook_server.py
```

El servidor se ejecutará en `http://localhost:8000`

### 2. Exponer el webhook públicamente con ngrok

Twilio necesita una URL pública para enviar webhooks. En desarrollo usamos ngrok:

```bash
# Instalar ngrok si no lo tienes
# Windows: choco install ngrok
# Mac: brew install ngrok
# Linux: snap install ngrok

# Exponer puerto 8000
ngrok http 8000
```

ngrok te dará una URL como: `https://abc123.ngrok.io`

### 3. Configurar webhook en Twilio Console

1. Ve a [Twilio Console](https://console.twilio.com/)
2. Ve a **Phone Numbers** > **Manage** > **Active numbers**
3. Selecciona tu número de WhatsApp
4. En la sección **Messaging**, configura:
   - **Webhook URL**: `https://tu-ngrok-url.ngrok.io/webhook/whatsapp`
   - **HTTP Method**: `POST`
5. Guarda los cambios

### 4. Probar el bot

1. Envía un mensaje WhatsApp a tu número de Twilio desde cualquier número
2. El bot debería responder automáticamente "Hola"
3. Revisa los logs en tu terminal para ver la actividad

## 📊 Logs y monitoreo

El servidor mostrará logs detallados:

```
📨 Webhook recibido de whatsapp:+5215572246258: Hola bot
🔄 Procesando mensaje en background...
📨 Mensaje recibido de +5215572246258: 'Hola bot'
✅ Respuesta enviada a +5215572246258. SID: SMxxxxxxxx
✅ Mensaje procesado exitosamente. Respuesta enviada: True
```

## 🔧 Endpoints disponibles

- `GET /` - Health check
- `POST /webhook/whatsapp` - Webhook principal para mensajes
- `GET /webhook/whatsapp` - Verificación del webhook

## ⚙️ Configuración avanzada

### Verificación de firma del webhook

Para mayor seguridad en producción, habilita la verificación de firma:

```env
WEBHOOK_VERIFY_SIGNATURE=true
```

### IPs permitidas

Restringe qué IPs pueden enviar webhooks:

```env
ALLOWED_WEBHOOK_IPS=["54.0.0.1", "54.0.0.2"]
```

## 🔍 Troubleshooting

### Error: Webhook no recibe mensajes

1. **Verifica la URL**: Asegúrate que la URL en Twilio Console sea correcta
2. **Verifica ngrok**: Que ngrok esté corriendo y la URL sea accesible
3. **Verifica logs**: Revisa si hay errores en el servidor

### Error: Bot no responde

1. **Verifica credenciales**: Que `TWILIO_AUTH_TOKEN` y `TWILIO_ACCOUNT_SID` sean correctos
2. **Verifica saldo**: Que tengas saldo en tu cuenta Twilio
3. **Verifica logs**: Busca errores en el envío de respuesta

## 🔄 Optimizaciones Recientes (Julio 2025)

### ✅ **Nuevo Script de Debug**
**Archivo**: `run_webhook_server_debug.py`

**Características**:
- 🔍 Debug prints visuales con emojis
- 📊 Análisis de intención en tiempo real
- 🤖 Respuestas de OpenAI visibles
- 📱 Envío de mensajes via Twilio
- 🧠 Memoria de usuario

**Uso**:
```bash
# Activar entorno virtual
venv_linux/bin/Activate.ps1

# Ejecutar servidor con debug
python run_webhook_server_debug.py
```

### ✅ **Corrección de Event Loop**
**Problema**: Conflicto de event loops al inicializar PostgreSQL.

**Solución**: Movido inicialización a evento de startup de FastAPI.

**Resultado**: Sistema estable sin conflictos.

### ✅ **Optimización de Respuesta Webhook**
**Problema**: Usuario veía "OK" antes de respuesta inteligente.

**Solución**: Procesamiento síncrono sin background tasks.

**Resultado**: Usuario solo ve respuesta inteligente.

### 📁 **Scripts Actualizados**

#### **Scripts Disponibles**:
```bash
# 1. Servidor webhook básico
python run_webhook_server.py

# 2. Servidor webhook con debug (RECOMENDADO)
python run_webhook_server_debug.py

# 3. Test básico de envío
python test_hello_world_clean.py

# 4. Test sistema inteligente completo
python test_intelligent_system.py
```

#### **Verificación de Estado**:
```bash
# Verificar puerto 8000
netstat -an | findstr :8000

# Verificar proceso Python
tasklist | findstr python

# Probar endpoint
Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET
```

### 🎯 **Resultados de Optimización**

#### **Performance**
- ✅ Respuesta < 10 segundos
- ✅ Sin timeouts de Twilio
- ✅ Sistema estable sin conflictos

#### **Experiencia de Usuario**
- ✅ **Solo ve**: Respuesta inteligente de Brenda
- ❌ **NO ve**: Confirmaciones técnicas
- ✅ Conversación natural y fluida

#### **Desarrollo**
- ✅ Logs detallados con emojis
- ✅ Debug fácil y visual
- ✅ Documentación actualizada

### 📚 **Documentación Relacionada**

- **`CURSOR.md`** - Documentación completa de cambios
- **`docs/DEVELOPMENT_PROGRESS.md`** - Progreso detallado
- **`docs/CLEAN_ARCHITECTURE.md`** - Arquitectura técnica
- **`TESTING_CLEAN_ARCHITECTURE.md`** - Guía de testing

### 🚀 **Estado Final**

El webhook está **completamente optimizado** con:
- ✅ **Recepción de mensajes** sin respuestas "OK"
- ✅ **Procesamiento inteligente** con OpenAI
- ✅ **Respuestas contextuales** enviadas via Twilio
- ✅ **Logs detallados** para desarrollo
- ✅ **Sistema estable** sin conflictos

**Listo para**: Pruebas con usuarios reales y migración de herramientas legacy.

## 🔄 Arquitectura del flujo

```