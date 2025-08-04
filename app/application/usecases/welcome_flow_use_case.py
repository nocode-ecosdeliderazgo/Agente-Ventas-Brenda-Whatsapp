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
            logger.info(f"🔍 DEBUG: Verificando flujo de bienvenida para usuario")
            logger.info(f"🔍 DEBUG: privacy_accepted = {user_memory.privacy_accepted}")
            logger.info(f"🔍 DEBUG: name = {user_memory.name}")
            logger.info(f"🔍 DEBUG: selected_course = {user_memory.selected_course}")
            logger.info(f"🔍 DEBUG: stage = {user_memory.stage}")
            
            # Si el usuario ya completó privacidad y tiene nombre, pero no ha seleccionado curso
            if (user_memory.privacy_accepted and 
                user_memory.name and 
                not user_memory.selected_course and
                user_memory.stage == "privacy_flow_completed"):
                
                logger.info(f"🎯 Usuario completó privacidad pero no tiene curso seleccionado - Activando flujo de bienvenida")
                return True
            
            logger.info(f"❌ No se activa flujo de bienvenida - Condiciones no cumplidas")
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
            
            # ELIMINAR CURSO PREVIO si existe
            if user_memory.selected_course:
                logger.info(f"🗑️ Eliminando curso previo: {user_memory.selected_course}")
                user_memory.selected_course = None
                self.memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
            
            # OBTENER CURSOS DE LA BASE DE DATOS
            available_courses = await self._get_courses_from_database()
            
            if not available_courses:
                logger.warning("⚠️ No se pudieron obtener cursos de la base de datos, usando cursos por defecto")
                available_courses = self.available_courses
            
            # Crear mensaje con cursos disponibles
            courses_message = self._create_courses_offer_message(user_memory, available_courses)
            
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
                # Guardar cursos disponibles en memoria para referencia
                user_memory.available_courses = [course['code'] for course in available_courses]
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
    
    async def _get_courses_from_database(self) -> List[Dict[str, Any]]:
        """
        Obtiene los cursos disponibles de la base de datos.
        
        Returns:
            Lista de cursos disponibles
        """
        try:
            if self.course_query_use_case:
                courses = await self.course_query_use_case.get_all_courses()
                if courses:
                    logger.info(f"✅ Obtenidos {len(courses)} cursos de la base de datos")
                    return courses
                else:
                    logger.warning("⚠️ No se encontraron cursos en la base de datos")
                    return []
            else:
                logger.warning("⚠️ Course query use case no disponible")
                return []
        except Exception as e:
            logger.error(f"Error obteniendo cursos de la base de datos: {e}")
            return []
    
    def _create_courses_offer_message(self, user_memory: LeadMemory, available_courses: List[Dict[str, Any]]) -> str:
        """
        Crea el mensaje ofreciendo los cursos disponibles.
        
        Args:
            user_memory: Memoria del usuario
            available_courses: Lista de cursos disponibles
            
        Returns:
            Mensaje con oferta de cursos
        """
        try:
            user_name = user_memory.name if user_memory.name != "Usuario" else ""
            name_greeting = f"{user_name}, " if user_name else ""
            
            message_parts = [
                f"¡Hola {name_greeting}perfecto! Te ayudo a elegir tu curso de IA 🤖",
                "",
                "📚 **CURSOS DISPONIBLES:**",
                ""
            ]
            
            # Agregar cada curso de forma MUY concisa
            for i, course in enumerate(available_courses, 1):
                course_name = course.get('name', course.get('title', 'Curso sin nombre'))
                course_price = course.get('price', course.get('cost', 'N/A'))
                course_level = course.get('level', course.get('difficulty', 'General'))
                
                message_parts.append(f"**{i}. {course_name}** | ${course_price} | {course_level}")
            
            message_parts.extend([
                "",
                "🎯 **¿Cuál prefieres?**",
                "Responde con el número (ej: 1)",
                "",
                "💡 Si es tu primera vez, empieza con nivel Básico."
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
            
            # Obtener cursos disponibles de la memoria o base de datos
            available_courses = await self._get_courses_from_database()
            if not available_courses:
                available_courses = self.available_courses
            
            selected_course = self._extract_course_selection(message_text, available_courses)
            
            if selected_course:
                logger.info(f"✅ Usuario {user_id} seleccionó curso: {selected_course.get('name', 'Curso seleccionado')}")
                
                # Guardar curso seleccionado en memoria
                course_code = selected_course.get('code', selected_course.get('id', 'curso_seleccionado'))
                user_memory.selected_course = course_code
                user_memory.waiting_for_response = ""
                user_memory.current_flow = "sales_conversation"
                user_memory.stage = "ready_for_sales_agent"
                user_memory.flow_step = 0
                
                # Agregar interés en el curso
                course_name = selected_course.get('name', selected_course.get('title', 'Curso de IA'))
                if user_memory.interests is None:
                    user_memory.interests = []
                if course_name not in user_memory.interests:
                    user_memory.interests.append(course_name)
                
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
                    'selected_course_code': course_code,
                    'selected_course_name': course_name,
                    'ready_for_intelligent_agent': True,
                    'stage': 'ready_for_sales_agent',
                    'response_text': confirmation_message,
                    'response_sid': result.get('message_sid'),
                    'welcome_flow_completed': True
                }
            else:
                # Solicitar selección válida
                return await self._request_valid_course_selection(user_id, user_memory, available_courses)
                
        except Exception as e:
            logger.error(f"Error manejando selección de curso: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_course_selection(self, message_text: str, available_courses: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extrae la selección de curso del mensaje del usuario usando interpretación inteligente.
        
        Args:
            message_text: Texto del mensaje
            available_courses: Lista de cursos disponibles
            
        Returns:
            Información del curso seleccionado o None
        """
        try:
            message_lower = message_text.lower().strip()
            
            # Buscar por número exacto
            if message_text.strip().isdigit():
                index = int(message_text.strip()) - 1
                if 0 <= index < len(available_courses):
                    return available_courses[index]
            
            # Palabras clave para niveles
            level_keywords = {
                'básico': ['básico', 'basico', 'principiante', 'inicial', 'introductorio', 'básica', 'basica'],
                'intermedio': ['intermedio', 'intermedia', 'medio', 'media', 'automatización', 'automatizacion'],
                'avanzado': ['avanzado', 'avanzada', 'experto', 'experta', 'transformación', 'transformacion', 'digital']
            }
            
            # Buscar por nivel
            for level, keywords in level_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    # Buscar cursos que coincidan con el nivel
                    for course in available_courses:
                        course_level = course.get('level', course.get('difficulty', '')).lower()
                        if level in course_level or any(keyword in course_level for keyword in keywords):
                            return course
            
            # Buscar por palabras específicas del nombre del curso
            for course in available_courses:
                course_name = course.get('name', course.get('title', '')).lower()
                course_description = course.get('description', '').lower()
                
                # Buscar coincidencias en el nombre
                if any(word in course_name for word in message_lower.split()):
                    return course
                
                # Buscar coincidencias en la descripción
                if any(word in course_description for word in message_lower.split()):
                    return course
            
            # Buscar por palabras clave específicas
            course_keywords = {
                'ia': ['inteligencia artificial', 'ia', 'ai', 'artificial'],
                'automatización': ['automatización', 'automatizacion', 'automatizar', 'procesos'],
                'transformación': ['transformación', 'transformacion', 'transformar', 'digital'],
                'marketing': ['marketing', 'ventas', 'comercial'],
                'operaciones': ['operaciones', 'operacional', 'procesos'],
                'datos': ['datos', 'analytics', 'análisis', 'analisis']
            }
            
            for keyword, variations in course_keywords.items():
                if any(variation in message_lower for variation in variations):
                    for course in available_courses:
                        course_name = course.get('name', '').lower()
                        course_description = course.get('description', '').lower()
                        
                        if keyword in course_name or keyword in course_description:
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
            
            course_name = selected_course.get('name', selected_course.get('title', 'Curso seleccionado'))
            course_description = selected_course.get('description', 'Descripción no disponible')
            course_price = selected_course.get('price', selected_course.get('cost', 'Precio no disponible'))
            course_level = selected_course.get('level', selected_course.get('difficulty', 'Nivel no disponible'))
            course_sessions = selected_course.get('sessions', selected_course.get('duration_weeks', 'Duración no disponible'))
            course_hours = selected_course.get('duration_hours', selected_course.get('total_hours', 'Horas no disponibles'))
            
            message_parts = [
                f"🎯 ¡Perfecto {name_greeting}has seleccionado el curso ideal para ti!",
                "",
                f"📚 **{course_name}**",
                f"📝 {course_description}",
                "",
                f"💰 **Inversión:** ${course_price} USD",
                f"📊 **Nivel:** {course_level}",
                f"🗓️ **Duración:** {course_sessions} sesiones ({course_hours} horas)",
                "",
                "✅ **Curso guardado en tu perfil**",
                "",
                "🚀 **¿Qué te gustaría hacer ahora?**",
                "",
                "¡Solo escríbeme lo que te interesa! 😊"
            ]
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"Error creando mensaje de confirmación: {e}")
            return f"✅ Curso seleccionado: {course_name}. ¿En qué puedo ayudarte?"
    
    async def _request_valid_course_selection(
        self, 
        user_id: str, 
        user_memory: LeadMemory,
        available_courses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Solicita una selección válida de curso.
        
        Args:
            user_id: ID del usuario
            user_memory: Memoria del usuario
            available_courses: Lista de cursos disponibles
            
        Returns:
            Resultado del procesamiento
        """
        try:
            message_parts = [
                "🤔 **Selección no válida**",
                "",
                "Por favor, selecciona uno de nuestros cursos disponibles:",
                "",
                "**📚 CURSOS DISPONIBLES:**"
            ]
            
            # Agregar cada curso disponible
            for i, course in enumerate(available_courses, 1):
                course_name = course.get('name', course.get('title', 'Curso sin nombre'))
                message_parts.append(f"{i}. {course_name}")
            
            message_parts.extend([
                "",
                "**Responde con:**",
                "• El número del curso",
                "• El nombre del curso que te interese",
                "• El nivel que prefieres (Básico, Intermedio, Avanzado)",
                "",
                "¿Cuál te interesa más?"
            ])
            
            message = "\n".join(message_parts)

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