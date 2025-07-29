"""
Templates para anuncios de cursos optimizados para WhatsApp.
Mensajes profesionales y atractivos para presentar cursos cuando el usuario envía códigos específicos.
"""
from typing import Dict, Any, List
from memory.lead_memory import LeadMemory


class CourseAnnouncementTemplates:
    """Templates para anuncios de cursos por código específico."""
    
    @staticmethod
    def course_summary_message(
        course_info: Dict[str, Any], 
        user_memory: LeadMemory
    ) -> str:
        """
        Crea mensaje de resumen del curso personalizado.
        
        Args:
            course_info: Información del curso
            user_memory: Memoria del usuario para personalización
            
        Returns:
            Mensaje de resumen personalizado
        """
        # Personalización por nombre
        user_name = user_memory.name if user_memory.name != "Usuario" else ""
        name_greeting = f"{user_name}, " if user_name else ""
        
        # Información básica
        course_name = course_info.get('name', 'Curso de IA')
        description = course_info.get('short_description', '')
        price = course_info.get('price', 497)
        currency = course_info.get('currency', 'USD')
        level = course_info.get('level', 'Todos los niveles')
        sessions = course_info.get('session_count', 8)
        duration = course_info.get('duration_hours', 12)
        
        # Construir mensaje principal
        message_parts = [
            f"🎯 ¡Perfecto {name_greeting}aquí tienes toda la información que necesitas!",
            "",
            f"📚 **{course_name}**",
            f"📝 {description}",
            "",
            "🔥 **INFORMACIÓN CLAVE:**",
            f"💰 Inversión: ${price} {currency}",
            f"📊 Nivel: {level}",
            f"🗓️ Duración: {sessions} sesiones ({duration} horas)",
            f"💻 Modalidad: Online con acceso 24/7",
            f"🎓 Certificación incluida"
        ]
        
        return "\n".join(message_parts)
    
    @staticmethod
    def course_detailed_description(course_info: Dict[str, Any]) -> str:
        """
        Crea descripción detallada del curso.
        
        Args:
            course_info: Información del curso
            
        Returns:
            Descripción detallada
        """
        description = course_info.get('description', '')
        if description:
            return f"📋 **DETALLES DEL CURSO:**\n{description}"
        
        # Descripción por defecto si no hay específica
        return """📋 **DETALLES DEL CURSO:**

🎯 **¿Para quién es este curso?**
Dirigido específicamente a líderes de PyMEs (20-200 empleados) que buscan:
• Automatizar procesos sin equipos técnicos
• Reducir costos operativos significativamente  
• Obtener ventaja competitiva con IA
• Implementar soluciones prácticas inmediatas

💡 **Metodología única:**
• Casos reales de PyMEs exitosas
• Herramientas listas para implementar
• ROI comprobado desde el primer mes
• Soporte durante toda la implementación"""
    
    @staticmethod
    def course_bonuses_section(bonuses: List[str]) -> str:
        """
        Crea sección de bonos del curso.
        
        Args:
            bonuses: Lista de bonos incluidos
            
        Returns:
            Sección de bonos formateada
        """
        if not bonuses:
            # Bonos por defecto
            bonuses = [
                "📚 Plantillas de automatización listas para usar",
                "🤖 Acceso a herramientas de IA por 6 meses",
                "💼 Consultoría personalizada 1-on-1 (30 min)",
                "📊 Dashboard de ROI personalizado",
                "🎯 Guía de implementación por sector"
            ]
        
        bonus_lines = [f"🎁 **BONOS INCLUIDOS ({len(bonuses)}):**"]
        for bonus in bonuses:
            bonus_lines.append(f"• {bonus}")
        
        return "\n".join(bonus_lines)
    
    @staticmethod
    def role_specific_roi_message(role: str, course_price: int) -> str:
        """
        Genera mensaje de ROI específico según el rol del usuario.
        
        Args:
            role: Rol/cargo del usuario
            course_price: Precio del curso
            
        Returns:
            Mensaje de ROI personalizado
        """
        role_lower = role.lower()
        
        # ROI para Marketing/Comercial
        if any(keyword in role_lower for keyword in ['marketing', 'digital', 'comercial', 'ventas']):
            return """💡 **ROI ESPECÍFICO PARA MARKETING DIGITAL:**

📈 **Beneficios inmediatos:**
• Automatiza creación de campañas → Ahorra $300 por campaña
• Genera contenido optimizado → Reduce tiempo 70%
• Análisis predictivo de leads → Incrementa conversión 35%

💰 **Retorno de inversión:**
• Recuperas inversión en solo 2 campañas automatizadas
• ROI proyectado: 200% en el primer mes
• Ahorro anual estimado: $14,400"""

        # ROI para Operaciones
        elif any(keyword in role_lower for keyword in ['operaciones', 'operations', 'gerente', 'director']):
            return """💡 **ROI ESPECÍFICO PARA OPERACIONES:**

⚡ **Optimizaciones operativas:**
• Automatiza reportes y dashboards → Ahorra 20h/semana
• Predice demanda y optimiza inventario → Reduce costos 25%
• Automatiza procesos repetitivos → Libera 2 empleados equivalentes

💰 **Retorno de inversión:**
• Ahorra $2,000 mensuales en procesos manuales
• ROI proyectado: 400% en el primer mes
• Ahorro anual estimado: $24,000"""

        # ROI para CEO/Fundadores
        elif any(keyword in role_lower for keyword in ['ceo', 'founder', 'fundador', 'director general', 'presidente']):
            return """💡 **ROI ESPECÍFICO PARA LIDERAZGO EJECUTIVO:**

🚀 **Impacto estratégico:**
• Toma de decisiones basada en datos → Reduce errores 60%
• Análisis competitivo automatizado → Ventaja estratégica
• Escalabilidad sin crecimiento de plantilla → Mantiene costos

💰 **Retorno de inversión:**
• Evitas contratar analista IA ($27,600/año) 
• Aceleras decisiones estratégicas críticas
• ROI proyectado: 1,380% anual"""

        # ROI para Recursos Humanos
        elif any(keyword in role_lower for keyword in ['rh', 'recursos humanos', 'hr', 'talent', 'talento']):
            return """💡 **ROI ESPECÍFICO PARA RECURSOS HUMANOS:**

👥 **Optimización de talento:**
• Automatiza screening de CVs → Reduce tiempo 80%
• Análisis predictivo de rotación → Previene renuncias
• Evaluaciones automatizadas → Mejora proceso selección

💰 **Retorno de inversión:**
• Ahorra $1,500 mensuales en reclutamiento
• Reduce tiempo contratación de 30 a 7 días
• ROI proyectado: 300% en el primer trimestre"""

        # ROI genérico para otros roles
        else:
            return """💡 **ROI GENERAL PARA PYMES:**

🎯 **Beneficios universales:**
• Automatización de procesos clave → Ahorra mínimo $1,000/mes
• Incrementa productividad del equipo → 35% más eficiencia
• Reduce errores humanos → Ahorra tiempo y recursos

💰 **Retorno de inversión:**
• ROI proyectado: 250% en los primeros 3 meses
• Ahorro anual estimado: $12,000 - $18,000
• Recuperas inversión en 6-8 semanas"""
    
    @staticmethod
    def pdf_resource_message(pdf_name: str) -> str:
        """
        Mensaje para el recurso PDF del curso.
        
        Args:
            pdf_name: Nombre del archivo PDF
            
        Returns:
            Mensaje del recurso PDF
        """
        return f"""📄 **GUÍA DESCARGABLE INCLUIDA:**

**{pdf_name}**

*[En producción se enviaría el archivo PDF real]*

📚 **Este documento contiene:**
• Guía de implementación paso a paso
• Plantillas y herramientas descargables  
• 12 casos de estudio con ROI real comprobado
• Checklist de implementación por semanas
• Recursos adicionales y enlaces útiles

💡 **Úsalo para:** Evaluar aplicabilidad en tu empresa específica y planificar la implementación."""
    
    @staticmethod
    def image_resource_message(image_name: str) -> str:
        """
        Mensaje para el recurso de imagen del curso.
        
        Args:
            image_name: Nombre del archivo de imagen
            
        Returns:
            Mensaje del recurso de imagen
        """
        return f"""🖼️ **INFOGRAFÍA DEL CURSO:**

**{image_name}**

*[En producción se enviaría la imagen real]*

🎨 **Esta infografía muestra:**
• Estructura visual completa del curso
• Herramientas específicas que vas a dominar
• Timeline de resultados esperados por módulo
• Roadmap de implementación en tu PyME

📱 **Ideal para:** Compartir con tu equipo y visualizar el plan de transformación."""
    
    @staticmethod
    def follow_up_engagement_message(course_info: Dict[str, Any]) -> str:
        """
        Mensaje de seguimiento para mantener engagement.
        
        Args:
            course_info: Información del curso
            
        Returns:
            Mensaje de seguimiento
        """
        course_name = course_info.get('name', 'este curso')
        price = course_info.get('price', 497)
        
        return f"""🚀 **¿LISTO PARA TRANSFORMAR TU PYME CON IA?**

👆 Acabas de recibir toda la información completa de **{course_name}**

💬 **TUS PRÓXIMOS PASOS:**
1️⃣ Revisa el documento PDF con todos los detalles
2️⃣ Analiza cómo aplicarías esto en tu empresa específica  
3️⃣ Si tienes preguntas, escríbeme aquí mismo

🎯 **OFERTA ESPECIAL DE LANZAMIENTO:**
• Reserva tu lugar ahora con solo $97 USD
• Resto del pago antes de iniciar el curso
• Garantía de satisfacción 30 días

❓ **DIME:** ¿Qué te parece más interesante del curso? ¿Tienes alguna pregunta específica sobre la implementación en tu sector?"""
    
    @staticmethod
    def course_not_found_message(course_code: str) -> str:
        """
        Mensaje cuando no se encuentra el curso solicitado.
        
        Args:
            course_code: Código del curso que no se encontró
            
        Returns:
            Mensaje de curso no encontrado
        """
        return f"""🤔 **CURSO NO ENCONTRADO**

Lo siento, no pude encontrar información para el código **{course_code}**.

📚 **CURSOS DISPONIBLES ACTUALMENTE:**

**#CursoIA1** - Introducción a IA para PyMEs
💰 $497 USD | 📊 Principiante | 🗓️ 8 sesiones

**#CursoIA2** - IA Intermedia para Automatización
💰 $797 USD | 📊 Intermedio | 🗓️ 12 sesiones

**#CursoIA3** - IA Avanzada: Transformación Digital
💰 $1,297 USD | 📊 Avanzado | 🗓️ 16 sesiones

💬 **¿Te interesa información detallada de alguno?** 
Solo escribe el código que te llame la atención (ej: #CursoIA1)"""
    
    @staticmethod
    def special_promotion_message(course_info: Dict[str, Any]) -> str:
        """
        Mensaje de promoción especial para crear urgencia.
        
        Args:
            course_info: Información del curso
            
        Returns:
            Mensaje de promoción especial
        """
        course_name = course_info.get('name', 'este curso')
        original_price = course_info.get('price', 497)
        promo_price = int(original_price * 0.8)  # 20% descuento
        savings = original_price - promo_price
        
        return f"""🔥 **PROMOCIÓN ESPECIAL LIMITADA**

**{course_name}**

💥 **OFERTA EXCLUSIVA POR WHATSAPP:**
~~${original_price} USD~~ → **${promo_price} USD**
💰 **¡Ahorras ${savings} USD!**

⏰ **VÁLIDA SOLO POR 48 HORAS**

🎁 **BONOS ADICIONALES SI RESERVAS HOY:**
• Sesión estratégica 1-on-1 personalizada (Valor: $200)
• Acceso VIP a comunidad exclusiva de PyMEs (Valor: $97)
• Templates premium adicionales (Valor: $150)

🚀 **TOTAL EN BONOS:** $447 USD ¡GRATIS!

💬 **Para reservar tu lugar:** Responde "QUIERO RESERVAR" y te envío el enlace de pago seguro."""
    
    @staticmethod
    def sector_specific_benefits(course_info: Dict[str, Any], user_memory: LeadMemory) -> str:
        """
        Beneficios específicos según el sector de la empresa del usuario.
        
        Args:
            course_info: Información del curso
            user_memory: Memoria del usuario
            
        Returns:
            Beneficios específicos por sector
        """
        # Intentar detectar sector desde el contexto del usuario
        context = " ".join(user_memory.conversation_context).lower()
        role = user_memory.role.lower() if user_memory.role != "No disponible" else ""
        
        # Detectar sector
        if any(keyword in context + role for keyword in ['agencia', 'marketing', 'publicidad', 'digital']):
            return """🎯 **BENEFICIOS ESPECÍFICOS PARA AGENCIAS:**

📈 **Automatización de campañas:**
• Generación automática de copy para ads
• Optimización de segmentación con IA
• Reportes automatizados para clientes

🤖 **Herramientas que dominarás:**
• ChatGPT para copy y contenido
• Claude para estrategia y análisis  
• MidJourney para creatividad visual
• Make.com para automatizaciones"""

        elif any(keyword in context + role for keyword in ['consultoria', 'consultor', 'asesor', 'servicios']):
            return """🎯 **BENEFICIOS ESPECÍFICOS PARA CONSULTORÍA:**

💼 **Escalabilidad de servicios:**
• Automatiza análisis y diagnósticos
• Genera propuestas personalizadas masivamente
• Crea metodologías replicables con IA

📊 **Herramientas que dominarás:**
• Análisis predictivo para clientes
• Automatización de reportes ejecutivos
• IA para research y benchmarking
• Sistemas de recomendaciones inteligentes"""

        elif any(keyword in context + role for keyword in ['comercio', 'retail', 'ventas', 'tienda']):
            return """🎯 **BENEFICIOS ESPECÍFICOS PARA COMERCIO:**

🛒 **Optimización de ventas:**
• Predicción de demanda y stock óptimo
• Personalización de ofertas por cliente
• Automatización de seguimiento post-venta

💰 **Incremento de rentabilidad:**
• Pricing dinámico inteligente
• Detección de patrones de compra
• Optimización de inventario
• Marketing automatizado por segmentos"""

        else:
            return """🎯 **BENEFICIOS UNIVERSALES PARA PYMES:**

⚡ **Automatización inmediata:**
• Procesos administrativos automatizados
• Generación de contenido profesional
• Análisis de datos y reportes inteligentes

🚀 **Crecimiento acelerado:**
• Toma de decisiones basada en datos
• Optimización continua de procesos  
• Escalabilidad sin crecer la plantilla
• Ventaja competitiva sostenible"""
    
    @staticmethod
    def urgency_closing_message() -> str:
        """
        Mensaje de cierre con urgencia para impulsar la acción.
        
        Returns:
            Mensaje de urgencia
        """
        return """⚡ **¡NO DEJES PASAR ESTA OPORTUNIDAD!**

🎯 **Solo quedan 7 lugares disponibles** para esta edición

⏰ **La promoción especial vence en 48 horas**

📈 **Empresas que ya implementaron IA reportan:**
• 40% incremento en productividad
• 25% reducción en costos operativos  
• ROI promedio de 300% en 6 meses

💬 **¿Listo para unirte a la transformación?**
Responde "SÍ, QUIERO INFORMACIÓN DE PAGO" y te envío todos los detalles para asegurar tu lugar."""