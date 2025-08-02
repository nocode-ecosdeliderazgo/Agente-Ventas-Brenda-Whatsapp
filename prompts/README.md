# prompts/ - Documentación de Prompts del Bot Brenda
prueba
Esta carpeta centraliza todos los prompts y plantillas de mensajes utilizados por el bot Brenda para WhatsApp.

## Estructura de Prompts

- **agent_prompts.py**: Contiene el prompt principal del agente (Brenda), incluyendo la personalidad, reglas de oro, tono y directrices generales para la IA. Aquí también se pueden incluir prompts globales para el flujo conversacional general.

- **tool_prompts.py**: Contiene los prompts y plantillas específicos para cada herramienta de conversión (recursos gratuitos, bonos, demos, cierre, etc.). Cada función o herramienta debe tener su propio mensaje o plantilla aquí, adaptado al formato de WhatsApp.

## Buenas prácticas
- Mantén los prompts lo más parametrizados posible (usa variables para nombre, rol, etc.).
- No mezcles lógica de negocio ni procesamiento de datos aquí, solo plantillas y textos.
- Si una herramienta nueva requiere un mensaje especial, agrégalo en tool_prompts.py.
- Si el prompt afecta a todo el agente o la conversación, agrégalo en agent_prompts.py.

## Ejemplo de uso
```python
from prompts.agent_prompts import SYSTEM_PROMPT
from prompts.tool_prompts import get_free_resources_message
```

## Notas
- Todos los prompts deben estar en español y adaptados para WhatsApp (sin botones inline avanzados).
- Si necesitas prompts para canales distintos, crea archivos separados por canal. 