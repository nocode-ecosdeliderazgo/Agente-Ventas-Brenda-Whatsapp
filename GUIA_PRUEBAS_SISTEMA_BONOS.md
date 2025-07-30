# 🧪 GUÍA DE PRUEBAS - SISTEMA DE BONOS INTELIGENTE

## 🚀 Pasos para Probar el Sistema

### **1. Iniciar el Servidor**

```bash
# Activar entorno virtual (si no está activado)
source venv_new/bin/activate  # Linux/Mac
# o
venv_new\Scripts\activate     # Windows

# Instalar dependencias (si no están instaladas)
pip install -r requirements-clean.txt

# Iniciar servidor en modo debug
python run_webhook_server_debug.py
```

**✅ Esperado:** Ver mensajes de debug como:
```
🚀 BOT BRENDA WHATSAPP - MODO DEBUG ACTIVADO
🔍 Debug activo en: webhook.py, analyze_message_intent.py, openai_client.py, generate_intelligent_response.py, twilio_client.py
🎯 Flujo: Recepción → Análisis OpenAI → Respuesta → Envío Twilio
🎮 SERVIDOR INICIANDO...
📡 Servidor: 0.0.0.0:8000 | Reload: True
```

### **2. Configurar ngrok (para recibir webhooks de Twilio)**

```bash
# Instalar ngrok si no lo tienes
# Descargar de: https://ngrok.com/download

# Exponer el puerto 8000
ngrok http 8000
```

**✅ Esperado:** Ver URL pública como:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8000
```

### **3. Configurar Twilio Webhook**

1. Ir a [Twilio Console](https://console.twilio.com/)
2. Buscar tu número de WhatsApp
3. Configurar webhook URL: `https://abc123.ngrok.io/webhook`
4. Método: POST

## 🧪 Secuencia de Pruebas

### **PRUEBA 1: Flujo de Privacidad Completo**

**Enviar desde WhatsApp:**
```
Hola
```

**✅ Esperado:**
1. Debug: `💬 GENERANDO RESPUESTA INTELIGENTE`
2. Debug: `🧠 Ejecutando análisis de intención...`
3. Respuesta: Mensaje de privacidad GDPR
4. Debug: `🎁 Activando bonos para categoría: privacy_flow`

### **PRUEBA 2: Consentimiento de Privacidad**

**Enviar desde WhatsApp:**
```
Sí, acepto
```

**✅ Esperado:**
1. Debug: `✅ Análisis completado - Intención: privacy_consent`
2. Respuesta: Solicitud de nombre
3. Debug: `🎯 Generando respuesta para categoría: privacy_flow`

### **PRUEBA 3: Proporcionar Nombre**

**Enviar desde WhatsApp:**
```
Me llamo Juan Pérez
```

**✅ Esperado:**
1. Debug: `✅ Análisis completado - Intención: name_provided`
2. Respuesta: Solicitud de rol/cargo
3. Debug: `🎁 Activando bonos para categoría: role_collection`

### **PRUEBA 4: Proporcionar Rol**

**Enviar desde WhatsApp:**
```
Soy Director de Marketing
```

**✅ Esperado:**
1. Debug: `✅ Análisis completado - Intención: role_provided`
2. Respuesta: Mensaje de bienvenida personalizado
3. Debug: `🎁 Activando bonos para categoría: sales_agent`
4. **BONOS ACTIVADOS:** Ver bonos específicos para Marketing

### **PRUEBA 5: Exploración de Curso**

**Enviar desde WhatsApp:**
```
Cuéntame sobre el curso
```

**✅ Esperado:**
1. Debug: `✅ Análisis completado - Intención: EXPLORATION`
2. Respuesta: Información del curso + bonos contextuales
3. Debug: `🎁 Bonos activados: X bonos priorizados`
4. **BONOS ESPECÍFICOS:** Workbook, Biblioteca prompts, Soporte Telegram

### **PRUEBA 6: Objeción de Precio**

**Enviar desde WhatsApp:**
```
Es muy caro
```

**✅ Esperado:**
1. Debug: `✅ Análisis completado - Intención: OBJECTION_PRICE`
2. Respuesta: Justificación de valor + bonos específicos
3. Debug: `🎯 Contexto detectado: price_objection`
4. **BONOS PRIORITARIOS:** Descuentos, Grabaciones, Comunidad

### **PRUEBA 7: Señales de Compra**

**Enviar desde WhatsApp:**
```
Quiero inscribirme
```

**✅ Esperado:**
1. Debug: `✅ Análisis completado - Intención: BUYING_SIGNALS`
2. Respuesta: Facilitación de compra + bonos de cierre
3. Debug: `🎯 Contexto detectado: buying_signals`
4. **BONOS DE CIERRE:** Descuentos, Grabaciones, Comunidad, Workbook

