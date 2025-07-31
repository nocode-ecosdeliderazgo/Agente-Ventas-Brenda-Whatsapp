# 🚀 HEROKU DEPLOYMENT GUIDE - BRENDA WHATSAPP BOT

## 📋 RESUMEN EJECUTIVO

**Objetivo:** Desplegar el bot Brenda en Heroku para funcionamiento 24/7 sin necesidad de ngrok.

**Ventajas:**
- ✅ **URL pública directa** (sin ngrok)
- ✅ **Funcionamiento 24/7** (servidor siempre activo)
- ✅ **Escalable** (maneja múltiples conexiones)
- ✅ **Integración directa** con Twilio Console
- ✅ **Logs centralizados** en Heroku

---

## 🎯 REQUISITOS PREVIOS

### **1. Heroku CLI**
```bash
# Instalar Heroku CLI
# Windows: https://devcenter.heroku.com/articles/heroku-cli
# macOS: brew install heroku/brew/heroku
# Linux: curl https://cli-assets.heroku.com/install.sh | sh
```

### **2. Cuenta de Heroku**
- Crear cuenta en [heroku.com](https://heroku.com)
- Verificar email
- Agregar método de pago (requerido para PostgreSQL)

### **3. Variables de Entorno**
- `OPENAI_API_KEY`: Tu API key de OpenAI
- `TWILIO_ACCOUNT_SID`: Account SID de Twilio
- `TWILIO_AUTH_TOKEN`: Auth Token de Twilio
- `TWILIO_PHONE_NUMBER`: Número de WhatsApp de Twilio
- `DATABASE_URL`: URL de PostgreSQL (Heroku Postgres)

---

## 🚀 DESPLIEGUE AUTOMATIZADO

### **Opción 1: Script Automático**
```bash
# Ejecutar script de despliegue
python deploy_heroku.py
```

### **Opción 2: Comandos Manuales**
```bash
# 1. Crear aplicación Heroku
heroku create brenda-whatsapp-bot

# 2. Configurar variables de entorno
heroku config:set OPENAI_API_KEY=tu_api_key --app brenda-whatsapp-bot
heroku config:set TWILIO_ACCOUNT_SID=tu_sid --app brenda-whatsapp-bot
heroku config:set TWILIO_AUTH_TOKEN=tu_token --app brenda-whatsapp-bot
heroku config:set TWILIO_PHONE_NUMBER=tu_numero --app brenda-whatsapp-bot
heroku config:set DATABASE_URL=tu_url_db --app brenda-whatsapp-bot
heroku config:set APP_ENVIRONMENT=production --app brenda-whatsapp-bot

# 3. Desplegar
git push heroku main
```

---

## 📦 ARCHIVOS DE CONFIGURACIÓN

### **Procfile**
```
web: python run_webhook_server_debug.py
```

### **runtime.txt**
```
python-3.11.7
```

### **requirements.txt**
```
# Dependencias para Heroku
pydantic>=2.0.0
pydantic-settings>=2.0.0
twilio>=8.0.0
openai>=1.30.0
python-dotenv>=1.0.0
colorlog>=6.0.0
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
httpx>=0.24.0
python-dateutil>=2.8.0
asyncpg>=0.28.0
gunicorn>=21.0.0
```

### **app.json**
```json
{
  "name": "Brenda WhatsApp Bot",
  "description": "Bot inteligente de WhatsApp con OpenAI y PostgreSQL",
  "env": {
    "OPENAI_API_KEY": {"required": true},
    "TWILIO_ACCOUNT_SID": {"required": true},
    "TWILIO_AUTH_TOKEN": {"required": true},
    "TWILIO_PHONE_NUMBER": {"required": true},
    "DATABASE_URL": {"required": true},
    "APP_ENVIRONMENT": {"value": "production"}
  }
}
```

---

## 🔧 CONFIGURACIÓN PASO A PASO

### **Paso 1: Preparar el Proyecto**
```bash
# Asegurarse de estar en la rama correcta
git checkout dev-Gael

# Verificar que todos los archivos estén commiteados
git status
git add .
git commit -m "🚀 Heroku deployment setup"
```

### **Paso 2: Crear Aplicación Heroku**
```bash
# Crear nueva app
heroku create brenda-whatsapp-bot

# O usar script automático
python deploy_heroku.py
```

### **Paso 3: Configurar Base de Datos**
```bash
# Agregar PostgreSQL a Heroku
heroku addons:create heroku-postgresql:mini --app brenda-whatsapp-bot

# Obtener URL de la base de datos
heroku config:get DATABASE_URL --app brenda-whatsapp-bot
```

### **Paso 4: Configurar Variables de Entorno**
```bash
# Configurar todas las variables requeridas
heroku config:set OPENAI_API_KEY=sk-... --app brenda-whatsapp-bot
heroku config:set TWILIO_ACCOUNT_SID=AC... --app brenda-whatsapp-bot
heroku config:set TWILIO_AUTH_TOKEN=... --app brenda-whatsapp-bot
heroku config:set TWILIO_PHONE_NUMBER=+14155238886 --app brenda-whatsapp-bot
heroku config:set APP_ENVIRONMENT=production --app brenda-whatsapp-bot
```

### **Paso 5: Desplegar**
```bash
# Agregar Heroku como remote
git remote add heroku https://git.heroku.com/brenda-whatsapp-bot.git

# Push a Heroku
git push heroku main
```

### **Paso 6: Verificar Despliegue**
```bash
# Ver logs en tiempo real
heroku logs --tail --app brenda-whatsapp-bot

# Verificar que la app esté funcionando
curl https://brenda-whatsapp-bot.herokuapp.com/
```

---

## 🔗 CONFIGURACIÓN DE TWILIO

### **1. Obtener URL del Webhook**
```
https://brenda-whatsapp-bot.herokuapp.com/webhook
```

### **2. Configurar en Twilio Console**
1. Ir a [Twilio Console](https://console.twilio.com/)
2. Navegar a **Messaging** → **Settings** → **WhatsApp Sandbox**
3. En **Webhook URL**, agregar: `https://brenda-whatsapp-bot.herokuapp.com/webhook`
4. Guardar configuración

### **3. Probar Webhook**
```bash
# Enviar mensaje de prueba
curl -X POST https://brenda-whatsapp-bot.herokuapp.com/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&Body=Hola&MessageSid=test123"
```

---

## 📊 MONITOREO Y LOGS

### **Ver Logs en Tiempo Real**
```bash
heroku logs --tail --app brenda-whatsapp-bot
```

### **Ver Logs Específicos**
```bash
# Logs de errores
heroku logs --tail --app brenda-whatsapp-bot | grep ERROR

# Logs de webhook
heroku logs --tail --app brenda-whatsapp-bot | grep webhook
```

### **Métricas de la Aplicación**
```bash
# Ver uso de recursos
heroku ps --app brenda-whatsapp-bot

# Ver métricas
heroku metrics:web --app brenda-whatsapp-bot
```

---

## 🔄 ACTUALIZACIONES

### **Desplegar Cambios**
```bash
# Hacer cambios en el código
git add .
git commit -m "Actualización del bot"

# Desplegar a Heroku
git push heroku main
```

### **Reiniciar Aplicación**
```bash
# Reiniciar dyno
heroku restart --app brenda-whatsapp-bot

# Ver estado
heroku ps --app brenda-whatsapp-bot
```

---

## 🚨 TROUBLESHOOTING

### **Problema: App no inicia**
```bash
# Ver logs de build
heroku logs --app brenda-whatsapp-bot

# Verificar variables de entorno
heroku config --app brenda-whatsapp-bot
```

### **Problema: Error de base de datos**
```bash
# Verificar conexión a PostgreSQL
heroku pg:info --app brenda-whatsapp-bot

# Resetear base de datos si es necesario
heroku pg:reset DATABASE_URL --app brenda-whatsapp-bot
```

### **Problema: Webhook no responde**
```bash
# Verificar que la app esté funcionando
curl https://brenda-whatsapp-bot.herokuapp.com/

# Ver logs de webhook
heroku logs --tail --app brenda-whatsapp-bot | grep webhook
```

---

## 💰 COSTOS ESTIMADOS

### **Heroku Free Tier (Descontinuado)**
- ❌ Ya no disponible

### **Heroku Basic Dyno**
- 💰 **$7/mes** por dyno básico
- ✅ 512MB RAM
- ✅ Funcionamiento 24/7
- ✅ Logs completos

### **Heroku Postgres**
- 💰 **$5/mes** por PostgreSQL Mini
- ✅ 1GB almacenamiento
- ✅ 20 conexiones simultáneas
- ✅ Backups automáticos

**Total estimado: $12/mes**

---

## 🎯 PRÓXIMOS PASOS

### **1. Despliegue Inicial**
- [ ] Crear aplicación Heroku
- [ ] Configurar variables de entorno
- [ ] Desplegar código
- [ ] Verificar funcionamiento

### **2. Configuración de Twilio**
- [ ] Configurar webhook URL en Twilio Console
- [ ] Probar envío de mensajes
- [ ] Verificar recepción de respuestas

### **3. Monitoreo**
- [ ] Configurar alertas de Heroku
- [ ] Monitorear logs regularmente
- [ ] Verificar métricas de rendimiento

### **4. Optimización**
- [ ] Optimizar tiempos de respuesta
- [ ] Configurar auto-scaling si es necesario
- [ ] Implementar health checks

---

## 🎉 CONCLUSIÓN

Con Heroku tendrás:
- ✅ **URL pública directa** para Twilio
- ✅ **Funcionamiento 24/7** sin interrupciones
- ✅ **Logs centralizados** para debugging
- ✅ **Escalabilidad** automática
- ✅ **Integración perfecta** con Twilio

**¡El bot estará siempre disponible para tus usuarios!** 🚀 