"""
Templates profesionales para el flujo de consentimiento de privacidad en WhatsApp.
Adaptados para WhatsApp sin botones, usando mensajes de texto estructurados.
"""
from typing import Optional

class PrivacyFlowTemplates:
    """
    Templates para el flujo de consentimiento de privacidad.
    Diseñados específicamente para WhatsApp con formato profesional.
    """
    
    @staticmethod
    def privacy_consent_request(whatsapp_name: Optional[str] = None) -> str:
        """
        Mensaje de solicitud de consentimiento de privacidad.
        
        Args:
            whatsapp_name: Nombre extraído de WhatsApp (perfil o contacto)
            
        Returns:
            Mensaje de consentimiento profesional
        """
        # Personalizar saludo según si tenemos nombre o no
        greeting = f"¡Hola {whatsapp_name}! 👋" if whatsapp_name else "¡Hola! 👋"
        
        return f"""{greeting}

Soy **Brenda**, tu asesora especializada en cursos de Inteligencia Artificial. ¡Me alegra mucho que estemos conectando!

**Para continuar con nuestra conversación, necesito que revises nuestro aviso de privacidad:**

📋 **Aviso de Privacidad:**
https://aviso-privacidad-ecos-b6b7ad47fe00.herokuapp.com/
https://aviso-privacidad -ecos-b6b7ad47fe00.herokuapp.com/

**Al continuar, estás aceptando nuestro aviso de privacidad y autorizas el procesamiento de tus datos personales para brindarte la mejor asesoría.**
"""

    @staticmethod
    def privacy_accepted_name_request() -> str:
        """
        Mensaje después de aceptar privacidad pidiendo el nombre preferido.
        
        Returns:
            Mensaje solicitando nombre preferido
        """
        return """¿Con quién tengo el gusto de hablar? 😊"""

    @staticmethod
    def privacy_rejected() -> str:
        """
        Mensaje cuando el usuario rechaza el consentimiento.
        
        Returns:
            Mensaje de despedida profesional
        """
        return """Entiendo perfectamente tu decisión y la respeto. 🤝

Si en algún momento cambias de opinión y te interesa conocer más sobre nuestros cursos de Inteligencia Artificial, no dudes en escribirme nuevamente.

¡Que tengas un excelente día! 👋

_Para reactivar esta conversación en el futuro, simplemente envía cualquier mensaje._"""

    @staticmethod
    def name_confirmed(user_name: str) -> str:
        """
        Mensaje de confirmación después de recibir el nombre.
        
        Args:
            user_name: Nombre proporcionado por el usuario
            
        Returns:
            Mensaje de bienvenida personalizado
        """
        return f"""¡Perfecto, **{user_name}**! 🎉

**Para ofrecerte la mejor asesoría, ¿podrías decirme en qué área de tu empresa te desempeñas?**"""

    @staticmethod
    def privacy_consent_reminder() -> str:
        """
        Recordatorio suave si el usuario no responde al consentimiento.
        
        Returns:
            Mensaje de recordatorio amigable
        """
        return """Hola de nuevo 👋

Veo que aún no has respondido sobre el consentimiento de privacidad.

**No hay prisa**, tómate el tiempo que necesites. Solo necesito saber si estás de acuerdo con que procesemos tus datos para poder ayudarte mejor.

_Recuerda que puedes responder:_
✅ **"ACEPTO"** para continuar
❌ **"NO ACEPTO"** si prefieres no continuar

¿Te gustaría que te explique algo más sobre nuestras políticas de privacidad?"""

    @staticmethod
    def invalid_privacy_response() -> str:
        """
        Mensaje cuando la respuesta sobre privacidad no es clara.
        
        Returns:
            Mensaje pidiendo clarificación
        """
        return """No estoy segura de entender tu respuesta 🤔

**Para continuar, necesito una respuesta clara sobre el consentimiento de privacidad.**

_Por favor responde con:_
✅ **"ACEPTO"** o **"SÍ"** - para aceptar el procesamiento de datos
❌ **"NO ACEPTO"** o **"NO"** - si prefieres no continuar

¿Podrías ayudarme con una respuesta más específica?"""

    @staticmethod
    def name_request_reminder() -> str:
        """
        Recordatorio para proporcionar el nombre después de aceptar privacidad.
        
        Returns:
            Mensaje recordatorio para el nombre
        """
        return """Hola de nuevo 😊

Veo que aceptaste nuestras condiciones de privacidad (¡gracias!), pero aún no me has dicho cómo te gustaría que te llame.

**¿Podrías decirme tu nombre preferido?**

_Solo escribe cómo quieres que me dirija a ti (ejemplo: "Ana", "Carlos", "Ing. López", etc.)_

Esto me ayuda mucho a personalizar nuestra conversación."""

    @staticmethod 
    def get_whatsapp_display_name(raw_data: dict) -> Optional[str]:
        """
        Extrae el nombre de visualización de WhatsApp desde los datos del webhook.
        
        Args:
            raw_data: Datos crudos del webhook de Twilio
            
        Returns:
            Nombre si está disponible, None si no
        """
        # Twilio puede proporcionar ProfileName en algunos casos
        profile_name = raw_data.get('ProfileName', '').strip()
        if profile_name and profile_name != '':
            return profile_name
            
        # También puede venir como WaId o contacto guardado
        wa_id = raw_data.get('WaId', '').strip()
        if wa_id and wa_id != '':
            # Si WaId es diferente del número, podría ser un nombre
            from_number = raw_data.get('From', '').replace('whatsapp:', '').replace('+', '')
            if wa_id != from_number:
                return wa_id
        
        # Verificar si hay información de contacto
        contact_name = raw_data.get('ContactName', '').strip()
        if contact_name and contact_name != '':
            return contact_name
            
        return None

    @staticmethod
    def extract_consent_response(message_text: str) -> Optional[bool]:
        """
        Extrae la respuesta de consentimiento del mensaje del usuario.
        
        Args:
            message_text: Texto del mensaje del usuario
            
        Returns:
            True si acepta, False si rechaza, None si no está claro
        """
        text = message_text.lower().strip()
        
        # PRIMERO verificar respuestas negativas (más específicas)
        reject_keywords = [
            'no acepto', 'no acepto', 'no estoy de acuerdo', 'no quiero', 
            'no deseo', 'cancelar', 'no continuar', 'no continúo', 'no continuo',
            'rechazar', 'rechazo'
        ]
        
        for keyword in reject_keywords:
            if keyword in text:
                return False
        
        # Verificar "no" solo (pero no si está en contexto de aceptación)
        if text == 'no' or text == 'nop' or text == 'nope':
            return False
            
        # DESPUÉS verificar respuestas afirmativas
        accept_keywords = [
            'acepto', 'si', 'sí', 'yes', 'ok', 'okay', 
            'de acuerdo', 'estoy de acuerdo', 'está bien', 'esta bien',
            'continuar', 'continúo', 'continuo', 'adelante', 'dale',
            'perfecto', 'correcto', 'claro', 'por supuesto'
        ]
        
        for keyword in accept_keywords:
            if keyword in text:
                return True
                
        return None

    @staticmethod
    def extract_user_name(message_text: str) -> Optional[str]:
        """
        Extrae y valida el nombre del usuario del mensaje.
        
        Args:
            message_text: Texto del mensaje del usuario
            
        Returns:
            Nombre limpio y validado, None si no es válido
        """
        name = message_text.strip()
        
        # Filtrar respuestas que no son nombres
        invalid_responses = [
            'no se', 'no sé', 'no tengo', 'nada', 'cualquiera', 'da igual',
            'como sea', 'no importa', 'sin nombre', 'anonimo', 'anónimo'
        ]
        
        if name.lower() in invalid_responses:
            return None
            
        # Validar longitud básica
        if len(name) < 2 or len(name) > 50:
            return None
            
        # Limpiar y capitalizar apropiadamente
        # Separar por espacios y capitalizar cada palabra
        words = name.split()
        cleaned_words = []
        
        for word in words:
            # Solo mantener palabras con caracteres alfanuméricos y algunos especiales
            clean_test = word.replace('-', '').replace("'", '').replace('.', '')
            if clean_test.isalpha():
                # Manejar palabras con guiones especialmente
                if '-' in word:
                    parts = word.split('-')
                    capitalized_parts = [part.capitalize() for part in parts if part]
                    cleaned_words.append('-'.join(capitalized_parts))
                else:
                    cleaned_words.append(word.capitalize())
        
        if not cleaned_words:
            return None
            
        return ' '.join(cleaned_words)
        
    @staticmethod
    def is_privacy_flow_message(message_text: str) -> bool:
        """
        Determina si el mensaje está relacionado con el flujo de privacidad.
        
        Args:
            message_text: Texto del mensaje
            
        Returns:
            True si parece ser parte del flujo de privacidad
        """
        text = message_text.lower().strip()
        
        privacy_keywords = [
            'acepto', 'acepto', 'no acepto', 'no acepto', 'privacidad',
            'consentimiento', 'datos', 'si', 'sí', 'no', 'de acuerdo',
            'términos', 'condiciones', 'política'
        ]
        
        return any(keyword in text for keyword in privacy_keywords)