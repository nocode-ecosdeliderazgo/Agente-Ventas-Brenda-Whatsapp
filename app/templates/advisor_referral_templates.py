"""
Plantillas para referir usuarios a asesores humanos.
Optimizadas para WhatsApp con información de contacto del asesor.
"""

from app.config.settings import settings


class AdvisorReferralTemplates:
    """Plantillas para referir usuarios a asesores comerciales."""
    
    @staticmethod
    def advisor_referral_message(user_name: str = "") -> str:
        """
        Mensaje de confirmación al usuario de que un asesor lo contactará.
        
        Args:
            user_name: Nombre del usuario (opcional)
            
        Returns:
            Mensaje formateado para WhatsApp
        """
        greeting = f"¡Perfecto, {user_name}!" if user_name else "¡Perfecto!"
        
        return f"""{greeting} 

He recibido tu solicitud para hablar con un asesor especializado en IA. 

📞 **Un {settings.advisor_title} se contactará contigo muy pronto** para ayudarte de manera personalizada con todas tus dudas sobre nuestros cursos.

⏰ **Tiempo estimado de contacto**: Dentro de las próximas 2 horas en horario laboral (9 AM - 6 PM, México).

Mientras tanto, puedes seguir preguntándome cualquier duda que tengas sobre IA y nuestros cursos.

¡Gracias por tu interés! 🚀"""

    @staticmethod
    def advisor_referral_with_context(user_name: str, user_role: str, specific_interest: str = "") -> str:
        """
        Mensaje de confirmación personalizado al usuario de que un asesor lo contactará.
        
        Args:
            user_name: Nombre del usuario
            user_role: Rol/cargo del usuario
            specific_interest: Interés específico mencionado por el usuario
            
        Returns:
            Mensaje personalizado para WhatsApp
        """
        context_info = f"sobre {specific_interest}" if specific_interest else "sobre IA"
        
        return f"""¡Excelente, {user_name}! 

Como {user_role}, entiendo que tienes necesidades muy específicas de IA. He enviado tu solicitud a nuestro {settings.advisor_title} especializado en trabajar con profesionales en tu área.

📞 **Un asesor se contactará contigo muy pronto** para ayudarte de manera personalizada {context_info}.

⏰ **Tiempo estimado de contacto**: Dentro de las próximas 2 horas en horario laboral (9 AM - 6 PM, México).

El {settings.advisor_title} podrá ofrecerte:
✅ Análisis personalizado de tu caso como {user_role}
✅ Recomendaciones específicas para tu industria  
✅ Propuesta de implementación de IA en tu área
✅ Precios corporativos y facilidades de pago

Mientras esperamos su contacto, ¿hay algo más en lo que pueda ayudarte? 🎯"""

    @staticmethod
    def advisor_not_available_fallback() -> str:
        """
        Mensaje de respaldo cuando el asesor no está disponible.
        
        Returns:
            Mensaje con información alternativa
        """
        return f"""Te conectaré con nuestro {settings.advisor_title} especializado.

👨‍💼 **{settings.advisor_name}**
📱 **{settings.advisor_phone_number}**

*Horarios de atención:*
📅 Lunes a Viernes: 9:00 AM - 6:00 PM (México)
📅 Sábados: 10:00 AM - 2:00 PM (México)

*Para contactarlo:*
1️⃣ Haz clic en: {settings.advisor_phone_number}
2️⃣ Menciónale que vienes de parte de Brenda
3️⃣ Si no responde inmediatamente, déjale un mensaje y él te contactará pronto

¡Estoy segura de que podrá ayudarte con todo lo que necesitas! 😊"""

    @staticmethod
    def advisor_follow_up_message() -> str:
        """
        Mensaje de seguimiento después de referir al asesor.
        
        Returns:
            Mensaje de seguimiento
        """
        return f"""¿Ya pudiste contactar a nuestro {settings.advisor_title}? 

Si tienes algún problema para comunicarte con él, puedes:
📱 Intentar nuevamente: {settings.advisor_phone_number}
💬 Dejarle un mensaje mencionando que vienes de parte de Brenda

Mientras tanto, ¿hay algo más en lo que pueda ayudarte sobre nuestros cursos de IA?"""

    @staticmethod
    def urgent_contact_message() -> str:
        """
        Mensaje para casos urgentes o de alta prioridad.
        
        Returns:
            Mensaje con información de contacto prioritario
        """
        return f"""¡Entiendo que es urgente! 🚨

He marcado tu solicitud como PRIORIDAD y he notificado inmediatamente a nuestro {settings.advisor_title}.

📞 **Se contactará contigo INMEDIATAMENTE** para atender tu caso urgente.

⚡ **Tiempo estimado de contacto**: Dentro de los próximos 30 minutos.

Si no recibes el contacto en ese tiempo, por favor escríbeme nuevamente mencionando "URGENTE" y escalaré tu caso.

¡Te atenderá con la prioridad que mereces! ⚡"""

    @staticmethod
    def advisor_notification_message(user_phone: str, user_name: str, user_role: str, specific_interest: str = "", urgency_level: str = "normal") -> str:
        """
        Mensaje que se envía al asesor para notificarle sobre un nuevo lead.
        
        Args:
            user_phone: Número de teléfono del usuario
            user_name: Nombre del usuario
            user_role: Rol/cargo del usuario
            specific_interest: Interés específico mencionado
            urgency_level: Nivel de urgencia (normal, high, urgent)
            
        Returns:
            Mensaje formateado para enviar al asesor
        """
        urgency_emoji = {
            'normal': '📞',
            'high': '🔥', 
            'urgent': '🚨'
        }
        
        urgency_text = {
            'normal': 'NUEVO LEAD',
            'high': 'LEAD PRIORITARIO',
            'urgent': 'LEAD URGENTE - CONTACTAR INMEDIATAMENTE'
        }
        
        emoji = urgency_emoji.get(urgency_level, '📞')
        priority = urgency_text.get(urgency_level, 'NUEVO LEAD')
        
        interest_line = f"• **Interés específico**: {specific_interest}" if specific_interest else "• **Consulta**: General sobre IA"
        
        return f"""{emoji} **{priority}** {emoji}

Un usuario ha solicitado contacto con un asesor a través de Brenda (el bot).

**DATOS DEL LEAD:**
• **Nombre**: {user_name}
• **Cargo/Rol**: {user_role}
• **Teléfono**: {user_phone}
{interest_line}
• **Urgencia**: {urgency_level.upper()}

**ACCIÓN REQUERIDA:**
Contactar al usuario lo antes posible vía WhatsApp al número proporcionado.

**MENSAJE SUGERIDO:**
"Hola {user_name}, soy el Asesor Comercial de Aprenda y Aplique IA. Brenda me notificó que necesitas asesoría sobre nuestros cursos de IA. ¿Cómo puedo ayudarte?"

⏰ **Generado por**: Brenda Bot
📅 **Fecha**: {AdvisorReferralTemplates._get_current_timestamp()}"""

    @staticmethod
    def _get_current_timestamp() -> str:
        """Obtiene timestamp actual formateado."""
        from datetime import datetime
        import pytz
        
        # Timezone de México
        mexico_tz = pytz.timezone('America/Mexico_City')
        now = datetime.now(mexico_tz)
        return now.strftime("%d/%m/%Y %H:%M:%S México")