"""
Caso de uso para manejar el flujo de anuncio de cursos cuando el usuario envía un código específico.
Ejemplo: #CursoIA1 -> Muestra resumen del curso, PDF y imagen
"""
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from memory.lead_memory import LeadMemory

logger = logging.getLogger(__name__)


class CourseAnnouncementUseCase:
    """Caso de uso para manejar anuncios de cursos por código específico."""
    
    def __init__(
        self, 
        course_query_use_case: QueryCourseInformationUseCase,
        memory_use_case: ManageUserMemoryUseCase,
        twilio_client
    ):
        self.course_query_use_case = course_query_use_case
        self.memory_use_case = memory_use_case
        self.twilio_client = twilio_client
        
        # Mapeo de códigos de curso a IDs de base de datos
        # TODO: Esto debería venir de la base de datos o configuración
        self.course_code_mapping = {
            "#CursoIA1": "curso-ia-basico-001",  # ID del curso en la base de datos
            "#CursoIA2": "curso-ia-intermedio-001",
            "#CursoIA3": "curso-ia-avanzado-001",
            # Nuevos códigos para curso específico con archivos reales
            "#Experto_IA_GPT_Gemini": "experto-ia-profesionales-001",
            "#ADSIM_05": "experto-ia-profesionales-001"  # Mismo curso, diferente código de campaña
        }
    
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
            
            for code in self.course_code_mapping.keys():
                if code.lower() in message_lower:
                    return code
            
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
            
            # PRIMERO: Usar información mock específica para códigos especiales
            if course_code in ["#Experto_IA_GPT_Gemini", "#ADSIM_05"]:
                logger.info(f"📚 Usando información específica para código: {course_code}")
                return self._get_mock_course_information(course_code)
            
            # Si tenemos conexión a base de datos, obtener información real
            if self.course_query_use_case:
                try:
                    # Buscar por nombre o descripción (simulando búsqueda por ID)
                    courses = await self.course_query_use_case.search_courses_by_keyword("IA", 1)
                    if courses:
                        course = courses[0]
                        detailed_content = await self.course_query_use_case.get_course_detailed_content(course.id_course)
                        return {
                            'course': course,
                            'detailed_content': detailed_content,
                            'found_in_database': True
                        }
                except Exception as e:
                    logger.warning(f"Error accediendo a base de datos: {e}")
            
            # Fallback: Información predefinida para testing
            return self._get_mock_course_information(course_code)
            
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
            
            # Registrar interés en el curso
            if course_info.get('name'):
                course_name = course_info['name']
                if course_name not in user_memory.interests:
                    user_memory.interests.append(course_name)
            
            # Agregar señal de compra
            buying_signal = f"Solicitó información de {course_code}"
            if buying_signal not in user_memory.buying_signals:
                user_memory.buying_signals.append(buying_signal)
            
            # Incrementar score por interés específico en curso
            user_memory.lead_score += 15
            
            # Actualizar contexto - agregar a message_history en lugar de add_context_entry
            if user_memory.message_history is None:
                user_memory.message_history = []
            
            user_memory.message_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'course_request',
                'course_code': course_code,
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
            main_message = self._create_course_summary_message(course_info, user_memory)
            
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
            
            # Enviar mensaje de seguimiento
            follow_up_message = self._create_follow_up_message(course_info, user_memory)
            
            follow_up_outgoing = OutgoingMessage(
                to_number=user_id,
                body=follow_up_message,
                message_type=MessageType.TEXT
            )
            
            follow_up_result = await self.twilio_client.send_message(follow_up_outgoing)
            
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
                    'follow_up_sent': follow_up_result.get('success', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Error enviando respuesta de anuncio: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_course_summary_message(
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
                price = getattr(db_course, 'price', 0)
                currency = getattr(db_course, 'currency', 'USD')
                level = getattr(db_course, 'level', 'Todos los niveles')
                sessions = getattr(db_course, 'session_count', 8)
                duration = getattr(db_course, 'duration_hours', 12)
            else:
                # Mock data - acceso directo
                course_name = course_info.get('name', 'Curso de IA')
                description = course_info.get('short_description', '')
                price = course_info.get('price', 0)
                currency = course_info.get('currency', 'USD')
                level = course_info.get('level', 'Todos los niveles')
                sessions = course_info.get('session_count', 8)
                duration = course_info.get('duration_hours', 12)
            
            # Crear mensaje principal (VERSIÓN CORTA para evitar límite de 1600 caracteres)
            message_parts = [
                f"🎯 ¡Perfecto {name_greeting}aquí tienes la información!",
                "",
                f"📚 **{course_name}**",
                f"💰 **Inversión:** ${price} {currency}",
                f"📊 **Nivel:** {level} | 🗓️ {sessions} sesiones ({duration}h)",
                ""
            ]
            
            # Agregar solo descripción corta si existe
            if description:
                message_parts.extend([
                    f"📝 {description}",
                    ""
                ])
            
            # Agregar solo los primeros 3 bonos más importantes
            bonuses = course_info.get('bonuses', [])
            if bonuses:
                message_parts.extend([
                    f"🎁 **BONOS INCLUIDOS:**"
                ])
                # Mostrar solo los primeros 3 bonos para ahorrar caracteres
                for bonus in bonuses[:3]:
                    message_parts.append(f"• {bonus}")
                if len(bonuses) > 3:
                    message_parts.append(f"• ...y {len(bonuses) - 3} bonos más")
                message_parts.append("")
            
            # Agregar ROI personalizado según el rol del usuario (versión corta)
            role = user_memory.role if user_memory.role != "No disponible" else ""
            if role:
                roi_message = self._get_role_specific_roi_message_short(role, price)
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
    
    def _get_role_specific_roi_message(self, role: str, course_price: int) -> str:
        """
        Genera mensaje de ROI específico según el rol del usuario.
        
        Args:
            role: Rol/cargo del usuario
            course_price: Precio del curso
            
        Returns:
            Mensaje de ROI personalizado
        """
        try:
            role_lower = role.lower()
            
            if any(keyword in role_lower for keyword in ['marketing', 'digital', 'comercial']):
                return f"💡 **ROI para Marketing Digital:**\n• Ahorra $300 por campaña automatizada\n• Recuperas la inversión en solo 2 campañas\n• ROI proyectado: 200% en el primer mes"
            
            elif any(keyword in role_lower for keyword in ['operaciones', 'operations', 'gerente', 'director']):
                return f"💡 **ROI para Operaciones:**\n• Ahorra $2,000 mensuales en procesos manuales\n• Incrementa eficiencia operativa en 40%\n• ROI proyectado: 400% en el primer mes"
            
            elif any(keyword in role_lower for keyword in ['ceo', 'founder', 'fundador', 'director general']):
                return f"💡 **ROI para Liderazgo Ejecutivo:**\n• Ahorra $27,600 anuales vs contratar analista IA\n• Acelera toma de decisiones estratégicas\n• ROI proyectado: 1,380% anual"
            
            elif any(keyword in role_lower for keyword in ['rh', 'recursos humanos', 'hr', 'talent']):
                return f"💡 **ROI para Recursos Humanos:**\n• Reduce 80% tiempo en procesos de selección\n• Ahorra $1,500 mensuales en reclutamiento\n• ROI proyectado: 300% en el primer trimestre"
            
            else:
                return f"💡 **ROI General para PyMEs:**\n• Ahorra mínimo $1,000 mensuales en automatización\n• Incrementa productividad del equipo en 35%\n• ROI proyectado: 250% en los primeros 3 meses"
                
        except Exception as e:
            logger.error(f"Error generando ROI específico: {e}")
            return ""
    
    def _get_role_specific_roi_message_short(self, role: str, course_price: int) -> str:
        """
        Genera mensaje de ROI específico CORTO según el rol del usuario.

        Args:
            role: Rol/cargo del usuario
            course_price: Precio del curso
            
        Returns:
            Mensaje de ROI personalizado corto
        """
        try:
            role_lower = role.lower()
            
            if any(keyword in role_lower for keyword in ['marketing', 'digital', 'comercial']):
                return f"💡 **ROI Marketing:** Ahorra $300/campaña → ROI 200% primer mes"
            
            elif any(keyword in role_lower for keyword in ['operaciones', 'operations', 'gerente', 'director']):
                return f"💡 **ROI Operaciones:** Ahorra $2,000/mes → ROI 400% primer mes"
            
            elif any(keyword in role_lower for keyword in ['ceo', 'founder', 'fundador', 'director general']):
                return f"💡 **ROI Ejecutivo:** Ahorra $27,600/año → ROI 1,380% anual"
            
            elif any(keyword in role_lower for keyword in ['rh', 'recursos humanos', 'hr', 'talent']):
                return f"💡 **ROI RH:** Ahorra $1,500/mes → ROI 300% primer trimestre"
            
            else:
                return f"💡 **ROI PyME:** Ahorra $1,000/mes → ROI 250% primeros 3 meses"
                
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
            
            # Mensaje acompañando a la imagen
            image_message = f"""🎯 **ESTRUCTURA VISUAL DEL CURSO**

Esta imagen te muestra de un vistazo:

🧠 **Módulos de aprendizaje** organizados progresivamente
⚡ **Herramientas prácticas** que dominarás
📊 **Resultados medibles** que obtendrás
🚀 **Plan de implementación** semana a semana

*¡La transformación de tu empresa empieza aquí!* ✨"""

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
                f"🎯 **Oferta especial:** Reserva tu lugar ahora con solo $97 (resto antes de iniciar)",
                "",
                "¿Qué te parece más interesante del curso? ¿Tienes alguna pregunta específica sobre la implementación en tu sector?"
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