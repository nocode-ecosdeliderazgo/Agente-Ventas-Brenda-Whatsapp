# 🔍 Guía del Sistema de Debug

Este documento explica el sistema de debug visual implementado para monitorear el flujo interno del bot WhatsApp en tiempo real.

## 🎯 ¿Qué verás en consola?

### **1. Debug Prints Visuales**
Cada debug print tiene este formato visual:
```
================================================================================
🔍 DEBUG [archivo.py::función]
================================================================================
📋 Mensaje de debug detallado
================================================================================
```

### **2. Iconos por Componente**
- 🔍 **webhook.py** - Recepción de mensajes y coordinación
- 🧠 **analyze_message_intent.py** - Análisis de intención con IA
- 🤖 **openai_client.py** - Comunicación con OpenAI GPT-4o-mini
- 💬 **generate_intelligent_response.py** - Generación de respuestas
- 📱 **twilio_client.py** - Envío de mensajes WhatsApp

## 🚀 Cómo usar el sistema de debug

### **Iniciar el servidor con debug completo:**
```bash
python run_webhook_server_debug.py
```

### **Flujo que verás en consola:**

#### **1. Inicialización (al arrancar)**
```
🔍 DEBUG [webhook.py::startup] - Inicializando cliente Twilio...
✅ Cliente Twilio inicializado correctamente

🤖 Inicializando cliente OpenAI...
✅ Cliente OpenAI inicializado correctamente

🗄️ Intentando inicializar sistema de cursos PostgreSQL...
[✅ o ❌ dependiendo si tienes PostgreSQL configurado]
```

#### **2. Recepción de mensaje WhatsApp**
```
🔍 DEBUG [webhook.py::whatsapp_webhook]
📋 📨 MENSAJE RECIBIDO!
📱 Desde: whatsapp:+1234567890
💬 Texto: 'Hola'
🆔 SID: SMxxxxxxxxxxxxx
```

#### **3. Análisis de intención**
```
🧠 DEBUG [analyze_message_intent.py::execute]
📋 🔍 INICIANDO ANÁLISIS DE INTENCIÓN
👤 Usuario: whatsapp:+1234567890
💬 Mensaje: 'Hola'

🤖 DEBUG [openai_client.py::analyze_intent]
📋 🔍 ANALIZANDO INTENCIÓN
💬 Mensaje: 'Hola'
👤 Usuario: Anónimo

🚀 Enviando petición a OpenAI...
📥 RESPUESTA CRUDA DE OPENAI:
{
  "category": "GENERAL_QUESTION",
  "confidence": 0.8,
  ...
}
```

#### **4. Generación de respuesta**
```
💬 DEBUG [generate_intelligent_response.py::execute]
📋 💬 GENERANDO RESPUESTA INTELIGENTE
👤 Usuario: whatsapp:+1234567890
📨 Mensaje: 'Hola'

✅ Análisis completado - Intención: GENERAL_QUESTION
📝 Generando respuesta contextual...
✅ Respuesta generada: ¡Hola! Soy Brenda, tu asesora...
```

#### **5. Envío de respuesta**
```
📱 DEBUG [twilio_client.py::send_message]
📋 📤 ENVIANDO MENSAJE WHATSAPP
👤 A: +1234567890
💬 Texto: '¡Hola! Soy Brenda, tu asesora...'

🚀 Llamando API de Twilio...
✅ MENSAJE ENVIADO EXITOSAMENTE!
🔗 SID: SMyyyyyyyyyyy
📊 Status: queued
```

## 🔧 Información detallada que verás

### **📊 Estado de OpenAI**
- ✅ Conexión exitosa y respuesta recibida
- ❌ Error de API (rate limit, API key inválida, etc.)
- 🔄 Fallback automático si OpenAI falla

### **🗄️ Estado de PostgreSQL**
- ✅ Conexión exitosa - cursos disponibles
- ❌ Error de conexión - funcionará sin BD
- 📦 Información de cursos cargada

### **🧠 Análisis de intención detallado**
- 🎯 Categoría detectada (EXPLORATION, BUYING_SIGNALS, etc.)
- 📊 Nivel de confianza (0-1)
- 📚 Información extraída del usuario
- 🔄 Actualización de memoria

### **💬 Generación de respuestas**
- 📝 Tipo de respuesta (IA vs template)
- 🎯 Información de cursos incluida (si aplica)
- ✅ Respuesta final generada

### **📱 Envío WhatsApp**
- 📞 Números from/to
- 🔗 SID del mensaje
- 📊 Status de entrega

## 🚨 Detección de errores

### **Errores de OpenAI**
```
❌ ERROR CRÍTICO EN ANÁLISIS: HTTPError: 401 Unauthorized
🚨 Usando FALLBACK CRÍTICO
```
**Solución**: Verificar OPENAI_API_KEY en .env

### **Errores de Twilio**
```
❌ ERROR DE TWILIO: Unable to create record: The message body cannot be empty
```
**Solución**: Verificar TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN

### **Errores de PostgreSQL**
```
❌ Error conectando PostgreSQL: could not connect to server
⚠️ Sistema de cursos no disponible, usando respuestas estándar
```
**Solución**: Verificar DATABASE_URL o continuar sin BD

## 📋 Casos de prueba recomendados

### **1. Mensaje básico**
Envía: `"Hola"`
Espera ver: GENERAL_QUESTION → Respuesta de bienvenida

### **2. Mensaje con nombre**
Envía: `"Hola, soy María"`
Espera ver: Extracción de nombre → Actualización de memoria

### **3. Pregunta sobre cursos**
Envía: `"¿Qué cursos tienen?"`
Espera ver: EXPLORATION → Respuesta con información de cursos

### **4. Interés de compra**
Envía: `"Me interesa el curso de IA"`
Espera ver: BUYING_SIGNALS → Respuesta de seguimiento

### **5. Objeción de precio**
Envía: `"¿Cuánto cuesta?"`
Espera ver: OBJECTION_PRICE → Respuesta específica para objeciones

## 🛠️ Troubleshooting

### **Si no ves debug prints:**
1. Verifica que uses `run_webhook_server_debug.py`
2. Asegúrate de que el servidor arranque correctamente
3. Envía un mensaje WhatsApp para activar el flujo

### **Si OpenAI no funciona:**
1. Verifica OPENAI_API_KEY en .env
2. Revisa los límites de tu cuenta OpenAI
3. El sistema funcionará en modo fallback

### **Si Twilio no funciona:**
1. Verifica las credenciales de Twilio
2. Confirma que el webhook esté configurado
3. Asegúrate de que ngrok esté ejecutándose

### **Si hay muchos prints:**
- Los debug prints están diseñados para ser informativos
- Cada sección está claramente marcada con iconos
- Puedes filtrar por archivo usando el formato [archivo.py::función]

## 🎓 Entendiendo el flujo completo

```
📨 Mensaje WhatsApp recibido
   ↓
🔐 Verificación de firma (si está habilitada)
   ↓
📦 Procesamiento en background
   ↓
📚 Obtención de memoria del usuario
   ↓
🤖 Envío a OpenAI para análisis
   ↓
🧠 Análisis de intención + extracción de info
   ↓
🔄 Actualización de memoria de usuario
   ↓
🗄️ Consulta de cursos (si aplica)
   ↓
💬 Generación de respuesta contextual
   ↓
📱 Envío via Twilio
   ↓
✅ Confirmación de entrega
```

Cada paso tiene sus propios debug prints, así que puedes identificar exactamente dónde ocurre cualquier problema.

---

**💡 Tip**: Mantén esta guía abierta mientras pruebas el sistema para entender mejor lo que está pasando internamente.