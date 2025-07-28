"""
Caso de uso para activación inteligente de bonos basado en contexto del usuario.
Sistema que utiliza los bonos reales de la base de datos para impulsar conversiones.
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.infrastructure.database.repositories.course_repository import CourseRepository
from memory.lead_memory import LeadMemory

logger = logging.getLogger(__name__)

class BonusActivationUseCase:
    """
    Sistema inteligente para activar bonos específicos según contexto del usuario.
    Utiliza datos reales de la tabla 'bond' para maximizar conversiones.
    """
    
    def __init__(self):
        self.course_repo = CourseRepository()
        
        # Mapeo de buyer personas a bonos prioritarios (por índice en BD)
        self.buyer_persona_bonus_mapping = {
            'lucia_copypro': [1, 6, 3, 7],  # Workbook, Biblioteca prompts, Telegram, LinkedIn
            'marcos_multitask': [1, 2, 8, 4],  # Workbook, Grabaciones, Descuentos, Comunidad
            'sofia_visionaria': [4, 5, 9, 10],  # Comunidad, Bolsa empleo, Q&A, Boletín
            'ricardo_rh': [4, 5, 9, 3],  # Comunidad, Bolsa empleo, Q&A, Telegram
            'daniel_data': [6, 1, 10, 8]  # Biblioteca prompts, Workbook, Boletín, Descuentos
        }
        
        # Mapeo de contextos de conversación a bonos relevantes
        self.context_bonus_mapping = {
            'price_objection': [8, 2, 4],  # Descuentos, Grabaciones, Comunidad
            'time_objection': [2, 1, 3],  # Grabaciones, Workbook, Soporte
            'value_objection': [1, 6, 5],  # Workbook, Biblioteca, Bolsa empleo
            'trust_objection': [4, 9, 7],  # Comunidad, Q&A, LinkedIn
            'technical_fear': [3, 1, 6],  # Soporte, Workbook, Biblioteca
            'career_growth': [5, 7, 4],  # Bolsa empleo, LinkedIn, Comunidad
            'content_creation': [6, 1, 3],  # Biblioteca prompts, Workbook, Soporte
            'automation_need': [1, 6, 8],  # Workbook, Biblioteca, Descuentos
            'team_training': [2, 4, 9],  # Grabaciones, Comunidad, Q&A
            'buying_signals': [8, 2, 4, 1]  # Descuentos, Grabaciones, Comunidad, Workbook
        }
    
    async def get_contextual_bonuses(
        self,
        course_id: UUID,
        user_memory: LeadMemory,
        conversation_context: str,
        limit: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Obtiene bonos contextuales basados en el perfil del usuario y conversación.
        
        Args:
            course_id: ID del curso
            user_memory: Memoria del usuario con contexto empresarial
            conversation_context: Contexto actual de la conversación
            limit: Número máximo de bonos a retornar
            
        Returns:
            Lista de bonos priorizados para el contexto específico
        """
        try:
            # Obtener todos los bonos del curso
            all_bonuses = await self.course_repo.get_course_bonds(course_id)
            if not all_bonuses:
                logger.warning(f"No se encontraron bonos para el curso {course_id}")
                return []
            
            # Convertir a diccionario para fácil acceso por índice
            bonuses_dict = {i+1: bonus.__dict__ for i, bonus in enumerate(all_bonuses)}
            
            # Determinar prioridad de bonos según contexto
            prioritized_bonus_ids = self._get_prioritized_bonus_ids(
                user_memory, conversation_context
            )
            
            # Seleccionar bonos priorizados que existan en BD
            contextual_bonuses = []
            for bonus_id in prioritized_bonus_ids[:limit]:
                if bonus_id in bonuses_dict:
                    bonus_data = bonuses_dict[bonus_id]
                    # Agregar información de contexto
                    bonus_data['priority_reason'] = self._get_bonus_priority_reason(
                        bonus_id, user_memory, conversation_context
                    )
                    bonus_data['sales_angle'] = self._get_bonus_sales_angle(
                        bonus_id, user_memory
                    )
                    contextual_bonuses.append(bonus_data)
            
            logger.info(f"Seleccionados {len(contextual_bonuses)} bonos contextuales para {user_memory.role if user_memory else 'usuario'}")
            return contextual_bonuses
            
        except Exception as e:
            logger.error(f"Error obteniendo bonos contextuales: {e}")
            return []
    
    def _get_prioritized_bonus_ids(
        self,
        user_memory: LeadMemory,
        conversation_context: str
    ) -> List[int]:
        """
        Determina la prioridad de bonos según buyer persona y contexto.
        
        Args:
            user_memory: Memoria del usuario
            conversation_context: Contexto de la conversación
            
        Returns:
            Lista de IDs de bonos priorizados
        """
        # Inicializar con todos los bonos disponibles
        all_bonus_ids = list(range(1, 11))  # Bonos 1-10 según BD
        prioritized_ids = []
        
        try:
            # Prioridad 1: Contexto de conversación específico
            if conversation_context in self.context_bonus_mapping:
                context_bonuses = self.context_bonus_mapping[conversation_context]
                prioritized_ids.extend(context_bonuses)
                logger.info(f"Bonos por contexto '{conversation_context}': {context_bonuses}")
            
            # Prioridad 2: Buyer persona del usuario
            if user_memory and hasattr(user_memory, 'buyer_persona_match'):
                persona = getattr(user_memory, 'buyer_persona_match', 'general_pyme')
                if persona in self.buyer_persona_bonus_mapping:
                    persona_bonuses = self.buyer_persona_bonus_mapping[persona]
                    prioritized_ids.extend(persona_bonuses)
                    logger.info(f"Bonos por buyer persona '{persona}': {persona_bonuses}")
            
            # Prioridad 3: Rol del usuario (inferencia)
            if user_memory and user_memory.role:
                role_bonuses = self._get_bonuses_by_role(user_memory.role)
                prioritized_ids.extend(role_bonuses)
            
            # Prioridad 4: Resto de bonos disponibles
            remaining_bonuses = [bid for bid in all_bonus_ids if bid not in prioritized_ids]
            prioritized_ids.extend(remaining_bonuses)
            
            # Eliminar duplicados manteniendo orden
            seen = set()
            unique_prioritized = []
            for bid in prioritized_ids:
                if bid not in seen:
                    seen.add(bid)
                    unique_prioritized.append(bid)
            
            return unique_prioritized
            
        except Exception as e:
            logger.error(f"Error priorizando bonos: {e}")
            return all_bonus_ids
    
    def _get_bonuses_by_role(self, role: str) -> List[int]:
        """Obtiene bonos relevantes según el rol del usuario."""
        role_lower = role.lower()
        
        if any(keyword in role_lower for keyword in ['marketing', 'content', 'comunicac']):
            return [6, 1, 7]  # Biblioteca prompts, Workbook, LinkedIn
        elif any(keyword in role_lower for keyword in ['operaciones', 'operations', 'gerente']):
            return [1, 2, 8]  # Workbook, Grabaciones, Descuentos
        elif any(keyword in role_lower for keyword in ['ceo', 'director', 'fundador']):
            return [4, 5, 9]  # Comunidad, Bolsa empleo, Q&A
        elif any(keyword in role_lower for keyword in ['rh', 'recursos', 'talent']):
            return [4, 5, 9]  # Comunidad, Bolsa empleo, Q&A
        elif any(keyword in role_lower for keyword in ['analista', 'data', 'bi']):
            return [6, 10, 1]  # Biblioteca, Boletín, Workbook
        else:
            return [1, 4, 2]  # Bonos generales: Workbook, Comunidad, Grabaciones
    
    def _get_bonus_priority_reason(
        self,
        bonus_id: int,
        user_memory: LeadMemory,
        conversation_context: str
    ) -> str:
        """Genera razón de prioridad del bono para contexto de ventas."""
        reasons = {
            1: "Aplicación práctica inmediata con ejercicios personalizables",
            2: "Acceso completo sin restricciones de tiempo durante el curso",
            3: "Soporte directo para resolver dudas específicas de tu sector",
            4: "Networking con líderes de empresas similares a la tuya",
            5: "Oportunidades laborales exclusivas para expertos en IA",
            6: "Templates listos para implementar en tu empresa inmediatamente",
            7: "Credencial verificable que aumenta tu autoridad profesional",
            8: "Ahorro adicional para implementar automatizaciones de inmediato",
            9: "Acceso directo al instructor para resolver casos específicos",
            10: "Información privilegiada de tendencias y oportunidades de mercado"
        }
        return reasons.get(bonus_id, "Valor agregado para tu desarrollo profesional")
    
    def _get_bonus_sales_angle(self, bonus_id: int, user_memory: LeadMemory) -> str:
        """Genera ángulo de ventas específico para el bono."""
        role = user_memory.role.lower() if user_memory and user_memory.role else "profesional"
        
        sales_angles = {
            1: f"Como {role}, tendrás plantillas específicas para tu sector que puedes personalizar",
            2: "Puedes revisar las sesiones a tu ritmo, ideal para agendas ejecutivas ocupadas",  
            3: "Soporte especializado que entiende los retos específicos de PyMEs",
            4: "Conecta con otros líderes que han implementado IA exitosamente en sus empresas",
            5: "Acceso preferencial a posiciones senior en empresas que buscan expertos en IA",
            6: "Más de 100 prompts empresariales listos para usar en tu trabajo diario",
            7: "Diferénciate en LinkedIn como experto certificado en IA empresarial",
            8: "Recupera la inversión del curso con este descuento en herramientas",
            9: "Sesiones exclusivas con el instructor para resolver tus casos específicos",
            10: "Mantente actualizado con análisis de mercado y tendencias empresariales"
        }
        return sales_angles.get(bonus_id, "Valor exclusivo para profesionales como tú")
    
    async def format_bonuses_for_whatsapp(
        self,
        bonuses: List[Dict[str, Any]],
        conversation_context: str = "general",
        user_name: str = ""
    ) -> str:
        """
        Formatea bonos contextuales para WhatsApp con enfoque de ventas.
        
        Args:
            bonuses: Lista de bonos contextuales
            conversation_context: Contexto de la conversación
            user_name: Nombre del usuario
            
        Returns:
            Texto formateado para WhatsApp optimizado para conversión
        """
        if not bonuses:
            return "🎁 Bonos incluidos con el curso para maximizar tu ROI"
        
        name_part = f"{user_name}, " if user_name else ""
        
        # Encabezado contextual
        context_headers = {
            'price_objection': f"¡Perfecto{', ' + name_part if name_part else ''}! Además del curso, incluyes estos bonos SIN COSTO EXTRA:",
            'value_objection': f"Te entiendo{', ' + name_part if name_part else ''}. Por eso incluimos bonos que multiplican el valor:",
            'buying_signals': f"¡Excelente decisión{', ' + name_part if name_part else ''}! Tu inversión incluye estos bonos exclusivos:",
            'general': f"🎁 **BONOS INCLUIDOS PARA TI{', ' + name_part.upper() if name_part else ''}:**"
        }
        
        header = context_headers.get(conversation_context, context_headers['general'])
        
        # Formatear bonos
        formatted_bonuses = [header]
        
        for i, bonus in enumerate(bonuses[:4], 1):  # Máximo 4 bonos para no saturar
            content = bonus.get('content', 'Bono disponible')
            sales_angle = bonus.get('sales_angle', '')
            
            # Truncar contenido si es muy largo
            if len(content) > 80:
                content = content[:80] + "..."
            
            formatted_bonuses.append(f"**{i}. {content}**")
            if sales_angle and len(sales_angle) < 100:
                formatted_bonuses.append(f"   💡 {sales_angle}")
        
        # Agregar call-to-action contextual
        if conversation_context == 'price_objection':
            formatted_bonuses.append(f"\n💰 **Valor total bonos:** +$2,000 USD incluidos GRATIS")
        elif conversation_context == 'buying_signals':
            formatted_bonuses.append(f"\n🚀 **¿Listo para comenzar tu transformación con IA?**")
        else:
            formatted_bonuses.append(f"\n✨ **Valor agregado:** Más de $2,000 en bonos incluidos")
        
        return "\n".join(formatted_bonuses)
    
    async def get_bonus_activation_triggers(
        self,
        user_message: str,
        user_memory: LeadMemory,
        intent_category: str
    ) -> Dict[str, Any]:
        """
        Determina si se deben activar bonos específicos y cuáles.
        
        Args:
            user_message: Mensaje del usuario
            user_memory: Memoria del usuario
            intent_category: Categoría de intención detectada
            
        Returns:
            Diccionario con información de activación de bonos
        """
        message_lower = user_message.lower()
        
        # Triggers de activación de bonos
        bonus_triggers = {
            'price_triggers': ['precio', 'costo', 'caro', 'barato', 'inversión', 'presupuesto'],
            'value_triggers': ['vale la pena', 'beneficio', 'retorno', 'roi', 'valor', 'útil'],
            'time_triggers': ['tiempo', 'ocupado', 'rápido', 'cuando', 'horario', 'disponible'],
            'trust_triggers': ['confianza', 'seguro', 'garantía', 'testimonios', 'referencias'],
            'career_triggers': ['trabajo', 'empleo', 'carrera', 'oportunidad', 'linkedin'],
            'automation_triggers': ['automatizar', 'procesos', 'eficiencia', 'productividad'],
            'content_triggers': ['contenido', 'marketing', 'prompts', 'plantillas']
        }
        
        # Detectar contexto por triggers
        detected_context = 'general'
        for context, triggers in bonus_triggers.items():
            if any(trigger in message_lower for trigger in triggers):
                detected_context = context.replace('_triggers', '')
                break
        
        # Mapear contexto a configuración
        context_mapping = {
            'price': 'price_objection',
            'value': 'value_objection', 
            'time': 'time_objection',
            'trust': 'trust_objection',
            'career': 'career_growth',
            'automation': 'automation_need',
            'content': 'content_creation'
        }
        
        conversation_context = context_mapping.get(detected_context, 'general')
        
        # Determinar si activar bonos
        should_activate = (
            detected_context != 'general' or
            intent_category in ['OBJECTION_PRICE', 'BUYING_SIGNALS', 'EXPLORATION_ROI'] or
            (user_memory and user_memory.interaction_count >= 2)
        )
        
        return {
            'should_activate_bonuses': should_activate,
            'conversation_context': conversation_context,
            'detected_triggers': [trigger for trigger in bonus_triggers.get(f'{detected_context}_triggers', []) if trigger in message_lower],
            'recommended_bonus_count': 4 if should_activate else 2,
            'urgency_level': 'high' if detected_context in ['price', 'value'] else 'medium'
        }