"""
Caso de uso para manejar el flujo de bienvenida genérico cuando el usuario inicia con saludos o mensajes genéricos.
Replica exactamente la lógica del flujo de anuncios pero para usuarios que no vienen de campañas específicas.
"""
import logging
import re
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from memory.lead_memory import LeadMemory

logger = logging.getLogger(__name__)


class WelcomeFlowUseCase:
    """
    Caso de uso para manejar el flujo de bienvenida genérico.
    
    Responsabilidades:
    - Detectar si el usuario necesita flujo de privacidad
    - Ofrecer cursos disponibles al usuario
    - Asegurar selección obligatoria de un curso
    - Guardar curso seleccionado en memoria
    - Activar agente inteligente con personalización completa
    """
    
    def __init__(
        self,
        privacy_flow_use_case: PrivacyFlowUseCase,
        course_query_use_case: QueryCourseInformationUseCase,
        memory_use_case: ManageUserMemoryUseCase,
        twilio_client
    ):
        self.privacy_flow_use_case = privacy_flow_use_case
        self.course_query_use_case = course_query_use_case
        self.memory_use_case = memory_use_case
        self.twilio_client = twilio_client
        
        # Cursos disponibles para ofrecer
        self.available_courses = [
            {
                'code': 'CURSO_IA_BASICO',
                'name': 'Introducción a la Inteligencia Artificial para PyMEs',
                'description': 'Aprende los fundamentos de IA aplicada a pequeñas y medianas empresas',
                'price': 497,
                'level': 'Principiante',
                'sessions': 8,
                'duration': 12
            },
            {
                'code': 'CURSO_IA_INTERMEDIO',
                'name': 'IA Intermedia para Automatización Empresarial',
                'description': 'Automatiza procesos complejos y toma de decisiones con IA',
                'price': 797,
                'level': 'Intermedio',
                'sessions': 12,
                'duration': 18
            },
            {
                'code': 'CURSO_IA_AVANZADO',
                'name': 'IA Avanzada: Transformación Digital Completa',
                'description': 'Implementa sistemas de IA para transformación digital integral',
                'price': 1297,
                'level': 'Avanzado',
                'sessions': 16,
                'duration': 24
            }
        ]
    
    def should_handle_welcome_flow(self, incoming_message: IncomingMessage, user_memory: LeadMemory) -> bool:
        """
        Determina si debe manejar el flujo de bienvenida genérico.
        
        Args:
            incoming_message: Mensaje entrante del usuario
            user_memory: Memoria del usuario
            
        Returns:
            True si debe manejar el flujo de bienvenida
        """
        try:
            # Si el usuario ya completó privacidad y tiene nombre, pero no ha seleccionado curso
            if (user_memory.privacy_accepted and 
                user_memory.name and 
                not user_memory.selected_course and
                user_memory.stage == "privacy_flow_completed"):
                
                # Verificar si es un mensaje genérico (saludo, pregunta general, etc.)
                message_text = incoming_message.body.lower().strip()
                
                # Patrones de mensajes genéricos que activan el flujo de bienvenida
                generic_patterns = [
                    r'^hola',
                    r'^buenos días',
                    r'^buenas tardes',
                    r'^buenas noches',
                    r'^saludos',
                    r'^qué tal',
                    r'^cómo estás',
                    r'^me interesa',
                    r'^información',
                    r'^cursos',
                    r'^ayuda',
                    r'^inicio',
                    r'^empezar'
                ]
                
                for pattern in generic_patterns:
                    if re.search(pattern, message_text):
                        logger.info(f"🎯 Mensaje genérico detectado: '{incoming_message.body}' - Activando flujo de bienvenida")
                        return True
                
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando flujo de bienvenida: {e}")
            return False
    
    async def handle_welcome_flow(
        self, 
        user_id: str, 
        incoming_message: IncomingMessage
    ) -> Dict[str, Any]:
        """
        Maneja el flujo completo de bienvenida genérico.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje entrante
            
        Returns:
            Resultado del procesamiento
        """
        try:
            logger.info(f"🎯 Iniciando flujo de bienvenida genérico para usuario {user_id}")
            
            # Obtener memoria del usuario
            user_memory = self.memory_use_case.get_user_memory(user_id)
            
            # Verificar si necesita flujo de privacidad
            if self.privacy_flow_use_case.should_handle_privacy_flow(user_memory):
                logger.info(f"🔐 Usuario necesita flujo de privacidad - Delegando a PrivacyFlowUseCase")
                return await self.privacy_flow_use_case.handle_privacy_flow(user_id, incoming_message)
            
            # Si ya completó privacidad pero no ha seleccionado curso
            if (user_memory.privacy_accepted and 
                user_memory.name and 
                not user_memory.selected_course):
                
                # Verificar si está esperando selección de curso
                if user_memory.waiting_for_response == "course_selection":
                    return await self._handle_course_selection(user_id, incoming_message, user_memory)
                
                # Si no está esperando selección, ofrecer cursos
                else:
                    return await self._offer_courses(user_id, incoming_message, user_memory)
            
            # Si ya tiene curso seleccionado, activar agente inteligente
            elif user_memory.selected_course:
                logger.info(f"✅ Usuario ya tiene curso seleccionado: {user_memory.selected_course}")
                return {
                    'success': True,
                    'welcome_flow_completed': True,
                    'course_selected': True,
                    'ready_for_intelligent_agent': True,
                    'stage': 'ready_for_sales_agent'
                }
            
            # Caso por defecto: ofrecer cursos
            else:
                return await self._offer_courses(user_id, incoming_message, user_memory)
                
        except Exception as e:
            logger.error(f"Error en flujo de bienvenida: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _offer_courses(
        self, 
        user_id: str, 
        incoming_message: IncomingMessage, 
        user_memory: LeadMemory
    ) -> Dict[str, Any]:
        """
        Ofrece los cursos disponibles al usuario.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje entrante
            user_memory: Memoria del usuario
            
        Returns:
            Resultado del procesamiento
        """
        try:
            logger.info(f"📚 Ofreciendo cursos disponibles a usuario {user_id}")
            
            # Crear mensaje con cursos disponibles
            courses_message = self._create_courses_offer_message(user_memory)
            
            # Enviar mensaje
            outgoing_message = OutgoingMessage(
                to_number=f"whatsapp:+{user_id}",
                body=courses_message,
                message_type=MessageType.TEXT
            )
            
            result = await self.twilio_client.send_message(outgoing_message)
            
            if result.get('success'):
                # Actualizar memoria para esperar selección de curso
                user_memory.waiting_for_response = "course_selection"
                user_memory.current_flow = "course_selection"
                user_memory.flow_step = 1
                user_memory.stage = "course_selection"
                self.memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
                
                logger.info(f"✅ Cursos ofrecidos exitosamente a usuario {user_id}")
                
                return {
                    'success': True,
                    'courses_offered': True,
                    'waiting_for_course_selection': True,
                    'response_text': courses_message,
                    'response_sid': result.get('message_sid')
                }
            else:
                logger.error(f"❌ Error enviando oferta de cursos: {result}")
                return {'success': False, 'error': 'Error enviando mensaje'}
                
        except Exception as e:
            logger.error(f"Error ofreciendo cursos: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_courses_offer_message(self, user_memory: LeadMemory) -> str:
        """
        Crea el mensaje ofreciendo los cursos disponibles.
        
        Args:
            user_memory: Memoria del usuario
            
        Returns:
            Mensaje con oferta de cursos
        """
        try:
            user_name = user_memory.name if user_memory.name != "Usuario" else ""
            name_greeting = f"{user_name}, " if user_name else ""
            
            message_parts = [
                f"¡Hola {name_greeting}me da mucho gusto que te interese la Inteligencia Artificial! 🤖",
                "",
                "🎯 **Te ayudo a elegir el curso perfecto para tu PyME:**",
                "",
                "**📚 NUESTROS CURSOS DISPONIBLES:**",
                ""
            ]
            
            # Agregar cada curso
            for i, course in enumerate(self.available_courses, 1):
                message_parts.extend([
                    f"**{i}. {course['name']}**",
                    f"📝 {course['description']}",
                    f"💰 Inversión: ${course['price']} USD",
                    f"📊 Nivel: {course['level']}",
                    f"🗓️ Duración: {course['sessions']} sesiones ({course['duration']} horas)",
                    ""
                ])
            
            message_parts.extend([
                "**🎯 ¿CUÁL TE INTERESA MÁS?**",
                "",
                "Responde con el número del curso (1, 2 o 3) o escribe el nombre del curso que te interese.",
                "",
                "💡 **Recomendación:** Si es tu primera vez con IA, te sugiero empezar con el curso 1 (Principiante)."
            ])
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"Error creando mensaje de oferta de cursos: {e}")
            return "📚 Tenemos varios cursos de IA disponibles. ¿Cuál te interesa más?"
    
    async def _handle_course_selection(
        self, 
        user_id: str, 
        incoming_message: IncomingMessage, 
        user_memory: LeadMemory
    ) -> Dict[str, Any]:
        """
        Maneja la selección de curso del usuario.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje entrante
            user_memory: Memoria del usuario
            
        Returns:
            Resultado del procesamiento
        """
        try:
            message_text = incoming_message.body.strip()
            selected_course = self._extract_course_selection(message_text)
            
            if selected_course:
                logger.info(f"✅ Usuario {user_id} seleccionó curso: {selected_course['name']}")
                
                # Guardar curso seleccionado en memoria
                user_memory.selected_course = selected_course['code']
                user_memory.waiting_for_response = ""
                user_memory.current_flow = "sales_conversation"
                user_memory.stage = "ready_for_sales_agent"
                user_memory.flow_step = 0
                
                # Agregar interés en el curso
                if selected_course['name'] not in user_memory.interests:
                    user_memory.interests.append(selected_course['name'])
                
                # Incrementar score por selección específica
                user_memory.lead_score += 20
                
                self.memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
                
                # Enviar confirmación de selección
                confirmation_message = self._create_course_confirmation_message(selected_course, user_memory)
                
                outgoing_message = OutgoingMessage(
                    to_number=f"whatsapp:+{user_id}",
                    body=confirmation_message,
                    message_type=MessageType.TEXT
                )
                
                result = await self.twilio_client.send_message(outgoing_message)
                
                return {
                    'success': True,
                    'course_selected': True,
                    'selected_course_code': selected_course['code'],
                    'selected_course_name': selected_course['name'],
                    'ready_for_intelligent_agent': True,
                    'stage': 'ready_for_sales_agent',
                    'response_text': confirmation_message,
                    'response_sid': result.get('message_sid'),
                    'welcome_flow_completed': True
                }
            else:
                # Solicitar selección válida
                return await self._request_valid_course_selection(user_id, user_memory)
                
        except Exception as e:
            logger.error(f"Error manejando selección de curso: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_course_selection(self, message_text: str) -> Optional[Dict[str, Any]]:
        """
        Extrae la selección de curso del mensaje del usuario.
        
        Args:
            message_text: Texto del mensaje
            
        Returns:
            Información del curso seleccionado o None
        """
        try:
            message_lower = message_text.lower()
            
            # Buscar por número
            if message_text.strip() in ['1', '2', '3']:
                index = int(message_text.strip()) - 1
                if 0 <= index < len(self.available_courses):
                    return self.available_courses[index]
            
            # Buscar por palabras clave
            course_keywords = {
                'básico': 0,
                'basico': 0,
                'principiante': 0,
                'introducción': 0,
                'introduccion': 0,
                'intermedio': 1,
                'intermedio': 1,
                'automatización': 1,
                'automatizacion': 1,
                'avanzado': 2,
                'avanzado': 2,
                'transformación': 2,
                'transformacion': 2,
                'digital': 2
            }
            
            for keyword, index in course_keywords.items():
                if keyword in message_lower:
                    if 0 <= index < len(self.available_courses):
                        return self.available_courses[index]
            
            # Buscar por nombre del curso
            for course in self.available_courses:
                course_name_lower = course['name'].lower()
                if any(word in course_name_lower for word in message_lower.split()):
                    return course
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo selección de curso: {e}")
            return None
    
    def _create_course_confirmation_message(
        self, 
        selected_course: Dict[str, Any], 
        user_memory: LeadMemory
    ) -> str:
        """
        Crea mensaje de confirmación de selección de curso.
        
        Args:
            selected_course: Curso seleccionado
            user_memory: Memoria del usuario
            
        Returns:
            Mensaje de confirmación
        """
        try:
            user_name = user_memory.name if user_memory.name != "Usuario" else ""
            name_greeting = f"{user_name}, " if user_name else ""
            
            message_parts = [
                f"🎯 ¡Perfecto {name_greeting}has seleccionado el curso ideal para ti!",
                "",
                f"📚 **{selected_course['name']}**",
                f"📝 {selected_course['description']}",
                "",
                f"💰 **Inversión:** ${selected_course['price']} USD",
                f"📊 **Nivel:** {selected_course['level']}",
                f"🗓️ **Duración:** {selected_course['sessions']} sesiones ({selected_course['duration']} horas)",
                "",
                "✅ **Curso guardado en tu perfil**",
                "",
                "🚀 **¿Qué te gustaría hacer ahora?**",
                "",
                "• 📋 Ver temario completo del curso",
                "• 💰 Conocer opciones de pago",
                "• 🎯 Ver casos de éxito en tu sector",
                "• 👥 Conectarte con un asesor especializado",
                "• ❓ Hacer preguntas específicas sobre el curso",
                "",
                "¡Solo escríbeme lo que te interesa! 😊"
            ]
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"Error creando mensaje de confirmación: {e}")
            return f"✅ Curso seleccionado: {selected_course['name']}. ¿En qué puedo ayudarte?"
    
    async def _request_valid_course_selection(
        self, 
        user_id: str, 
        user_memory: LeadMemory
    ) -> Dict[str, Any]:
        """
        Solicita una selección válida de curso.
        
        Args:
            user_id: ID del usuario
            user_memory: Memoria del usuario
            
        Returns:
            Resultado del procesamiento
        """
        try:
            message = """🤔 **Selección no válida**

Por favor, selecciona uno de nuestros cursos disponibles:

**📚 CURSOS DISPONIBLES:**
1. Introducción a la Inteligencia Artificial para PyMEs
2. IA Intermedia para Automatización Empresarial  
3. IA Avanzada: Transformación Digital Completa

**Responde con:**
• El número del curso (1, 2 o 3)
• El nombre del curso que te interese
• El nivel que prefieres (Principiante, Intermedio, Avanzado)

¿Cuál te interesa más?"""

            outgoing_message = OutgoingMessage(
                to_number=f"whatsapp:+{user_id}",
                body=message,
                message_type=MessageType.TEXT
            )
            
            result = await self.twilio_client.send_message(outgoing_message)
            
            return {
                'success': True,
                'valid_selection_requested': True,
                'waiting_for_course_selection': True,
                'response_text': message,
                'response_sid': result.get('message_sid')
            }
            
        except Exception as e:
            logger.error(f"Error solicitando selección válida: {e}")
            return {'success': False, 'error': str(e)} 