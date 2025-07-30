"""
Integración entre Dynamic Course Info Provider y templates de respuesta.
Elimina dependencias de información hardcodeada en templates.
"""
import logging
from typing import Dict, Any, Optional, Union
from memory.lead_memory import LeadMemory
from app.application.usecases.dynamic_course_info_provider import DynamicCourseInfoProvider

logger = logging.getLogger(__name__)


class DynamicTemplateIntegration:
    """
    Integra información dinámica de cursos con templates de respuesta.
    Reemplaza valores hardcodeados con datos reales de BD.
    """
    
    def __init__(self, dynamic_course_provider: DynamicCourseInfoProvider):
        self.course_provider = dynamic_course_provider
    
    async def get_dynamic_price_objection_response(
        self, 
        role: str = "", 
        sector: str = "", 
        user_memory: Optional[LeadMemory] = None
    ) -> Dict[str, Any]:
        """
        Genera respuesta a objeciones de precio con información dinámica de BD.
        
        Args:
            role: Rol del usuario
            sector: Sector empresarial
            user_memory: Memoria del usuario
            
        Returns:
            Dict con respuesta personalizada y datos del curso
        """
        try:
            # Obtener información dinámica del curso
            course_data = await self.course_provider.get_primary_course_info()
            
            # Datos reales del curso
            course_price = course_data['price']
            price_formatted = course_data['price_formatted']
            course_name = course_data['name']
            
            # ROI dinámico basado en precio real
            roi_examples = self._generate_dynamic_roi_examples(course_price, role)
            
            # Construir respuesta
            response_text = self._build_price_objection_text(
                price_formatted, roi_examples, course_name, role, sector
            )
            
            return {
                'response_text': response_text,
                'course_data': course_data,
                'roi_examples': roi_examples,
                'has_real_data': course_price > 0
            }
            
        except Exception as e:
            logger.error(f"Error generando respuesta dinámica de precio: {e}")
            return self._get_fallback_price_response(role, sector)
    
    def _generate_dynamic_roi_examples(self, course_price: int, role: str) -> str:
        """
        Genera ejemplos de ROI basados en el precio real del curso.
        
        Args:
            course_price: Precio real del curso desde BD
            role: Rol del usuario
            
        Returns:
            String con ejemplo de ROI específico
        """
        if course_price <= 0:
            return "ROI personalizado según tu empresa y necesidades específicas"
        
        # Calcular ROI dinámico basado en rol
        if "marketing" in role.lower() or "content" in role.lower():
            monthly_savings = 1200  # 4 campañas * $300 ahorro
            months_to_break_even = max(1, round(course_price / monthly_savings, 1))
            return f"""
**💡 ROI para Marketing (basado en casos reales):**
• Antes: 8 horas/campaña × $50/hora = $400 por campaña
• Después: 2 horas con IA × $50/hora = $100 por campaña
• **Ahorro: $300 por campaña**
• **Break-even: {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}** (4 campañas/mes)"""
        
        elif "operaciones" in role.lower() or "manufactura" in role.lower():
            monthly_savings = 2000  # Ahorro en procesos
            months_to_break_even = max(1, round(course_price / monthly_savings, 1))
            return f"""
**💡 ROI para Operaciones (casos documentados):**
• Antes: 12 horas/semana reportes × $50/hora = $2,400/mes
• Después: 2 horas automatizadas × $50/hora = $400/mes  
• **Ahorro mensual: $2,000**
• **Break-even: {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}**"""
        
        elif "ceo" in role.lower() or "fundador" in role.lower():
            monthly_savings = 2300  # Costo analista vs curso
            months_to_break_even = max(1, round(course_price / monthly_savings, 1))
            yearly_savings = monthly_savings * 12
            return f"""
**💡 ROI Ejecutivo (análisis de costos):**
• Costo analista junior: $2,500/mes = $30,000/año
• Costo curso + tiempo propio: ${round(course_price/12):,}/mes = ${course_price:,}/año
• **Ahorro anual: ${yearly_savings:,}**
• **Break-even: {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}**"""
        
        else:
            # ROI genérico para otros roles
            estimated_monthly_savings = max(1000, course_price // 4)  # Estimación conservadora
            months_to_break_even = max(1, round(course_price / estimated_monthly_savings, 1))
            return f"""
**💡 ROI Personalizado:**
• Ahorro estimado: ${estimated_monthly_savings:,}/mes en procesos optimizados
• **Break-even: {months_to_break_even} {'mes' if months_to_break_even == 1 else 'meses'}**
• ROI anual proyectado: {round((estimated_monthly_savings * 12 / course_price) * 100)}%"""
    
    def _build_price_objection_text(
        self, 
        price_formatted: str, 
        roi_examples: str, 
        course_name: str,
        role: str, 
        sector: str
    ) -> str:
        """Construye el texto completo de respuesta a objeciones de precio."""
        
        return f"""Entiendo la preocupación por el presupuesto - es típico de líderes PyME responsables. 💰

**🏢 PERSPECTIVA EMPRESARIAL:**
• {course_name}: {price_formatted} (inversión única, resultados permanentes)
• Contratar especialista IA: $3,000-5,000/mes (+ prestaciones)
• Consultoría externa: $200/hora × 40 horas = $8,000 USD
• Seguir perdiendo eficiencia: **Costo de oportunidad ilimitado**

**📊 VALOR ESPECÍFICO PARA PYMES:**
• Framework IMPULSO: aplicable a cualquier proceso desde día 1
• Sin dependencia técnica: tu equipo actual puede implementarlo
• Actualizaciones incluidas: siempre al día con nueva tecnología
• Casos reales PyME: ejemplos de tu mismo tamaño de empresa{roi_examples}

**🎯 LA PREGUNTA ESTRATÉGICA:**
¿Puedes permitirte que tu competencia implemente IA antes que tú?

¿Te gustaría que revisemos un plan de implementación por fases para optimizar tu inversión?"""
    
    def _get_fallback_price_response(self, role: str, sector: str) -> Dict[str, Any]:
        """Respuesta de fallback cuando no hay datos de BD."""
        return {
            'response_text': f"""Entiendo tu preocupación por el presupuesto. 💰

**🏢 PERSPECTIVA EMPRESARIAL:**
• Curso profesional de IA: Inversión única, resultados permanentes
• Contratar especialista: $3,000-5,000/mes + prestaciones
• Consultoría externa: $200/hora × 40 horas = $8,000 USD

**📊 VALOR PARA PYMES:**
• Sin dependencia técnica: tu equipo actual puede implementarlo
• Actualizaciones incluidas: siempre al día con tecnología
• ROI personalizado según tu empresa específica

¿Te gustaría que revisemos un plan de implementación personalizado?""",
            'course_data': {},
            'roi_examples': "ROI por confirmar según tu empresa",
            'has_real_data': False
        }
    
    async def get_dynamic_course_summary(
        self, 
        user_memory: Optional[LeadMemory] = None,
        course_code: str = ""
    ) -> Dict[str, Any]:
        """
        Genera resumen de curso con información dinámica de BD.
        
        Args:
            user_memory: Memoria del usuario
            course_code: Código del curso solicitado
            
        Returns:
            Dict con resumen personalizado y datos del curso
        """
        try:
            course_data = await self.course_provider.get_course_for_templates()
            
            # Personalización por usuario
            user_name = user_memory.name if user_memory and user_memory.name != "Usuario" else ""
            name_greeting = f"{user_name}, " if user_name else ""
            
            # Información del curso con datos reales
            summary_text = f"""🎯 ¡Perfecto {name_greeting}aquí tienes toda la información!

📚 **{course_data['name']}**

🔥 **INFORMACIÓN CLAVE:**
💰 Inversión: {course_data['price_text']}
📊 Nivel: {course_data['level']}
🗓️ Duración: {course_data['session_count']} sesiones ({course_data['duration_hours']} horas)
🌐 Modalidad: {course_data['modality']}

**🎁 BONOS INCLUIDOS:**"""
            
            # Agregar bonos reales de BD
            for i, bond in enumerate(course_data['bonds'], 1):
                summary_text += f"\n{i}. {bond['content']}"
            
            if not course_data['bonds']:
                summary_text += "\n• Recursos complementarios incluidos"
            
            summary_text += f"""

**💡 ROI PARA TU PERFIL:**
{course_data.get('roi_' + user_memory.role.lower().replace(' ', '_'), 'ROI personalizado según tu empresa') if user_memory and user_memory.role else 'ROI adaptado a tu negocio'}

¿Te gustaría conocer más detalles de algún módulo específico?"""
            
            return {
                'summary_text': summary_text,
                'course_data': course_data,
                'has_real_data': course_data['price'] > 0
            }
            
        except Exception as e:
            logger.error(f"Error generando resumen dinámico de curso: {e}")
            return {
                'summary_text': "📚 Información del curso disponible. Te contactaremos con los detalles específicos.",
                'course_data': {},
                'has_real_data': False
            }