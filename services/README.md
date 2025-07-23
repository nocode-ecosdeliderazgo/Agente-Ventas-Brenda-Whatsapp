# services/ - Integraciones Externas y Servicios

Esta carpeta contiene todos los servicios que interactúan con APIs externas, bases de datos, y otros sistemas fuera del bot Brenda.

## Componentes principales
- **twilio_service.py**: Servicio para enviar mensajes SMS y WhatsApp usando la API de Twilio. Debe ser el único punto de acceso para enviar mensajes salientes.
- Otros servicios futuros: conexión a base de datos, OpenAI, recursos multimedia, etc.

## Buenas prácticas
- Cada integración externa debe tener su propio archivo de servicio.
- No mezcles lógica de negocio ni prompts aquí, solo integración y adaptación de datos.
- Maneja y reporta errores de forma clara y estructurada.
- Centraliza la configuración de credenciales en config/.

## TwilioService
- Métodos: enviar_sms, enviar_whatsapp, (futuro: enviar_multimedia, plantillas)
- No almacena estado, solo actúa como puente entre el bot y Twilio.
- Si necesitas agregar nuevas funciones (ej. multimedia), hazlo aquí y documenta los cambios.

## Ejemplo de uso
```python
from services.twilio_service import TwilioService
``` 