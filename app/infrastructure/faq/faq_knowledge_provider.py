#!/usr/bin/env python3
"""
Proveedor de conocimiento FAQ para respuestas inteligentes.
Compatible con el sistema de base de datos y el agente inteligente.
"""

import asyncio
from typing import Dict, Any, List, Optional
from app.infrastructure.faq.faq_processor import FAQProcessor


class FAQKnowledgeProvider:
    """
    Proveedor de conocimiento FAQ que proporciona información contextual
    al agente inteligente para generar respuestas naturales e inteligentes.
    """
    
    def __init__(self):
        """Inicializa el proveedor de conocimiento FAQ."""
        self.faq_processor = FAQProcessor()
    
    async def get_faq_context_for_intelligence(self, message: str, user_context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Obtiene contexto FAQ para que el agente inteligente pueda responder naturalmente.
        
        Args:
            message: Mensaje del usuario
            user_context: Contexto del usuario (rol, empresa, etc.)
            
        Returns:
            Dict con contexto FAQ para el agente inteligente
        """
        # Detectar si es una FAQ
        faq_match = await self.faq_processor.detect_faq(message)
        
        if not faq_match:
            return {
                'is_faq': False,
                'context': ''
            }
        
        # Construir contexto completo para el agente inteligente
        faq_context = {
            'is_faq': True,
            'category': faq_match['category'],
            'question': faq_match['question'],
            'base_answer': faq_match['answer'],
            'escalation_needed': faq_match.get('escalation_needed', False),
            'priority': faq_match.get('priority', 'medium'),
            'keywords': faq_match.get('keywords', []),
            'context_for_ai': self._build_ai_context(faq_match, user_context)
        }
        
        return faq_context
    
    def _build_ai_context(self, faq_match: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """
        Construye contexto específico para que el AI genere respuestas naturales.
        
        Args:
            faq_match: FAQ encontrada
            user_context: Contexto del usuario
            
        Returns:
            String con contexto para el AI
        """
        category = faq_match['category']
        base_answer = faq_match['answer']
        escalation_needed = faq_match.get('escalation_needed', False)
        
        # Información adicional por categoría para personalización inteligente
        additional_context = self._get_additional_context_by_category(category, user_context)
        
        context = f"""
INFORMACIÓN FAQ DETECTADA:
- Categoría: {category}
- Pregunta tipo: {faq_match['question']}
- Respuesta base: {base_answer}
- Requiere escalación: {'Sí' if escalation_needed else 'No'}

CONTEXTO ADICIONAL:
{additional_context}

INSTRUCCIONES PARA RESPUESTA:
- Usa la información base pero hazla natural y conversacional
- Personaliza según el contexto del usuario
- Si requiere escalación, menciona que se conectará con un especialista
- Mantén el tono profesional pero amigable
- No inventes información que no esté en el contexto
"""
        
        return context.strip()
    
    def _get_additional_context_by_category(self, category: str, user_context: Dict[str, Any]) -> str:
        """
        Obtiene contexto adicional específico por categoría de FAQ.
        
        Args:
            category: Categoría de la FAQ
            user_context: Contexto del usuario
            
        Returns:
            Contexto adicional específico
        """
        user_role = user_context.get('user_role', '')
        company_size = user_context.get('company_size', '')
        industry = user_context.get('industry', '')
        
        additional_contexts = {
            'precio': f"""
INFORMACIÓN ADICIONAL DE PRECIOS:
- Precio principal: $2,990 MXN
- Modalidades de pago: Pago completo o 2 exhibiciones sin interés
- Descuento grupal: 10% por inscripción grupal (más de 3 personas)
- ROI típico: 300-500% en 6 meses
- Incluye: Acceso completo, soporte, certificado, comunidad privada
- Para {user_role}: Enfócate en ROI y beneficios empresariales
- Empresa {company_size}: Adaptable a tu presupuesto
""",
            
            'duración': f"""
📅 **DURACIÓN DEL CURSO:**
• 4 sesiones en vivo + práctica guiada
• 12 horas contenido + 8 horas ejercicios
• 8 semanas (2-3 horas/semana)
• Grabaciones + acceso por 12 meses
• Para {user_role}: Aplicación inmediata
""",
            
            'implementación': f"""
🚀 **IMPLEMENTACIÓN:**
• 5 fases: Evaluación → Configuración → Entrenamiento → Piloto → Despliegue
• Tiempo total: 6 semanas
• Para {industry}: Casos específicos disponibles
• Empresa {company_size}: Proceso adaptado
• 📞 Consultoría especializada requerida
""",
            
            'requisitos': f"""
✅ **REQUISITOS:**
• Computadora + Internet
• Conocimientos básicos de computación
• NO necesitas programación ni experiencia en IA
• Dirigido a: Ejecutivos, managers, emprendedores, PyMEs
• Para {user_role}: Perfil ideal para transformación digital
""",
            
            'casos_éxito': f"""
🏆 **CASOS DE ÉXITO:**
• Tecnológica: 50% ↓ tiempo desarrollo, $150K ahorro
• Hospital: 30% ↑ atención paciente, 45% ↓ errores  
• Manufactura: 60% ↑ eficiencia, 25% ↓ costos
• Para {industry}: Casos específicos disponibles
""",
            
            'roi': f"""
💰 **ROI ESPERADO:**
• 300-500% en primeros 6 meses
• Ahorros: Tiempo, productividad, costos
• Para {user_role}: Impacto directo en resultados
• Empresa {company_size}: ROI escalable
• 📊 Cálculo personalizado disponible
""",
            
            'certificado': f"""
🎓 **CERTIFICADO:**
• "Experto en IA para Profesionales" con código único
• Examen práctico: proyecto + casos (90 min)
• Requisitos: 75% asistencia + 70% calificación
• Reconocido por empresas, válido CV/LinkedIn
• Para {user_role}: Credencial liderazgo digital
""",
            
            'soporte': f"""
🤝 **SOPORTE:**
• 2 sesiones Q&A en vivo
• Foro privado + networking
• "AplicaAI Helper" 24/7
• Comunidad exclusiva post-curso
• Para {user_role}: Soporte especializado
""",
            
            'acceso': f"""
🔓 **ACCESO:**
• 12 meses acceso total
• Grabaciones inmediatas (4 sesiones)
• Materiales: PDF, plantillas, docs
• Foro privado + comunidad
• Actualizaciones incluidas
• 24/7 desde cualquier dispositivo
""",
            
            'garantía': f"""
🛡️ **GARANTÍA:**
• 30 días satisfacción garantizada
• Devolución completa sin preguntas
• Para {user_role}: Inversión sin riesgo
""",
            
            'incluye': f"""
📦 **INCLUYE:**
• Manual PDF completo
• Plantillas prompting + GPTs personalizados
• Grabaciones 4 sesiones
• 2 sesiones Q&A en vivo
• Foro privado + networking
• Para {user_role}: Recursos específicos
• Empresa {company_size}: Plantillas adaptadas
""",
            
            'ventajas': f"""
⭐ **VENTAJAS ÚNICAS:**
• Práctica guiada en vivo
• Recursos premium para productividad
• Soporte post-curso 24/7 + foro exclusivo
• Proyecto real para tu organización
• Para {user_role}: Aplicación directa
• Industria {industry}: Casos específicos
""",
            
            'examen': f"""
📋 **EXAMEN:**
• 100% práctico (proyecto + casos, 90 min)
• Escenarios reales + diseño de prompts
• Preparación: Plantillas IMPULSO + Custom GPTs
• Para {user_role}: Evaluación aplicación profesional
• Objetivo: Demostrar capacidad real IA
"""
        }
        
        return additional_contexts.get(category, f"Información específica para {category} adaptada a tu perfil {user_role}.")
    
    async def should_use_intelligent_faq(self, message: str) -> bool:
        """
        Determina si el mensaje debe ser manejado por el agente inteligente con contexto FAQ.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            True si debe usar el agente inteligente para FAQ
        """
        # Siempre usar agente inteligente para FAQs para respuestas más naturales
        faq_match = await self.faq_processor.detect_faq(message)
        return faq_match is not None
    
    async def get_all_faq_categories(self) -> List[str]:
        """
        Obtiene todas las categorías de FAQ disponibles.
        
        Returns:
            Lista de categorías FAQ
        """
        return [faq['category'] for faq in self.faq_processor.faq_database]
    
    async def get_faq_by_category(self, category: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una FAQ específica por categoría.
        
        Args:
            category: Categoría de la FAQ
            
        Returns:
            FAQ encontrada o None
        """
        for faq in self.faq_processor.faq_database:
            if faq['category'] == category:
                return faq
        return None
    
    async def get_related_faqs(self, category: str) -> List[Dict[str, Any]]:
        """
        Obtiene FAQs relacionadas a una categoría.
        
        Args:
            category: Categoría principal
            
        Returns:
            Lista de FAQs relacionadas
        """
        # Mapeo de categorías relacionadas
        related_categories = {
            'precio': ['roi', 'garantía', 'incluye'],
            'roi': ['precio', 'casos_éxito', 'ventajas'],
            'implementación': ['duración', 'requisitos', 'soporte'],
            'duración': ['implementación', 'acceso', 'incluye'],
            'requisitos': ['implementación', 'soporte', 'ventajas'],
            'casos_éxito': ['roi', 'implementación', 'ventajas'],
            'certificado': ['acceso', 'garantía', 'examen'],
            'soporte': ['implementación', 'acceso', 'incluye'],
            'acceso': ['duración', 'soporte', 'incluye'],
            'garantía': ['precio', 'certificado'],
            'incluye': ['precio', 'acceso', 'ventajas'],
            'ventajas': ['roi', 'casos_éxito', 'incluye'],
            'examen': ['certificado', 'requisitos']
        }
        
        related_cats = related_categories.get(category, [])
        related_faqs = []
        
        for cat in related_cats:
            faq = await self.get_faq_by_category(cat)
            if faq:
                related_faqs.append(faq)
        
        return related_faqs