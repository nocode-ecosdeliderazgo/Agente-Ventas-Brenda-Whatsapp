"""
Procesador de flujo de anuncios para infraestructura.
"""
import os
from typing import Dict, Any, List
from app.templates.ad_flow_templates import AdFlowTemplates


class AdFlowProcessor:
    """Procesador de flujo de anuncios para infraestructura"""
    
    def __init__(self):
        self.templates = AdFlowTemplates()
    
    def process_ad_message(self, message_data: Dict[str, Any], 
                          user_data: Dict[str, Any],
                          hashtags_info: Dict[str, Any],
                          memory_service,
                          privacy_service,
                          course_service) -> Dict[str, Any]:
        """
        Procesa mensaje que viene de anuncio
        
        Args:
            message_data: Datos del mensaje
            user_data: Datos del usuario
            hashtags_info: Información de hashtags detectados
            memory_service: Servicio de memoria
            privacy_service: Servicio de privacidad
            course_service: Servicio de cursos
            
        Returns:
            Dict con respuesta del flujo de anuncios
        """
        try:
            user_id = str(user_data.get('id', user_data.get('user_id')))
            course_id = hashtags_info.get('course_id')
            
            # 1. Verificar privacidad y nombre
            privacy_valid = self._validate_privacy_and_name(user_id, memory_service)
            
            if not privacy_valid:
                # Mostrar flujo de privacidad existente
                return privacy_service.execute(message_data, user_data)
            
            # 2. DESACTIVAR AGENTE - Iniciar flujo de anuncio
            responses = []
            
            # 3. Mostrar mensaje de bienvenida
            user_memory = memory_service.get_user_memory(user_id)
            user_name = user_memory.name or user_data.get('first_name', 'amigo')
            is_first_time = user_memory.interaction_count == 0
            
            welcome_message = self.templates.get_welcome_message(user_name, is_first_time)
            responses.append(welcome_message)
            
            # 4. Enviar PDF del curso
            pdf_message = self._send_course_pdf(course_id)
            responses.append(pdf_message)
            
            # 5. Enviar imagen del curso
            image_message = self._send_course_image(course_id)
            responses.append(image_message)
            
            # 6. Mostrar plantilla con datos del curso
            course_template = self._present_course_template(course_id, user_name, course_service)
            responses.append(course_template)
            
            # 7. Mostrar mensaje motivador
            motivational_message = self.templates.get_motivational_message(user_name)
            responses.append(motivational_message)
            
            # 8. Guardar selected_course en memoria
            self._save_selected_course_to_memory(user_id, course_id, memory_service)
            
            # 9. REACTIVAR AGENTE - Combinar todas las respuestas
            combined_response = "\n\n".join(responses)
            
            return {
                'success': True,
                'response_text': combined_response,
                'processed': True,
                'ad_flow_completed': True,
                'course_id': course_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processed': False,
                'ad_flow_completed': False
            }
    
    def _validate_privacy_and_name(self, user_id: str, memory_service) -> bool:
        """Verifica que aceptó privacidad Y tiene nombre guardado"""
        try:
            user_memory = memory_service.get_user_memory(user_id)
            return user_memory.has_accepted_privacy and user_memory.name
        except Exception:
            return False
    
    def _send_course_pdf(self, course_id: str) -> str:
        """Envía PDF del curso (simulador: mensaje, Twilio: archivo real)"""
        pdf_path = "resources/course_materials/experto_ia_profesionales.pdf"
        
        if os.path.exists(pdf_path):
            return self.templates.get_simulator_pdf_message()
        else:
            return self.templates.get_pdf_message()
    
    def _send_course_image(self, course_id: str) -> str:
        """Envía imagen del curso (simulador: mensaje, Twilio: archivo real)"""
        image_path = "resources/course_materials/experto_ia_profesionales.jpg"
        
        if os.path.exists(image_path):
            return self.templates.get_simulator_image_message()
        else:
            return self.templates.get_image_message()
    
    def _present_course_template(self, course_id: str, user_name: str, course_service) -> str:
        """Presenta plantilla específica del curso desde anuncio (datos desde BD)"""
        try:
            # Obtener datos del curso desde BD
            course_data = course_service.get_course_details(course_id)
            
            if course_data:
                return self.templates.get_course_template(course_data)
            else:
                return "❌ No se pudo obtener información del curso desde la base de datos."
                
        except Exception as e:
            return f"❌ Error obteniendo datos del curso: {str(e)}"
    
    def _save_selected_course_to_memory(self, user_id: str, course_id: str, memory_service):
        """Guarda selected_course en memoria automáticamente"""
        try:
            user_memory = memory_service.get_user_memory(user_id)
            user_memory.selected_course = course_id
            memory_service.save_user_memory(user_id, user_memory)
        except Exception as e:
            print(f"Error guardando selected_course en memoria: {e}") 