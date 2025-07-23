# config/ - Configuración y Variables de Entorno

Esta carpeta centraliza la configuración del bot Brenda, incluyendo credenciales y parámetros de servicios externos.

## Componentes principales
- **twilio_settings.py**: Carga y valida las credenciales de Twilio desde variables de entorno.
- Otros archivos de configuración para OpenAI, base de datos, etc. pueden agregarse aquí.

## Buenas prácticas
- Nunca subas archivos con credenciales reales al repositorio.
- Usa variables de entorno y un archivo `.env` para gestionar credenciales.
- Si agregas una nueva integración, crea un archivo de configuración aquí y documenta las variables necesarias.

## Archivo .env
- El archivo `.env` (no versionado) debe contener todas las credenciales necesarias:
  - TWILIO_ACCOUNT_SID
  - TWILIO_AUTH_TOKEN
  - TWILIO_PHONE_NUMBER
  - OPENAI_API_KEY
  - DATABASE_URL
- Si necesitas agregar más credenciales, simplemente añade una nueva línea en `.env` y actualiza el archivo de ejemplo `.env.example`. 