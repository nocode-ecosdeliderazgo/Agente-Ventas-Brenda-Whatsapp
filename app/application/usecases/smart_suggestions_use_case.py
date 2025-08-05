"""
Sistema de Sugerencias Inteligentes de Próximos Pasos
Genera recomendaciones contextuales para continuar la conversación
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from app.infrastructure.openai.client import OpenAIClient
from memory.lead_memory import LeadMemoryManager

logger = logging.getLogger(__name__)

class SmartSuggestionsUseCase:
    """Genera sugerencias inteligentes de próximos pasos"""
    
    def __init__(self, openai_client: OpenAIClient, memory_manager: LeadMemoryManager):
        self.openai_client = openai_client
        self.memory_manager = memory_manager
        self.logger = logger
        
        # Rutas de conversación estructuradas
        self.conversation_paths = {
            "awareness": {
                "stage": "descubrimiento",
                "next_steps": [
                    "show_problem_impact",
                    "demonstrate_solution",
                    "share_success_stories"
                ]
            },
            "interest": {
                "stage": "interés",
                "next_steps": [
                    "provide_detailed_info",
                    "show_roi_calculation",
                    "offer_demo"
                ]
            },
            "consideration": {
                "stage": "consideración",
                "next_steps": [
                    "address_objections",
                    "show_social_proof",
                    "create_urgency"
                ]
            },
            "intent": {
                "stage": "intención de compra",
                "next_steps": [
                    "present_offer",
                    "facilitate_purchase",
                    "provide_guarantees"
                ]
            }
        }
    
    async def generate_suggestions(self, user_id: str, current_context: Dict) -> Dict:
        """
        Genera sugerencias inteligentes basadas en el contexto actual
        
        Args:
            user_id: ID del usuario
            current_context: Contexto actual de la conversación
        
        Returns:
            Dict con sugerencias estructuradas
        """
        try:
            # 1. Analizar estado actual del usuario
            user_state = await self._analyze_user_state(user_id, current_context)
            
            # 2. Identificar fase de la conversación
            conversation_stage = self._identify_conversation_stage(user_state)
            
            # 3. Generar sugerencias contextuales
            suggestions = await self._generate_contextual_suggestions(
                user_state, conversation_stage, current_context
            )
            
            # 4. Personalizar por buyer persona
            personalized_suggestions = self._personalize_suggestions(
                suggestions, user_state
            )
            
            # 5. Priorizar sugerencias
            prioritized_suggestions = self._prioritize_suggestions(
                personalized_suggestions, user_state
            )
            
            return {
                "suggestions": prioritized_suggestions,
                "user_stage": conversation_stage,
                "confidence": 0.85,
                "reasoning": user_state.get("reasoning", ""),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generando sugerencias: {e}")
            return {
                "suggestions": self._get_fallback_suggestions(),
                "user_stage": "unknown",
                "confidence": 0.5,
                "error": str(e)
            }
    
    async def _analyze_user_state(self, user_id: str, context: Dict) -> Dict:
        """Analiza el estado actual del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            # Datos básicos
            state = {
                "user_id": user_id,
                "buyer_persona": getattr(user_memory, 'buyer_persona', None),
                "current_emotion": getattr(user_memory, 'current_emotion', 'neutral'),
                "lead_score": getattr(user_memory, 'lead_score', 0),
                "purchase_signals": getattr(user_memory, 'purchase_signals', 0),
                "interaction_count": len(getattr(user_memory, 'message_history', [])),
                "last_interaction": getattr(user_memory, 'last_interaction', None),
                "course_announcement_sent": getattr(user_memory, 'course_announcement_sent', False),
                "bonuses_shown": getattr(user_memory, 'bonuses_shown', []),
                "objections_raised": getattr(user_memory, 'objections_raised', []),
                "questions_asked": self._extract_question_topics(user_memory),
                "engagement_level": self._calculate_engagement_level(user_memory),
                "time_in_funnel": self._calculate_time_in_funnel(user_memory)
            }
            
            # Analizar intenciones recientes
            state["recent_intents"] = self._analyze_recent_intents(user_memory, context)
            
            # Determinar barreras identificadas
            state["barriers"] = self._identify_barriers(user_memory)
            
            # Calcular propensión a compra
            state["purchase_propensity"] = self._calculate_purchase_propensity(state)
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error analizando estado del usuario: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    def _identify_conversation_stage(self, user_state: Dict) -> str:
        """Identifica en qué fase de la conversación está el usuario"""
        
        lead_score = user_state.get("lead_score", 0)
        purchase_signals = user_state.get("purchase_signals", 0)
        interaction_count = user_state.get("interaction_count", 0)
        engagement_level = user_state.get("engagement_level", "low")
        purchase_propensity = user_state.get("purchase_propensity", 0)
        
        # Lógica de clasificación por etapas
        if purchase_signals >= 3 or purchase_propensity >= 80:
            return "intent"
        elif (lead_score >= 60 and engagement_level in ["high", "very_high"]) or interaction_count >= 8:
            return "consideration"
        elif lead_score >= 30 or interaction_count >= 3:
            return "interest"
        else:
            return "awareness"
    
    async def _generate_contextual_suggestions(self, user_state: Dict, stage: str, context: Dict) -> List[Dict]:
        """Genera sugerencias específicas para el contexto actual"""
        
        base_suggestions = []
        stage_config = self.conversation_paths.get(stage, self.conversation_paths["awareness"])
        
        for next_step in stage_config["next_steps"]:
            suggestion = await self._create_suggestion_for_step(
                next_step, user_state, context
            )
            if suggestion:
                base_suggestions.append(suggestion)
        
        # Agregar sugerencias específicas del contexto
        contextual_suggestions = await self._add_contextual_suggestions(
            base_suggestions, user_state, context
        )
        
        return contextual_suggestions
    
    async def _create_suggestion_for_step(self, step: str, user_state: Dict, context: Dict) -> Optional[Dict]:
        """Crea una sugerencia específica para un paso dado"""
        
        suggestion_templates = {
            "show_problem_impact": {
                "type": "problem_awareness",
                "priority": 8,
                "message": "💡 **¿Sabías que las PyMEs pierden 15 horas/semana en tareas que la IA puede automatizar?**\n\n¿Cuánto tiempo crees que tu equipo dedica a tareas repetitivas?",
                "action": "calculate_time_waste",
                "expected_outcome": "awareness_of_problem"
            },
            "demonstrate_solution": {
                "type": "solution_demo",
                "priority": 9,
                "message": "🎯 **Te muestro cómo esto funciona en la práctica:**\n\nTe envío un video de 3 minutos donde ves exactamente cómo un CEO como tú automatizó su área de ventas.\n\n¿Te interesa verlo?",
                "action": "send_demo_video",
                "expected_outcome": "solution_understanding"
            },
            "share_success_stories": {
                "type": "social_proof",
                "priority": 7,
                "message": "📈 **Caso real:** Una empresa como la tuya aumentó productividad 40% en 30 días.\n\n¿Te gustaría conocer exactamente qué implementaron?",
                "action": "share_case_study",
                "expected_outcome": "credibility_building"
            },
            "provide_detailed_info": {
                "type": "information",
                "priority": 8,
                "message": "📚 **Información completa del programa:**\n\n• 8 sesiones prácticas con tu empresa real\n• Templates listos para usar\n• Soporte directo del instructor\n• Garantía de resultados\n\n¿Qué parte te gustaría explorar primero?",
                "action": "provide_course_details",
                "expected_outcome": "informed_interest"
            },
            "show_roi_calculation": {
                "type": "value_demonstration",
                "priority": 9,
                "message": "💰 **Calculemos tu ROI específico:**\n\nSi automatizas solo 10 horas/semana x $500/hora = $5,000/semana de ahorro.\n\nEn 1 mes: $20,000 vs inversión de $4,500\n\n**ROI: 344% en el primer mes**\n\n¿Estos números tienen sentido para tu caso?",
                "action": "personalized_roi",
                "expected_outcome": "value_realization"
            },
            "offer_demo": {
                "type": "experience",
                "priority": 9,
                "message": "🎥 **Demo personalizada para tu empresa:**\n\n15 minutos donde te muestro exactamente cómo aplicarías esto en TU negocio específico.\n\n¿Tienes tiempo hoy o mañana?",
                "action": "schedule_demo",
                "expected_outcome": "hands_on_experience"
            },
            "address_objections": {
                "type": "objection_handling",
                "priority": 8,
                "message": self._generate_objection_response(user_state),
                "action": "handle_objections",
                "expected_outcome": "barrier_removal"
            },
            "show_social_proof": {
                "type": "credibility",
                "priority": 7,
                "message": "👥 **Lo que dicen otros CEOs:**\n\n\"En 2 semanas ya tenía 3 automatizaciones funcionando\" - María, CEO TechStart\n\n\"El ROI se pagó en el primer mes\" - Carlos, Director Operaciones\n\n¿Te gustaría hablar con alguno de ellos?",
                "action": "connect_testimonials",
                "expected_outcome": "trust_building"
            },
            "create_urgency": {
                "type": "urgency",
                "priority": 6,
                "message": "⏰ **Último día de oferta especial:**\n\n• 15% descuento (solo hoy)\n• Bonus: Sesión estratégica 1-on-1\n• Garantía 30 días\n\n¿Aprovechamos esta oportunidad?",
                "action": "limited_time_offer",
                "expected_outcome": "decision_acceleration"
            },
            "present_offer": {
                "type": "sales_offer",
                "priority": 10,
                "message": "🎯 **Perfecto momento para empezar:**\n\n💎 **Paquete CEO:**\n• Programa completo: $4,500\n• Descuento ejecutivo: -$675\n• **Total: $3,825**\n\n💳 Pagos flexibles disponibles\n\n¿Confirmo tu lugar?",
                "action": "present_purchase_options",
                "expected_outcome": "purchase_decision"
            },
            "facilitate_purchase": {
                "type": "purchase_support",
                "priority": 10,
                "message": "💳 **Opciones de pago para CEOs:**\n\n1️⃣ Pago único: $3,825 (máximo descuento)\n2️⃣ 2 pagos: $2,250 c/u\n3️⃣ 3 pagos: $1,575 c/u\n\n**¿Con cuál opción arrancamos?**",
                "action": "facilitate_payment",
                "expected_outcome": "completed_purchase"
            },
            "provide_guarantees": {
                "type": "risk_reduction",
                "priority": 8,
                "message": "🛡️ **Garantías para tu tranquilidad:**\n\n✅ 30 días de garantía total\n✅ Si no ves resultados, 100% reembolso\n✅ Soporte ilimitado durante el programa\n\n**Cero riesgo para ti.**\n\n¿Esto elimina tus preocupaciones?",
                "action": "provide_security",
                "expected_outcome": "risk_mitigation"
            }
        }
        
        template = suggestion_templates.get(step)
        if not template:
            return None
        
        # Verificar si la sugerencia es relevante para el usuario actual
        if self._is_suggestion_relevant(template, user_state):
            return {
                **template,
                "id": f"{step}_{user_state['user_id']}_{int(datetime.now().timestamp())}",
                "created_at": datetime.now().isoformat()
            }
        
        return None
    
    def _generate_objection_response(self, user_state: Dict) -> str:
        """Genera respuesta específica a objeciones identificadas"""
        
        objections = user_state.get("objections_raised", [])
        
        if "precio" in objections or "costo" in objections:
            return "💰 **Entiendo la preocupación por la inversión...**\n\nPiénsalo así: si no automatizas ahora, ¿cuánto te costará seguir haciendo todo manual por 6 meses más?\n\n¿Hacemos el cálculo específico para tu caso?"
        
        elif "tiempo" in objections:
            return "⏰ **Sé que el tiempo es oro para un CEO...**\n\nPor eso el programa es intensivo: 8 sesiones de 1.5h cada una. En 1 mes tienes todo funcionando.\n\n¿Prefieres seguir perdiendo 15 horas/semana para siempre?"
        
        elif "resultados" in objections or "funciona" in objections:
            return "📊 **Te entiendo, necesitas certeza de resultados...**\n\nPor eso ofrecemos:\n• Casos documentados de éxito\n• Garantía 30 días\n• Primeros resultados en semana 1\n\n¿Te gustaría ver evidencia específica de tu industria?"
        
        else:
            return "🤔 **Veo que tienes algunas dudas...**\n\n¿Cuál es tu principal preocupación? Prefiero abordarlo directamente que asumir qué te inquieta.\n\n¿Es el tiempo, la inversión, o los resultados?"
    
    async def _add_contextual_suggestions(self, base_suggestions: List[Dict], user_state: Dict, context: Dict) -> List[Dict]:
        """Añade sugerencias específicas del contexto"""
        
        # Sugerencias basadas en emoción actual
        current_emotion = user_state.get("current_emotion", "neutral")
        
        if current_emotion == "frustrado":
            base_suggestions.append({
                "id": f"emotion_frustrado_{int(datetime.now().timestamp())}",
                "type": "emotional_support",
                "priority": 10,
                "message": "🤝 **Siento que algo no está quedando claro...**\n\n¿Qué te está generando más confusión? Prefiero explicarte exactamente lo que necesitas saber.\n\n¿Empezamos de nuevo con lo básico?",
                "action": "clarify_confusion",
                "expected_outcome": "reduced_frustration"
            })
        
        elif current_emotion == "emocionado":
            base_suggestions.append({
                "id": f"emotion_emocionado_{int(datetime.now().timestamp())}",
                "type": "momentum_acceleration",
                "priority": 10,
                "message": "🚀 **¡Perfecto! Veo que estás convencido del potencial...**\n\nAprovechemos este momentum:\n• Te reservo lugar ahora mismo\n• Empezamos la próxima semana\n• Bonus por decidir hoy\n\n**¿Confirmamos?**",
                "action": "accelerate_close",
                "expected_outcome": "immediate_action"
            })
        
        # Sugerencias basadas en tiempo en el funnel
        time_in_funnel = user_state.get("time_in_funnel", 0)
        
        if time_in_funnel > 7:  # Más de 7 días
            base_suggestions.append({
                "id": f"time_urgency_{int(datetime.now().timestamp())}",
                "type": "urgency_creator",
                "priority": 8,
                "message": "📅 **Han pasado varios días desde que empezamos a conversar...**\n\nEntiendo que tomar decisiones lleva tiempo, pero cada día sin automatizar es productividad perdida.\n\n¿Qué necesitas para tomar la decisión final?",
                "action": "create_urgency",
                "expected_outcome": "decision_acceleration"
            })
        
        # Sugerencias basadas en buyer persona
        buyer_persona = user_state.get("buyer_persona")
        
        if buyer_persona == "CEO":
            base_suggestions.append({
                "id": f"persona_ceo_{int(datetime.now().timestamp())}",
                "type": "executive_focus",
                "priority": 9,
                "message": "👔 **Como CEO, tu tiempo vale oro...**\n\nEste programa te da ROI desde el primer mes. No es un gasto, es la inversión más rentable que puedes hacer.\n\n¿Calculamos el impacto específico en tu P&L?",
                "action": "executive_roi",
                "expected_outcome": "strategic_alignment"
            })
        
        return base_suggestions
    
    def _personalize_suggestions(self, suggestions: List[Dict], user_state: Dict) -> List[Dict]:
        """Personaliza sugerencias según el perfil del usuario"""
        
        buyer_persona = user_state.get("buyer_persona")
        current_emotion = user_state.get("current_emotion", "neutral")
        
        for suggestion in suggestions:
            # Ajustar tono según emoción
            if current_emotion == "ansioso":
                suggestion["message"] = "⚡ " + suggestion["message"]
            elif current_emotion == "escéptico":
                suggestion["message"] = suggestion["message"].replace("🚀", "📊")
            
            # Ajustar lenguaje según buyer persona
            if buyer_persona == "Operations Manager":
                suggestion["message"] = suggestion["message"].replace("CEO", "líder de operaciones")
                suggestion["message"] = suggestion["message"].replace("productividad", "eficiencia operacional")
            elif buyer_persona == "Marketing Manager":
                suggestion["message"] = suggestion["message"].replace("automatizar", "optimizar campañas")
        
        return suggestions
    
    def _prioritize_suggestions(self, suggestions: List[Dict], user_state: Dict) -> List[Dict]:
        """Prioriza sugerencias según el contexto del usuario"""
        
        # Factores de priorización
        lead_score = user_state.get("lead_score", 0)
        purchase_signals = user_state.get("purchase_signals", 0)
        engagement_level = user_state.get("engagement_level", "low")
        
        # Ajustar prioridades
        for suggestion in suggestions:
            base_priority = suggestion.get("priority", 5)
            
            # Aumentar prioridad para usuarios de alto potencial
            if lead_score > 70:
                suggestion["priority"] = min(10, base_priority + 2)
            
            # Priorizar ofertas para usuarios con señales de compra
            if purchase_signals >= 2 and suggestion["type"] in ["sales_offer", "purchase_support"]:
                suggestion["priority"] = 10
            
            # Priorizar educación para usuarios de baja participación
            if engagement_level == "low" and suggestion["type"] in ["problem_awareness", "solution_demo"]:
                suggestion["priority"] = min(10, base_priority + 1)
        
        # Ordenar por prioridad
        suggestions.sort(key=lambda x: x.get("priority", 5), reverse=True)
        
        # Retornar top 5 sugerencias
        return suggestions[:5]
    
    def _is_suggestion_relevant(self, suggestion: Dict, user_state: Dict) -> bool:
        """Determina si una sugerencia es relevante para el usuario actual"""
        
        suggestion_type = suggestion.get("type")
        purchase_signals = user_state.get("purchase_signals", 0)
        course_sent = user_state.get("course_announcement_sent", False)
        
        # No ofrecer demo si ya se envió curso
        if suggestion_type == "solution_demo" and course_sent:
            return False
        
        # No presionar venta si no hay señales de compra
        if suggestion_type in ["sales_offer", "purchase_support"] and purchase_signals < 1:
            return False
        
        # No crear urgencia si el usuario acaba de llegar
        if suggestion_type == "urgency" and user_state.get("interaction_count", 0) < 3:
            return False
        
        return True
    
    def _get_fallback_suggestions(self) -> List[Dict]:
        """Sugerencias de respaldo cuando falla el análisis"""
        return [
            {
                "id": "fallback_1",
                "type": "general_info",
                "priority": 5,
                "message": "📚 ¿Te gustaría conocer más detalles sobre cómo la IA puede ayudar a tu empresa específicamente?",
                "action": "provide_general_info",
                "expected_outcome": "continued_engagement"
            },
            {
                "id": "fallback_2",
                "type": "question_prompt",
                "priority": 5,
                "message": "🤔 ¿Hay alguna pregunta específica que tengas sobre automatización con IA?",
                "action": "encourage_questions",
                "expected_outcome": "user_engagement"
            }
        ]
    
    def _extract_question_topics(self, user_memory) -> List[str]:
        """Extrae temas de preguntas del historial"""
        topics = []
        message_history = getattr(user_memory, 'message_history', [])
        
        topic_keywords = {
            "precio": ["precio", "costo", "cuanto", "inversión"],
            "tiempo": ["tiempo", "duración", "cuando", "horario"],
            "contenido": ["contenido", "temario", "aprendo", "enseñan"],
            "resultados": ["resultados", "funciona", "efectivo", "garantía"],
            "modalidad": ["online", "presencial", "modalidad", "formato"]
        }
        
        for message in message_history[-10:]:  # Últimos 10 mensajes
            message_lower = message.lower()
            for topic, keywords in topic_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    if topic not in topics:
                        topics.append(topic)
        
        return topics
    
    def _calculate_engagement_level(self, user_memory) -> str:
        """Calcula nivel de engagement del usuario"""
        message_count = len(getattr(user_memory, 'message_history', []))
        question_count = len(self._extract_question_topics(user_memory))
        
        if message_count >= 10 and question_count >= 5:
            return "very_high"
        elif message_count >= 6 and question_count >= 3:
            return "high"
        elif message_count >= 3:
            return "medium"
        else:
            return "low"
    
    def _calculate_time_in_funnel(self, user_memory) -> int:
        """Calcula días desde primera interacción"""
        try:
            first_interaction = getattr(user_memory, 'first_interaction', None)
            if not first_interaction:
                return 0
            
            start_date = datetime.fromisoformat(first_interaction)
            days_diff = (datetime.now() - start_date).days
            
            return days_diff
            
        except:
            return 0
    
    def _analyze_recent_intents(self, user_memory, context: Dict) -> List[str]:
        """Analiza intenciones recientes del usuario"""
        intents = []
        
        # Buscar en mensajes recientes
        recent_messages = getattr(user_memory, 'message_history', [])[-5:]
        
        intent_patterns = {
            "purchase": ["comprar", "adquirir", "me apunto", "cuanto cuesta"],
            "demo": ["demo", "ejemplo", "mostrar", "ver"],
            "info": ["información", "detalles", "contenido", "temario"],
            "comparison": ["comparar", "diferencia", "versus", "opciones"],
            "objection": ["pero", "sin embargo", "preocupa", "duda"]
        }
        
        for message in recent_messages:
            message_lower = message.lower()
            for intent, patterns in intent_patterns.items():
                if any(pattern in message_lower for pattern in patterns):
                    if intent not in intents:
                        intents.append(intent)
        
        return intents
    
    def _identify_barriers(self, user_memory) -> List[str]:
        """Identifica barreras identificadas del usuario"""
        barriers = []
        
        # Buscar objeciones en el historial
        objections_raised = getattr(user_memory, 'objections_raised', [])
        barriers.extend(objections_raised)
        
        # Buscar en mensajes recientes
        recent_messages = getattr(user_memory, 'message_history', [])[-5:]
        
        barrier_patterns = {
            "budget": ["caro", "precio alto", "presupuesto", "no tengo dinero"],
            "time": ["no tengo tiempo", "ocupado", "cuando"],
            "skepticism": ["funciona realmente", "garantía", "seguro", "dudas"],
            "complexity": ["complicado", "difícil", "no entiendo"]
        }
        
        for message in recent_messages:
            message_lower = message.lower()
            for barrier, patterns in barrier_patterns.items():
                if any(pattern in message_lower for pattern in patterns):
                    if barrier not in barriers:
                        barriers.append(barrier)
        
        return barriers
    
    def _calculate_purchase_propensity(self, user_state: Dict) -> int:
        """Calcula propensión de compra del usuario (0-100)"""
        score = 0
        
        # Factores positivos
        lead_score = user_state.get("lead_score", 0)
        score += min(40, lead_score * 0.4)  # Max 40 puntos
        
        purchase_signals = user_state.get("purchase_signals", 0)
        score += min(30, purchase_signals * 10)  # Max 30 puntos
        
        engagement_level = user_state.get("engagement_level", "low")
        engagement_scores = {"very_high": 20, "high": 15, "medium": 10, "low": 5}
        score += engagement_scores.get(engagement_level, 5)
        
        # Factores de emoción
        current_emotion = user_state.get("current_emotion", "neutral")
        emotion_scores = {"emocionado": 15, "decidido": 20, "curioso": 10, "neutral": 5, "frustrado": -5, "escéptico": 0}
        score += emotion_scores.get(current_emotion, 5)
        
        # Factores negativos
        barriers = user_state.get("barriers", [])
        score -= len(barriers) * 5  # -5 por cada barrera
        
        time_in_funnel = user_state.get("time_in_funnel", 0)
        if time_in_funnel > 14:  # Más de 2 semanas
            score -= 10
        
        return max(0, min(100, score))