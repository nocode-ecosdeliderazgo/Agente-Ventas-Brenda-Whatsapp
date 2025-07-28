"""
SISTEMA DE HERRAMIENTAS DE CONVERSIÓN - BOT BRENDA
==================================================
Estructura base del sistema de herramientas de conversión basado en el sistema legacy.
Esta implementación provee la arquitectura completa sin los mensajes específicos.

Estado: ✅ ESTRUCTURA BASE PREPARADA
Fecha: Julio 2025
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# ============================================================================
# 1. INTERFAZ BASE DE HERRAMIENTAS
# ============================================================================

class BaseTool(ABC):
    """
    Interfaz base para todas las herramientas de conversión.
    
    Funcionalidad:
    - Define estructura común para todas las herramientas
    - Maneja logging y métricas automáticamente
    - Proporciona validación de parámetros
    """
    
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.usage_count = 0
        
    @abstractmethod
    async def execute(self, user_id: str, course_id: str = None, **kwargs) -> Dict[str, Any]:
        """Ejecuta la herramienta específica."""
        pass
    
    async def log_usage(self, user_id: str, course_id: str, success: bool = True):
        """Registra el uso de la herramienta para métricas."""
        try:
            self.usage_count += 1
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'tool_name': self.name,
                'category': self.category,
                'user_id': user_id,
                'course_id': course_id,
                'success': success
            }
            
            logger.info(f"🛠️ HERRAMIENTA ACTIVADA: {self.name} | {user_id} | {success}")
            
            # Guardar en archivo de métricas
            log_file = "tool_usage_metrics.json"
            try:
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                else:
                    logs = []
                
                logs.append(log_entry)
                
                # Mantener solo los últimos 1000 registros
                if len(logs) > 1000:
                    logs = logs[-1000:]
                
                with open(log_file, 'w') as f:
                    json.dump(logs, f, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                logger.error(f"Error guardando métricas de herramientas: {e}")
                
        except Exception as e:
            logger.error(f"Error registrando uso de herramienta: {e}")

# ============================================================================
# 2. HERRAMIENTAS DE DEMOSTRACIÓN
# ============================================================================

class EnviarRecursosGratuitos(BaseTool):
    """
    Herramienta para enviar recursos gratuitos desde la base de datos.
    """
    
    def __init__(self, resource_service, db_service=None):
        super().__init__("enviar_recursos_gratuitos", "demonstration")
        self.resource_service = resource_service
        self.db_service = db_service
    
    async def execute(self, user_id: str, course_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta el envío de recursos gratuitos.
        
        Returns:
            Dict con tipo 'multimedia' y recursos para enviar
        """
        try:
            # Obtener recursos desde servicio
            resources = await self.resource_service.get_free_resources(course_id)
            
            if not resources:
                # Recursos de fallback
                resources = [
                    {
                        "type": "document",
                        "url": "https://recursos.aprenda-ia.com/guia-prompting-principiantes.pdf",
                        "caption": "📖 Guía de Prompting para Principiantes"
                    },
                    {
                        "type": "document", 
                        "url": "https://recursos.aprenda-ia.com/plantillas-prompts-listos.pdf",
                        "caption": "📝 Plantillas de Prompts Listos para Usar"
                    }
                ]
            
            # TODO: Aquí iría el mensaje personalizado (implementar después)
            mensaje = "¡Te comparto estos recursos de valor que te van a ayudar muchísimo!"
            
            await self.log_usage(user_id, course_id, True)
            
            return {
                "type": "multimedia",
                "content": mensaje,
                "resources": resources,
                "tool_activated": True
            }
            
        except Exception as e:
            logger.error(f"Error en enviar_recursos_gratuitos: {e}")
            await self.log_usage(user_id, course_id, False)
            return {
                "type": "error",
                "content": "Déjame consultar los recursos disponibles para ti.",
                "tool_activated": False
            }

