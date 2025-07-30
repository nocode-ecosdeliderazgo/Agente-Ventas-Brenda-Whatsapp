#!/usr/bin/env python3
"""
Caso de uso para el sistema de FAQ (Preguntas Frecuentes).
Permite responder automáticamente preguntas frecuentes.
"""

import asyncio
from typing import Dict, Any, Optional, List
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.templates.faq_templates import FAQTemplates
from app.infrastructure.faq.faq_processor import FAQProcessor


class FAQFlowUseCase:
    """
    Caso de uso para manejar el flujo de FAQ.
    """
    
    def __init__(
        self,
        memory_use_case: ManageUserMemoryUseCase,
        twilio_client: TwilioWhatsAppClient
    ):
        self.memory_use_case = memory_use_case
        self.twilio_client = twilio_client
        self.templates = FAQTemplates()
        self.faq_processor = FAQProcessor()
    
    async def execute(
        self, 
        webhook_data: Dict[str, Any], 
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta el flujo de FAQ completo.
        
        Args:
            webhook_data: Datos del webhook de Twilio
            user_data: Datos del usuario
            
        Returns:
            Dict con el resultado del flujo
        """
        try:
            print("❓ INICIANDO FLUJO DE FAQ")
            print(f"   Usuario: {user_data.get('id', 'unknown')}")
            print(f"   Mensaje: {webhook_data.get('Body', '')}")
            
            user_message = webhook_data.get('Body', '').strip()
            
            # Obtener memoria del usuario
            user_memory = self.memory_use_case.get_user_memory(user_data['id'])
            
            # Detectar si es una pregunta frecuente
            faq_match = await self.faq_processor.detect_faq(user_message)
            
            if faq_match:
                print(f"✅ FAQ detectada: {faq_match['category']}")
                return await self._handle_faq_response(
                    webhook_data, 
                    user_data, 
                    user_memory, 
                    faq_match
                )
            else:
                print("❌ No es una FAQ")
                return {
                    'success': False,
                    'is_faq': False,
                    'response_text': None
                }
                
        except Exception as e:
            print(f"❌ Error en flujo de FAQ: {e}")
            return {
                'success': False,
                'error': str(e),
                'response_text': 'Lo siento, hubo un error procesando tu pregunta. Por favor, intenta de nuevo.'
            }
    
    async def _handle_faq_response(
        self, 
        webhook_data: Dict[str, Any], 
        user_data: Dict[str, Any],
        user_memory: Any,
        faq_match: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Maneja la respuesta a una FAQ."""
        print(f"📝 Procesando respuesta de FAQ: {faq_match['category']}")
        
        # Obtener información del usuario para personalización
        user_role = getattr(user_memory, 'user_role', '')
        company_size = getattr(user_memory, 'company_size', '')
        industry = getattr(user_memory, 'industry', '')
        
        # Generar respuesta personalizada
        response_text = self.templates.get_faq_response(
            faq_match['category'],
            faq_match['answer'],
            user_data.get('first_name', 'Usuario'),
            user_role,
            company_size,
            industry
        )
        
        # Guardar FAQ en memoria
        self._update_faq_memory(user_data['id'], faq_match)
        
        # Enviar respuesta
        await self.twilio_client.send_message(response_text)
        
        return {
            'success': True,
            'is_faq': True,
            'faq_category': faq_match['category'],
            'response_text': response_text,
            'escalation_needed': faq_match.get('escalation_needed', False)
        }
    
    def _update_faq_memory(self, user_id: str, faq_match: Dict[str, Any]) -> None:
        """
        Actualiza la memoria con información de la FAQ.
        
        Args:
            user_id: ID del usuario
            faq_match: Información de la FAQ
        """
        try:
            memory = self.memory_use_case.get_user_memory(user_id)
            
            # Agregar FAQ al historial
            if not hasattr(memory, 'faq_history'):
                memory.faq_history = []
            
            faq_entry = {
                'category': faq_match['category'],
                'question': faq_match['question'],
                'timestamp': asyncio.get_event_loop().time(),
                'escalation_needed': faq_match.get('escalation_needed', False)
            }
            
            memory.faq_history.append(faq_entry)
            
            # Mantener solo las últimas 10 FAQs
            if len(memory.faq_history) > 10:
                memory.faq_history = memory.faq_history[-10:]
            
            # Guardar memoria actualizada
            self.memory_use_case.memory_manager.save_lead_memory(user_id, memory)
            
        except Exception as e:
            print(f"❌ Error actualizando memoria de FAQ: {e}")
    
    async def detect_faq_intent(self, message: str) -> bool:
        """
        Detecta si el mensaje indica intención de FAQ.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            True si hay intención de FAQ
        """
        faq_keywords = [
            'pregunta', 'duda', 'cómo', 'qué', 'cuándo', 'dónde', 'por qué',
            'información', 'ayuda', 'soporte', 'problema', 'error', 'funciona',
            'precio', 'costo', 'duración', 'tiempo', 'horario', 'fecha',
            'requisitos', 'necesito', 'busco', 'encontrar', 'saber'
        ]
        
        message_lower = message.lower()
        
        # Verificar palabras clave
        for keyword in faq_keywords:
            if keyword in message_lower:
                return True
        
        # Verificar patrones de pregunta
        question_patterns = [
            '¿', '?', 'como', 'que', 'cuando', 'donde', 'por que',
            'cual', 'quien', 'cuanto', 'donde', 'cuando'
        ]
        
        for pattern in question_patterns:
            if pattern in message_lower:
                return True
        
        return False
    
    async def get_faq_suggestions(self, user_id: str) -> List[str]:
        """
        Obtiene sugerencias de FAQ basadas en el historial del usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de sugerencias de FAQ
        """
        try:
            memory = self.memory_use_case.get_user_memory(user_id)
            
            # Obtener FAQs más frecuentes
            common_faqs = await self.faq_processor.get_common_faqs()
            
            # Filtrar basado en el perfil del usuario
            user_role = getattr(memory, 'user_role', '')
            company_size = getattr(memory, 'company_size', '')
            industry = getattr(memory, 'industry', '')
            
            suggestions = []
            for faq in common_faqs:
                if self._is_relevant_for_user(faq, user_role, company_size, industry):
                    suggestions.append(faq['question'])
            
            return suggestions[:5]  # Máximo 5 sugerencias
            
        except Exception as e:
            print(f"❌ Error obteniendo sugerencias de FAQ: {e}")
            return []
    
    def _is_relevant_for_user(
        self, 
        faq: Dict[str, Any], 
        user_role: str, 
        company_size: str, 
        industry: str
    ) -> bool:
        """
        Determina si una FAQ es relevante para el usuario.
        
        Args:
            faq: Información de la FAQ
            user_role: Rol del usuario
            company_size: Tamaño de la empresa
            industry: Industria del usuario
            
        Returns:
            True si es relevante
        """
        # Lógica simple de relevancia
        if 'precio' in faq['category'].lower() and 'CEO' in user_role:
            return True
        if 'implementación' in faq['category'].lower() and 'tecnología' in industry.lower():
            return True
        if 'empresa' in faq['category'].lower() and company_size:
            return True
        
        return True  # Por defecto, mostrar todas 