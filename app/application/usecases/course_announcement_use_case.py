"""
Caso de uso para manejar el flujo de anuncio de cursos cuando el usuario envía un código específico.
Ejemplo: #CursoIA1 -> Muestra resumen del curso, PDF y imagen
"""
import logging
import re
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.dynamic_course_info_provider import DynamicCourseInfoProvider
from app.config.campaign_config import (
    COURSE_HASHTAG_MAPPING, 
    get_course_id_from_hashtag, 
    is_course_hashtag
)
from memory.lead_memory import LeadMemory

logger = logging.getLogger(__name__)


class CourseAnnouncementUseCase:
    """Caso de uso para manejar anuncios de cursos por código específico."""
    
    def __init__(
        self, 
        course_query_use_case: QueryCourseInformationUseCase,
        memory_use_case: ManageUserMemoryUseCase,
        dynamic_course_provider: DynamicCourseInfoProvider,
        twilio_client
    ):
        self.course_query_use_case = course_query_use_case
        self.memory_use_case = memory_use_case
        self.dynamic_course_provider = dynamic_course_provider
        self.twilio_client = twilio_client
        
        # Usar mapeo centralizado desde campaign_config.py
        # Extender con códigos adicionales si es necesario
        additional_mappings = {
            "#CursoIA1": "curso-ia-basico-001",  # ID del curso en la base de datos
            "#CursoIA2": "curso-ia-intermedio-001",
            "#CursoIA3": "curso-ia-avanzado-001",
        }
        
        # Combinar mapeo centralizado con códigos adicionales
        self.course_code_mapping = {}
        
        # Agregar mapeos desde campaign_config.py (con # para compatibilidad)
        for hashtag, course_id in COURSE_HASHTAG_MAPPING.items():
            # Agregar tanto con # como sin # para flexibilidad
            self.course_code_mapping[f"#{hashtag}"] = course_id
            self.course_code_mapping[hashtag] = course_id
        
        # Agregar mapeos adicionales
        self.course_code_mapping.update(additional_mappings)
        
        logger.info(f"📋 Mapeo de códigos de curso cargado: {list(self.course_code_mapping.keys())}")
    
    def should_handle_course_announcement(self, incoming_message: IncomingMessage) -> bool:
        """
        Determina si el mensaje contiene un código de curso que debe ser procesado.
        
        Args:
            incoming_message: Mensaje entrante del usuario
            
        Returns:
            True si contiene un código de curso válido, False en caso contrario
        """
        try:
            message_text = incoming_message.body.strip()
            
            # Buscar códigos de curso en el mensaje
            for code in self.course_code_mapping.keys():
                if code.lower() in message_text.lower():
                    logger.info(f"📚 Código de curso detectado: {code}")
                    return True
            
            # También buscar usando el sistema centralizado (sin #)
            for hashtag in COURSE_HASHTAG_MAPPING.keys():
                if hashtag.lower() in message_text.lower():
                    logger.info(f"📚 Hashtag de curso centralizado detectado: {hashtag}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando código de curso: {e}")
            return False
    
    def extract_course_code(self, message_text: str) -> Optional[str]:
        """
        Extrae el código de curso del mensaje.
        
        Args:
            message_text: Texto del mensaje
            
        Returns:
            Código de curso encontrado o None
        """
        try:
            message_lower = message_text.lower()
            
            # Buscar en mapeo local primero
            for code in self.course_code_mapping.keys():
                if code.lower() in message_lower:
                    return code
            
            # Buscar en mapeo centralizado (sin #)
            for hashtag in COURSE_HASHTAG_MAPPING.keys():
                if hashtag.lower() in message_lower:
                    return f"#{hashtag}"  # Retornar con # para compatibilidad
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo código de curso: {e}")
            return None
    
    async def handle_course_announcement(
        self, 
        user_id: str, 
        incoming_message: IncomingMessage
    ) -> Dict[str, Any]:
        """
        Maneja el flujo completo de anuncio de curso.
        
        Args:
            user_id: ID del usuario
            incoming_message: Mensaje entrante
            
        Returns:
            Resultado del procesamiento
        """
        try:
            logger.info(f"🎯 Iniciando flujo de anuncio de curso para usuario {user_id}")
            
            # Extraer código de curso
            course_code = self.extract_course_code(incoming_message.body)
            if not course_code:
                logger.warning("No se pudo extraer código de curso válido")
                return {'success': False, 'error': 'Código de curso no válido'}
            
            logger.info(f"📋 Código extraído: {course_code}")
            
            # Obtener información del curso
            course_info = await self._get_course_information(course_code)
            if not course_info:
                return await self._send_course_not_found_message(user_id, course_code)
            
            # Actualizar memoria del usuario
            await self._update_user_memory(user_id, course_code, course_info)
            
            # Enviar respuesta completa con resumen, PDF e imagen
            result = await self._send_course_announcement_response(
                user_id, course_code, course_info
            )
            
            logger.info(f"✅ Flujo de anuncio completado para {course_code}")
            return result
            
        except Exception as e:
            logger.error(f"Error en flujo de anuncio de curso: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _get_course_information(self, course_code: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del curso desde la base de datos.
        
        Args:
            course_code: Código del curso
            
        Returns:
            Información del curso o None si no se encuentra
        """
        try:
            # Obtener ID del curso desde el mapeo
            course_id = self.course_code_mapping.get(course_code)
            if not course_id:
                logger.warning(f"Código de curso no mapeado: {course_code}")
                return None
            
            # PRIMERO: Intentar obtener datos reales de la base de datos
            if self.course_query_use_case:
                try:
                    # Para códigos específicos, buscar por nombre exacto en la BD
                    if course_code in ["#Experto_IA_GPT_Gemini", "#ADSIM_05"]:
                        # Buscar curso específico por nombre en BD
                        courses = await self.course_query_use_case.search_courses_by_keyword("Experto", 5)
                        logger.info(f"🔍 Búsqueda en BD para {course_code}: encontrados {len(courses) if courses else 0} cursos")
                        
                        if courses:
                            # Buscar el curso que mejor coincida
                            target_course = None
                            for course in courses:
                                course_name_lower = getattr(course, 'name', '').lower()
                                if 'experto' in course_name_lower and ('gpt' in course_name_lower or 'gemini' in course_name_lower or 'profesional' in course_name_lower):
                                    target_course = course
                                    break
                            
                            if not target_course and courses:
                                # Si no encontramos coincidencia exacta, usar el primero
                                target_course = courses[0]
                            
                            if target_course:
                                logger.info(f"✅ Curso encontrado en BD: {getattr(target_course, 'name', 'Sin nombre')}")
                                detailed_content = await self.course_query_use_case.get_course_detailed_content(target_course.id_course)
                                
                                # Obtener bonos desde la tabla bond
                                bonuses = []
                                try:
                                    from app.infrastructure.database.repositories.course_repository import CourseRepository
                                    repo = CourseRepository()
                                    bonuses_data = await repo.get_course_bonuses(target_course.id_course)
                                    bonuses = [bonus.content for bonus in bonuses_data] if bonuses_data else []
                                    logger.info(f"📦 Bonos encontrados en BD: {len(bonuses)}")
                                except Exception as e:
                                    logger.warning(f"Error obteniendo bonos: {e}")
                                
                                return {
                                    'course': target_course,
                                    'detailed_content': detailed_content,
                                    'bonuses': bonuses,
                                    'found_in_database': True,
                                    'course_code': course_code
                                }
                    else:
                        # Para otros códigos, buscar genérico
                        courses = await self.course_query_use_case.search_courses_by_keyword("IA", 1)
                        if courses:
                            course = courses[0]
                            detailed_content = await self.course_query_use_case.get_course_detailed_content(course.id_course)
                            return {
                                'course': course,
                                'detailed_content': detailed_content,
                                'found_in_database': True,
                                'course_code': course_code
                            }
                            
                except Exception as e:
                    logger.error(f"Error accediendo a base de datos para {course_code}: {e}")
            
            # Fallback: Información predefinida solo si falla la BD
            logger.warning(f"⚠️ Usando datos mock para {course_code} - BD no disponible")
            mock_data = self._get_mock_course_information(course_code)
            mock_data['found_in_database'] = False
            mock_data['course_code'] = course_code
            return mock_data
            
        except Exception as e:
            logger.error(f"Error obteniendo información del curso {course_code}: {e}")
            return None
    
    def _get_mock_course_information(self, course_code: str) -> Dict[str, Any]:
        """
        Obtiene información mock del curso para testing.
        
        Args:
            course_code: Código del curso
            
        Returns:
            Información mock del curso
        """
        mock_courses = {
            "#CursoIA1": {
                'name': "Introducción a la Inteligencia Artificial para PyMEs",
                'short_description': "Aprende los fundamentos de IA aplicada a pequeñas y medianas empresas",
                'price': 0,  # Se obtendrá dinámicamente de BD
                'currency': "USD",
                'level': "Principiante",
                'modality': "Online",
                'session_count': 8,
                'duration_hours': 12,
                'description': """
¿Quieres transformar tu PyME con Inteligencia Artificial pero no sabes por dónde empezar?

Este curso está diseñado específicamente para líderes de empresas de 20-200 empleados que buscan automatizar procesos, reducir costos operativos y obtener ventaja competitiva sin necesidad de equipos técnicos.

**Lo que aprenderás:**
• Fundamentos de IA aplicados a tu sector específico
• Herramientas de automatización para reportes y dashboards
• Estrategias de contenido con IA para marketing
• Casos de éxito reales con ROI comprobado
• Plan de implementación paso a paso

**Dirigido a:** Gerentes, Directores y Fundadores de PyMEs en servicios, comercio, salud, educación y consultoría.
                """.strip(),
                'bonuses': [
                    "📚 Plantillas de automatización listas para usar",
                    "🤖 Acceso a herramientas de IA por 6 meses",
                    "💼 Consultoría personalizada 1-on-1 (30 min)",
                    "📊 Dashboard de ROI personalizado",
                    "🎯 Guía de implementación por sector"
                ],
                'pdf_resource': "guia-ia-pymes-fundamentos.pdf",
                'image_resource': "curso-ia-pymes-banner.png",
                'found_in_database': False
            },
            "#CursoIA2": {
                'name': "IA Intermedia para Automatización Empresarial",
                'short_description': "Automatiza procesos complejos y toma de decisiones con IA",
                'price': 797,
                'currency': "USD",
                'level': "Intermedio",
                'modality': "Online",
                'session_count': 12,
                'duration_hours': 18,
                'found_in_database': False
            },
            "#CursoIA3": {
                'name': "IA Avanzada: Transformación Digital Completa",
                'short_description': "Implementa sistemas de IA para transformación digital integral",
                'price': 1297,
                'currency': "USD",
                'level': "Avanzado",
                'modality': "Online",
                'session_count': 16,
                'duration_hours': 24,
                'found_in_database': False
            },
            # Curso específico con archivos reales
            "#Experto_IA_GPT_Gemini": {
                'name': "Experto en IA para Profesionales: Dominando ChatGPT y Gemini",
                'short_description': "Domina las herramientas de IA más poderosas para maximizar tu productividad profesional",
                'price': 4500,
                'currency': "MXN",
                'level': "Intermedio-Avanzado",
                'modality': "Online en Vivo + Grabaciones",
                'session_count': 10,
                'duration_hours': 20,
                'description': """
🚀 **¿Listo para ser el experto en IA que tu empresa necesita?**

Este curso intensivo está diseñado para profesionales ambiciosos que quieren dominar ChatGPT, Gemini y las mejores herramientas de IA para multiplicar su productividad y convertirse en referentes en su campo.

**🎯 Lo que dominarás:**
• Técnicas avanzadas de prompt engineering para resultados profesionales
• Automatización de tareas complejas con ChatGPT y Gemini
• Integración de IA en flujos de trabajo empresariales
• Herramientas complementarias para análisis, creación y optimización
• Estrategias para liderar la transformación digital en tu organización

**👥 Perfecto para:**
Gerentes, Directores, Consultores, Freelancers y Emprendedores que buscan ventaja competitiva real con IA.

**🏆 Resultados garantizados:**
Al finalizar serás capaz de implementar soluciones de IA que generen ROI medible en tu trabajo diario.
                """.strip(),
                'bonuses': [
                    "🎯 Plantillas de prompts profesionales (30+ casos de uso)",
                    "🤖 Acceso premium a herramientas de IA por 3 meses",
                    "📊 Dashboard personal de productividad con IA",
                    "💼 Sesión de consultoría 1-on-1 para tu caso específico",
                    "🚀 Certificado de finalización avalado",
                    "👥 Acceso a comunidad privada de expertos en IA",
                    "📚 Biblioteca de recursos actualizada mensualmente"
                ],
                'pdf_resource': "experto_ia_profesionales.pdf",  # Archivo real
                'image_resource': "experto_ia_profesionales.jpg",  # Archivo real
                'found_in_database': False
            },
            "#ADSIM_05": {
                # Mismo curso, diferente código de campaña publicitaria
                'name': "Experto en IA para Profesionales: Dominando ChatGPT y Gemini",
                'short_description': "Domina las herramientas de IA más poderosas para maximizar tu productividad profesional",
                'price': 4500,
                'currency': "MXN",
                'level': "Intermedio-Avanzado",
                'modality': "Online en Vivo + Grabaciones",
                'session_count': 10,
                'duration_hours': 20,
                'description': """
🚀 **¿Listo para ser el experto en IA que tu empresa necesita?**

Este curso intensivo está diseñado para profesionales ambiciosos que quieren dominar ChatGPT, Gemini y las mejores herramientas de IA para multiplicar su productividad y convertirse en referentes en su campo.

**🎯 Lo que dominarás:**
• Técnicas avanzadas de prompt engineering para resultados profesionales
• Automatización de tareas complejas con ChatGPT y Gemini
• Integración de IA en flujos de trabajo empresariales
• Herramientas complementarias para análisis, creación y optimización
• Estrategias para liderar la transformación digital en tu organización

**👥 Perfecto para:**
Gerentes, Directores, Consultores, Freelancers y Emprendedores que buscan ventaja competitiva real con IA.

**🏆 Resultados garantizados:**
Al finalizar serás capaz de implementar soluciones de IA que generen ROI medible en tu trabajo diario.
                """.strip(),
                'bonuses': [
                    "🎯 Plantillas de prompts profesionales (30+ casos de uso)",
                    "🤖 Acceso premium a herramientas de IA por 3 meses",
                    "📊 Dashboard personal de productividad con IA",
                    "💼 Sesión de consultoría 1-on-1 para tu caso específico",
                    "🚀 Certificado de finalización avalado",
                    "👥 Acceso a comunidad privada de expertos en IA",
                    "📚 Biblioteca de recursos actualizada mensualmente"
                ],
                'pdf_resource': "experto_ia_profesionales.pdf",  # Archivo real
                'image_resource': "experto_ia_profesionales.jpg",  # Archivo real
                'found_in_database': False
            }
        }
        
        return mock_courses.get(course_code, {})
    
    async def _update_user_memory(
        self, 
        user_id: str, 
        course_code: str, 
        course_info: Dict[str, Any]
    ) -> None:
        """
        Actualiza la memoria del usuario con información del curso solicitado.
        
        Args:
            user_id: ID del usuario
            course_code: Código del curso
            course_info: Información del curso
        """
        try:
            user_memory = self.memory_use_case.get_user_memory(user_id)
            
            # Inicializar listas si no existen
            if user_memory.interests is None:
                user_memory.interests = []
            if user_memory.buying_signals is None:
                user_memory.buying_signals = []
            if user_memory.message_history is None:
                user_memory.message_history = []
            
            # Registrar interés en el curso
            if course_info.get('name'):
                course_name = course_info['name']
                if course_name not in user_memory.interests:
                    user_memory.interests.append(course_name)
            
            # 🆕 GUARDAR HASHTAG ORIGINAL EN LA MEMORIA
            # Extraer hashtag limpio (sin #) para guardar en memoria
            hashtag_clean = course_code.replace('#', '')
            
            # Guardar el hashtag en el campo original_message_body para rastreo
            user_memory.original_message_body = course_code
            
            # También agregarlo a los intereses como hashtag
            hashtag_interest = f"hashtag:{hashtag_clean}"
            if hashtag_interest not in user_memory.interests:
                user_memory.interests.append(hashtag_interest)
            
            # Mapear hashtag a course_id usando sistema centralizado
            course_id = get_course_id_from_hashtag(hashtag_clean)
            if course_id:
                course_id_interest = f"course_id:{course_id}"
                if course_id_interest not in user_memory.interests:
                    user_memory.interests.append(course_id_interest)
                logger.info(f"💾 Hashtag {hashtag_clean} mapeado a course_id {course_id} y guardado en memoria")
            
            # Agregar señal de compra
            buying_signal = f"Solicitó información de {course_code}"
            if buying_signal not in user_memory.buying_signals:
                user_memory.buying_signals.append(buying_signal)
            
            # Incrementar score por interés específico en curso
            user_memory.lead_score += 15
            
            # Actualizar contexto - agregar a message_history
            user_memory.message_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'course_request',
                'course_code': course_code,
                'hashtag_clean': hashtag_clean,
                'course_id': course_id,
                'course_name': course_info.get('name', 'Curso IA'),
                'description': f"Solicitó información detallada del curso {course_code}: {course_info.get('name', 'Curso IA')}"
            })
            
            self.memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
            logger.info(f"💾 Memoria actualizada para usuario {user_id} - curso {course_code}")
            
        except Exception as e:
            logger.error(f"Error actualizando memoria para curso {course_code}: {e}")
    
    async def _send_course_announcement_response(
        self, 
        user_id: str, 
        course_code: str, 
        course_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Envía la respuesta completa del anuncio del curso.
        
        Args:
            user_id: ID del usuario
            course_code: Código del curso
            course_info: Información del curso
            
        Returns:
            Resultado del envío
        """
        try:
            # Obtener memoria del usuario para personalización
            user_memory = self.memory_use_case.get_user_memory(user_id)
            
            # Crear mensaje principal con resumen del curso
            main_message = await self._create_course_summary_message(course_info, user_memory)
            
            # Enviar mensaje principal
            outgoing_message = OutgoingMessage(
                to_number=user_id,
                body=main_message,
                message_type=MessageType.TEXT
            )
            
            main_result = await self.twilio_client.send_message(outgoing_message)
            
            if not main_result.get('success'):
                logger.error(f"Error enviando mensaje principal: {main_result}")
                return {'success': False, 'error': 'Error enviando mensaje'}
            
            # Enviar PDF (simulado por ahora)
            pdf_result = await self._send_course_pdf(user_id, course_info)
            
            # Enviar imagen (simulado por ahora)
            image_result = await self._send_course_image(user_id, course_info)
            
            # Esperar 13 segundos para que los archivos se carguen antes de enviar los mensajes de texto
            logger.info("⏳ Esperando 13 segundos para que los archivos se carguen...")
            await asyncio.sleep(13)
            
            # Enviar mensaje de seguimiento
            follow_up_message = self._create_follow_up_message(course_info, user_memory)
            
            follow_up_outgoing = OutgoingMessage(
                to_number=user_id,
                body=follow_up_message,
                message_type=MessageType.TEXT
            )
            
            follow_up_result = await self.twilio_client.send_message(follow_up_outgoing)
            
            # Enviar mensaje adicional con pregunta sobre qué le parece más interesante
            engagement_message = "¿Qué te parece más interesante del curso?"
            
            engagement_outgoing = OutgoingMessage(
                to_number=user_id,
                body=engagement_message,
                message_type=MessageType.TEXT
            )
            
            engagement_result = await self.twilio_client.send_message(engagement_outgoing)
            
            return {
                'success': True,
                'processed': True,
                'response_sent': True,
                'response_text': main_message,
                'response_sid': main_result.get('message_sid'),
                'course_code': course_code,
                'course_name': course_info.get('name'),
                'additional_resources_sent': {
                    'pdf_sent': pdf_result.get('success', False),
                    'image_sent': image_result.get('success', False),
                    'follow_up_sent': follow_up_result.get('success', False),
                    'engagement_sent': engagement_result.get('success', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Error enviando respuesta de anuncio: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _create_course_summary_message(
        self, 
        course_info: Dict[str, Any], 
        user_memory: LeadMemory
    ) -> str:
        """
        Crea el mensaje de resumen del curso personalizado para el usuario.
        
        Args:
            course_info: Información del curso
            user_memory: Memoria del usuario
            
        Returns:
            Mensaje personalizado del curso
        """
        try:
            # Obtener nombre del usuario para personalización
            user_name = user_memory.name if user_memory.name != "Usuario" else ""
            name_greeting = f"{user_name}, " if user_name else ""
            
            # Información básica del curso
            # Si viene de BD, extraer de la estructura anidada
            if course_info.get('found_in_database') and course_info.get('course'):
                db_course = course_info['course']
                course_name = getattr(db_course, 'name', 'Curso de IA')
                description = getattr(db_course, 'short_description', '')
                price = getattr(db_course, 'price', '0')
                currency = getattr(db_course, 'currency', 'USD')
                level = getattr(db_course, 'level', 'Todos los niveles')
                sessions = getattr(db_course, 'session_count', 8)
                # total_duration_min contiene horas (no minutos, solo el nombre es confuso)
                duration = getattr(db_course, 'total_duration_min', 12) or 12
                modality = getattr(db_course, 'modality', 'Online')
                
                # Obtener bonos de la BD
                bonuses_from_db = course_info.get('bonuses', [])
                logger.info(f"📦 Bonos desde BD: {len(bonuses_from_db)} bonos encontrados")
            else:
                # Mock data - acceso directo
                course_name = course_info.get('name', 'Curso de IA')
                description = course_info.get('short_description', '')
                price = course_info.get('price', 0)
                currency = course_info.get('currency', 'USD')
                level = course_info.get('level', 'Todos los niveles')
                sessions = course_info.get('session_count', 8)
                duration = course_info.get('duration_hours', 12)
                modality = course_info.get('modality', 'Online')
                bonuses_from_db = []
            
            # Crear mensaje principal (VERSIÓN CORTA para evitar límite de 1600 caracteres)
            message_parts = [
                f"🎯 ¡Perfecto {name_greeting}aquí tienes la información!",
                "",
                f"📚 **{course_name}**",
                f"💰 **Inversión:** ${price} {currency}",
                f"📊 **Nivel:** {level} | 🗓️ {sessions} sesiones ({duration}h)",
                f"💻 **Modalidad:** {modality}",
                ""
            ]
            
            # Agregar solo descripción corta si existe
            if description:
                message_parts.extend([
                    f"📝 {description}",
                    ""
                ])
            
            # Usar bonos de la BD primero, fallback a mock data si no hay
            bonuses = bonuses_from_db if bonuses_from_db else course_info.get('bonuses', [])
            
            if bonuses:
                message_parts.extend([
                    f"🎁 **BONOS INCLUIDOS:**"
                ])
                # Mostrar solo los primeros 3 bonos para ahorrar caracteres
                for i, bonus in enumerate(bonuses[:3]):
                    message_parts.append(f"• {bonus}")
                if len(bonuses) > 3:
                    message_parts.append(f"• ...y {len(bonuses) - 3} bonos más")
                message_parts.append("")
            
            # Agregar ROI personalizado según el rol del usuario (versión corta)
            role = user_memory.role if user_memory.role != "No disponible" else ""
            if role:
                roi_message = await self._get_role_specific_roi_message_short(role, price)
                if roi_message:
                    message_parts.extend([roi_message, ""])
            
            # Agregar llamada a la acción
            message_parts.extend([
                "📄 Te envío el PDF completo con todos los detalles.",
                "🖼️ También recibirás la imagen con la estructura del curso.",
                "",
                "¿Tienes alguna pregunta específica?"
            ])
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"Error creando mensaje de resumen: {e}")
            return f"📚 Información del curso disponible. Precio: {course_info.get('price_formatted', 'Consultar precio')}"
    
    async def _get_role_specific_roi_message(self, role: str, course_price: int) -> str:
        """
        Genera mensaje de ROI específico según el rol del usuario.
        Ahora usa datos dinámicos de la base de datos.
        
        Args:
            role: Rol/cargo del usuario
            course_price: Precio del curso
            
        Returns:
            Mensaje de ROI personalizado
        """
        try:
            # Obtener datos dinámicos de ROI desde la base de datos
            if self.dynamic_course_provider:
                course_data = await self.dynamic_course_provider.get_primary_course_info()
                roi_examples = course_data.get('roi_examples', {})
            else:
                # Fallback a valores por defecto si no hay proveedor dinámico
                roi_examples = {}
            
            role_lower = role.lower()
            
            if any(keyword in role_lower for keyword in ['marketing', 'digital', 'comercial']):
                marketing_roi = roi_examples.get('marketing_manager', {})
                roi_percentage = marketing_roi.get('roi_percentage', 100)
                monthly_benefits = marketing_roi.get('monthly_benefits', 416.67)
                break_even = marketing_roi.get('roi_months_to_break_even', 1)
                calculation_basis = marketing_roi.get('calculation_basis', 'ROI calculado desde BD')
                return f"💡 **ROI para Marketing Digital:**\n• ROI: {roi_percentage:.1f}%\n• Beneficios mensuales: ${monthly_benefits:,.2f}\n• Recuperas inversión en {break_even} {'mes' if break_even == 1 else 'meses'}\n• Cálculo: {calculation_basis}"
            
            elif any(keyword in role_lower for keyword in ['operaciones', 'operations', 'gerente', 'director']):
                operations_roi = roi_examples.get('operations_manager', {})
                roi_percentage = operations_roi.get('roi_percentage', 100)
                monthly_benefits = operations_roi.get('monthly_benefits', 416.67)
                break_even = operations_roi.get('roi_months_to_break_even', 1)
                calculation_basis = operations_roi.get('calculation_basis', 'ROI calculado desde BD')
                return f"💡 **ROI para Operaciones:**\n• ROI: {roi_percentage:.1f}%\n• Beneficios mensuales: ${monthly_benefits:,.2f}\n• Recuperas inversión en {break_even} {'mes' if break_even == 1 else 'meses'}\n• Cálculo: {calculation_basis}"
            
            elif any(keyword in role_lower for keyword in ['ceo', 'founder', 'fundador', 'director general']):
                ceo_roi = roi_examples.get('ceo_founder', {})
                roi_percentage = ceo_roi.get('roi_percentage', 100)
                yearly_benefits = ceo_roi.get('yearly_benefits', 5000)
                break_even = ceo_roi.get('roi_months_to_break_even', 1)
                calculation_basis = ceo_roi.get('calculation_basis', 'ROI calculado desde BD')
                return f"💡 **ROI para Liderazgo Ejecutivo:**\n• ROI: {roi_percentage:.1f}%\n• Beneficios anuales: ${yearly_benefits:,.2f}\n• Recuperas inversión en {break_even} {'mes' if break_even == 1 else 'meses'}\n• Cálculo: {calculation_basis}"
            
            elif any(keyword in role_lower for keyword in ['rh', 'recursos humanos', 'hr', 'talent']):
                # Usar datos generales si no hay específicos para RH
                return f"💡 **ROI para Recursos Humanos:**\n• Reduce 80% tiempo en procesos de selección\n• Ahorra $1,500 mensuales en reclutamiento\n• ROI proyectado: 300% en el primer trimestre"
            
            else:
                # ROI general usando datos dinámicos
                general_savings = 1000  # Valor base conservador
                break_even = max(1, round(course_price / general_savings, 1))
                return f"💡 **ROI General para PyMEs:**\n• Ahorra mínimo ${general_savings:,} mensuales en automatización\n• Incrementa productividad del equipo en 35%\n• ROI proyectado: {int(general_savings * 12 / course_price * 100)}% anual"
                
        except Exception as e:
            logger.error(f"Error generando ROI específico: {e}")
            return ""
    
    async def _get_role_specific_roi_message_short(self, role: str, course_price: int) -> str:
        """
        Genera mensaje de ROI específico CORTO según el rol del usuario.
        Ahora usa datos dinámicos de la base de datos.

        Args:
            role: Rol/cargo del usuario
            course_price: Precio del curso
            
        Returns:
            Mensaje de ROI personalizado corto
        """
        try:
            # Obtener datos dinámicos de ROI desde la base de datos
            if self.dynamic_course_provider:
                course_data = await self.dynamic_course_provider.get_primary_course_info()
                roi_examples = course_data.get('roi_examples', {})
            else:
                # Fallback a valores por defecto si no hay proveedor dinámico
                roi_examples = {}
            
            role_lower = role.lower()
            
            if any(keyword in role_lower for keyword in ['marketing', 'digital', 'comercial']):
                marketing_roi = roi_examples.get('marketing_manager', {})
                roi_percentage = marketing_roi.get('roi_percentage', 100)
                monthly_benefits = marketing_roi.get('monthly_benefits', 416.67)
                return f"💡 **ROI Marketing:** {roi_percentage:.1f}% → ${monthly_benefits:,.2f}/mes"
            
            elif any(keyword in role_lower for keyword in ['operaciones', 'operations', 'gerente', 'director']):
                operations_roi = roi_examples.get('operations_manager', {})
                roi_percentage = operations_roi.get('roi_percentage', 100)
                monthly_benefits = operations_roi.get('monthly_benefits', 416.67)
                return f"💡 **ROI Operaciones:** {roi_percentage:.1f}% → ${monthly_benefits:,.2f}/mes"
            
            elif any(keyword in role_lower for keyword in ['ceo', 'founder', 'fundador', 'director general']):
                ceo_roi = roi_examples.get('ceo_founder', {})
                roi_percentage = ceo_roi.get('roi_percentage', 100)
                yearly_benefits = ceo_roi.get('yearly_benefits', 5000)
                return f"💡 **ROI Ejecutivo:** {roi_percentage:.1f}% → ${yearly_benefits:,.2f}/año"
            
            elif any(keyword in role_lower for keyword in ['rh', 'recursos humanos', 'hr', 'talent']):
                return f"💡 **ROI RH:** Ahorra $1,500/mes → ROI 300% primer trimestre"
            
            else:
                # ROI general usando datos dinámicos
                general_savings = 1000
                break_even = max(1, round(course_price / general_savings, 1))
                return f"💡 **ROI PyME:** Ahorra ${general_savings:,}/mes → ROI en {break_even} {'mes' if break_even == 1 else 'meses'}"
                
        except Exception as e:
            logger.error(f"Error generando ROI corto: {e}")
            return ""
    
    async def _send_course_pdf(self, user_id: str, course_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía el PDF del curso real desde la carpeta resources.
        
        Args:
            user_id: ID del usuario
            course_info: Información del curso
            
        Returns:
            Resultado del envío
        """
        try:
            pdf_filename = course_info.get('pdf_resource', 'experto_ia_profesionales.pdf')
            
            # Intentar usar ngrok si está disponible, sino fallback
            from app.config import settings
            ngrok_url = settings.ngrok_url
            
            if ngrok_url:
                # Asegurar que no haya doble barra en la URL
                base_url = ngrok_url.rstrip('/')
                pdf_url = f"{base_url}/resources/course_materials/{pdf_filename}"
                logger.info(f"📄 Usando URL ngrok para PDF: {pdf_url}")
            else:
                pdf_url = None  # Forzar fallback si no hay ngrok
                logger.info(f"⚠️ NGROK_URL no configurado, usando fallback para PDF")
            
            # Mensaje acompañando al PDF
            pdf_message = f"""📄 **GUÍA COMPLETA DEL CURSO**

Te envío la guía detallada con toda la información que necesitas:

📝 **Incluye:**
• Estructura completa del programa
• Objetivos de aprendizaje por módulo  
• Herramientas y recursos incluidos
• Plan de implementación paso a paso
• Casos de éxito con ROI comprobado

*¡Revísala y me cuentas qué te parece!* 👀"""

            # Si tenemos URL válida, enviar archivo; si no, usar fallback
            if pdf_url and pdf_url.startswith('http'):
                # Crear mensaje con archivo adjunto
                outgoing_message = OutgoingMessage(
                    to_number=user_id,
                    body=pdf_message,
                    message_type=MessageType.DOCUMENT,
                    media_url=pdf_url
                )
                
                result = await self.twilio_client.send_message(outgoing_message)
                logger.info(f"📄 PDF real enviado: {pdf_filename} desde {pdf_url}")
                
                return result
            else:
                # Fallback: enviar solo mensaje de texto informativo
                raise Exception("URL no disponible - usar fallback")
            
        except Exception as e:
            logger.error(f"Error enviando PDF real: {e}")
            # Fallback: enviar mensaje de texto si falla el archivo
            fallback_message = f"""📄 **DOCUMENTO DEL CURSO**

Hubo un problema técnico enviando el PDF. 

📧 **Solución alternativa:**
Te enviaremos el documento por correo electrónico o puedes solicitarlo directamente a nuestro asesor.

🔗 También está disponible en nuestro sitio web."""
            
            fallback_outgoing = OutgoingMessage(
                to_number=user_id,
                body=fallback_message,
                message_type=MessageType.TEXT
            )
            
            return await self.twilio_client.send_message(fallback_outgoing)
    
    async def _send_course_image(self, user_id: str, course_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía la imagen del curso real desde la carpeta resources.
        
        Args:
            user_id: ID del usuario
            course_info: Información del curso
            
        Returns:
            Resultado del envío
        """
        try:
            image_filename = course_info.get('image_resource', 'experto_ia_profesionales.jpg')
            
            # Intentar usar ngrok si está disponible, sino fallback
            from app.config import settings
            ngrok_url = settings.ngrok_url
            
            if ngrok_url:
                # Asegurar que no haya doble barra en la URL
                base_url = ngrok_url.rstrip('/')
                image_url = f"{base_url}/resources/course_materials/{image_filename}"
                logger.info(f"🖼️ Usando URL ngrok para imagen: {image_url}")
            else:
                image_url = None  # Forzar fallback si no hay ngrok
                logger.info(f"⚠️ NGROK_URL no configurado, usando fallback para imagen")
            
            # Mensaje acompañando a la imagen - solo título en negritas
            image_message = f"""🎯 **ESTRUCTURA VISUAL DEL CURSO**"""

            # Si tenemos URL válida, enviar archivo; si no, usar fallback
            if image_url and image_url.startswith('http'):
                # Crear mensaje con imagen adjunta
                outgoing_message = OutgoingMessage(
                    to_number=user_id,
                    body=image_message,
                    message_type=MessageType.IMAGE,
                    media_url=image_url
                )
                
                result = await self.twilio_client.send_message(outgoing_message)
                logger.info(f"🖼️ Imagen real enviada: {image_filename} desde {image_url}")
                
                return result
            else:
                # Fallback: enviar solo mensaje de texto informativo
                raise Exception("URL no disponible - usar fallback")
            
        except Exception as e:
            logger.error(f"Error enviando imagen real: {e}")
            # Fallback: enviar mensaje de texto si falla la imagen
            fallback_message = f"""🖼️ **IMAGEN DEL CURSO**

Hubo un problema técnico enviando la imagen. 

🎨 **Esta imagen muestra:**
• Estructura visual del curso completo
• Herramientas prácticas que dominarás
• Cronograma de implementación
• Resultados esperados por módulo

📧 **Solución alternativa:**
Te enviaremos las imágenes por correo electrónico o las puedes ver directamente con nuestro asesor."""
            
            fallback_outgoing = OutgoingMessage(
                to_number=user_id,
                body=fallback_message,
                message_type=MessageType.TEXT
            )
            
            return await self.twilio_client.send_message(fallback_outgoing)
    
    def _create_follow_up_message(
        self, 
        course_info: Dict[str, Any], 
        user_memory: LeadMemory
    ) -> str:
        """
        Crea mensaje de seguimiento para engagement.
        
        Args:
            course_info: Información del curso
            user_memory: Memoria del usuario
            
        Returns:
            Mensaje de seguimiento
        """
        try:
            course_name = course_info.get('name', 'este curso')
            price = course_info.get('price', 0)
            
            follow_up_parts = [
                f"🚀 **¿Listo para transformar tu PyME con IA?**",
                "",
                f"👆 Acabas de recibir toda la información de **{course_name}**",
                "",
                "💬 **Próximos pasos:**",
                "• Revisa el documento PDF con los detalles completos",
                "• Analiza cómo aplicarías esto en tu empresa específica",
                "• Si tienes preguntas específicas, escríbeme aquí mismo",
                "",
                f"🎯 **Oferta especial:** Reserva tu lugar ahora con solo $97 (resto antes de iniciar)"
            ]
            
            return "\n".join(follow_up_parts)
            
        except Exception as e:
            logger.error(f"Error creando mensaje de seguimiento: {e}")
            return "¿Tienes alguna pregunta sobre el curso? ¡Estoy aquí para ayudarte!"
    
    async def _send_course_not_found_message(
        self, 
        user_id: str, 
        course_code: str
    ) -> Dict[str, Any]:
        """
        Envía mensaje cuando no se encuentra el curso.
        
        Args:
            user_id: ID del usuario
            course_code: Código del curso que no se encontró
            
        Returns:
            Resultado del envío
        """
        try:
            message = f"""🤔 **Curso no encontrado**

Lo siento, no pude encontrar información para el código **{course_code}**.

📚 **Cursos disponibles:**
• #CursoIA1 - Introducción a IA para PyMEs
• #CursoIA2 - IA Intermedia para Automatización 
• #CursoIA3 - IA Avanzada: Transformación Digital

¿Te interesa información de alguno de estos cursos? Solo escribe el código que te interese."""

            outgoing_message = OutgoingMessage(
                to_number=user_id,
                body=message,
                message_type=MessageType.TEXT
            )
            
            result = await self.twilio_client.send_message(outgoing_message)
            
            return {
                'success': True,
                'processed': True,
                'response_sent': True,
                'response_text': message,
                'response_sid': result.get('message_sid'),
                'error_type': 'course_not_found'
            }
            
        except Exception as e:
            logger.error(f"Error enviando mensaje de curso no encontrado: {e}")
            return {'success': False, 'error': str(e)}