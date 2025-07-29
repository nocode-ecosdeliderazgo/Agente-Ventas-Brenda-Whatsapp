# 🤖 Simulador de Webhook - Guía de Desarrollo

## 📋 Resumen Ejecutivo

El **Simulador de Webhook** (`test_webhook_simulation.py`) es una réplica exacta del sistema de WhatsApp que permite desarrollar y probar todas las funcionalidades sin depender de Twilio. **A partir de ahora, el desarrollo se realizará principalmente a través de este simulador.**

## 🎯 Objetivo Principal

- **Desarrollo sin costos**: No gastar créditos de Twilio durante el desarrollo
- **Iteración rápida**: Probar funcionalidades inmediatamente
- **Debug completo**: Ver todo el proceso paso a paso
- **Funcionalidad idéntica**: Mismo comportamiento que el webhook real

## 🏗️ Arquitectura del Simulador

### Componentes Principales

```python
# Exactamente los mismos componentes que webhook.py
- ProcessIncomingMessageUseCase
- ManageUserMemoryUseCase  
- AnalyzeMessageIntentUseCase
- GenerateIntelligentResponseUseCase
- PrivacyFlowUseCase
- ToolActivationUseCase
- QueryCourseInformationUseCase
- MemoryManager (JSON-based)
- OpenAIClient
- ConsoleTwilioClient (simulado)
```

### Diferencias con Webhook Real

| Aspecto | Simulador | Twilio Webhook |
|---------|-----------|----------------|
| **Cliente Twilio** | `ConsoleTwilioClient` | `TwilioWhatsAppClient` |
| **Datos de Entrada** | Simulados | Reales de Twilio |
| **Verificación de Firma** | Deshabilitada | Habilitada |
| **Background Tasks** | Síncrono | Asíncrono |

## 🚀 Cómo Usar el Simulador

### 1. Ejecutar el Simulador

```bash
python test_webhook_simulation.py
```

### 2. Flujo de Uso

```
1. El simulador inicia y muestra el header
2. Espera tu primer mensaje
3. Procesa el mensaje exactamente como el webhook real
4. Muestra debug prints separados por #################################
5. Muestra la respuesta final de Brenda
6. Espera tu siguiente mensaje
7. Continúa indefinidamente hasta que escribas 'salir'
```

### 3. Comandos Disponibles

- **Cualquier mensaje**: Se procesa normalmente
- **'salir'**: Termina la conversación
- **'exit'**: Termina la conversación  
- **'quit'**: Termina la conversación
- **'s'**: Termina la conversación

## 📊 Funcionalidades Incluidas

### ✅ Sistema Completo Replicado

1. **🧠 Análisis de Intención**
   - Clasificación PyME-específica
   - Extracción de información del usuario
   - Análisis de buyer personas

2. **💾 Sistema de Memoria**
   - Persistencia JSON por usuario
   - Historial de conversación
   - Estado del flujo de privacidad
   - Preferencias y contexto

3. **🔒 Flujo de Privacidad**
   - Aceptación obligatoria de términos
   - Persistencia del estado
   - No se repite si ya fue aceptado

4. **🎁 Sistema de Bonos Inteligente**
   - Activación contextual
   - Basado en rol y conversación
   - Valor total mostrado

5. **📚 Acceso a Base de Datos**
   - Conexión PostgreSQL/Supabase
   - Información de cursos dinámica
   - Fallback a modo básico si falla

6. **🛠️ Herramientas de Conversión**
   - Sistema de herramientas activado
   - Preparado para futuras integraciones

## 📁 Estructura de Archivos

### Archivos del Simulador
```
test_webhook_simulation.py          # Simulador principal
logs/                               # Logs de conversaciones
  └── webhook_simulation_log_YYYYMMDD.json
memorias/                           # Memoria de usuarios
  └── memory_console_user_001.json
```

### Archivos de Logs
- **Conversaciones**: `logs/webhook_simulation_log_YYYYMMDD.json`
- **Memoria**: `memorias/memory_console_user_001.json`
- **Backups**: `memorias/memory_console_user_001.json.backup`

## 🔧 Configuración Requerida

### Variables de Entorno
```bash
# OpenAI
OPENAI_API_KEY=tu_api_key_aqui

# Twilio (para configuración, no para uso)
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_PHONE_NUMBER=tu_numero_whatsapp

# Base de Datos (opcional)
DATABASE_URL=tu_url_supabase
```

### Verificación de Configuración
El simulador verifica automáticamente:
- ✅ OpenAI API Key
- ✅ Twilio Phone Number  
- ✅ Database URL (opcional)
- ✅ Environment (development/production)

