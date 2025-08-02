"""
Plantillas para el flujo de anuncios.
"""
from typing import Dict, Any


class AdFlowTemplates:
    """Plantillas para el flujo de anuncios"""
    
    @staticmethod
    def get_welcome_message(user_name: str, is_first_time: bool) -> str:
        """Plantilla de mensaje de bienvenida"""
        if is_first_time:
            return f"""¡Gracias {user_name}! 😊 

Soy Brenda, tu asesora especializada en cursos de Inteligencia Artificial. 

Me da muchísimo gusto que te interese nuestro curso desde el anuncio. Te voy a compartir toda la información específica del programa que te interesa."""
        else:
            return f"""¡Hola {user_name}! 😊 

Me alegra verte de nuevo. Veo que te interesa nuestro curso desde el anuncio. Te comparto la información actualizada del programa."""
    
    @staticmethod
    def get_course_template(course_data) -> str:
        """Plantilla con datos del curso desde BD"""
        # Manejar objetos CourseInfo (que tienen atributo 'course')
        if hasattr(course_data, 'course'):
            # Es un objeto CourseInfo
            course = course_data.course
            name = getattr(course, 'name', 'Dato no encontrado en la base de datos')
            description = getattr(course, 'short_description', 'Dato no encontrado en la base de datos')
            duration = getattr(course, 'total_duration_min', 'Dato no encontrado en la base de datos')
            level = getattr(course, 'level', 'Dato no encontrado en la base de datos')
            price = getattr(course, 'price', 'Dato no encontrado en la base de datos')
            currency = getattr(course, 'currency', 'USD')
        elif hasattr(course_data, 'name'):
            # Es un objeto Course directo
            name = getattr(course_data, 'name', 'Dato no encontrado en la base de datos')
            description = getattr(course_data, 'short_description', 'Dato no encontrado en la base de datos')
            duration = getattr(course_data, 'total_duration_min', 'Dato no encontrado en la base de datos')
            level = getattr(course_data, 'level', 'Dato no encontrado en la base de datos')
            price = getattr(course_data, 'price', 'Dato no encontrado en la base de datos')
            currency = getattr(course_data, 'currency', 'USD')
        else:
            # Es un diccionario
            name = course_data.get('name', 'Dato no encontrado en la base de datos')
            description = course_data.get('short_description', 'Dato no encontrado en la base de datos')
            duration = course_data.get('total_duration_min', 'Dato no encontrado en la base de datos')
            level = course_data.get('level', 'Dato no encontrado en la base de datos')
            price = course_data.get('price', 'Dato no encontrado en la base de datos')
            currency = course_data.get('currency', 'USD')
        
        # total_duration_min contiene horas (aunque el nombre sugiera minutos)
        hours = duration if isinstance(duration, int) else 'Dato no encontrado'
        
        return f"""🎓 **{name}**

{description}

⏱️ **Duración**: {hours} horas
📊 **Nivel**: {level}
💰 **Inversión**: ${price} {currency}

¿Qué te gustaría saber más sobre este curso?"""
    
    @staticmethod
    def get_motivational_message(user_name: str) -> str:
        """Plantilla de mensaje motivador antes de reactivar agente"""
        return f"""¡Perfecto {user_name}! 🚀

Ya tienes toda la información del curso. Ahora puedes preguntarme cualquier duda específica sobre el programa, horarios, contenido, o cualquier otra cosa que necesites saber.

¡Estoy aquí para ayudarte a tomar la mejor decisión para tu desarrollo profesional! 💪"""
    
    @staticmethod
    def get_pdf_message() -> str:
        """Mensaje para PDF del curso"""
        return "📄 **Aquí tienes el PDF descriptivo del curso**"
    
    @staticmethod
    def get_image_message() -> str:
        """Mensaje para imagen del curso"""
        return "🖼️ **Imagen del curso**"
    
    @staticmethod
    def get_simulator_pdf_message() -> str:
        """Mensaje para simulador cuando se envía PDF"""
        return "📄 [SIMULADOR] PDF del curso enviado correctamente"
    
    @staticmethod
    def get_simulator_image_message() -> str:
        """Mensaje para simulador cuando se envía imagen"""
        return "🖼️ [SIMULADOR] Imagen del curso enviada correctamente" 