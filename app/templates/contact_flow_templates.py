#!/usr/bin/env python3
"""
Templates para el flujo de contacto con asesores.
"""

from typing import Dict, Any


class ContactFlowTemplates:
    """
    Templates para mensajes del flujo de contacto.
    """
    
    @staticmethod
    def get_contact_welcome_message(user_name: str) -> str:
        """
        Mensaje de bienvenida al flujo de contacto.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Mensaje de bienvenida
        """
        return f"""¡Hola {user_name}! 😊

Perfecto, entiendo que quieres hablar con un asesor especializado. 

Para conectar con el asesor más adecuado para ti, necesito que me cuentes brevemente:

🤔 **¿Cuál es el motivo principal de tu consulta?**

Por ejemplo:
• Dudas sobre el curso
• Información de precios
• Implementación en mi empresa
• Casos de éxito específicos
• Requisitos especiales

Cuéntame en tus propias palabras y te conectaré con el asesor ideal para tu situación. 📞"""
    
    @staticmethod
    def get_contact_confirmation_message(user_name: str, contact_info: Dict[str, Any]) -> str:
        """
        Mensaje de confirmación con la información recopilada.
        
        Args:
            user_name: Nombre del usuario
            contact_info: Información recopilada
            
        Returns:
            Mensaje de confirmación
        """
        reason = contact_info.get('contact_reason', 'Consulta general')
        role = contact_info.get('user_role', 'No especificado')
        company_size = contact_info.get('company_size', 'No especificado')
        industry = contact_info.get('industry', 'No especificado')
        
        return f"""Perfecto {user_name}! ✅

He recopilado la siguiente información para tu solicitud de contacto:

📋 **Detalles de tu consulta:**
• **Motivo:** {reason}
• **Tu rol:** {role}
• **Tamaño empresa:** {company_size}
• **Industria:** {industry}

👨‍💼 **Próximos pasos:**
1. Un asesor especializado revisará tu solicitud
2. Te contactará en las próximas 2-4 horas
3. Tendrás una consulta personalizada

¿Confirmas que esta información es correcta y procedo a enviar tu solicitud?

Responde "Sí" o "Confirmo" para continuar, o cuéntame si necesitas ajustar algo. 👍"""
    
    @staticmethod
    def get_contact_success_message(user_name: str) -> str:
        """
        Mensaje de éxito cuando se confirma el contacto.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Mensaje de éxito
        """
        return f"""¡Excelente {user_name}! 🎉

✅ **Tu solicitud de contacto ha sido enviada exitosamente**

📞 **Lo que sucede ahora:**
• Tu solicitud está siendo revisada por nuestro equipo
• Un asesor especializado te contactará en las próximas 2-4 horas
• Tendrás una consulta personalizada y sin compromiso

⏰ **Tiempo de respuesta:** 2-4 horas (horario laboral)

📱 **Formas de contacto del asesor:**
• WhatsApp (este mismo número)
• Llamada telefónica
• Email (si lo prefieres)

💡 **Mientras esperas:**
¿Te gustaría que te envíe información adicional sobre nuestros cursos o casos de éxito? Solo dime qué te interesa más.

¡Gracias por tu paciencia! Tu asesor se pondrá en contacto contigo muy pronto. 😊"""
    
    @staticmethod
    def get_contact_retry_message(user_name: str) -> str:
        """
        Mensaje cuando el usuario no confirma y se solicita nueva información.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Mensaje de reintento
        """
        return f"""No hay problema {user_name}! 😊

Entiendo que quizás necesitas ajustar algo o tienes dudas. 

Por favor, cuéntame nuevamente:

🤔 **¿Cuál es el motivo principal de tu consulta?**

O si prefieres, puedes ser más específico sobre:
• ¿Qué tipo de información necesitas?
• ¿Tienes alguna duda específica?
• ¿Hay algo en particular que te preocupe?

Estoy aquí para ayudarte a conectar con el asesor perfecto para tu situación. 📞"""
    
    @staticmethod
    def get_contact_pending_message(user_name: str) -> str:
        """
        Mensaje cuando el usuario ya tiene una solicitud pendiente.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Mensaje de solicitud pendiente
        """
        return f"""¡Hola {user_name}! 😊

Veo que ya tienes una solicitud de contacto en proceso. 

📋 **Estado de tu solicitud:** En revisión

⏰ **Tiempo estimado de respuesta:** 2-4 horas

👨‍💼 **Tu asesor especializado se pondrá en contacto contigo muy pronto.**

Mientras tanto, ¿hay algo más en lo que pueda ayudarte? Por ejemplo:
• Información adicional sobre nuestros cursos
• Casos de éxito específicos
• Preguntas sobre la implementación

¡Tu asesor llegará pronto! 🚀"""
    
    @staticmethod
    def get_contact_already_processed_message(user_name: str) -> str:
        """
        Mensaje cuando el usuario ya tuvo contacto procesado.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Mensaje de contacto ya procesado
        """
        return f"""¡Hola {user_name}! 😊

Veo que ya tuviste contacto con uno de nuestros asesores anteriormente.

¿Te gustaría:
1. **Nueva consulta** - Si tienes una nueva pregunta o situación
2. **Seguimiento** - Si necesitas seguimiento de tu consulta anterior
3. **Información adicional** - Si quieres más detalles sobre nuestros servicios

¿Cuál de estas opciones te interesa más? 

O si prefieres, puedes contarme directamente qué necesitas y te ayudo a conectar con el asesor más adecuado. 📞"""
    
    @staticmethod
    def get_contact_error_message(user_name: str) -> str:
        """
        Mensaje de error en el flujo de contacto.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Mensaje de error
        """
        return f"""Lo siento {user_name}, hubo un pequeño problema procesando tu solicitud de contacto. 😔

Por favor, intenta de nuevo en unos minutos o puedes:

📞 **Contactarnos directamente:**
• WhatsApp: +[número de contacto]
• Email: [email de contacto]

🔧 **Alternativa:**
¿Te gustaría que te envíe información detallada sobre nuestros servicios mientras tanto?

¡Disculpa las molestias! Tu consulta es importante para nosotros. 🙏"""
    
    @staticmethod
    def get_contact_urgent_message(user_name: str) -> str:
        """
        Mensaje especial para solicitudes urgentes.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Mensaje de urgencia
        """
        return f"""¡Entendido {user_name}! 🚨

Veo que tu consulta es urgente. He marcado tu solicitud como prioritaria.

⚡ **Procesamiento prioritario:**
• Tu solicitud será revisada inmediatamente
• Un asesor te contactará en las próximas 30-60 minutos
• Atención especial por ser urgente

📞 **Contacto inmediato disponible:**
Si necesitas atención inmediata, puedes llamar directamente al: +[número de emergencia]

⏰ **Tiempo de respuesta:** 30-60 minutos

¡Tu asesor se pondrá en contacto contigo lo antes posible! 🚀"""
    
    @staticmethod
    def get_contact_follow_up_message(user_name: str, advisor_name: str, contact_time: str) -> str:
        """
        Mensaje de seguimiento después del contacto.
        
        Args:
            user_name: Nombre del usuario
            advisor_name: Nombre del asesor
            contact_time: Hora del contacto
            
        Returns:
            Mensaje de seguimiento
        """
        return f"""¡Hola {user_name}! 😊

Espero que hayas tenido una excelente consulta con {advisor_name} a las {contact_time}.

📋 **Seguimiento:**
¿Cómo te fue con la consulta? ¿Tienes alguna pregunta adicional o necesitas más información?

💡 **Recursos adicionales:**
• Casos de éxito específicos
• Información de implementación
• Materiales complementarios

¿Hay algo más en lo que pueda ayudarte? Estoy aquí para apoyarte en todo el proceso. 🤝""" 