### **PRUEBA 8: Miedo Técnico**

**Enviar desde WhatsApp:**
```
No sé si podré aprender
```

**✅ Esperado:**
1. Debug: `✅ Análisis completado - Intención: TECHNICAL_FEAR`
2. Respuesta: Reducción de barreras + bonos de soporte
3. Debug: `🎯 Contexto detectado: technical_fear`
4. **BONOS DE SOPORTE:** Soporte Telegram, Workbook, Biblioteca

## 🔍 Verificación de Debug Logs

### **Logs Esperados por Prueba:**

#### **Activación de Bonos:**
```
🎁 Activando bonos para categoría: [CATEGORIA]
✅ Bonos activados: [X] bonos priorizados
🎯 Contexto detectado: [CONTEXTO]
🎯 Nivel de urgencia: [NIVEL]
```

#### **Generación de Respuesta:**
```
📝 Generando respuesta contextual...
✅ Respuesta con bonos generada exitosamente
📤 Enviando respuesta a WhatsApp: [NUMERO]
✅ MENSAJE ENVIADO EXITOSAMENTE!
```

#### **Análisis de Intención:**
```
🧠 Ejecutando análisis de intención...
✅ Análisis completado - Intención: [CATEGORIA]
```

## 🎯 Verificación de Bonos por Buyer Persona

### **Lucía CopyPro (Marketing Digital):**
- **Bonos esperados:** Workbook, Biblioteca prompts, Telegram, LinkedIn
- **Ángulo:** "Herramientas listas para campañas de marketing"

### **Marcos Multitask (Operaciones):**
- **Bonos esperados:** Workbook, Grabaciones, Descuentos, Comunidad
- **Ángulo:** "Optimiza procesos con recursos flexibles"

### **Sofía Visionaria (CEO/Founder):**
- **Bonos esperados:** Comunidad, Bolsa empleo, Q&A, Boletín
- **Ángulo:** "Red de líderes y tendencias estratégicas"

## 🚨 Solución de Problemas

### **Error: "Import could not be resolved"**
```bash
# Verificar que el archivo bonus_activation_use_case.py existe
ls app/application/usecases/bonus_activation_use_case.py
```

### **Error: "Cannot access attribute"**
- Los templates de WhatsApp pueden no tener todos los métodos
- El sistema funcionará con los métodos disponibles

### **Error: "get_recommended_courses is not a known attribute"**
- El sistema de cursos es opcional
- El sistema de bonos funcionará sin él

### **No se ven los debug prints:**
```bash
# Verificar que estás usando el archivo correcto
python run_webhook_server_debug.py
```

## 📊 Métricas de Éxito

### **✅ Prueba Exitosa si:**
1. **Debug logs aparecen** en la consola
2. **Bonos se activan** según el contexto
3. **Respuestas incluyen** información de bonos
4. **Mensajes se envían** correctamente
5. **Memoria se actualiza** con información del usuario

### **❌ Problemas Comunes:**
1. **No hay debug logs** → Verificar archivo de debug
2. **Bonos no aparecen** → Verificar activación contextual
3. **Errores de import** → Verificar estructura de archivos
4. **Mensajes no se envían** → Verificar configuración Twilio

## 🎉 ¡Sistema Funcionando!

**Si ves estos logs, el sistema está funcionando correctamente:**

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

**¡El sistema de bonos inteligente está operativo! 🚀**

---

## ⚡ Actualizaciones Recientes (Julio 2025)

### **🔧 Mejoras en Testing**
- ✅ **Validación de roles mejorada**: Ahora previene roles inválidos como "Hola"
- ⚡ **Respuestas más inteligentes**: Sistema usa respuestas OpenAI directas vs templates
- ⏳ **Pendiente validación**: Ejecutar `test_webhook_simulation.py` para confirmar mejoras

### **🎯 Nuevas Verificaciones de Testing**
- **Role validation check**: Verificar que rechace "Hola", "si", "temario" como roles
- **AI response check**: Confirmar respuestas específicas vs genéricas
- **Bonus activation check**: Validar bonos contextuales funcionan con nuevas mejoras

### **📋 Próximos Tests Recomendados**
1. **Test role inválido**: Enviar "Hola" como rol → debe rechazarse
2. **Test temario question**: Enviar "de que trata el curso" → debe usar respuesta OpenAI específica
3. **Test bonos con rol válido**: "Director de Marketing" → debe activar bonos correctos

---

**Estado**: ⚡ **FUNCIONAL CON MEJORAS RECIENTES**  
**Fecha**: Julio 2025 (Actualizado)  
**Próximo**: Validación completa de mejoras en respuestas inteligentes 