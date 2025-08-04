#!/usr/bin/env python3
"""
Procesador de FAQ para manejar preguntas frecuentes.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime


class FAQProcessor:
    """
    Procesador para manejar preguntas frecuentes.
    """
    
    def __init__(self):
        """Inicializa el procesador de FAQ."""
        self.faq_database = self._initialize_faq_database()
    
    def _initialize_faq_database(self) -> List[Dict[str, Any]]:
        """
        Inicializa la base de datos de FAQ.
        
        Returns:
            Lista de FAQs
        """
        return [
            {
                'id': 'FAQ_001',
                'category': 'precio',
                'question': '¿Cuál es el precio del curso?',
                'keywords': ['precio', 'costo', 'valor', 'cuánto cuesta', 'inversión', 'pago'],
                'answer': 'El curso tiene un precio de $2,990 MXN. Ofrecemos modalidades de pago flexibles: pago completo o pago en 2 exhibiciones sin interés. Además, tenemos un descuento del 10% por inscripción grupal (más de 3 personas). Incluye acceso completo, certificado, soporte técnico y comunidad privada.',
                'escalation_needed': False,
                'priority': 'high'
            },
            {
                'id': 'FAQ_002',
                'category': 'duración',
                'question': '¿Cuánto tiempo dura el curso?',
                'keywords': ['duración', 'tiempo', 'cuánto dura', 'horas', 'semanas', 'meses', 'sesiones', 'estructura'],
                'answer': 'El curso consta de 4 sesiones en vivo con práctica guiada donde cada concepto se aplica inmediatamente. Incluye 12 horas de contenido principal, 8 horas de ejercicios prácticos y 4 horas de casos de estudio. Al final desarrollarás un proyecto real que servirá como entregable práctico para tu organización, demostrando el valor inmediato de lo aprendido. Tiempo total estimado: 8 semanas dedicando 2-3 horas por semana.',
                'escalation_needed': False,
                'priority': 'high'
            },
            {
                'id': 'FAQ_003',
                'category': 'implementación',
                'question': '¿Cómo se implementa en mi empresa?',
                'keywords': ['implementación', 'empresa', 'organización', 'proceso', 'pasos'],
                'answer': 'El proceso de implementación incluye: evaluación inicial (1 semana), configuración básica (2 semanas), entrenamiento del equipo (3 semanas), piloto interno (4 semanas) y despliegue completo (6 semanas).',
                'escalation_needed': True,
                'priority': 'high'
            },
            {
                'id': 'FAQ_004',
                'category': 'requisitos',
                'question': '¿Qué requisitos necesito?',
                'keywords': ['requisitos', 'necesito', 'conocimientos', 'experiencia', 'perfil', 'dirigido', 'para quién'],
                'answer': 'Necesitas conocimientos básicos de computación, experiencia en gestión de equipos e interés en innovación tecnológica. No necesitas conocimientos de programación ni experiencia previa con IA. Está dirigido específicamente a: Ejecutivos y managers que necesitan optimizar procesos, Emprendedores y consultores que buscan escalar servicios, y Equipos de PYMES interesados en automatización inteligente. Ideal si buscas potenciar la toma de decisiones con IA, reducir tareas manuales repetitivas y generar insights en segundos.',
                'escalation_needed': False,
                'priority': 'medium'
            },
            {
                'id': 'FAQ_005',
                'category': 'casos_éxito',
                'question': '¿Hay casos de éxito similares?',
                'keywords': ['casos de éxito', 'ejemplos', 'resultados', 'testimonios', 'éxito'],
                'answer': 'Sí, tenemos múltiples casos de éxito. Por ejemplo: empresa tecnológica con 50% reducción en tiempo de desarrollo, hospital con 30% mejora en atención al paciente, y manufactura con 60% mejora en eficiencia.',
                'escalation_needed': False,
                'priority': 'medium'
            },
            {
                'id': 'FAQ_006',
                'category': 'roi',
                'question': '¿Cuál es el ROI esperado?',
                'keywords': ['roi', 'retorno', 'beneficio', 'inversión', 'ganancia'],
                'answer': 'El ROI típico es de 300-500% en los primeros 6 meses. Esto incluye ahorros en tiempo, mejora en productividad y reducción de costos operativos.',
                'escalation_needed': True,
                'priority': 'high'
            },
            {
                'id': 'FAQ_007',
                'category': 'certificado',
                'question': '¿Incluye certificado?',
                'keywords': ['certificado', 'diploma', 'acreditación', 'reconocimiento', 'examen', 'evaluación', 'proyecto'],
                'answer': 'Sí, incluye certificado digital "Experto en IA para Profesionales" con código único. La evaluación consta de: Examen final práctico (proyecto integrador + diseño de workflow, duración 90 minutos) con escenarios reales, diseño de prompts y análisis de resultados. Requisitos para certificarse: Asistencia mínima al 75% de las sesiones y calificación mínima de 70% en el proyecto y examen práctico. Recomendaciones: Repasar plantillas IMPULSO, ejemplos de Custom GPTs y practicar workflows diarios.',
                'escalation_needed': False,
                'priority': 'high'
            },
            {
                'id': 'FAQ_008',
                'category': 'soporte',
                'question': '¿Qué tipo de soporte incluye?',
                'keywords': ['soporte', 'ayuda', 'asistencia', 'comunidad', 'consultoría', 'Q&A', 'foro', 'networking'],
                'answer': 'Incluye soporte completo: 2 sesiones Q&A en vivo para resolver dudas directamente, Foro privado para dudas y networking con otros participantes, Agente "AplicaAI Helper" disponible 24/7 para asistencia técnica, y comunidad exclusiva para compartir experiencias. También incluye soporte post-curso con actualizaciones continuas del contenido.',
                'escalation_needed': False,
                'priority': 'high'
            },
            {
                'id': 'FAQ_009',
                'category': 'acceso',
                'question': '¿Por cuánto tiempo tengo acceso?',
                'keywords': ['acceso', 'tiempo', 'duración', 'permanente', 'ilimitado', 'grabaciones', 'sesiones'],
                'answer': 'Tienes acceso completo por 12 meses que incluye: Acceso a grabaciones de las 4 sesiones en vivo, todos los materiales descargables (manual PDF, plantillas, documentación), foro privado y comunidad exclusiva, y todas las actualizaciones y mejoras que se agreguen durante ese período. Las grabaciones están disponibles inmediatamente después de cada sesión.',
                'escalation_needed': False,
                'priority': 'medium'
            },
            {
                'id': 'FAQ_010',
                'category': 'garantía',
                'question': '¿Hay garantía de satisfacción?',
                'keywords': ['garantía', 'satisfacción', 'devolución', 'reembolso', 'seguridad'],
                'answer': 'Sí, ofrecemos garantía de satisfacción de 30 días. Si no estás completamente satisfecho, te devolvemos tu dinero sin preguntas.',
                'escalation_needed': False,
                'priority': 'medium'
            },
            {
                'id': 'FAQ_011',
                'category': 'incluye',
                'question': '¿Qué incluye el curso?',
                'keywords': ['incluye', 'contiene', 'materiales', 'recursos', 'entregables', 'manual', 'plantillas'],
                'answer': 'El curso incluye recursos entregables completos: Manual completo en PDF con documentación detallada de todas las técnicas y metodologías, Plantillas de prompting, Gems y GPTs personalizados, Acceso a grabaciones de las 4 sesiones. Soporte adicional: 2 sesiones Q&A en vivo y Foro privado para dudas y networking. Todo diseñado para maximizar tu productividad con IA.',
                'escalation_needed': False,
                'priority': 'high'
            },
            {
                'id': 'FAQ_012',
                'category': 'ventajas',
                'question': '¿Cuáles son las ventajas principales?',
                'keywords': ['ventajas', 'beneficios', 'por qué', 'diferencias', 'única', 'práctica', 'premium'],
                'answer': 'Las ventajas únicas son: Práctica guiada en vivo donde cada concepto se aplica inmediatamente garantizando aprendizaje efectivo, Acceso a recursos premium con plantillas diseñadas específicamente para maximizar productividad con IA, Soporte post-curso con Agente "AplicaAI Helper" 24/7 y foro exclusivo, y Proyecto real que te dará un entregable práctico para tu organización demostrando valor inmediato.',
                'escalation_needed': False,
                'priority': 'high'
            },
            {
                'id': 'FAQ_013',
                'category': 'examen',
                'question': '¿Cómo es el examen?',
                'keywords': ['examen', 'evaluación', 'proyecto', 'preguntas', 'certificación', 'formato', 'duración'],
                'answer': 'El examen es 100% práctico: Proyecto integrador + preguntas tipo caso con duración de 90 minutos. Las preguntas incluyen escenarios reales, diseño de prompts y análisis de resultados. Para prepararte recomendamos: Repasar plantillas IMPULSO y ejemplos de Custom GPTs, Practicar con workflows diarios y medir tiempos. Es una evaluación práctica que demuestra tu capacidad real de aplicar IA en situaciones profesionales.',
                'escalation_needed': False,
                'priority': 'medium'
            }
        ]
    
    async def detect_faq(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Detecta si el mensaje corresponde a una FAQ.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            FAQ encontrada o None
        """
        message_lower = message.lower()
        
        # Buscar coincidencias por palabras clave
        for faq in self.faq_database:
            for keyword in faq['keywords']:
                if keyword in message_lower:
                    return faq
        
        # Buscar coincidencias por categoría
        category_keywords = {
            'precio': ['precio', 'costo', 'valor', 'cuánto cuesta', 'inversión'],
            'duración': ['duración', 'tiempo', 'cuánto dura', 'horas'],
            'implementación': ['implementación', 'empresa', 'proceso', 'pasos'],
            'requisitos': ['requisitos', 'necesito', 'conocimientos'],
            'casos_éxito': ['casos de éxito', 'ejemplos', 'resultados'],
            'roi': ['roi', 'retorno', 'beneficio'],
            'certificado': ['certificado', 'diploma'],
            'soporte': ['soporte', 'ayuda', 'asistencia'],
            'acceso': ['acceso', 'tiempo', 'ilimitado'],
            'garantía': ['garantía', 'satisfacción', 'devolución']
        }
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    # Buscar FAQ de esa categoría
                    for faq in self.faq_database:
                        if faq['category'] == category:
                            return faq
        
        return None
    
    async def get_common_faqs(self) -> List[Dict[str, Any]]:
        """
        Obtiene las FAQs más comunes.
        
        Returns:
            Lista de FAQs comunes
        """
        # Ordenar por prioridad y devolver las más importantes
        sorted_faqs = sorted(self.faq_database, key=lambda x: self._get_priority_score(x['priority']), reverse=True)
        return sorted_faqs[:5]
    
    def _get_priority_score(self, priority: str) -> int:
        """
        Obtiene el score de prioridad.
        
        Args:
            priority: Prioridad de la FAQ
            
        Returns:
            Score de prioridad
        """
        priority_scores = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_scores.get(priority, 1)
    
    async def search_faqs(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca FAQs por consulta.
        
        Args:
            query: Consulta de búsqueda
            
        Returns:
            Lista de FAQs que coinciden
        """
        query_lower = query.lower()
        matches = []
        
        for faq in self.faq_database:
            # Buscar en pregunta
            if query_lower in faq['question'].lower():
                matches.append(faq)
                continue
            
            # Buscar en palabras clave
            for keyword in faq['keywords']:
                if query_lower in keyword:
                    matches.append(faq)
                    break
            
            # Buscar en respuesta
            if query_lower in faq['answer'].lower():
                matches.append(faq)
        
        # Ordenar por relevancia
        matches.sort(key=lambda x: self._calculate_relevance_score(x, query_lower), reverse=True)
        return matches
    
    def _calculate_relevance_score(self, faq: Dict[str, Any], query: str) -> int:
        """
        Calcula el score de relevancia de una FAQ.
        
        Args:
            faq: FAQ a evaluar
            query: Consulta de búsqueda
            
        Returns:
            Score de relevancia
        """
        score = 0
        
        # Pregunta exacta
        if query in faq['question'].lower():
            score += 10
        
        # Palabras clave
        for keyword in faq['keywords']:
            if query in keyword:
                score += 5
        
        # Respuesta
        if query in faq['answer'].lower():
            score += 3
        
        # Prioridad
        score += self._get_priority_score(faq['priority'])
        
        return score
    
    async def get_faq_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Obtiene FAQs por categoría.
        
        Args:
            category: Categoría de FAQ
            
        Returns:
            Lista de FAQs de esa categoría
        """
        return [faq for faq in self.faq_database if faq['category'] == category]
    
    async def get_faq_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de las FAQs.
        
        Returns:
            Dict con estadísticas
        """
        total_faqs = len(self.faq_database)
        
        # Contar por categoría
        categories = {}
        for faq in self.faq_database:
            category = faq['category']
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        # Contar por prioridad
        priorities = {}
        for faq in self.faq_database:
            priority = faq['priority']
            if priority not in priorities:
                priorities[priority] = 0
            priorities[priority] += 1
        
        # Contar que requieren escalación
        escalation_count = len([faq for faq in self.faq_database if faq['escalation_needed']])
        
        return {
            'total_faqs': total_faqs,
            'categories': categories,
            'priorities': priorities,
            'escalation_needed': escalation_count,
            'escalation_rate': round(escalation_count / total_faqs * 100, 2)
        }
    
    async def add_faq(self, category: str, question: str, answer: str, keywords: List[str] = None) -> bool:
        """
        Agrega una nueva FAQ.
        
        Args:
            category: Categoría de la FAQ
            question: Pregunta
            answer: Respuesta
            keywords: Palabras clave opcionales
            
        Returns:
            True si se agregó exitosamente
        """
        try:
            new_faq = {
                'id': f"FAQ_{len(self.faq_database) + 1:03d}",
                'category': category,
                'question': question,
                'keywords': keywords or [],
                'answer': answer,
                'escalation_needed': False,
                'priority': 'medium'
            }
            
            self.faq_database.append(new_faq)
            return True
            
        except Exception as e:
            print(f"❌ Error agregando FAQ: {e}")
            return False
    
    async def update_faq(self, faq_id: str, updates: Dict[str, Any]) -> bool:
        """
        Actualiza una FAQ existente.
        
        Args:
            faq_id: ID de la FAQ
            updates: Actualizaciones a aplicar
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            for faq in self.faq_database:
                if faq['id'] == faq_id:
                    faq.update(updates)
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error actualizando FAQ: {e}")
            return False 