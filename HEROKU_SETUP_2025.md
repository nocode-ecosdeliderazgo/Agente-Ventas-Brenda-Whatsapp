# 🚀 DESPLIEGUE HEROKU - BOT BRENDA WHATSAPP 2025

## ✅ Aplicación Creada Exitosamente

**Nombre de la aplicación:** `brenda-whatsapp-bot-2025`  
**URL:** https://brenda-whatsapp-bot-2025-540353a4be47.herokuapp.com/  
**Git URL:** https://git.heroku.com/brenda-whatsapp-bot-2025.git

## 🔧 Configuración de Variables de Entorno

### 1. Configurar Variables Básicas
```bash
heroku config:set APP_ENVIRONMENT=production --app brenda-whatsapp-bot-2025
heroku config:set LOG_LEVEL=INFO --app brenda-whatsapp-bot-2025
heroku config:set WEBHOOK_VERIFY_SIGNATURE=false --app brenda-whatsapp-bot-2025
```

### 2. Configurar Credenciales de Twilio
```bash
heroku config:set TWILIO_ACCOUNT_SID=tu_account_sid --app brenda-whatsapp-bot-2025
heroku config:set TWILIO_AUTH_TOKEN=tu_auth_token --app brenda-whatsapp-bot-2025
heroku config:set TWILIO_PHONE_NUMBER=tu_numero_twilio --app brenda-whatsapp-bot-2025
```

### 3. Configurar OpenAI
```bash
heroku config:set OPENAI_API_KEY=tu_openai_api_key --app brenda-whatsapp-bot-2025
```

### 4. Configurar Base de Datos (Opcional)
```bash
heroku config:set DATABASE_URL=tu_database_url --app brenda-whatsapp-bot-2025
```

### 5. Configurar Asesor
```bash
heroku config:set ADVISOR_PHONE_NUMBER="+52 1 56 1468 6075" --app brenda-whatsapp-bot-2025
heroku config:set ADVISOR_NAME="Especialista en IA" --app brenda-whatsapp-bot-2025
heroku config:set ADVISOR_TITLE="Asesor Comercial" --app brenda-whatsapp-bot-2025
```

## 🚀 Proceso de Despliegue

### 1. Agregar Remote de Heroku
```bash
git remote add heroku-2025 https://git.heroku.com/brenda-whatsapp-bot-2025.git
```

### 2. Hacer Commit de los Cambios Actuales
```bash
git add .
git commit -m "Despliegue Bot Brenda WhatsApp 2025 - Versión actualizada"
```

### 3. Desplegar a Heroku
```bash
git push heroku-2025 main
```

### 4. Verificar el Despliegue
```bash
heroku logs --tail --app brenda-whatsapp-bot-2025
```

## 🌐 Configuración de Webhook en Twilio

1. Ve a tu [Consola de Twilio](https://console.twilio.com/)
2. Navega a Messaging > Settings > WhatsApp Sandbox
3. Configura la URL del webhook:
   ```
   https://brenda-whatsapp-bot-2025-540353a4be47.herokuapp.com/webhook/whatsapp
   ```
4. Guarda la configuración

## 🧪 Pruebas

1. Envía un mensaje de WhatsApp a tu número de Twilio
2. El bot debería responder automáticamente
3. Verifica los logs en Heroku para confirmar que todo funciona

## 📋 Comandos Útiles

### Ver Variables de Entorno
```bash
heroku config --app brenda-whatsapp-bot-2025
```

### Ver Logs en Tiempo Real
```bash
heroku logs --tail --app brenda-whatsapp-bot-2025
```

### Reiniciar la Aplicación
```bash
heroku restart --app brenda-whatsapp-bot-2025
```

### Abrir la Aplicación en el Navegador
```bash
heroku open --app brenda-whatsapp-bot-2025
```

## 🔍 Verificación de Estado

### Verificar que la Aplicación Esté Funcionando
```bash
curl https://brenda-whatsapp-bot-2025-540353a4be47.herokuapp.com/
```

### Verificar el Endpoint del Webhook
```bash
curl https://brenda-whatsapp-bot-2025-540353a4be47.herokuapp.com/webhook/whatsapp
```

## ⚠️ Notas Importantes

1. **Credenciales:** Asegúrate de tener las credenciales correctas de Twilio y OpenAI
2. **Número de Twilio:** Verifica que el número esté configurado para WhatsApp
3. **Webhook:** La URL del webhook debe ser accesible públicamente
4. **Logs:** Revisa los logs si hay problemas con el despliegue

## 🎯 Próximos Pasos

1. Configurar las variables de entorno con tus credenciales reales
2. Desplegar el código usando Git
3. Configurar el webhook en Twilio
4. Probar el bot enviando un mensaje de WhatsApp
5. Monitorear los logs para verificar el funcionamiento

---

**Estado:** ✅ Aplicación creada en Heroku  
**Próximo:** Configurar variables de entorno y desplegar código 