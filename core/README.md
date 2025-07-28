# core/ - Núcleo Lógico del Bot Brenda

Esta carpeta contiene los componentes centrales de la lógica del bot Brenda para WhatsApp.

## ¿Qué debe ir aquí?
- Agentes principales (ej. whatsapp_agent.py): lógica de orquestación y flujo conversacional.
- Análisis de intención (intent_analyzer.py): clasificación de mensajes y activación de herramientas.
- Coordinadores de herramientas y lógica de negocio principal.

## ¿Qué NO debe ir aquí?
- Lógica específica de canal (eso va en handlers/ o services/).
- Plantillas de mensajes o prompts (eso va en prompts/).
- Acceso directo a la base de datos o servicios externos (eso va en services/).
- Lógica de persistencia de memoria (eso va en memory/).

## Buenas prácticas
- Mantener la lógica de orquestación y decisión centralizada aquí.
- Usar servicios y módulos externos a través de interfaces bien definidas.
- No acoplar lógica de canal ni detalles de integración aquí.

## Ejemplo de uso
```python
from core.whatsapp_agent import procesar_mensaje_entrante
from core.intent_analyzer import IntentAnalyzer
``` 