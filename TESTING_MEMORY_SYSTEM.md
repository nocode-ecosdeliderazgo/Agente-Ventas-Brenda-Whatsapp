# Testing Enhanced Memory System

Este documento describe cómo probar el sistema de memoria mejorado del bot Brenda.

## 🎯 Qué Sistema Probamos

El sistema de memoria mejorado gestiona **flujos de conversación personalizados**:

```
👤 Usuario nuevo → Primera interacción → Flujo privacidad → 
Selección cursos → Agente ventas inteligente
```

## 🧪 Comando de Prueba Principal

```bash
python3 test_memory_system.py
```

## 📋 Qué Valida el Test

### ✅ Paso 1: Primera Interacción
- Detecta correctamente usuarios nuevos
- Identifica que necesitan flujo de privacidad
- No están listos para agente de ventas

### ✅ Paso 2: Flujo de Privacidad  
- Inicia correctamente el flujo de privacidad
- Cambia stage a `privacy_flow`
- Establece `waiting_for_response = "privacy_acceptance"`

### ✅ Paso 3: Aceptación de Privacidad
- Marca privacidad como aceptada
- Transiciona a `course_selection` stage
- Usuario queda listo para agente de ventas

### ✅ Paso 4: Información del Usuario
- Guarda nombre, rol e intereses correctamente
- Genera contexto rico para el agente
- Mantiene historial de mensajes

### ✅ Paso 5: Agente de Ventas
- Activa correctamente el agente inteligente
- Cambia stage a `sales_agent`
- Flujo cambia a `sales_conversation`

### ✅ Paso 6: Persistencia
- Guarda y carga datos desde JSON
- Preserva toda la información del usuario
- Mantiene compatibilidad hacia atrás

## 🔍 Salida Esperada del Test

```
==================================================
🔍 INICIANDO PRUEBA DEL SISTEMA DE MEMORIA
==================================================

✅ Detección de primera interacción: CORRECTA
✅ Flujo de privacidad: INICIADO CORRECTAMENTE  
✅ Aceptación de privacidad: CORRECTA
✅ Agente de ventas: INICIADO CORRECTAMENTE
✅ Persistencia: FUNCIONANDO CORRECTAMENTE

🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE
```

## 🏗️ Estructura de Archivos de Memoria

Los archivos se guardan en `memorias/`:
```
memorias/
└── memory_5213334567890.json  # Memoria por número de teléfono
```

### Ejemplo de Archivo JSON Generado:
```json
{
  "user_id": "5213334567890",
  "name": "Juan Pérez",
  "role": "Marketing Manager", 
  "stage": "sales_agent",
  "current_flow": "sales_conversation",
  "privacy_accepted": true,
  "interests": ["automatización", "análisis de datos"],
  "interaction_count": 5,
  "message_history": [
    {
      "timestamp": "2025-01-28T...",
      "content": "Hola",
      "phone": "+5213334567890"
    }
  ]
}
```

## ⚡ Tests Rápidos

### Verificar Configuración
```bash
python3 -c "from memory.lead_memory import MemoryManager; print('✅ Memory system ready')"
```

### Verificar Use Cases
```bash
python3 -c "from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase; print('✅ Memory use cases ready')"
```

### Test Solo Detección de Primera Interacción
```python
from memory.lead_memory import MemoryManager, LeadMemory

# Crear usuario nuevo
manager = MemoryManager(memory_dir="test_mem")
memory = manager.get_lead_memory("test_user")

print(f"Primera interacción: {memory.is_first_interaction()}")  # True
print(f"Necesita privacidad: {memory.needs_privacy_flow()}")   # True
print(f"Listo para ventas: {memory.is_ready_for_sales_agent()}") # False
```

## 🚨 Solución de Problemas

### Error: "No such file or directory"
```bash
# El sistema crea directorios automáticamente, pero si hay problemas:
mkdir memorias
chmod 755 memorias
```

### Error: "ModuleNotFoundError"
```bash
# Asegúrate de estar en el directorio correcto:
cd /ruta/al/proyecto/Bot_WhatsApp/Agente-Ventas-Brenda-Whatsapp
python3 test_memory_system.py
```

### Error: Datos Corruptos
```bash
# El sistema crea backups automáticos:
ls memorias/memory_*.json.backup
```

## 🎯 Casos de Uso Reales

### Usuario Primera Vez:
1. Envía "Hola" → `is_first_interaction() = True`
2. Sistema inicia flujo privacidad
3. Usuario acepta → Transición a selección curso
4. Sistema activa agente ventas

### Usuario Recurrente:
1. Envía mensaje → `is_first_interaction() = False`
2. `is_ready_for_sales_agent() = True` 
3. Sistema activa directamente agente ventas

## 📊 Métricas de Performance

El test mide:
- ⏱️ **Tiempo de persistencia**: < 50ms por operación
- 💾 **Tamaño archivo**: ~1-5KB por usuario
- 🔄 **Operaciones**: 6 save/load por test completo
- ✅ **Éxito**: 100% en condiciones normales

## 🔧 Personalización del Test

Para modificar el test:

```python
# Cambiar usuario de prueba
test_user_id = "tu_numero_aqui"

# Cambiar directorio de memorias
memory_manager = MemoryManager(memory_dir="mi_directorio")

# Agregar más verificaciones
assert memory.lead_score >= 50, "Score muy bajo"
```

---

**Estado**: ✅ Sistema completamente funcional  
**Última prueba**: 2025-01-28  
**Compatibilidad**: JSON + futura PostgreSQL