## 🧪 Casos de Prueba Recomendados

### 1. Flujo Básico
```
Usuario: "Hola"
→ Debe iniciar flujo de privacidad
→ Preguntar nombre y cargo
```

### 2. Flujo de Privacidad
```
Usuario: "Acepto"
→ Debe confirmar aceptación
→ Continuar con conversación normal
```

### 3. Información Personal
```
Usuario: "Gael"
→ Debe recordar el nombre
→ Preguntar cargo en la empresa
```

### 4. Exploración de Cursos
```
Usuario: "¿Qué cursos tienen?"
→ Debe mostrar información de cursos
→ Activar bonos relevantes
```

### 5. Objeciones
```
Usuario: "Es muy caro"
→ Debe manejar objeción de precio
→ Mostrar valor y ROI
```

## 🔄 Flujo de Desarrollo

### 1. Desarrollo en Simulador
```bash
# 1. Hacer cambios en el código
# 2. Ejecutar simulador
python test_webhook_simulation.py

# 3. Probar funcionalidad
# 4. Verificar logs y memoria
# 5. Iterar hasta que funcione perfectamente
```

### 2. Verificación de Funcionalidad
- ✅ Análisis de intención funciona
- ✅ Respuestas son apropiadas
- ✅ Memoria se guarda correctamente
- ✅ Bonos se activan contextualmente
- ✅ Base de datos se consulta (si está disponible)

### 3. Migración a Twilio (cuando sea necesario)
```bash
# 1. El webhook real ya tiene la funcionalidad
# 2. Solo cambiar ConsoleTwilioClient por TwilioWhatsAppClient
# 3. Probar con Twilio real
```

## 📈 Ventajas del Desarrollo con Simulador

### 🚀 Velocidad
- **Iteración inmediata**: Sin esperar webhooks
- **Debug completo**: Ver todo el proceso
- **Pruebas exhaustivas**: Sin límites de uso

### 💰 Economía
- **Sin costos de Twilio**: No gastas créditos
- **Sin límites de uso**: Pruebas ilimitadas
- **Desarrollo continuo**: Sin restricciones

### 🐛 Calidad
- **Logs detallados**: Todo queda registrado
- **Memoria persistente**: Pruebas realistas
- **Debug visual**: Separadores claros

## 📋 Checklist de Desarrollo

### Antes de Implementar Nueva Funcionalidad
- [ ] ¿Funciona en el simulador?
- [ ] ¿Se guarda en memoria correctamente?
- [ ] ¿Los logs son claros?
- [ ] ¿La respuesta es apropiada?
- [ ] ¿Los bonos se activan correctamente?

### Antes de Migrar a Twilio
- [ ] ¿Todas las pruebas pasan en simulador?
- [ ] ¿La memoria funciona correctamente?
- [ ] ¿Los logs son consistentes?
- [ ] ¿La funcionalidad está completa?

## 🎯 Próximos Pasos de Desarrollo

### Funcionalidades Pendientes
1. **Sistema de Cursos Completo**
   - Integración completa con base de datos
   - Información dinámica de cursos
   - Precios y descripciones actualizadas

2. **Sistema de Bonos Avanzado**
   - Más tipos de bonos
   - Activación más inteligente
   - Tracking de bonos mostrados

3. **Análisis de Intención Mejorado**
   - Más categorías específicas
   - Mejor extracción de información
   - Buyer personas más detalladas

4. **Herramientas de Conversión**
   - Integración con calendario
   - Sistema de citas
   - Seguimiento de leads

## 📞 Soporte y Debug

### Comandos Útiles
```bash
# Ver logs de conversación
python view_conversation_logs.py

# Limpiar logs
python clear_conversation_logs.py

# Probar conexión a base de datos
python test_supabase_connection.py
```

### Archivos de Debug
- **Logs de conversación**: `logs/webhook_simulation_log_*.json`
- **Memoria de usuario**: `memorias/memory_*.json`
- **Debug prints**: En consola durante ejecución

## 🎉 Conclusión

El **Simulador de Webhook** es la herramienta principal para el desarrollo del sistema Brenda. Permite:

- ✅ **Desarrollo rápido** sin dependencias externas
- ✅ **Pruebas exhaustivas** sin costos
- ✅ **Debug completo** de todas las funcionalidades
- ✅ **Funcionalidad idéntica** al webhook real

**A partir de ahora, todo el desarrollo se realizará a través del simulador, y cuando esté listo, automáticamente funcionará en Twilio.**

---

*Última actualización: 28 de Julio, 2025*
*Versión del simulador: 1.0.0* 