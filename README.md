# Bot de Ventas Inteligente (Brenda) - WhatsApp (Twilio)

## Objetivo
Migrar y modernizar el bot de ventas "Brenda" para operar 100% sobre WhatsApp usando Twilio, con arquitectura modular, escalable y lista para producción.

## Componentes funcionales migrados
- Motor de IA conversacional (OpenAI GPT-4o-mini)
- Sistema de memoria persistente por usuario
- 35+ herramientas de conversión (recursos, demos, bonos, cierre, etc.)
- Activación inteligente de herramientas según intención
- Base de datos PostgreSQL (async)
- Flujos de conversación: Ads, cursos, contacto, FAQ
- Lead scoring y seguimiento
- Validación anti-alucinación

## Estructura modular (carpetas principales)
- `core/`         → Lógica principal, agentes, servicios
- `handlers/`     → Flujos conversacionales
- `services/`     → Integraciones externas (Twilio, OpenAI, BD)
- `memory/`       → Gestión de memoria y persistencia
- `prompts/`      → Prompts y plantillas centralizadas
- `config/`       → Configuración y variables de entorno
- `docs/`         → Documentación y roadmap
- `legacy/`       → Código obsoleto o en revisión
- `tests/`        → Pruebas unitarias e integración

## Instrucciones de uso
1. Copia tu archivo `.env.example` a `.env` y completa las variables:
   - TWILIO_ACCOUNT_SID
   - TWILIO_AUTH_TOKEN
   - TWILIO_PHONE_NUMBER
   - OPENAI_API_KEY
   - DATABASE_URL
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta el bot principal (ver documentación en `core/agents/` y `handlers/`).

## Migración a WhatsApp (Twilio)
- Toda la lógica de envío/recepción de mensajes se realiza vía Twilio.
- Los prompts y plantillas han sido adaptados para WhatsApp (sin dependencias de Telegram).
- Los handlers y servicios están preparados para recibir webhooks de Twilio.
- Verifica la configuración en `config/twilio_settings.py`.
- Consulta `docs/ROADMAP.md` para el estado de la migración y próximos pasos.

---

> **Nota:** Si necesitas soporte para flujos especiales, integración CRM, analítica avanzada o multi-idioma, revisa el roadmap o solicita la extensión correspondiente.