#!/usr/bin/env python3
"""
Templates para el sistema de FAQ (Preguntas Frecuentes).
"""

from typing import Dict, Any


class FAQTemplates:
    """
    Templates para mensajes del sistema de FAQ.
    """
    
    @staticmethod
    def get_faq_response(
        category: str, 
        answer: str, 
        user_name: str, 
        user_role: str = '', 
        company_size: str = '', 
        industry: str = ''
    ) -> str:
        """
        Genera una respuesta personalizada para una FAQ.
        
        Args:
            category: Categoría de la FAQ
            answer: Respuesta base
            user_name: Nombre del usuario
            user_role: Rol del usuario
            company_size: Tamaño de la empresa
            industry: Industria del usuario
            
        Returns:
            Respuesta personalizada
        """
        
        # Personalización basada en el rol
        if 'CEO' in user_role or 'Director' in user_role:
            prefix = f"¡Hola {user_name}! Como líder de tu organización, "
        elif 'Manager' in user_role or 'Gerente' in user_role:
            prefix = f"¡Hola {user_name}! Como gerente, "
        else:
            prefix = f"¡Hola {user_name}! "
        
        # Personalización basada en el tamaño de la empresa
        if 'grande' in company_size.lower() or 'enterprise' in company_size.lower():
            size_context = "Para empresas de tu tamaño, "
        elif 'mediana' in company_size.lower():
            size_context = "Para empresas medianas como la tuya, "
        elif 'pequeña' in company_size.lower() or 'startup' in company_size.lower():
            size_context = "Para empresas pequeñas como la tuya, "
        else:
            size_context = ""
        
        # Personalización basada en la industria
        if 'tecnología' in industry.lower():
            industry_context = " especialmente en el sector tecnológico, "
        elif 'finanzas' in industry.lower():
            industry_context = " especialmente en el sector financiero, "
        elif 'salud' in industry.lower():
            industry_context = " especialmente en el sector salud, "
        else:
            industry_context = ""
        
        # Construir respuesta personalizada
        personalized_answer = f"{prefix}{size_context}{answer}{industry_context}"
        
        # Agregar contexto adicional según la categoría
        if 'precio' in category.lower():
            personalized_answer += "\n\n💡 **Consejo:** ¿Te gustaría que te ayude a calcular el ROI específico para tu empresa?"
        elif 'implementación' in category.lower():
            personalized_answer += "\n\n🚀 **Próximo paso:** ¿Te gustaría ver casos de éxito similares a tu industria?"
        elif 'duración' in category.lower():
            personalized_answer += "\n\n⏰ **Flexibilidad:** El programa se adapta a tu disponibilidad de tiempo."
        
        return personalized_answer
    
    @staticmethod
    def get_faq_not_found_message(user_name: str) -> str:
        """
        Mensaje cuando no se encuentra una FAQ específica.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Mensaje de FAQ no encontrada
        """
        return f"""¡Hola {user_name}! 😊

No encontré una respuesta específica para tu pregunta, pero puedo ayudarte de otras formas:

🤔 **Preguntas frecuentes populares:**
• ¿Cuál es el precio del curso?
• ¿Cuánto tiempo dura la implementación?
• ¿Qué requisitos necesito?
• ¿Hay casos de éxito similares?

📞 **Opciones de ayuda:**
1. **Contactar asesor** - Para preguntas específicas
2. **Ver casos de éxito** - Ejemplos reales
3. **Calculadora de ROI** - Beneficios para tu empresa

¿Cuál de estas opciones te interesa más? O si prefieres, puedes reformular tu pregunta de otra manera. 🤝"""
    
    @staticmethod
    def get_faq_suggestions_message(user_name: str, suggestions: list) -> str:
        """
        Mensaje con sugerencias de FAQ.
        
        Args:
            user_name: Nombre del usuario
            suggestions: Lista de sugerencias
            
        Returns:
            Mensaje con sugerencias
        """
        suggestions_text = "\n".join([f"• {suggestion}" for suggestion in suggestions])
        
        return f"""¡Hola {user_name}! 😊

Basándome en tu perfil, aquí tienes algunas preguntas que podrían interesarte:

🤔 **Preguntas sugeridas:**
{suggestions_text}

💡 **También puedes:**
• Hacer tu pregunta específica
• Contactar con un asesor
• Ver casos de éxito

¿Cuál de estas opciones te interesa más? 🤝"""
    
    @staticmethod
    def get_faq_escalation_message(user_name: str, category: str) -> str:
        """
        Mensaje cuando se requiere escalación a humano.
        
        Args:
            user_name: Nombre del usuario
            category: Categoría de la FAQ
            
        Returns:
            Mensaje de escalación
        """
        return f"""¡Hola {user_name}! 😊

Tu pregunta sobre "{category}" requiere atención especializada. 

👨‍💼 **Te conectaré con un asesor experto** que podrá darte una respuesta más detallada y personalizada.

⏰ **Tiempo de respuesta:** 2-4 horas

📞 **Mientras tanto:**
¿Te gustaría que te envíe información adicional sobre este tema mientras esperas?

¡Tu asesor se pondrá en contacto contigo muy pronto! 🚀"""
    
    @staticmethod
    def get_faq_category_response(category: str, user_name: str) -> str:
        """
        Respuesta específica por categoría de FAQ.
        
        Args:
            category: Categoría de la FAQ
            user_name: Nombre del usuario
            
        Returns:
            Respuesta por categoría
        """
        responses = {
            'precio': f"""¡Hola {user_name}! 💰

**Información sobre precios:**

📊 **Inversión:** $997 USD
💳 **Formas de pago:** 
• Pago único
• 3 pagos de $347 USD
• 6 pagos de $197 USD

🎁 **Incluye:**
• Acceso completo al curso
• Certificado oficial
• Soporte técnico
• Comunidad privada
• Actualizaciones de por vida

💡 **ROI típico:** 300-500% en los primeros 6 meses

¿Te gustaría que calcule el ROI específico para tu empresa? 📊""",
            
            'duración': f"""¡Hola {user_name}! ⏰

**Información sobre duración:**

📚 **Contenido del curso:**
• 12 horas de contenido principal
• 8 horas de ejercicios prácticos
• 4 horas de casos de estudio
• Acceso ilimitado por 12 meses

⏱️ **Flexibilidad:**
• Puedes avanzar a tu ritmo
• Contenido disponible 24/7
• Acceso desde cualquier dispositivo

📅 **Recomendación:** 2-3 horas por semana para completar en 8 semanas

¿Te gustaría ver el plan de estudios detallado? 📋""",
            
            'implementación': f"""¡Hola {user_name}! 🚀

**Información sobre implementación:**

🛠️ **Proceso de implementación:**
1. **Evaluación inicial** (1 semana)
2. **Configuración básica** (2 semanas)
3. **Entrenamiento del equipo** (3 semanas)
4. **Piloto interno** (4 semanas)
5. **Despliegue completo** (6 semanas)

📊 **Resultados típicos:**
• 40% reducción en tiempo de tareas
• 60% mejora en productividad
• 80% satisfacción del equipo

👥 **Soporte incluido:**
• Consultoría personalizada
• Soporte técnico 24/7
• Comunidad de usuarios

¿Te gustaría ver casos de éxito específicos de tu industria? 🏆""",
            
            'requisitos': f"""¡Hola {user_name}! ✅

**Requisitos del curso:**

💻 **Tecnológicos:**
• Computadora con Windows/Mac/Linux
• Conexión a internet estable
• Navegador web moderno

📚 **Conocimientos previos:**
• Conocimientos básicos de computación
• Experiencia en gestión de equipos
• Interés en innovación tecnológica

🎯 **Perfil recomendado:**
• Líderes de equipos
• Gerentes de proyectos
• Emprendedores
• Profesionales en transición

💡 **No necesitas:**
• Conocimientos de programación
• Experiencia previa con IA
• Equipos especializados

¿Te gustaría hacer una evaluación de tu perfil? 📊""",
            
            'casos_éxito': f"""¡Hola {user_name}! 🏆

**Casos de éxito destacados:**

🏢 **Empresa Tecnológica (200 empleados):**
• 50% reducción en tiempo de desarrollo
• $150K ahorro anual en costos operativos
• ROI del 400% en 6 meses

🏥 **Hospital Regional (500 empleados):**
• 30% mejora en atención al paciente
• 45% reducción en errores administrativos
• Implementación en 8 semanas

🏭 **Manufactura (150 empleados):**
• 60% mejora en eficiencia de producción
• 25% reducción en costos de calidad
• ROI del 350% en 4 meses

📊 **Estadísticas generales:**
• 95% de satisfacción de clientes
• 87% implementación exitosa
• 300% ROI promedio

¿Te gustaría ver casos específicos de tu industria? 🎯"""
        }
        
        return responses.get(category.lower(), f"""¡Hola {user_name}! 😊

Gracias por tu pregunta sobre {category}. 

Para darte la mejor respuesta posible, te recomiendo:

📞 **Contactar con un asesor especializado** que pueda darte información personalizada para tu situación específica.

⏰ **Tiempo de respuesta:** 2-4 horas

¿Te gustaría que te conecte con un asesor ahora? 🤝""")
    
    @staticmethod
    def get_faq_help_message(user_name: str) -> str:
        """
        Mensaje de ayuda general para FAQ.
        
        Args:
            user_name: Nombre del usuario
            
        Returns:
            Mensaje de ayuda
        """
        return f"""¡Hola {user_name}! 😊

**¿En qué puedo ayudarte?**

🤔 **Preguntas frecuentes:**
• Precios y formas de pago
• Duración y flexibilidad
• Proceso de implementación
• Requisitos y perfil
• Casos de éxito

📞 **Otras opciones:**
• Contactar con asesor
• Ver demostración
• Calcular ROI
• Solicitar propuesta

¿Qué te interesa más? Solo dime tu pregunta o elige una opción. 🤝""" 