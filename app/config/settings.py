"""
Configuración centralizada de la aplicación usando Pydantic.
Aquí van todas las credenciales y configuraciones de APIs.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import logging


class Settings(BaseSettings):
    """Configuración principal de la aplicación."""
    
    # === TWILIO CREDENTIALS ===
    twilio_account_sid: str
    twilio_auth_token: str  
    twilio_phone_number: str
    
    # === OPENAI CREDENTIALS ===
    openai_api_key: str
    
    # === DATABASE ===
    database_url: Optional[str] = None
    
    # === APPLICATION SETTINGS ===
    app_environment: str = "development"
    log_level: str = "INFO"
    webhook_verify_signature: bool = False
    
    # === ADVISOR CONFIGURATION ===
    advisor_phone_number: str = "+52 1 56 1468 6075"
    advisor_name: str = "Especialista en IA"
    advisor_title: str = "Asesor Comercial"
    
    # === SECURITY ===
    allowed_webhook_ips: str = "*"  # En producción, especificar IPs de Twilio como lista JSON
    
    # === NGROK CONFIGURATION ===
    ngrok_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignora variables extra del .env
        
    def get_log_level(self) -> int:
        """Convierte string log level a constante de logging."""
        return getattr(logging, self.log_level.upper(), logging.INFO)
        
    @property
    def is_production(self) -> bool:
        """Verifica si estamos en producción."""
        return self.app_environment.lower() == "production"
        
    @property
    def is_development(self) -> bool:
        """Verifica si estamos en desarrollo."""
        return self.app_environment.lower() == "development"
        
    def get_allowed_webhook_ips(self) -> list[str]:
        """Obtiene la lista de IPs permitidas para webhooks."""
        if self.allowed_webhook_ips == "*":
            return ["*"]
        try:
            import json
            return json.loads(self.allowed_webhook_ips)
        except (json.JSONDecodeError, TypeError):
            # Si no es JSON válido, tratar como una sola IP
            return [self.allowed_webhook_ips] if self.allowed_webhook_ips else []


# Instancia global de configuración
settings = Settings()