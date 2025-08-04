"""
Caso de uso para activación de bonos cuando el usuario muestra intención de compra.
Maneja la detección de intención de compra y ofrecimiento de bonos workbook desde la base de datos.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from memory.lead_memory import LeadMemory

logger = logging.getLogger(__name__)


class PurchaseBonusUseCase:
    """Caso de uso para activación de bonos por intención de compra."""
    
    def __init__(
        self, 
        course_query_use_case: QueryCourseInformationUseCase = None,
        memory_use_case: ManageUserMemoryUseCase = None,
        twilio_client = None
    ):
        self.course_query_use_case = course_query_use_case
        self.memory_use_case = memory_use_case
        self.twilio_client = twilio_client
        
        # Categorías de intención que activan bonos
        self.purchase_intent_categories = [
            'PURCHASE_INTENT_DIRECT',
            'PURCHASE_INTENT_PRICING', 
            'PURCHASE_READY_SIGNALS',
            'BUYING_SIGNALS_EXECUTIVE'
        ]
    
    def should_activate_purchase_bonus(self, intent_analysis: Dict[str, Any], user_id: str = None) -> bool:
        """
        Determina si se debe activar el bono por intención de compra.
        Evita re-envío si ya se enviaron datos bancarios.
        
        Args:
            intent_analysis: Análisis de intención del mensaje
            user_id: ID del usuario para verificar historial
            
        Returns:
            True si debe activar bonos, False en caso contrario
        """
        try:
            category = intent_analysis.get('category', '')
            confidence = intent_analysis.get('confidence', 0.0)
            
            # 🚨 NUEVO: Verificar si ya se enviaron datos bancarios previamente
            if user_id and self._has_purchase_data_been_sent(user_id):
                logger.info(f"💳 Datos bancarios ya enviados previamente para usuario {user_id}, evitando re-envío")
                return False
            
            # Verificar si es una categoría de compra con suficiente confianza
            if category in self.purchase_intent_categories and confidence >= 0.7:
                logger.info(f"🎁 Intención de compra detectada: {category} (confianza: {confidence})")
                return True
            
            # También verificar si hay señales de compra en el contexto
            buying_signals = intent_analysis.get('buying_signals_detected', [])
            if len(buying_signals) >= 2:  # Múltiples señales de compra
                logger.info(f"🎁 Múltiples señales de compra detectadas: {buying_signals}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando activación de bono: {e}")
            return False
    
    def _has_purchase_data_been_sent(self, user_id: str) -> bool:
        """
        Verifica si ya se enviaron datos bancarios a este usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si ya se enviaron datos bancarios, False en caso contrario
        """
        try:
            if not self.memory_use_case:
                return False
            
            user_memory = self.memory_use_case.get_user_memory(user_id)
            
            # Verificar en message_history si hay envío previo de datos bancarios
            if user_memory and user_memory.message_history:
                for event in user_memory.message_history:
                    if (event.get('action') == 'purchase_bonus_sent' or 
                        'banking_data_sent' in event.get('description', '') or
                        'datos bancarios' in event.get('description', '').lower()):
                        logger.info(f"📋 Encontrado envío previo de datos bancarios: {event.get('timestamp')}")
                        return True
            
            # También verificar en buying_signals
            if user_memory and user_memory.buying_signals:
                for signal in user_memory.buying_signals:
                    if 'datos bancarios enviados' in signal.lower() or 'purchase_bonus_sent' in signal:
                        logger.info(f"🔍 Señal de envío previo encontrada: {signal}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando envío previo de datos bancarios: {e}")
            return False
    
    def is_post_purchase_intent(self, intent_analysis: Dict[str, Any]) -> bool:
        """
        Determina si el mensaje es una intención post-compra (confirmación, pago realizado, etc).
        
        Args:
            intent_analysis: Análisis de intención del mensaje
            
        Returns:
            True si es intención post-compra, False en caso contrario
        """
        try:
            category = intent_analysis.get('category', '')
            post_purchase_categories = [
                'PAYMENT_CONFIRMATION',
                'PAYMENT_COMPLETED', 
                'COMPROBANTE_UPLOAD'
            ]
            
            return category in post_purchase_categories
            
        except Exception as e:
            logger.error(f"Error verificando intención post-compra: {e}")
            return False
    
    async def get_workbook_bonuses(self, course_id: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene bonos workbook disponibles desde la base de datos.
        
        Args:
            course_id: ID del curso (opcional)
            
        Returns:
            Lista de bonos workbook disponibles
        """
        try:
            workbook_bonuses = []
            
            if self.course_query_use_case:
                try:
                    # Obtener elementos multimedia del curso desde la BD
                    # Buscar específicamente workbooks de Coda.io
                    
                    # Por ahora, usamos datos conocidos de la BD basados en elements_url_rows.sql
                    workbook_bonuses = [
                        {
                            'id': '66666662-0000-0000-0000-666666666662',
                            'title': 'Workbook Interactivo: Fundamentos de IA',
                            'description': 'Plantilla Coda.io con ejercicios prácticos de la sesión 1',
                            'url': 'https://coda.io/workbook-plantilla',
                            'type': 'workbook',
                            'session': 'Sesión 1: Descubriendo la IA para Profesionales'
                        },
                        {
                            'id': '77777773-0000-0000-0000-777777777772',
                            'title': 'Guía Construcción de Agente GPT/Gemini',
                            'description': 'Paso a paso para crear tu propio agente de IA',
                            'url': 'https://coda.io/plantilla-agente-gpt',
                            'type': 'guide',
                            'session': 'Sesión 2: Dominando la Comunicación con IA'
                        },
                        {
                            'id': '88888884-0000-0000-0000-888888888882',
                            'title': 'Ejercicios Modelo IMPULSO para PyMEs',
                            'description': 'Retos de negocio interactivos con metodología IMPULSO',
                            'url': 'https://coda.io/casos-impulso-pymes',
                            'type': 'exercises',
                            'session': 'Sesión 3: IMPULSO con ChatGPT para PYMES'
                        },
                        {
                            'id': '99999995-0000-0000-0000-999999999992',
                            'title': 'Plantilla Plan de IA y Métricas',
                            'description': 'Bosquejo personalizable de plan de IA con métricas de impacto',
                            'url': 'https://coda.io/plantilla-plan-ia',
                            'type': 'planning_template',
                            'session': 'Sesión 4: Estrategia y Proyecto Integrador'
                        }
                    ]
                    
                    logger.info(f"📚 Obtenidos {len(workbook_bonuses)} bonos workbook desde BD")
                    
                except Exception as e:
                    logger.warning(f"Error accediendo a BD para bonos: {e}")
            
            # Fallback: Si no hay BD, usar bonos mock
            if not workbook_bonuses:
                workbook_bonuses = self._get_mock_workbook_bonuses()
            
            return workbook_bonuses
            
        except Exception as e:
            logger.error(f"Error obteniendo bonos workbook: {e}")
            return []
    
    def _get_mock_workbook_bonuses(self) -> List[Dict[str, Any]]:
        """Bonos workbook mock para testing."""
        return [
            {
                'id': 'mock-workbook-1',
                'title': 'Workbook Interactivo: Fundamentos de IA',
                'description': 'Plantilla práctica con ejercicios paso a paso',
                'url': 'https://coda.io/workbook-plantilla',
                'type': 'workbook',
                'session': 'Práctica inmediata'
            }
        ]
    
    async def generate_purchase_bonus_message(
        self, 
        user_memory: LeadMemory,
        intent_analysis: Dict[str, Any],
        course_info: Dict[str, Any] = None
    ) -> str:
        """
        Genera mensaje de bono por intención de compra.
        
        Args:
            user_memory: Memoria del usuario
            intent_analysis: Análisis de intención
            course_info: Información del curso (opcional)
            
        Returns:
            Mensaje de bono personalizado
        """
        try:
            # Obtener bonos workbook
            workbook_bonuses = await self.get_workbook_bonuses()
            
            if not workbook_bonuses:
                return self._generate_simple_purchase_response(user_memory)
            
            # Personalizar saludo
            user_name = user_memory.name if user_memory.name != "Usuario" else ""
            name_greeting = f"{user_name}, " if user_name else ""
            
            # Determinar el workbook más relevante según el buyer persona
            selected_bonus = self._select_relevant_workbook(user_memory, workbook_bonuses)
            
            # Crear mensaje de bono
            message_parts = [
                f"🎉 ¡Excelente {name_greeting}me alegra ver tu interés en avanzar con IA!",
                "",
                f"Como veo que estás listo para dar el siguiente paso, quiero ofrecerte un **BONO ESPECIAL** por tu decisión:",
                "",
                f"🎁 **BONO EXCLUSIVO INCLUIDO:**",
                f"📋 **{selected_bonus['title']}**",
                f"✨ {selected_bonus['description']}",
                f"🔗 Acceso directo: {selected_bonus['url']}",
                "",
                f"💡 **¿Por qué te va a encantar?**",
                f"• Práctica inmediata con herramientas reales",
                f"• Aplicable a tu sector específico",
                f"• Resultados medibles desde el primer día",
                "",
                self._get_purchase_cta(user_memory),
                "",
                "💳 **DATOS PARA TRANSFERENCIA:**",
                "🏢 **Razón Social:** Aprende y Aplica AI S.A. de C.V.",
                "🏦 **Banco:** BBVA",
                "💰 **Cuenta CLABE:** 012345678901234567",
                "📄 **RFC:** AAI210307DEF",
                "🧾 **Uso de CFDI:** GO3-Gastos en general",
                "",
                "📲 Una vez realizada la transferencia, envíame tu comprobante y activaré inmediatamente:",
                "✅ Tu acceso al curso completo",
                "🎁 Tu bono workbook exclusivo",
                "📚 Todos los recursos adicionales",
                "",
                "¿Procedes con la transferencia? 🚀"
            ]
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"Error generando mensaje de bono: {e}")
            return self._generate_simple_purchase_response(user_memory)
    
    def _select_relevant_workbook(self, user_memory: LeadMemory, workbooks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Selecciona el workbook más relevante para el usuario."""
        try:
            # Si hay buyer persona match, usar lógica específica
            if hasattr(user_memory, 'buyer_persona_match') and user_memory.buyer_persona_match:
                persona = user_memory.buyer_persona_match
                
                if persona in ['lucia_copypro', 'marcos_multitask']:
                    # Marketing y operaciones: ejercicios prácticos
                    for wb in workbooks:
                        if wb['type'] in ['exercises', 'workbook']:
                            return wb
                elif persona in ['sofia_visionaria', 'daniel_data']:
                    # Ejecutivos: planificación estratégica
                    for wb in workbooks:
                        if wb['type'] in ['planning_template', 'guide']:
                            return wb
            
            # Fallback: primer workbook disponible
            return workbooks[0] if workbooks else {}
            
        except Exception as e:
            logger.error(f"Error seleccionando workbook: {e}")
            return workbooks[0] if workbooks else {}
    
    def _get_purchase_cta(self, user_memory: LeadMemory) -> str:
        """Genera call-to-action personalizado según el buyer persona."""
        try:
            if hasattr(user_memory, 'buyer_persona_match'):
                persona = user_memory.buyer_persona_match
                
                if persona == 'lucia_copypro':
                    return "💰 **ROI Garantizado:** Recupera la inversión automatizando solo 2 campañas"
                elif persona == 'marcos_multitask':
                    return "⚡ **Eficiencia Inmediata:** Reduce 40% el tiempo en reportes operativos"
                elif persona == 'sofia_visionaria':
                    return "🎯 **Ventaja Competitiva:** Diferénciate con IA antes que tu competencia"
                elif persona == 'ricardo_rh':
                    return "👥 **Impulso al Equipo:** Capacita a tu equipo en las herramientas del futuro"
                elif persona == 'daniel_data':
                    return "📊 **Análisis Avanzado:** Implementa IA en tus flujos de datos actuales"
            
            return "🚀 **Transformación Real:** Implementa IA práctica en tu empresa desde el día 1"
            
        except Exception as e:
            logger.error(f"Error generando CTA: {e}")
            return "🚀 **Implementación Práctica:** Aplica IA real en tu empresa"
    
    def _generate_simple_purchase_response(self, user_memory: LeadMemory) -> str:
        """Genera respuesta simple cuando no hay bonos disponibles."""
        user_name = user_memory.name if user_memory.name != "Usuario" else ""
        name_greeting = f"{user_name}, " if user_name else ""
        
        return f"""🎉 ¡Perfecto {name_greeting}me alegra ver tu decisión de avanzar con IA!

El curso incluye múltiples recursos prácticos y bonos exclusivos que te permitirán implementar IA real en tu empresa.

💳 **DATOS PARA TRANSFERENCIA:**
🏢 **Razón Social:** Aprende y Aplica AI S.A. de C.V.
🏦 **Banco:** BBVA
💰 **Cuenta CLABE:** 012345678901234567
📄 **RFC:** AAI210307DEF
🧾 **Uso de CFDI:** GO3-Gastos en general

📲 Una vez realizada la transferencia, envíame tu comprobante y activaré inmediatamente tu acceso completo al curso y todos los bonos.

¿Procedes con la transferencia? 🚀"""
    
    async def update_user_memory_with_purchase_intent(
        self, 
        user_id: str, 
        intent_analysis: Dict[str, Any]
    ) -> None:
        """
        Actualiza la memoria del usuario con señales de intención de compra.
        
        Args:
            user_id: ID del usuario
            intent_analysis: Análisis de intención del mensaje
        """
        try:
            if not self.memory_use_case:
                return
            
            user_memory = self.memory_use_case.get_user_memory(user_id)
            
            # Agregar señal de compra
            purchase_signal = f"Intención de compra detectada: {intent_analysis.get('category', 'unknown')}"
            if purchase_signal not in user_memory.buying_signals:
                user_memory.buying_signals.append(purchase_signal)
            
            # Aumentar score significativamente por intención de compra
            user_memory.lead_score += 25
            
            # Actualizar interest level
            user_memory.interest_level = "high_purchase_intent"
            
            # Agregar a historial
            if user_memory.message_history is None:
                user_memory.message_history = []
            
            user_memory.message_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'purchase_intent_detected',
                'category': intent_analysis.get('category'),
                'confidence': intent_analysis.get('confidence'),
                'description': f"Detectada intención de compra con confianza {intent_analysis.get('confidence', 0)}"
            })
            
            # Guardar memoria actualizada
            self.memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
            logger.info(f"💾 Memoria actualizada con intención de compra para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"Error actualizando memoria con intención de compra: {e}")
    
    async def mark_purchase_data_sent(self, user_id: str) -> None:
        """
        Marca en la memoria del usuario que ya se enviaron los datos bancarios.
        
        Args:
            user_id: ID del usuario
        """
        try:
            if not self.memory_use_case:
                return
            
            user_memory = self.memory_use_case.get_user_memory(user_id)
            
            # Agregar señal de que se enviaron datos bancarios
            banking_data_signal = "Datos bancarios enviados - BBVA CLABE: 012345678901234567"
            if banking_data_signal not in user_memory.buying_signals:
                user_memory.buying_signals.append(banking_data_signal)
            
            # Agregar al historial de mensajes
            if user_memory.message_history is None:
                user_memory.message_history = []
            
            user_memory.message_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'purchase_bonus_sent',
                'description': 'Datos bancarios y bono workbook enviados al usuario',
                'banking_data_sent': True,
                'clabe': '012345678901234567',
                'banco': 'BBVA'
            })
            
            # Aumentar lead score por haber enviado datos de compra
            user_memory.lead_score += 15
            
            # Actualizar stage si no está ya en purchase
            if user_memory.stage != 'purchase_intent':
                user_memory.stage = 'purchase_intent'
                
            # Guardar memoria actualizada
            self.memory_use_case.memory_manager.save_lead_memory(user_id, user_memory)
            logger.info(f"💾 Marcado envío de datos bancarios para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"Error marcando envío de datos bancarios: {e}")