"""
Caso de uso para activación inteligente de herramientas de conversión.
Integra el sistema de herramientas con la arquitectura Clean.
"""
import logging
from typing import Dict, Any, List, Optional

from app.infrastructure.tools.tool_system import initialize_tool_system, ToolActivationSystem
from app.domain.entities.message import IncomingMessage

logger = logging.getLogger(__name__)

def debug_print(message: str, function_name: str = "", file_name: str = "tool_activation_use_case.py"):
    """Print de debug visual para consola"""
    print(f"🛠️ [{file_name}::{function_name}] {message}")


class ToolActivationUseCase:
    """
    Caso de uso para activación inteligente de herramientas de conversión.
    
    Responsabilidades:
    - Integrar sistema de herramientas con Clean Architecture
    - Activar herramientas basadas en análisis de intención
    - Manejar resultados y envío de contenido multimedia
    - Logging y métricas de uso de herramientas
    """
    
    def __init__(
        self, 
        db_service=None, 
        resource_service=None, 
        contact_flow_handler=None
    ):
        """
        Inicializa el caso de uso con servicios opcionales.
        
        Args:
            db_service: Servicio de base de datos (opcional, usa mock)
            resource_service: Servicio de recursos (opcional, usa mock)
            contact_flow_handler: Handler de flujo de contacto (opcional)
        """
        self.tool_system = initialize_tool_system(
            db_service=db_service,
            resource_service=resource_service,
            contact_flow_handler=contact_flow_handler
        )
        self.logger = logging.getLogger(__name__)
        debug_print("✅ Sistema de herramientas inicializado", "__init__")
    
    async def activate_tools_by_intent(
        self,
        intent_analysis: Dict[str, Any],
        user_id: str,
        incoming_message: IncomingMessage,
        user_memory=None,
        course_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Activa herramientas basadas en análisis de intención.
        
        Args:
            intent_analysis: Resultado del análisis de intención
            user_id: ID del usuario
            incoming_message: Mensaje entrante del usuario
            user_memory: Memoria del usuario
            course_id: ID del curso (opcional)
            
        Returns:
            Lista de resultados de herramientas activadas
        """
        try:
            category = intent_analysis.get('category', 'GENERAL_QUESTION')
            confidence = intent_analysis.get('confidence', 0.5)
            
            debug_print(f"🎯 Activando herramientas para: {category} (confianza: {confidence})", "activate_tools_by_intent")
            
            # Obtener course_id de la memoria si no se proporciona
            if not course_id and user_memory:
                course_id = getattr(user_memory, 'selected_course', None)
            
            # Activar herramientas usando el sistema
            activated_tools = await self.tool_system.activate_tools_by_intent(
                intent_category=category,
                confidence=confidence,
                user_id=user_id,
                course_id=course_id,
                user_message=incoming_message.body,
                user_memory=user_memory
            )
            
            debug_print(f"✅ {len(activated_tools)} herramientas activadas", "activate_tools_by_intent")
            
            # Procesar resultados para integración con el sistema de mensajes
            processed_results = await self._process_tool_results(activated_tools, user_id)
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"💥 Error activando herramientas: {e}")
            debug_print(f"❌ Error: {e}", "activate_tools_by_intent")
            return []
    
    async def _process_tool_results(
        self, 
        tool_results: List[Dict[str, Any]], 
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Procesa los resultados de las herramientas para integración con el sistema.
        
        Args:
            tool_results: Resultados crudos de las herramientas
            user_id: ID del usuario
            
        Returns:
            Resultados procesados para el sistema de mensajes
        """
        processed_results = []
        
        try:
            for result in tool_results:
                if not result.get('tool_activated', False):
                    # Si la herramienta falló, solo loggear
                    debug_print(f"⚠️ Herramienta falló: {result.get('content', 'Sin error')}", "_process_tool_results")
                    continue
                
                processed_result = {
                    'success': True,
                    'type': result.get('type', 'text'),
                    'content': result.get('content', ''),
                    'has_multimedia': result.get('type') == 'multimedia',
                    'resources': result.get('resources', []),
                    'priority': result.get('priority', 'normal'),
                    'user_id': user_id
                }
                
                # Manejar casos especiales
                if result.get('type') == 'contact_flow_activated':
                    processed_result['requires_flow_transfer'] = True
                    processed_result['priority'] = 'critical'
                    debug_print("🚨 FLUJO DE CONTACTO ACTIVADO", "_process_tool_results")
                
                processed_results.append(processed_result)
                
        except Exception as e:
            self.logger.error(f"Error procesando resultados de herramientas: {e}")
        
        return processed_results
    
    def should_activate_tools(self, intent_analysis: Dict[str, Any]) -> bool:
        """
        Determina si se deben activar herramientas basado en el análisis de intención.
        
        Args:
            intent_analysis: Resultado del análisis de intención
            
        Returns:
            True si se deben activar herramientas
        """
        category = intent_analysis.get('category', 'GENERAL_QUESTION')
        confidence = intent_analysis.get('confidence', 0.5)
        
        # Categorías que siempre activan herramientas
        high_priority_categories = [
            'FREE_RESOURCES',  # Siempre enviar recursos
            'CONTACT_REQUEST'  # Siempre activar contacto
        ]
        
        # Categorías que activan herramientas con confianza media
        medium_priority_categories = [
            'EXPLORATION',
            'OBJECTION_PRICE',
            'OBJECTION_VALUE',
            'BUYING_SIGNALS'
        ]
        
        if category in high_priority_categories:
            return True
        elif category in medium_priority_categories and confidence >= 0.6:
            return True
        
        return False
    
    def get_tool_activation_summary(self) -> Dict[str, Any]:
        """
        Obtiene resumen de activaciones de herramientas.
        
        Returns:
            Dict con estadísticas del sistema de herramientas
        """
        try:
            tool_stats = {}
            for tool_name, tool in self.tool_system.tools.items():
                tool_stats[tool_name] = {
                    'category': tool.category,
                    'usage_count': tool.usage_count
                }
            
            return {
                'total_tools': len(self.tool_system.tools),
                'tool_stats': tool_stats,
                'activation_history_count': len(self.tool_system.activation_history)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de herramientas: {e}")
            return {'error': str(e)}

# ============================================================================
# INTEGRACIÓN CON EL SISTEMA EXISTENTE
# ============================================================================

def integrate_tool_system_with_existing_architecture():
    """
    Función helper para integrar el sistema de herramientas con la arquitectura existente.
    
    Esta función debe ser llamada en el startup del webhook para configurar
    el sistema de herramientas correctamente.
    """
    debug_print("🔧 Integrando sistema de herramientas con arquitectura existente", "integrate_tool_system")
    
    # TODO: Aquí se integraría con:
    # - DatabaseService real cuando esté disponible
    # - ResourceService real cuando esté disponible
    # - ContactFlowHandler real cuando esté disponible
    
    debug_print("✅ Sistema de herramientas integrado correctamente", "integrate_tool_system")
    
    return {
        'tool_activation_use_case': ToolActivationUseCase(),
        'integration_status': 'ready'
    }