class MostrarSyllabusInteractivo(BaseTool):
    """
    Herramienta para mostrar el syllabus completo del curso.
    """
    
    def __init__(self, db_service):
        super().__init__("mostrar_syllabus_interactivo", "demonstration")
        self.db_service = db_service
    
    async def execute(self, user_id: str, course_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la muestra del syllabus interactivo.
        """
        try:
            # Obtener información del curso
            course_info = await self.db_service.get_course_details(course_id)
            sessions = await self.db_service.get_course_sessions(course_id)
            
            # TODO: Generar mensaje formateado (implementar después)
            mensaje = f"📚 **Temario Completo - {course_info.get('name', 'Curso de IA')}**"
            
            # Agregar sesiones si existen
            if sessions:
                for i, session in enumerate(sessions, 1):
                    mensaje += f"\n**Sesión {i}:** {session.get('title', f'Sesión {i}')}"
            
            resources = [{
                "type": "document",
                "url": f"https://recursos.aprenda-ia.com/syllabus-{course_id}.pdf",
                "caption": "📋 Syllabus Completo - Descarga PDF"
            }]
            
            await self.log_usage(user_id, course_id, True)
            
            return {
                "type": "multimedia",
                "content": mensaje,
                "resources": resources,
                "tool_activated": True
            }
            
        except Exception as e:
            logger.error(f"Error en mostrar_syllabus_interactivo: {e}")
            await self.log_usage(user_id, course_id, False)
            return {
                "type": "error",
                "content": "Déjame consultar el temario detallado para ti.",
                "tool_activated": False
            }

class EnviarPreviewCurso(BaseTool):
    """
    Herramienta para enviar preview en video del curso.
    """
    
    def __init__(self, resource_service):
        super().__init__("enviar_preview_curso", "demonstration")
        self.resource_service = resource_service
    
    async def execute(self, user_id: str, course_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta el envío del preview del curso.
        """
        try:
            preview_url = await self.resource_service.get_course_preview(course_id)
            
            # TODO: Mensaje personalizado (implementar después)
            mensaje = "🎬 **Vista Previa del Curso** - Te comparto un adelanto de lo que vas a encontrar"
            
            resources = [{
                "type": "video",
                "url": preview_url or "https://recursos.aprenda-ia.com/preview-curso.mp4",
                "caption": "🎥 Preview del Curso - 5 minutos"
            }]
            
            await self.log_usage(user_id, course_id, True)
            
            return {
                "type": "multimedia",
                "content": mensaje,
                "resources": resources,
                "tool_activated": True
            }
            
        except Exception as e:
            logger.error(f"Error en enviar_preview_curso: {e}")
            await self.log_usage(user_id, course_id, False)
            return {
                "type": "error",
                "content": "Déjame obtener el preview del curso para ti.",
                "tool_activated": False
            }

# ============================================================================
# 3. HERRAMIENTAS DE PERSUASIÓN
# ============================================================================

class MostrarComparativaPrecios(BaseTool):
    """
    Herramienta para mostrar análisis de inversión vs mercado.
    """
    
    def __init__(self, db_service):
        super().__init__("mostrar_comparativa_precios", "persuasion")
        self.db_service = db_service
    
    async def execute(self, user_id: str, course_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la comparativa de precios.
        """
        try:
            course_info = await self.db_service.get_course_details(course_id)
            price = course_info.get('price_usd', 249)
            
            # TODO: Generar mensaje personalizado con ROI (implementar después)
            mensaje = f"💰 **Análisis de Inversión Inteligente** - Precio: ${price} USD"
            
            await self.log_usage(user_id, course_id, True)
            
            return {
                "type": "text",
                "content": mensaje,
                "tool_activated": True
            }
            
        except Exception as e:
            logger.error(f"Error en mostrar_comparativa_precios: {e}")
            await self.log_usage(user_id, course_id, False)
            return {
                "type": "error",
                "content": "Déjame preparar un análisis de inversión para tu caso específico.",
                "tool_activated": False
            }

class MostrarBonosExclusivos(BaseTool):
    """
    Herramienta para mostrar bonos por tiempo limitado.
    """
    
    def __init__(self, db_service):
        super().__init__("mostrar_bonos_exclusivos", "persuasion")
        self.db_service = db_service
    
    async def execute(self, user_id: str, course_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la muestra de bonos exclusivos.
        """
        try:
            bonos = await self.db_service.get_active_bonuses(course_id)
            
            # TODO: Generar mensaje con bonos reales (implementar después)
            mensaje = "🎁 **BONOS EXCLUSIVOS DISPONIBLES AHORA**"
            
            await self.log_usage(user_id, course_id, True)
            
            return {
                "type": "text",
                "content": mensaje,
                "tool_activated": True
            }
            
        except Exception as e:
            logger.error(f"Error en mostrar_bonos_exclusivos: {e}")
            await self.log_usage(user_id, course_id, False)
            return {
                "type": "error",
                "content": "Déjame consultar los bonos especiales disponibles para ti.",
                "tool_activated": False
            }

# ============================================================================
# 4. HERRAMIENTAS DE CIERRE
# ============================================================================

class ContactarAsesorDirecto(BaseTool):
    """
    Herramienta crítica para activar flujo de contacto directo.
    """
    
    def __init__(self, contact_flow_handler=None):
        super().__init__("contactar_asesor_directo", "closing")
        self.contact_flow_handler = contact_flow_handler
    
    async def execute(self, user_id: str, course_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta el flujo de contacto directo con asesor.
        
        IMPORTANTE: Esta herramienta tiene prioridad máxima y transfiere el control
        """
        try:
            if self.contact_flow_handler:
                # Activar flujo de contacto si está disponible
                result = await self.contact_flow_handler.start_contact_flow(user_id, course_id)
                content = result
            else:
                # Flujo básico de contacto
                content = "Te voy a conectar con un asesor. Por favor compárteme tu email para coordinar el contacto."
            
            await self.log_usage(user_id, course_id, True)
            
            return {
                "type": "contact_flow_activated",
                "content": content,
                "tool_activated": True,
                "priority": "critical"
            }
            
        except Exception as e:
            logger.error(f"Error en contactar_asesor_directo: {e}")
            await self.log_usage(user_id, course_id, False)
            return {
                "type": "error",
                "content": "Te voy a conectar con un asesor. Déjame un momento para coordinar.",
                "tool_activated": False
            }

# ============================================================================
# 5. SISTEMA DE ACTIVACIÓN INTELIGENTE
# ============================================================================

class ToolActivationSystem:
    """
    Sistema de activación inteligente de herramientas basado en intención.
    
    Funcionalidad:
    - Analiza intención y activa herramientas apropiadas
    - Máximo 2 herramientas por interacción
    - Prioriza herramientas más efectivas
    """
    
    def __init__(self):
        self.tools = {}
        self.activation_history = []
    
    def register_tool(self, tool: BaseTool):
        """Registra una herramienta en el sistema."""
        self.tools[tool.name] = tool
        logger.info(f"🛠️ Herramienta registrada: {tool.name} ({tool.category})")
    
    async def activate_tools_by_intent(
        self, 
        intent_category: str, 
        confidence: float,
        user_id: str, 
        course_id: str = None,
        user_message: str = "",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Activa herramientas basadas en la intención detectada.
        
        Args:
            intent_category: Categoría de intención (EXPLORATION, OBJECTION_PRICE, etc.)
            confidence: Nivel de confianza del análisis
            user_id: ID del usuario
            course_id: ID del curso
            user_message: Mensaje original del usuario
            
        Returns:
            Lista de resultados de herramientas activadas
        """
        activated_tools = []
        
        try:
            # Mapping de intenciones a herramientas
            intent_tool_mapping = {
                'EXPLORATION': self._handle_exploration_intent,
                'FREE_RESOURCES': self._handle_free_resources_intent,
                'OBJECTION_PRICE': self._handle_price_objection_intent,
                'OBJECTION_VALUE': self._handle_value_objection_intent,
                'BUYING_SIGNALS': self._handle_buying_signals_intent,
                'CONTACT_REQUEST': self._handle_contact_request_intent
            }
            
            # Activar herramientas según intención
            if intent_category in intent_tool_mapping and confidence > 0.6:
                handler = intent_tool_mapping[intent_category]
                tools_to_activate = await handler(user_message, user_id, course_id, **kwargs)
                
                # Ejecutar herramientas (máximo 2)
                for tool_name in tools_to_activate[:2]:
                    if tool_name in self.tools:
                        result = await self.tools[tool_name].execute(user_id, course_id, **kwargs)
                        activated_tools.append(result)
            
            # Registrar activación
            self.activation_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'intent_category': intent_category,
                'confidence': confidence,
                'user_id': user_id,
                'tools_activated': [r.get('tool_activated', False) for r in activated_tools]
            })
            
        except Exception as e:
            logger.error(f"Error activando herramientas para intención {intent_category}: {e}")
        
        return activated_tools
    
    async def _handle_exploration_intent(self, message: str, user_id: str, course_id: str, **kwargs) -> List[str]:
        """Maneja intención de exploración."""
        if 'contenido' in message.lower() or 'módulo' in message.lower():
            return ['mostrar_syllabus_interactivo']
        elif 'ver' in message.lower() or 'ejemplo' in message.lower():
            return ['enviar_preview_curso']
        else:
            return ['enviar_recursos_gratuitos']
    
    async def _handle_free_resources_intent(self, message: str, user_id: str, course_id: str, **kwargs) -> List[str]:
        """Maneja solicitud directa de recursos."""
        return ['enviar_recursos_gratuitos']
    
    async def _handle_price_objection_intent(self, message: str, user_id: str, course_id: str, **kwargs) -> List[str]:
        """Maneja objeciones de precio."""
        return ['mostrar_comparativa_precios']
    
    async def _handle_value_objection_intent(self, message: str, user_id: str, course_id: str, **kwargs) -> List[str]:
        """Maneja objeciones de valor."""
        return ['mostrar_bonos_exclusivos']
    
    async def _handle_buying_signals_intent(self, message: str, user_id: str, course_id: str, **kwargs) -> List[str]:
        """Maneja señales de compra."""
        if 'asesor' in message.lower() or 'contactar' in message.lower():
            return ['contactar_asesor_directo']
        else:
            return ['mostrar_bonos_exclusivos']
    
    async def _handle_contact_request_intent(self, message: str, user_id: str, course_id: str, **kwargs) -> List[str]:
        """Maneja solicitudes de contacto - CRÍTICO."""
        return ['contactar_asesor_directo']

# ============================================================================
# 6. SERVICIOS MOCK PARA DESARROLLO
# ============================================================================

class MockResourceService:
    """Servicio mock de recursos para desarrollo."""
    
    async def get_free_resources(self, course_id: str) -> List[Dict[str, str]]:
        """Mock de recursos gratuitos."""
        return [
            {
                "type": "document",
                "url": f"https://recursos.aprenda-ia.com/guia-{course_id}.pdf",
                "caption": "📖 Guía de Implementación"
            }
        ]
    
    async def get_course_preview(self, course_id: str) -> str:
        """Mock de preview del curso."""
        return f"https://recursos.aprenda-ia.com/preview-{course_id}.mp4"

class MockDatabaseService:
    """Servicio mock de base de datos para desarrollo."""
    
    async def get_course_details(self, course_id: str) -> Dict[str, Any]:
        """Mock de detalles del curso."""
        return {
            'name': 'Curso de IA Ejemplo',
            'price_usd': 299,
            'total_duration': '8 semanas',
            'level': 'Intermedio'
        }
    
    async def get_course_sessions(self, course_id: str) -> List[Dict[str, Any]]:
        """Mock de sesiones del curso."""
        return [
            {
                'title': 'Introducción a IA',
                'objective': 'Conceptos fundamentales',
                'duration_minutes': 60
            }
        ]
    
    async def get_active_bonuses(self, course_id: str) -> List[Dict[str, Any]]:
        """Mock de bonos activos."""
        return [
            {
                'name': 'Consultoría 1:1',
                'description': 'Sesión personalizada',
                'value_usd': 150
            }
        ]

# ============================================================================
# 7. INICIALIZACIÓN DEL SISTEMA
# ============================================================================

def initialize_tool_system(db_service=None, resource_service=None, contact_flow_handler=None):
    """
    Inicializa el sistema completo de herramientas.
    
    Args:
        db_service: Servicio de base de datos (opcional, usa mock si no se proporciona)
        resource_service: Servicio de recursos (opcional, usa mock si no se proporciona)
        contact_flow_handler: Handler de flujo de contacto (opcional)
        
    Returns:
        ToolActivationSystem configurado con todas las herramientas
    """
    # Usar servicios mock si no se proporcionan
    if not db_service:
        db_service = MockDatabaseService()
    if not resource_service:
        resource_service = MockResourceService()
    
    # Crear sistema de activación
    tool_system = ToolActivationSystem()
    
    # Registrar herramientas de demostración
    tool_system.register_tool(EnviarRecursosGratuitos(resource_service, db_service))
    tool_system.register_tool(MostrarSyllabusInteractivo(db_service))
    tool_system.register_tool(EnviarPreviewCurso(resource_service))
    
    # Registrar herramientas de persuasión
    tool_system.register_tool(MostrarComparativaPrecios(db_service))
    tool_system.register_tool(MostrarBonosExclusivos(db_service))
    
    # Registrar herramientas de cierre
    tool_system.register_tool(ContactarAsesorDirecto(contact_flow_handler))
    
    logger.info(f"✅ Sistema de herramientas inicializado con {len(tool_system.tools)} herramientas")
    
    return tool_system

# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Ejemplo de uso del sistema de herramientas.
    """
    import asyncio
    
    async def test_tool_system():
        """Test básico del sistema de herramientas."""
        # Inicializar sistema
        tool_system = initialize_tool_system()
        
        # Simular activación por intención
        results = await tool_system.activate_tools_by_intent(
            intent_category='FREE_RESOURCES',
            confidence=0.8,
            user_id='test_user_123',
            course_id='test_course_456',
            user_message='¿Tienen recursos gratuitos?'
        )
        
        print("Resultados de herramientas activadas:")
        for result in results:
            print(f"- Tipo: {result.get('type')}")
            print(f"- Activada: {result.get('tool_activated')}")
            print(f"- Contenido: {result.get('content', '')[:100]}...")
    
    # Ejecutar test
    # asyncio.run(test_tool_system())
    print("✅ Sistema de herramientas listo para integración")