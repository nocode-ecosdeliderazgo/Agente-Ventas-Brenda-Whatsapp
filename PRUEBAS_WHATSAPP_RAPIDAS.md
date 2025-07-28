# 🚀 PRUEBAS RÁPIDAS WHATSAPP - SISTEMA DE BONOS

## ✅ Estado Actual
- **Sistema de bonos:** ✅ Funcionando
- **Servidor webhook:** ✅ Ejecutándose en puerto 8000
- **Lógica de activación:** ✅ Verificada
- **Formateo de respuestas:** ✅ Verificada

## 📱 Configuración Rápida para WhatsApp

### **1. Configurar ngrok**
```bash
# En una nueva terminal
ngrok http 8000
```

**✅ Esperado:**
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8000
```

### **2. Configurar Twilio Webhook**
1. Ir a [Twilio Console](https://console.twilio.com/)
2. Buscar tu número de WhatsApp
3. Configurar webhook URL: `https://abc123.ngrok.io/webhook`
4. Método: POST

## 🧪 Secuencia de Pruebas WhatsApp

### **PRUEBA 1: Flujo de Privacidad**
```
Enviar: "Hola"
Esperado: Mensaje de privacidad GDPR
```

### **PRUEBA 2: Consentimiento**
```
Enviar: "Sí, acepto"
Esperado: Solicitud de nombre
```

### **PRUEBA 3: Nombre**
```
Enviar: "Me llamo Juan Pérez"
Esperado: Solicitud de rol/cargo
```

### **PRUEBA 4: Rol**
```
Enviar: "Soy Director de Marketing"
Esperado: Bienvenida + bonos específicos para Marketing
```

### **PRUEBA 5: Exploración**
```
Enviar: "Cuéntame sobre el curso"
Esperado: Información del curso + bonos contextuales
```

### **PRUEBA 6: Objeción de Precio**
```
Enviar: "Es muy caro"
Esperado: Justificación + bonos de descuento
```

### **PRUEBA 7: Señales de Compra**
```
Enviar: "Quiero inscribirme"
Esperado: Facilitación + bonos de cierre
```

## 🎁 Verificación de Bonos por Rol

### **Marketing Digital:**
- ✅ Workbook interactivo en Coda.io
- ✅ Biblioteca de prompts avanzada
- ✅ Soporte en Telegram
- ✅ Insignia digital LinkedIn

### **Operaciones:**
- ✅ Workbook interactivo
- ✅ Acceso a grabaciones
- ✅ Descuento exclusivo 10%
- ✅ Comunidad privada

### **CEO/Founder:**
- ✅ Comunidad privada vitalicia
- ✅ Bolsa de empleo especializada
- ✅ Sesiones Q&A trimestrales
- ✅ Suscripción "AI Trends"

## 🔍 Logs de Debug Esperados

### **Activación de Bonos:**
```
🎁 Activando bonos para categoría: EXPLORATION
✅ Bonos activados: 3 bonos priorizados
🎯 Contexto detectado: general
🎯 Nivel de urgencia: medium
```

### **Generación de Respuesta:**
```
📝 Generando respuesta contextual...
✅ Respuesta con bonos generada exitosamente
📤 Enviando respuesta a WhatsApp: +1234567890
✅ MENSAJE ENVIADO EXITOSAMENTE!
```

## 🚨 Solución de Problemas

### **No se ven los debug logs:**
- Verificar que usas `run_webhook_server_debug.py`
- Verificar que el servidor está ejecutándose en puerto 8000

### **Bonos no aparecen:**
- Verificar que el usuario completó el flujo de privacidad
- Verificar que se proporcionó rol/cargo
- Verificar que el contexto es apropiado

### **Mensajes no se envían:**
- Verificar configuración de Twilio
- Verificar URL de webhook en Twilio Console
- Verificar que ngrok está funcionando

## 📊 Métricas de Éxito

### **✅ Prueba Exitosa si:**
1. **Debug logs aparecen** en la consola
2. **Bonos se activan** según el contexto
3. **Respuestas incluyen** información de bonos
4. **Mensajes se envían** correctamente
5. **Memoria se actualiza** con información del usuario

### **🎯 Logs de Éxito:**
```
🎁 Activando bonos para categoría: EXPLORATION
✅ Bonos activados: 3 bonos priorizados
🎯 Contexto detectado: general
🎯 Nivel de urgencia: medium
📝 Generando respuesta contextual...
✅ Respuesta con bonos generada exitosamente
📤 Enviando respuesta a WhatsApp: +1234567890
✅ MENSAJE ENVIADO EXITOSAMENTE!
```

## 🎉 ¡Sistema Listo!

**Si ves estos logs, el sistema está funcionando correctamente y listo para producción:**

- ✅ **Sistema de bonos inteligente** activado
- ✅ **Activación contextual** funcionando
- ✅ **Formateo de respuestas** con bonos
- ✅ **Integración con WhatsApp** operativa

**¡El agente Brenda ahora puede activar bonos específicos según el contexto del usuario! 🚀** 