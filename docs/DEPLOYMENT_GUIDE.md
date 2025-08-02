# 🚀 GUÍA DE DESPLIEGUE - BRENDA WHATSAPP BOT

## 📋 **ÍNDICE**
1. [Configuración Inicial](#configuración-inicial)
2. [Desarrollo Local](#desarrollo-local)
3. [Despliegue a Heroku](#despliegue-a-heroku)
4. [Configuración de Twilio](#configuración-de-twilio)
5. [Scripts de Utilidad](#scripts-de-utilidad)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 **CONFIGURACIÓN INICIAL**

### ✅ **Requisitos Previos**
- Python 3.11+
- Cuenta de Twilio
- Cuenta de Heroku
- Cuenta de OpenAI
- ngrok (para desarrollo local)

### ✅ **Instalación de Dependencias**
```bash
# Clonar repositorio
git clone https://github.com/nocode-ecosdeliderazgo/Agente-Ventas-Brenda-Whatsapp.git
cd Agente-Ventas-Brenda-Whatsapp

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

### ✅ **Variables de Entorno Requeridas**
```env
# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+14155238886

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Base de Datos (opcional)
DATABASE_URL=postgresql://user:password@host:port/database

# Configuración de la App
APP_ENVIRONMENT=development
LOG_LEVEL=INFO
WEBHOOK_VERIFY_SIGNATURE=true
```

---

## 💻 **DESARROLLO LOCAL**

### ✅ **Configuración de ngrok**
```bash
# Instalar ngrok
# Descargar desde: https://ngrok.com/download

# Ejecutar ngrok
ngrok http 8000

# Tu URL será: https://xxxxx.ngrok-free.app
```

### ✅ **Ejecutar Servidor de Desarrollo**
```bash
# Opción 1: Servidor completo
python run_development.py

# Opción 2: Servidor con debug
python run_webhook_server_debug.py

# Opción 3: Simulación de webhooks
python test_webhook_simulation.py
```

### ✅ **Configurar Webhook para Desarrollo**
```bash
# Cambiar webhook a desarrollo
python switch_webhook.py
# Seleccionar opción 1 (Desarrollo)
# Usar URL de ngrok
```

### ✅ **Probar Conexión**
```bash
# Probar credenciales de Twilio
python test_whatsapp_connection.py

# Ver información de la cuenta
python get_twilio_info.py

# Ver logs de conversaciones
python view_conversation_logs.py
```

---

## ☁️ **DESPLIEGUE A HEROKU**

### ✅ **Configuración de Heroku CLI**
```bash
# Instalar Heroku CLI
# Descargar desde: https://devcenter.heroku.com/articles/heroku-cli

# Login a Heroku
heroku login

# Conectar repositorio
heroku git:remote -a brenda-whatsapp-bot
```

### ✅ **Despliegue Automático**
```bash
# Despliegue completo
python deploy_heroku.py

# O manualmente:
git push heroku main
```

### ✅ **Configurar Variables de Entorno en Heroku**
```bash
# Configurar variables
heroku config:set TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx --app brenda-whatsapp-bot
heroku config:set TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx --app brenda-whatsapp-bot
heroku config:set TWILIO_PHONE_NUMBER=
heroku config:set OPENAI_API_KEY=
heroku config:set DATABASE_URL=postgresql://user:password@host:port/database --app brenda-whatsapp-bot

# Verificar configuración
heroku config --app brenda-whatsapp-bot
```

### ✅ **Gestionar la Aplicación**
```bash
# Ver logs en tiempo real
heroku logs --tail --app brenda-whatsapp-bot

# Ver estado de los procesos
heroku ps --app brenda-whatsapp-bot

# Reiniciar aplicación
heroku restart --app brenda-whatsapp-bot

# Escalar dynos
heroku ps:scale web=1 --app brenda-whatsapp-bot
```

---

## 📱 **CONFIGURACIÓN DE TWILIO**

### ✅ **Configurar WhatsApp Sandbox**
1. **Ir a Twilio Console**: https://console.twilio.com/
2. **Seleccionar tu subcuenta**
3. **Ir a Messaging → Settings → WhatsApp Sandbox**
4. **Configurar webhook**:
   - **When a message comes in**: 
   - **Method**: `POST`
5. **Hacer clic en "Save"**

### ✅ **Obtener Credenciales**
1. **Ir a Settings → API Keys & Tokens**
2. **Copiar Account SID** (empieza con `AC`)
3. **Copiar Auth Token**
4. **Configurar en variables de entorno**

### ✅ **Probar WhatsApp**
1. **Enviar mensaje** al 
2. **Con código**: 
3. **Enviar cualquier mensaje** para probar

---

## 🛠️ **SCRIPTS DE UTILIDAD**

### ✅ **Scripts de Desarrollo**
```bash
# Ejecutar servidor de desarrollo
python run_development.py

# Probar conexión de WhatsApp
python test_whatsapp_connection.py

# Ver logs de conversaciones
python view_conversation_logs.py

# Limpiar logs
python clear_conversation_logs.py
```

### ✅ **Scripts de Despliegue**
```bash
# Despliegue automático a Heroku
python deploy_heroku.py

# Cambiar entre desarrollo y producción
python switch_webhook.py

# Corregir credenciales de Twilio
python fix_twilio_credentials.py
```

### ✅ **Scripts de Configuración**
```bash
# Configurar WhatsApp Sandbox
python setup_whatsapp_sandbox.py

# Obtener información de Twilio
python get_twilio_info.py

# Simular webhooks
python test_webhook_simulation.py
```

---

## 🔍 **TROUBLESHOOTING**

### ❌ **Problema: App no inicia en Heroku**
```bash
# Ver logs de build
heroku logs --app brenda-whatsapp-bot

# Verificar variables de entorno
heroku config --app brenda-whatsapp-bot

# Reiniciar aplicación
heroku restart --app brenda-whatsapp-bot
```

### ❌ **Problema: Error de credenciales de Twilio**
```bash
# Verificar credenciales
python fix_twilio_credentials.py

# Probar conexión
python test_whatsapp_connection.py

# Obtener información de cuenta
python get_twilio_info.py
```

### ❌ **Problema: Webhook no responde**
```bash
# Verificar que la app esté funcionando
curl https://brenda-whatsapp-bot-f1bace3c0d6e.herokuapp.com/webhook

# Ver logs de webhook
heroku logs --tail --app brenda-whatsapp-bot | grep webhook

# Verificar configuración en Twilio Console
```

### ❌ **Problema: ngrok no funciona**
```bash
# Verificar que ngrok esté ejecutándose
curl http://localhost:4040/api/tunnels

# Reiniciar ngrok
ngrok http 8000

# Verificar puerto local
netstat -an | findstr :8000
```

### ❌ **Problema: Variables de entorno no cargan**
```bash
# Verificar archivo .env
cat .env

# Crear .env.local para desarrollo
cp .env .env.local

# Verificar variables cargadas
python -c "import os; print(os.getenv('TWILIO_ACCOUNT_SID'))"
```

---

## 📊 **MONITOREO Y LOGS**

### ✅ **Logs de Heroku**
```bash
# Ver logs en tiempo real
heroku logs --tail --app brenda-whatsapp-bot

# Ver logs de errores
heroku logs --app brenda-whatsapp-bot | grep ERROR

# Ver logs de webhook
heroku logs --app brenda-whatsapp-bot | grep webhook
```

### ✅ **Logs Locales**
```bash
# Ver conversaciones
python view_conversation_logs.py

# Limpiar logs
python clear_conversation_logs.py

# Ver logs de simulación
python test_webhook_simulation.py
```

### ✅ **Monitoreo de Recursos**
```bash
# Ver estado de dynos
heroku ps --app brenda-whatsapp-bot

# Ver uso de recursos
heroku logs --app brenda-whatsapp-bot | grep dyno

# Ver métricas de la app
heroku apps:info --app brenda-whatsapp-bot
```

---

## 🎯 **COMANDOS RÁPIDOS**

### ✅ **Desarrollo**
```bash
# Iniciar desarrollo
python run_development.py

# Probar conexión
python test_whatsapp_connection.py

# Ver logs
python view_conversation_logs.py
```

### ✅ **Producción**
```bash
# Ver logs de producción
heroku logs --tail --app brenda-whatsapp-bot

# Reiniciar app
heroku restart --app brenda-whatsapp-bot

# Ver estado
heroku ps --app brenda-whatsapp-bot
```



---

## 📞 **SOPORTE**

### 👥 **Equipo de Desarrollo**
- **Gael**: Configuración y despliegue
- **Israel**: Funcionalidades de IA
- **Equipo**: Integración y testing

### 📧 **Recursos Adicionales**
- **Documentación**: Carpeta `docs/`
- **Logs**: Carpeta `logs/`
- **Configuración**: Archivo `.env`
- **Scripts**: Archivos `.py` en raíz

### 🔗 **URLs Importantes**
- **Heroku**: https://brenda-whatsapp-bot-f1bace3c0d6e.herokuapp.com/
- **Twilio Console**: https://console.twilio.com/
- **ngrok Dashboard**: http://localhost:4040/

---

**🎉 ¡BRENDA WHATSAPP BOT ESTÁ LISTO PARA PRODUCCIÓN!** 