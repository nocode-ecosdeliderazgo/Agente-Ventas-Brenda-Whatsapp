# Migración técnica a WhatsApp (Twilio)

## Pasos principales
1. Eliminar dependencias de Telegram y adaptar lógica de handlers a WhatsApp.
2. Usar TwilioService para envío de mensajes (texto y multimedia).
3. Recibir mensajes entrantes vía webhook (FastAPI).
4. Adaptar prompts y plantillas para formato WhatsApp (sin botones inline avanzados).
5. Probar envío y recepción con números verificados y credenciales reales.

## Diferencias clave con Telegram
- WhatsApp requiere plantillas preaprobadas para mensajes outbound a usuarios nuevos.
- El formato de mensajes es más limitado (no hay botones inline, solo texto, imagen, video, documento).
- El webhook de Twilio debe estar expuesto públicamente (ngrok o despliegue en cloud).
- El número de Twilio debe estar habilitado para WhatsApp Business API.

## Recomendaciones
- Centralizar toda la lógica de canal en servicios y handlers.
- Validar autenticidad de los webhooks de Twilio.
- Probar primero con mensajes de texto antes de multimedia.
- Documentar cada punto de integración con TODOs claros. 