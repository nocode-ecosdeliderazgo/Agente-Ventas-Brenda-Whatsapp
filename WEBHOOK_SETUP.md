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

### Error: 403 Forbidden

Si tienes `WEBHOOK_VERIFY_SIGNATURE=true`, verifica que la firma sea válida.

## 🔄 Arquitectura del flujo

```
WhatsApp → Twilio → Webhook (ngrok) → FastAPI → Caso de Uso → Twilio → WhatsApp
    ↓                ↓                    ↓           ↓           ↓        ↓
Usuario envía    Twilio recibe    Webhook procesa   Genera    Envía    Usuario
mensaje         y reenvía        en background     "Hola"   respuesta  recibe
```

## 🎯 Próximos pasos

Una vez que esto funcione:
1. ✅ Respuesta automática "Hola" 
2. 🔄 Análisis de intención de mensajes
3. 🔄 Integración con OpenAI
4. 🔄 Sistema de memoria de usuarios
5. 🔄 Herramientas de conversión avanzadas

## 📝 Notas importantes

- El webhook responde inmediatamente "OK" a Twilio
- El procesamiento del mensaje se hace en background
- Solo se procesan mensajes de WhatsApp (se ignoran SMS)
- Todos los números pueden enviar mensajes y recibir respuesta