"""
Caso de uso principal para procesar el flujo completo de anuncios.
"""
import os
from typing import Dict, Any, List
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.templates.ad_flow_templates import AdFlowTemplates


class ProcessAdFlowUseCase:
    """Caso de uso principal para procesar el flujo completo de anuncios"""
    
    def __init__(self, memory_use_case: ManageUserMemoryUseCase, 
                 privacy_flow_use_case: PrivacyFlowUseCase,
                 course_query_use_case: QueryCourseInformationUseCase,
                 twilio_client=None):
        self.memory_use_case = memory_use_case
        self.privacy_flow_use_case = privacy_flow_use_case
        self.course_query_use_case = course_query_use_case
        self.twilio_client = twilio_client
        self.templates = AdFlowTemplates()
    
    async def execute(self, message_data: Dict[str, Any], 
                     user_data: Dict[str, Any], 
                     hashtags_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el flujo completo de anuncios
        
        Args:
            message_data: Datos del mensaje
            user_data: Datos del usuario
            hashtags_info: Información de hashtags detectados
            
        Returns:
            Dict con respuesta del flujo de anuncios
        """
        try:
            user_id = str(user_data.get('id', user_data.get('user_id')))
            course_id = hashtags_info.get('course_id')
            
            # 1. Verificar privacidad y nombre
            privacy_valid = await self._validate_privacy_and_name(user_id)
            
            if not privacy_valid:
                # Mostrar flujo de privacidad existente
                # Crear IncomingMessage desde webhook_data
                from app.domain.entities.message import IncomingMessage
                incoming_message = IncomingMessage.from_twilio_webhook(message_data)
                return await self.privacy_flow_use_case.handle_privacy_flow(user_id, incoming_message)
            
            # 2. DESACTIVAR AGENTE - Iniciar flujo de anuncio
            responses = []
            
            # 3. Mostrar mensaje de bienvenida
            user_memory = self.memory_use_case.get_user_memory(user_id)
            user_name = user_memory.name or user_data.get('first_name', 'amigo')
            is_first_time = user_memory.interaction_count == 0
            
            welcome_message = self.templates.get_welcome_message(user_name, is_first_time)
            responses.append(welcome_message)
            
            # 4. Enviar PDF del curso
            if course_id:
                pdf_message = await self._send_course_pdf(course_id)
                responses.append(pdf_message)
            
            # 5. Enviar imagen del curso
            if course_id:
                image_message = await self._send_course_image(course_id)
                responses.append(image_message)
            
            # 6. Mostrar plantilla con datos del curso
            if course_id:
                course_template = await self._present_course_template(course_id, user_name)
                responses.append(course_template)
            
            # 7. Mostrar mensaje motivador
            motivational_message = self.templates.get_motivational_message(user_name)
            responses.append(motivational_message)
            
            # 8. Guardar selected_course en memoria
            if course_id:
                await self._save_selected_course_to_memory(user_id, course_id)
            
            # 9. REACTIVAR AGENTE - ENVIAR MENSAJES POR SEPARADO (no combinar)
            # Para evitar límite de 1600 caracteres de WhatsApp
            
            # 10. ENVIAR REALMENTE LOS MENSAJES A TWILIO UNO POR UNO
            response_sids = []
            combined_response = ""  # Para logging
            
            if self.twilio_client:
                from app.domain.entities.message import OutgoingMessage, MessageType
                
                for i, response_text in enumerate(responses):
                    if response_text.strip():  # Solo enviar si no está vacío
                        outgoing_message = OutgoingMessage(
                            to_number=user_id,
                            body=response_text.strip(),
                            message_type=MessageType.TEXT
                        )
                        twilio_result = await self.twilio_client.send_message(outgoing_message)
                        response_sids.append(twilio_result.get('message_sid'))
                        combined_response += response_text + "\n\n"  # Solo para logging
                        
                        # Pequeña pausa entre mensajes para orden correcto
                        import asyncio
                        await asyncio.sleep(0.5)
            
            # Si no hay Twilio, combinar para respuesta (testing)
            if not self.twilio_client:
                combined_response = "\n\n".join(responses)
            
            return {
                'success': True,
                'response_text': combined_response,
                'response_sid': response_sids, # Cambiado para devolver los SIDs
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
    
    async def _validate_privacy_and_name(self, user_id: str) -> bool:
        """Verifica que aceptó privacidad Y tiene nombre guardado"""
        try:
            user_memory = self.memory_use_case.get_user_memory(user_id)
            return bool(user_memory.privacy_accepted and user_memory.name)
        except Exception:
            return False
    
    async def _send_course_pdf(self, course_id: str) -> str:
        """Envía PDF del curso (simulador: mensaje, Twilio: archivo real)"""
        pdf_path = "resources/course_materials/experto_ia_profesionales.pdf"
        
        if os.path.exists(pdf_path):
            return self.templates.get_simulator_pdf_message()
        else:
            return self.templates.get_pdf_message()
    
    async def _send_course_image(self, course_id: str) -> str:
        """Envía imagen del curso (simulador: mensaje, Twilio: archivo real)"""
        image_path = "resources/course_materials/experto_ia_profesionales.jpg"
        
        if os.path.exists(image_path):
            return self.templates.get_simulator_image_message()
        else:
            return self.templates.get_image_message()
    
    async def _present_course_template(self, course_id: str, user_name: str) -> str:
        """Presenta plantilla específica del curso desde anuncio (datos desde BD)"""
        try:
            # Convertir string a UUID
            from uuid import UUID
            course_uuid = UUID(course_id)
            
            # Obtener datos del curso desde BD
            course_data = await self.course_query_use_case.get_course_details(course_uuid)
            
            if course_data:
                return self.templates.get_course_template(course_data)
            else:
                return "❌ No se pudo obtener información del curso desde la base de datos."
                
        except Exception as e:
            return f"❌ Error obteniendo datos del curso: {str(e)}"
    
    async def _save_selected_course_to_memory(self, user_id: str, course_id: str):
        """Guarda selected_course en memoria automáticamente"""
        try:
            user_memory = self.memory_use_case.get_user_memory(user_id)
            user_memory.selected_course = course_id
            # Usar el memory_manager directamente
            self.memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
        except Exception as e:
            print(f"Error guardando selected_course en memoria: {e}") 