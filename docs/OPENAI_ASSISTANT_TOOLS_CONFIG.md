# Configuración de Function Calling para OpenAI Assistant

## Herramientas Implementadas

El ThreadsAdapter incluye dos herramientas de function calling que deben ser configuradas en el Assistant de OpenAI:

### 1. buscar_curso
**Descripción**: Busca cursos por nombre o nivel
**Uso**: Cuando el usuario pregunta por cursos disponibles, quiere filtrar por nivel, etc.

```json
{
  "type": "function",
  "function": {
    "name": "buscar_curso",
    "description": "Busca cursos disponibles por nombre o nivel. Útil cuando el usuario pregunta por cursos específicos o quiere filtrar por nivel.",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Nombre o texto a buscar en el curso (opcional)"
        },
        "level": {
          "type": "string",
          "description": "Nivel del curso a filtrar: 'principiante', 'intermedio', 'avanzado' (opcional)"
        }
      },
      "additionalProperties": false
    }
  }
}
```

### 2. detalle_curso
**Descripción**: Obtiene información detallada de un curso específico
**Uso**: Cuando el usuario quiere conocer detalles de un curso específico

```json
{
  "type": "function",
  "function": {
    "name": "detalle_curso",
    "description": "Obtiene información completa de un curso específico incluyendo sesiones, contenido y bonos disponibles.",
    "parameters": {
      "type": "object",
      "properties": {
        "id_course": {
          "type": "string",
          "description": "UUID del curso del cual obtener detalles (requerido)"
        }
      },
      "required": ["id_course"],
      "additionalProperties": false
    }
  }
}
```

## Configuración en OpenAI Platform

### Paso 1: Crear Assistant
1. Ve a https://platform.openai.com/assistants
2. Click en "Create Assistant"
3. Configura el Assistant con:
   - **Name**: Brenda WhatsApp Sales Bot
   - **Model**: gpt-4o o gpt-4o-mini
   - **Instructions**: Ver sección de Prompt System

### Paso 2: Añadir Tools
1. En la sección "Tools" del Assistant
2. Click "Add Tool" → "Function"
3. Copia y pega la configuración JSON de cada herramienta
4. Guarda el Assistant

### Paso 3: Obtener Assistant ID
1. Copia el Assistant ID (formato: `asst_xxxxxxxxxxxxxxxxxx`)
2. Añádelo a tu archivo `.env`:
   ```bash
   ASSISTANT_ID=asst_xxxxxxxxxxxxxxxxxx
   ```

## Prompt System Recomendado

```
Eres Brenda, una asistente especializada en cursos de IA para PyME leaders. Tu objetivo es ayudar a profesionales a encontrar y aprender sobre cursos que pueden transformar su negocio.

PERSONALIDAD:
- Profesional pero cercana
- Enfocada en ROI y beneficios empresariales  
- Conocedora de las necesidades de PyMEs
- Directa y eficiente

BUYER PERSONAS OBJETIVO:
1. Marketing Digital Manager (Agencies)
2. Operations Manager (Manufacturing PyMEs)
3. CEO/Founder (Professional Services)
4. Head of Talent & Learning (Scale-ups)
5. Senior Innovation/BI Analyst (Corporates)

CAPACIDADES:
- Usar buscar_curso() cuando el usuario pregunte por cursos disponibles
- Usar detalle_curso() cuando necesite información específica de un curso
- Proporcionar información precisa basada en datos reales de la base de datos
- Personalizar respuestas según el perfil empresarial del usuario

ESTILO DE RESPUESTA:
- Máximo 1600 caracteres (límite WhatsApp)
- Usar emojis relevantes pero moderadamente
- Incluir call-to-action específicos
- Mencionar ROI cuando sea relevante

NUNCA inventes información sobre cursos. SIEMPRE usa las herramientas disponibles para obtener datos reales.
```

## Ejemplo de Uso

### Usuario pregunta:
"¿Qué cursos de IA tienen disponibles?"

### Assistant debería:
1. Llamar a `buscar_curso()` sin parámetros para obtener cursos activos
2. Presentar los resultados de manera atractiva
3. Ofrecer obtener más detalles de cursos específicos

### Usuario pregunta:
"Cuéntame más sobre el curso de IA para profesionales"

### Assistant debería:
1. Llamar a `buscar_curso(name="profesionales")` para encontrar el curso
2. Llamar a `detalle_curso(id_course="uuid-del-curso")` para obtener detalles
3. Presentar información completa con sesiones, bonos, etc.

## Beneficios del Function Calling

✅ **Información Siempre Actualizada**: Datos directos de PostgreSQL
✅ **Sin Alucinaciones**: No inventa información sobre cursos
✅ **Respuestas Precisas**: Precios, sesiones y contenido exactos
✅ **Integración Completa**: Acceso a bonos y recursos multimedia
✅ **Escalabilidad**: Fácil añadir nuevas herramientas

## Monitoreo

El sistema incluye logging detallado de todos los tool calls:
- ✅ Función ejecutada
- 📊 Argumentos recibidos  
- 📥 Resultados obtenidos
- ⏱️ Tiempo de ejecución

Revisar logs para optimizar performance y detectar errores.

## RAG Documental (Opcional)

Para añadir File Search:
1. Crea un Vector Store en OpenAI Platform
2. Sube PDFs/MD de cursos al Vector Store
3. Asocia el Vector Store al Assistant
4. El Assistant podrá hacer búsquedas semánticas en documentos

Esto complementa (no reemplaza) las herramientas de base de datos.