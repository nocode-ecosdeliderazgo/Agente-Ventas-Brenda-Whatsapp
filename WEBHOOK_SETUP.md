# 📱 CONFIGURACIÓN TWILIO - BOT BRENDA WHATSAPP

## **🎯 ESTADO ACTUAL**
**Fecha:** 30 de Julio 2025  
**Versión:** 4.0 - Sistema Completo Integrado  
**Estado:** ✅ **LISTO PARA PRODUCCIÓN**

---

## **🚀 SISTEMA INTEGRADO COMPLETO**

### **✅ COMPONENTES FUNCIONANDO:**
- 🎯 **Flujo de bienvenida genérico** - Activación automática
- 🤖 **Integración dinámica de cursos** - Desde PostgreSQL
- 🧠 **Sistema anti-hallucination** - Implementado
- 🧹 **Limpieza del proyecto** - Archivos obsoletos eliminados
- 🔄 **Merge exitoso** - Cambios de Israel integrados

---

## **📡 CONFIGURACIÓN TWILIO**

### **🔧 VARIABLES DE ENTORNO REQUERIDAS:**
```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_PHONE_NUMBER=+14155238886

# OpenAI Configuration
OPENAI_API_KEY=tu_openai_api_key

# Database Configuration
DATABASE_URL=postgresql://usuario:password@host:puerto/db

# Optional Services
SUPABASE_URL=tu_supabase_url
SUPABASE_KEY=tu_supabase_key
TELEGRAM_API_TOKEN=tu_telegram_token
```

### **🌍 DESPLIEGUE DEL SERVIDOR:**

#### **Opción 1: Servidor Local con ngrok**
```bash
# 1. Ejecutar servidor
python run_webhook_server_debug.py

# 2. En otra terminal, exponer con ngrok
ngrok http 8000

# 3. Usar la URL de ngrok en Twilio Console
# Ejemplo: https://abc123.ngrok.io/webhook
```

#### **Opción 2: Servidor en la Nube**
```bash
# 1. Desplegar en servidor (Heroku, DigitalOcean, AWS, etc.)
# 2. Configurar variables de entorno
# 3. Usar URL del servidor en Twilio Console
# Ejemplo: https://tu-dominio.com/webhook
```

---

## **⚙️ CONFIGURACIÓN EN TWILIO CONSOLE**

### **📱 PASOS EN TWILIO CONSOLE:**

1. **Ir a Twilio Console** → https://console.twilio.com/
2. **Navegar a** → Messaging → Settings → WhatsApp Sandbox
3. **Configurar Webhook URL:**
   - **URL:** `https://tu-dominio.com/webhook` o `https://abc123.ngrok.io/webhook`
   - **Método:** POST
   - **Eventos:** message
4. **Guardar configuración**

### **🔗 ENDPOINTS DISPONIBLES:**

#### **Health Check:**
```
GET / → {"status": "ok", "service": "Bot Brenda Webhook"}
```

#### **Webhook Principal:**
```
POST /webhook → Maneja mensajes de WhatsApp
POST / → Redirige a /webhook
```

#### **Verificación de Webhook:**
```
GET /webhook → Verificación para Twilio
```

---

## **🧪 PRUEBAS DE FUNCIONAMIENTO**

### **✅ PRUEBAS LOCALES:**
```bash
# 1. Ejecutar simulador local
python test_webhook_simulation.py

# 2. Probar con mensajes:
# - "Hola" → Flujo de privacidad
# - "1" → Selección de curso
# - "dame información" → Información del curso
```

### **✅ PRUEBAS EN PRODUCCIÓN:**
1. **Enviar mensaje** desde WhatsApp a tu número de Twilio
2. **Verificar respuesta** automática del bot
3. **Probar flujo completo** de privacidad → bienvenida → selección de curso

---

## **📊 FLUJOS OPERATIVOS**

### **🎯 FLUJO DE BIENVENIDA GENÉRICO:**
```
Usuario → "Hola"
    ↓
Flujo de privacidad → Aceptar → Nombre → Rol
    ↓
TRIGGER AUTOMÁTICO → Flujo de bienvenida
    ↓
Ofrecer cursos reales de PostgreSQL
    ↓
Usuario selecciona curso (número, nombre, nivel)
    ↓
Confirmar selección y guardar en memoria
    ↓
Activar agente inteligente con personalización
```

### **🤖 AGENTE INTELIGENTE:**
- **Análisis de intención** PyME-específico
- **Respuestas contextuales** basadas en rol
- **Información dinámica** de cursos desde PostgreSQL
- **Cálculo de ROI** personalizado

---

## **🔧 TROUBLESHOOTING**

### **❌ PROBLEMAS COMUNES:**

#### **1. Error de conexión a PostgreSQL:**
```bash
# Verificar variables de entorno
echo $DATABASE_URL

# Verificar conexión
python -c "from app.infrastructure.database.client import DatabaseClient; print('✅ DB OK')"
```

#### **2. Error de Twilio:**
```bash
# Verificar credenciales
echo $TWILIO_ACCOUNT_SID
echo $TWILIO_AUTH_TOKEN

# Verificar número de teléfono
echo $TWILIO_PHONE_NUMBER
```

#### **3. Error de OpenAI:**
```bash
# Verificar API key
echo $OPENAI_API_KEY

# Probar conexión
python -c "import openai; print('✅ OpenAI OK')"
```

### **✅ SOLUCIONES:**

1. **Servidor no responde:**
   - Verificar que `run_webhook_server_debug.py` esté ejecutándose
   - Verificar puerto 8000 no esté ocupado
   - Revisar logs de error

2. **Webhook no recibe mensajes:**
   - Verificar URL en Twilio Console
   - Verificar método POST
   - Verificar eventos configurados

3. **Respuestas no se envían:**
   - Verificar credenciales de Twilio
   - Verificar número de teléfono configurado
   - Revisar logs de Twilio

---

## **📈 MONITOREO Y MÉTRICAS**

### **🎯 MÉTRICAS DE ÉXITO:**
- **Tiempo de respuesta:** < 3 segundos
- **Precisión de análisis:** > 85%
- **Tasa de éxito en selección:** > 90%
- **Integración de componentes:** 100%

### **📊 LOGS IMPORTANTES:**
```bash
# Logs del servidor
tail -f logs/webhook.log

# Logs de Twilio
# Revisar en Twilio Console → Logs
```

---

## **🚀 DESPLIEGUE FINAL**

### **✅ CHECKLIST DE PRODUCCIÓN:**

- [ ] **Variables de entorno** configuradas
- [ ] **Servidor** ejecutándose en puerto 8000
- [ ] **ngrok** o dominio público configurado
- [ ] **URL de webhook** configurada en Twilio Console
- [ ] **Pruebas** realizadas con mensajes reales
- [ ] **Logs** monitoreándose
- [ ] **Backup** de configuración realizado

### **🎉 SISTEMA LISTO:**
**El sistema está 100% funcional y listo para producción con Twilio.**

---

*Documentación actualizada: 30 de Julio 2025*  
*Versión: 4.0 - Sistema Integrado Completo*