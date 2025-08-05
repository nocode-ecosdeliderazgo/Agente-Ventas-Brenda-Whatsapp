#!/usr/bin/env python3
"""
Servidor webhook para Bot Brenda - Sistema completo de IA
=========================================================

Este script inicia el servidor webhook que:
1. Recibe mensajes de WhatsApp via Twilio
2. Procesa con IA (OpenAI GPT-4) y memoria persistente
3. Responde de forma inteligente según el contexto
4. Usa la arquitectura limpia Clean Architecture

Para probar:
1. Ejecuta este script
2. Usa ngrok para exponer el webhook públicamente  
3. Configura la URL del webhook en tu consola de Twilio
4. Envía un mensaje WhatsApp a tu número de Twilio

Uso:
    python run_webhook_server.py
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import os

# Agregar el directorio raíz al path (temporal hasta refactor completo)
project_root = Path(__file__).parent
sys.path.append(str(project_root))

import uvicorn
from app.config import settings

def setup_logging():
    """Configurar sistema de logging con rotación y múltiples handlers."""
    
    # Crear directorio de logs si no existe
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Configurar formateador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Handler para archivo con rotación (10MB, 5 archivos)
    file_handler = RotatingFileHandler(
        logs_dir / "brenda_webhook.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.get_log_level())
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return logging.getLogger(__name__)

def main():
    """Función principal para iniciar el servidor."""
    
    # Configurar logging
    logger = setup_logging()
    
    logger.info("🚀 INICIANDO SERVIDOR WEBHOOK - BOT BRENDA")
    logger.info("=" * 50)
    logger.info(f"🌍 Entorno: {settings.app_environment}")
    logger.info(f"📱 Número Twilio: {settings.twilio_phone_number}")
    logger.info(f"🔧 Log Level: {settings.log_level}")
    logger.info(f"🔐 Verificar firma: {settings.webhook_verify_signature}")
    logger.info("=" * 50)
    
    if settings.is_development:
        logger.info("\n📝 INSTRUCCIONES PARA DESARROLLO:")
        logger.info("1. Este servidor se ejecutará en http://localhost:8000")
        logger.info("2. Para que Twilio pueda enviar webhooks, necesitas usar ngrok:")
        logger.info("   - Instala ngrok: https://ngrok.com/")
        logger.info("   - En otra terminal ejecuta: ngrok http 8000")
        logger.info("   - Copia la URL https:// que te proporcione ngrok")
        logger.info("   - Ve a tu consola de Twilio y configura esa URL como webhook")
        logger.info("   - La URL completa sería: https://tu-ngrok-url.ngrok.io/webhook/whatsapp")
        logger.info("\n🎯 FUNCIONALIDAD ACTUAL:")
        logger.info("- Sistema completo con IA (OpenAI GPT-4)")
        logger.info("- Memoria persistente por usuario")
        logger.info("- Análisis inteligente de intenciones")
        logger.info("- Respuestas contextuales personalizadas")
        logger.info("- Sistema de flujos de privacidad y cursos")
        logger.info("- Logs estructurados con rotación automática")
        logger.info("\n🔄 Para probar:")
        logger.info("1. Configura el webhook en Twilio")
        logger.info("2. Envía un mensaje WhatsApp a tu número de Twilio")
        logger.info("3. El bot responderá de forma inteligente según el contexto")
        logger.info("=" * 50)
    
    try:
        logger.info("🌐 Iniciando servidor FastAPI en puerto 8000...")
        logger.info(f"📊 Configuración Uvicorn:")
        logger.info(f"   - Host: 0.0.0.0")
        logger.info(f"   - Port: 8000")
        logger.info(f"   - Reload: {settings.is_development}")
        logger.info(f"   - Log Level: {settings.log_level.lower()}")
        
        uvicorn.run(
            "app.presentation.api.webhook:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.is_development,
            log_level=settings.log_level.lower(),
            access_log=True,
            # Configuraciones de producción
            limit_concurrency=100 if settings.is_production else None,
            timeout_keep_alive=30 if settings.is_production else 5
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ Servidor detenido por el usuario")
        logger.info("👋 ¡Hasta luego!")
    except Exception as e:
        logger.exception(f"💥 Error crítico iniciando servidor")
        logger.error(f"Detalles del error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()