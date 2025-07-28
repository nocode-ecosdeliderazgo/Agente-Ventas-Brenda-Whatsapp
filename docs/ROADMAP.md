# ROADMAP MIGRACIÓN WHATSAPP (TWILIO)

## Fase 1: Modularización y limpieza
- [x] Separar lógica en core, handlers, services, memory, prompts, config
- [x] Eliminar dependencias de Telegram
- [x] Centralizar prompts y plantillas para WhatsApp

## Fase 2: Integración Twilio básica
- [x] Servicio de envío WhatsApp/SMS (Twilio)
- [ ] Webhook de recepción de mensajes entrantes (FastAPI)
- [ ] Adaptar handlers para entrada/salida vía Twilio

## Fase 3: Adaptación de herramientas y flujos
- [ ] Adaptar 35+ herramientas para WhatsApp (formato mensajes, multimedia)
- [ ] Pruebas de envío de PDFs, imágenes, videos
- [ ] Validación de respuestas y errores Twilio

## Fase 4: Integración avanzada
- [ ] Manejo de plantillas preaprobadas WhatsApp
- [ ] Recepción y procesamiento de multimedia entrante
- [ ] Integración con CRM y analítica avanzada

## Puntos bloqueados
- [ ] Falta de credenciales Twilio Business API para pruebas reales
- [ ] Falta de números verificados para pruebas WhatsApp

## Notas
- Toda la lógica de Telegram ha sido removida o marcada como legacy.
- El bot es 100% modular y listo para escalar.
- Consultar este roadmap antes de avanzar a producción. 