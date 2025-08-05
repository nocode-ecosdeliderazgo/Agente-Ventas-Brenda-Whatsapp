"""
Sistema de Calificación de Experiencia del Usuario
Recopila feedback y evalúa la experiencia con el chatbot
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from app.infrastructure.openai.client import OpenAIClient
from memory.lead_memory import LeadMemoryManager

logger = logging.getLogger(__name__)

class UserExperienceRatingUseCase:
    """Gestiona calificación y feedback de experiencia del usuario"""
    
    def __init__(self, openai_client: OpenAIClient, memory_manager: LeadMemoryManager):
        self.openai_client = openai_client
        self.memory_manager = memory_manager
        self.logger = logger
        
        # Triggers para solicitar feedback
        self.feedback_triggers = {
            "interaction_milestone": {
                "condition": lambda data: data.get("interaction_count", 0) in [5, 10, 20],
                "type": "milestone_feedback",
                "priority": "medium"
            },
            "purchase_completion": {
                "condition": lambda data: data.get("purchase_completed", False),
                "type": "post_purchase_feedback",
                "priority": "high"
            },
            "problem_resolution": {
                "condition": lambda data: data.get("problem_resolved", False),
                "type": "resolution_feedback",
                "priority": "high"
            },
            "extended_conversation": {
                "condition": lambda data: data.get("conversation_duration", 0) > 30,
                "type": "experience_feedback",
                "priority": "medium"
            },
            "emotion_shift_positive": {
                "condition": lambda data: self._check_positive_emotion_shift(data),
                "type": "satisfaction_feedback",
                "priority": "low"
            },
            "before_departure": {
                "condition": lambda data: data.get("inactivity_minutes", 0) > 15,
                "type": "departure_feedback",
                "priority": "high"
            }
        }
    
    async def should_request_feedback(self, user_id: str) -> Dict:
        """
        Determina si debe solicitar feedback del usuario
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Dict con recomendación de solicitud de feedback
        """
        try:
            # 1. Obtener datos del usuario
            user_data = self._get_user_interaction_data(user_id)
            
            # 2. Verificar si ya se solicitó feedback recientemente
            if self._feedback_requested_recently(user_data):
                return {"should_request": False, "reason": "feedback_recently_requested"}
            
            # 3. Evaluar triggers
            triggered_conditions = []
            for trigger_name, trigger_config in self.feedback_triggers.items():
                if trigger_config["condition"](user_data):
                    triggered_conditions.append({
                        "trigger": trigger_name,
                        "type": trigger_config["type"],
                        "priority": trigger_config["priority"]
                    })
            
            # 4. Seleccionar trigger de mayor prioridad
            if not triggered_conditions:
                return {"should_request": False, "reason": "no_triggers_activated"}
            
            primary_trigger = self._select_primary_trigger(triggered_conditions)
            
            # 5. Generar solicitud de feedback
            feedback_request = await self._generate_feedback_request(
                user_id, primary_trigger, user_data
            )
            
            return {
                "should_request": True,
                "trigger": primary_trigger,
                "request_message": feedback_request["message"],
                "feedback_type": feedback_request["type"],
                "questions": feedback_request["questions"]
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluando solicitud de feedback: {e}")
            return {"should_request": False, "reason": "error", "error": str(e)}
    
    async def process_feedback_response(self, user_id: str, feedback_data: Dict) -> Dict:
        """
        Procesa respuesta de feedback del usuario
        
        Args:
            user_id: ID del usuario
            feedback_data: Datos del feedback
        
        Returns:
            Dict con análisis del feedback
        """
        try:
            # 1. Validar y estructurar feedback
            structured_feedback = self._structure_feedback_data(feedback_data)
            
            # 2. Analizar sentimiento y contenido
            sentiment_analysis = await self._analyze_feedback_sentiment(
                structured_feedback
            )
            
            # 3. Extraer insights específicos
            insights = await self._extract_feedback_insights(
                structured_feedback, sentiment_analysis
            )
            
            # 4. Identificar áreas de mejora
            improvement_areas = self._identify_improvement_areas(
                insights, structured_feedback
            )
            
            # 5. Generar respuesta de agradecimiento
            thank_you_response = await self._generate_thank_you_response(
                user_id, structured_feedback, sentiment_analysis
            )
            
            # 6. Guardar feedback en memoria
            await self._save_feedback_to_memory(user_id, {
                "structured_feedback": structured_feedback,
                "sentiment_analysis": sentiment_analysis,
                "insights": insights,
                "improvement_areas": improvement_areas,
                "submitted_at": datetime.now().isoformat()
            })
            
            # 7. Actualizar métricas globales
            await self._update_global_metrics(structured_feedback, sentiment_analysis)
            
            return {
                "feedback_processed": True,
                "sentiment": sentiment_analysis,
                "insights": insights,
                "improvement_areas": improvement_areas,
                "thank_you_message": thank_you_response,
                "follow_up_actions": self._suggest_follow_up_actions(insights)
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando feedback: {e}")
            return {"feedback_processed": False, "error": str(e)}
    
    async def generate_feedback_summary(self, time_period: str = "week") -> Dict:
        """
        Genera resumen de feedback para análisis
        
        Args:
            time_period: Período de análisis (day, week, month)
        
        Returns:
            Dict con resumen de feedback
        """
        try:
            # 1. Obtener feedback del período
            feedback_data = self._get_feedback_for_period(time_period)
            
            # 2. Calcular métricas de satisfacción
            satisfaction_metrics = self._calculate_satisfaction_metrics(feedback_data)
            
            # 3. Analizar tendencias
            trends = self._analyze_feedback_trends(feedback_data)
            
            # 4. Identificar problemas comunes
            common_issues = self._identify_common_issues(feedback_data)
            
            # 5. Generar recomendaciones de mejora
            recommendations = await self._generate_improvement_recommendations(
                satisfaction_metrics, trends, common_issues
            )
            
            return {
                "period": time_period,
                "total_feedback_count": len(feedback_data),
                "satisfaction_metrics": satisfaction_metrics,
                "trends": trends,
                "common_issues": common_issues,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generando resumen de feedback: {e}")
            return {"error": str(e)}
    
    def _get_user_interaction_data(self, user_id: str) -> Dict:
        """Obtiene datos de interacción del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            # Calcular duración de conversación
            first_interaction = getattr(user_memory, 'first_interaction', None)
            last_interaction = getattr(user_memory, 'last_interaction', None)
            
            conversation_duration = 0
            if first_interaction and last_interaction:
                start_time = datetime.fromisoformat(first_interaction)
                end_time = datetime.fromisoformat(last_interaction)
                conversation_duration = (end_time - start_time).total_seconds() / 60
            
            # Calcular inactividad
            inactivity_minutes = 0
            if last_interaction:
                last_time = datetime.fromisoformat(last_interaction)
                inactivity_minutes = (datetime.now() - last_time).total_seconds() / 60
            
            return {
                "user_id": user_id,
                "interaction_count": len(getattr(user_memory, 'message_history', [])),
                "conversation_duration": conversation_duration,
                "inactivity_minutes": inactivity_minutes,
                "current_emotion": getattr(user_memory, 'current_emotion', 'neutral'),
                "emotion_history": getattr(user_memory, 'emotion_history', []),
                "purchase_completed": getattr(user_memory, 'purchase_completed', False),
                "problem_resolved": getattr(user_memory, 'problem_resolved', False),
                "lead_score": getattr(user_memory, 'lead_score', 0),
                "buyer_persona": getattr(user_memory, 'buyer_persona', None),
                "feedback_history": getattr(user_memory, 'feedback_history', []),
                "last_feedback_date": getattr(user_memory, 'last_feedback_date', None)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos de interacción: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    def _feedback_requested_recently(self, user_data: Dict) -> bool:
        """Verifica si se solicitó feedback recientemente"""
        last_feedback_date = user_data.get("last_feedback_date")
        
        if not last_feedback_date:
            return False
        
        try:
            last_date = datetime.fromisoformat(last_feedback_date)
            hours_since_last = (datetime.now() - last_date).total_seconds() / 3600
            
            # No solicitar feedback si fue hace menos de 24 horas
            return hours_since_last < 24
            
        except:
            return False
    
    def _check_positive_emotion_shift(self, user_data: Dict) -> bool:
        """Verifica cambio positivo en emociones"""
        emotion_history = user_data.get("emotion_history", [])
        
        if len(emotion_history) < 3:
            return False
        
        # Obtener últimas 3 emociones
        recent_emotions = emotion_history[-3:]
        
        positive_emotions = {"emocionado", "curioso", "decidido"}
        negative_emotions = {"frustrado", "escéptico"}
        
        # Verificar si hubo cambio de negativo a positivo
        early_emotions = [e.get("emotion") for e in recent_emotions[:2]]
        latest_emotion = recent_emotions[-1].get("emotion")
        
        had_negative = any(e in negative_emotions for e in early_emotions)
        now_positive = latest_emotion in positive_emotions
        
        return had_negative and now_positive
    
    def _select_primary_trigger(self, triggered_conditions: List[Dict]) -> Dict:
        """Selecciona el trigger de mayor prioridad"""
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        triggered_conditions.sort(
            key=lambda x: priority_order.get(x["priority"], 0),
            reverse=True
        )
        
        return triggered_conditions[0]
    
    async def _generate_feedback_request(self, user_id: str, trigger: Dict, user_data: Dict) -> Dict:
        """Genera solicitud de feedback personalizada"""
        
        feedback_type = trigger["type"]
        buyer_persona = user_data.get("buyer_persona", "")
        current_emotion = user_data.get("current_emotion", "neutral")
        
        # Templates base por tipo de feedback
        feedback_templates = {
            "milestone_feedback": {
                "message": f"""🤔 **¡Un momento para tu opinión!**

Hemos conversado bastante y me gustaría conocer tu experiencia hasta ahora.

**📊 ¿Cómo calificas nuestra conversación?**
• ⭐⭐⭐⭐⭐ Excelente
• ⭐⭐⭐⭐ Muy buena  
• ⭐⭐⭐ Regular
• ⭐⭐ Mejorable
• ⭐ Necesita mejoras

**¿Qué te ha gustado más y qué podría mejorar?**""",
                "questions": [
                    "¿Cómo calificas la claridad de mis respuestas?",
                    "¿La información ha sido útil para ti?",
                    "¿Qué mejorarías de la experiencia?"
                ]
            },
            "post_purchase_feedback": {
                "message": f"""🎉 **¡Felicidades por tu decisión!**

Me da mucho gusto que hayas decidido invertir en automatizar tu empresa.

**📝 Para mejorar la experiencia de otros líderes como tú:**

**¿Cómo fue el proceso de compra?**
• ⭐⭐⭐⭐⭐ Muy fácil y claro
• ⭐⭐⭐⭐ Bastante bueno
• ⭐⭐⭐ Aceptable
• ⭐⭐ Complicado
• ⭐ Muy confuso

**¿Qué fue lo que más te convenció?**""",
                "questions": [
                    "¿El proceso de compra fue claro y fácil?",
                    "¿Qué información fue más valiosa para tu decisión?",
                    "¿Qué mejorarías del proceso de venta?"
                ]
            },
            "resolution_feedback": {
                "message": f"""✅ **¡Problema resuelto!**

Me alegra haber podido ayudarte a resolver tu consulta.

**🔍 Tu feedback es valioso:**

**¿Qué tan efectiva fue la solución?**
• ⭐⭐⭐⭐⭐ Resolvió completamente
• ⭐⭐⭐⭐ Muy útil
• ⭐⭐⭐ Parcialmente útil
• ⭐⭐ Poco útil
• ⭐ No resolvió nada

**¿Cómo fue el proceso de resolución?**""",
                "questions": [
                    "¿La solución fue clara y comprensible?",
                    "¿El tiempo de resolución fue adecuado?",
                    "¿Qué mejorarías del proceso de ayuda?"
                ]
            },
            "experience_feedback": {
                "message": f"""💭 **Hemos conversado un buen rato...**

Y me interesa conocer tu experiencia para seguir mejorando.

**🎯 Como {buyer_persona or 'líder'}, ¿cómo ha sido esta experiencia?**

**Califica la conversación:**
• ⭐⭐⭐⭐⭐ Excepcional
• ⭐⭐⭐⭐ Muy buena
• ⭐⭐⭐ Buena
• ⭐⭐ Regular
• ⭐ Mala

**¿Qué te pareció más valioso de nuestra charla?**""",
                "questions": [
                    "¿Las respuestas fueron relevantes para tu rol?",
                    "¿El tono de conversación fue apropiado?",
                    "¿Qué información adicional te habría gustado?"
                ]
            },
            "satisfaction_feedback": {
                "message": f"""😊 **¡Noto que tu experiencia ha mejorado!**

Es genial ver que la conversación tomó un rumbo positivo.

**👍 ¿Qué cambió tu perspectiva?**

**Califica tu satisfacción actual:**
• ⭐⭐⭐⭐⭐ Muy satisfecho
• ⭐⭐⭐⭐ Satisfecho
• ⭐⭐⭐ Neutral
• ⭐⭐ Insatisfecho
• ⭐ Muy insatisfecho

**¿Qué fue lo que más te convenció o aclaró?**""",
                "questions": [
                    "¿Qué información cambió tu perspectiva?",
                    "¿El cambio en la conversación fue natural?",
                    "¿Cómo puedo mantener esta experiencia positiva?"
                ]
            },
            "departure_feedback": {
                "message": f"""👋 **Antes de que te vayas...**

Veo que no has respondido en un rato. Entiendo que puedas estar ocupado.

**⚡ Solo 30 segundos de tu tiempo:**

**¿Cómo fue tu experiencia conmigo?**
• ⭐⭐⭐⭐⭐ Muy útil
• ⭐⭐⭐⭐ Útil
• ⭐⭐⭐ Regular
• ⭐⭐ Poco útil
• ⭐ No útil

**¿Algo específico que mejorarías?**

¡Gracias y que tengas excelente día! 🚀""",
                "questions": [
                    "¿Por qué no continuaste la conversación?",
                    "¿Qué te faltó para tomar una decisión?",
                    "¿Volverías a usar este tipo de asistente?"
                ]
            }
        }
        
        template = feedback_templates.get(feedback_type, feedback_templates["milestone_feedback"])
        
        # Personalizar según emoción actual
        if current_emotion == "frustrado":
            template["message"] = template["message"].replace("😊", "🤝").replace("¡", "")
        elif current_emotion == "emocionado":
            template["message"] = "🚀 " + template["message"]
        
        return {
            "type": feedback_type,
            "message": template["message"],
            "questions": template["questions"]
        }
    
    def _structure_feedback_data(self, feedback_data: Dict) -> Dict:
        """Estructura los datos de feedback"""
        
        structured = {
            "overall_rating": feedback_data.get("rating", 3),
            "feedback_text": feedback_data.get("text", ""),
            "specific_ratings": feedback_data.get("specific_ratings", {}),
            "feedback_type": feedback_data.get("type", "general"),
            "response_time": feedback_data.get("response_time", None),
            "completion_status": feedback_data.get("completed", True),
            "submitted_at": datetime.now().isoformat()
        }
        
        return structured
    
    async def _analyze_feedback_sentiment(self, feedback: Dict) -> Dict:
        """Analiza sentimiento del feedback"""
        
        try:
            feedback_text = feedback.get("feedback_text", "")
            overall_rating = feedback.get("overall_rating", 3)
            
            if not feedback_text:
                return {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "rating_based": True,
                    "text_analysis": None
                }
            
            # Usar OpenAI para análisis de sentimiento
            prompt = f"""Analiza el sentimiento de este feedback del usuario sobre un chatbot de ventas:

"{feedback_text}"

Rating numérico: {overall_rating}/5

Responde en formato JSON:
{{
    "sentiment": "positive|neutral|negative",
    "confidence": 0.85,
    "key_emotions": ["satisfacción", "frustración", "curiosidad"],
    "main_themes": ["facilidad_uso", "calidad_respuestas", "tiempo_respuesta"],
    "suggestions": ["mejorar X", "mantener Y"]
}}"""

            response = await self.openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            # Parsear respuesta
            analysis = json.loads(response.get('content', '{}'))
            analysis["rating_based"] = False
            analysis["text_analysis"] = True
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error en análisis de sentimiento: {e}")
            
            # Fallback basado en rating
            if overall_rating >= 4:
                sentiment = "positive"
            elif overall_rating >= 3:
                sentiment = "neutral"
            else:
                sentiment = "negative"
            
            return {
                "sentiment": sentiment,
                "confidence": 0.7,
                "rating_based": True,
                "text_analysis": False,
                "fallback_reason": str(e)
            }
    
    async def _extract_feedback_insights(self, feedback: Dict, sentiment: Dict) -> Dict:
        """Extrae insights específicos del feedback"""
        
        insights = {
            "satisfaction_level": self._categorize_satisfaction(feedback.get("overall_rating", 3)),
            "key_strengths": self._extract_strengths(feedback, sentiment),
            "improvement_opportunities": self._extract_improvements(feedback, sentiment),
            "user_expectations": self._analyze_expectations(feedback, sentiment),
            "recommendation_likelihood": self._calculate_nps(feedback.get("overall_rating", 3))
        }
        
        return insights
    
    def _categorize_satisfaction(self, rating: int) -> str:
        """Categoriza nivel de satisfacción"""
        if rating >= 5:
            return "muy_alta"
        elif rating >= 4:
            return "alta"
        elif rating >= 3:
            return "media"
        elif rating >= 2:
            return "baja"
        else:
            return "muy_baja"
    
    def _extract_strengths(self, feedback: Dict, sentiment: Dict) -> List[str]:
        """Extrae fortalezas mencionadas"""
        strengths = []
        
        feedback_text = feedback.get("feedback_text", "").lower()
        
        strength_keywords = {
            "rapidez": ["rápido", "veloz", "inmediato", "pronto"],
            "claridad": ["claro", "comprensible", "fácil entender"],
            "utilidad": ["útil", "valioso", "ayuda", "efectivo"],
            "personalización": ["personalizado", "específico", "adaptado"],
            "conocimiento": ["experto", "conoce", "información completa"]
        }
        
        for strength, keywords in strength_keywords.items():
            if any(keyword in feedback_text for keyword in keywords):
                strengths.append(strength)
        
        # Agregar basado en sentiment analysis
        if sentiment.get("sentiment") == "positive":
            main_themes = sentiment.get("main_themes", [])
            strengths.extend(main_themes)
        
        return list(set(strengths))  # Eliminar duplicados
    
    def _extract_improvements(self, feedback: Dict, sentiment: Dict) -> List[str]:
        """Extrae oportunidades de mejora"""
        improvements = []
        
        feedback_text = feedback.get("feedback_text", "").lower()
        
        improvement_keywords = {
            "velocidad": ["lento", "demora", "tardó", "más rápido"],
            "claridad": ["confuso", "no entendí", "complicado"],
            "información": ["más detalles", "falta información", "incompleto"],
            "personalización": ["genérico", "no específico", "muy general"],
            "opciones": ["más opciones", "alternativas", "flexibilidad"]
        }
        
        for improvement, keywords in improvement_keywords.items():
            if any(keyword in feedback_text for keyword in keywords):
                improvements.append(improvement)
        
        # Agregar basado en rating bajo
        if feedback.get("overall_rating", 3) < 3:
            improvements.extend(["experiencia_general", "satisfacción_usuario"])
        
        return list(set(improvements))
    
    def _analyze_expectations(self, feedback: Dict, sentiment: Dict) -> Dict:
        """Analiza expectativas del usuario"""
        
        rating = feedback.get("overall_rating", 3)
        
        if rating >= 4:
            expectation_level = "superadas"
        elif rating >= 3:
            expectation_level = "cumplidas"
        else:
            expectation_level = "no_cumplidas"
        
        return {
            "level": expectation_level,
            "rating": rating,
            "sentiment": sentiment.get("sentiment", "neutral")
        }
    
    def _calculate_nps(self, rating: int) -> Dict:
        """Calcula Net Promoter Score equivalente"""
        
        if rating >= 5:
            category = "promotor"
            likelihood = "muy_alta"
        elif rating >= 4:
            category = "pasivo"
            likelihood = "media"
        else:
            category = "detractor"
            likelihood = "baja"
        
        return {
            "category": category,
            "likelihood": likelihood,
            "score": rating
        }
    
    def _identify_improvement_areas(self, insights: Dict, feedback: Dict) -> List[Dict]:
        """Identifica áreas específicas de mejora"""
        
        improvement_areas = []
        
        # Basado en satisfacción
        satisfaction = insights.get("satisfaction_level", "media")
        if satisfaction in ["baja", "muy_baja"]:
            improvement_areas.append({
                "area": "experiencia_general",
                "priority": "alta",
                "description": "Mejorar experiencia general del usuario"
            })
        
        # Basado en oportunidades identificadas
        opportunities = insights.get("improvement_opportunities", [])
        for opportunity in opportunities:
            improvement_areas.append({
                "area": opportunity,
                "priority": "media",
                "description": f"Mejorar {opportunity.replace('_', ' ')}"
            })
        
        # Basado en NPS
        nps = insights.get("recommendation_likelihood", {})
        if nps.get("category") == "detractor":
            improvement_areas.append({
                "area": "satisfaccion_cliente",
                "priority": "alta",
                "description": "Reducir detractores y aumentar satisfacción"
            })
        
        return improvement_areas
    
    async def _generate_thank_you_response(self, user_id: str, feedback: Dict, sentiment: Dict) -> str:
        """Genera respuesta de agradecimiento personalizada"""
        
        rating = feedback.get("overall_rating", 3)
        sentiment_type = sentiment.get("sentiment", "neutral")
        
        if rating >= 4 and sentiment_type == "positive":
            return """🙏 **¡Muchísimas gracias por tu feedback!**

Me alegra saber que tuviste una buena experiencia. Tu opinión me ayuda a mejorar para servir mejor a otros líderes como tú.

🚀 **¿Continuamos con el siguiente paso?**"""
        
        elif rating >= 3:
            return """🤝 **Gracias por tu honest feedback.**

Valoro mucho tu tiempo para darnos tu opinión. Tomaré en cuenta tus comentarios para mejorar la experiencia.

💪 **¿Hay algo más en lo que pueda ayudarte ahora?**"""
        
        else:
            return """🤝 **Gracias por tu sinceridad.**

Lamento que la experiencia no haya sido la esperada. Tu feedback es muy valioso para mejorar y servir mejor a futuros usuarios.

🔧 **¿Te gustaría que intentemos resolver algo específico?**"""
    
    async def _save_feedback_to_memory(self, user_id: str, feedback_data: Dict):
        """Guarda feedback en memoria del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            if not hasattr(user_memory, 'feedback_history'):
                user_memory.feedback_history = []
            
            user_memory.feedback_history.append(feedback_data)
            
            # Mantener solo los últimos 5 feedbacks
            if len(user_memory.feedback_history) > 5:
                user_memory.feedback_history = user_memory.feedback_history[-5:]
            
            # Actualizar fecha del último feedback
            user_memory.last_feedback_date = datetime.now().isoformat()
            
            # Actualizar métricas de satisfacción
            latest_rating = feedback_data["structured_feedback"].get("overall_rating", 3)
            user_memory.latest_satisfaction_rating = latest_rating
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error guardando feedback en memoria: {e}")
    
    async def _update_global_metrics(self, feedback: Dict, sentiment: Dict):
        """Actualiza métricas globales de feedback"""
        # Este método actualizaría métricas en base de datos o sistema central
        # Por ahora, solo log la información
        self.logger.info(f"Feedback global update: rating={feedback.get('overall_rating')}, sentiment={sentiment.get('sentiment')}")
    
    def _suggest_follow_up_actions(self, insights: Dict) -> List[str]:
        """Sugiere acciones de seguimiento"""
        
        actions = []
        
        satisfaction = insights.get("satisfaction_level", "media")
        nps = insights.get("recommendation_likelihood", {})
        
        if satisfaction in ["alta", "muy_alta"]:
            actions.append("continuar_proceso_venta")
            actions.append("solicitar_referencia")
        
        elif satisfaction == "media":
            actions.append("identificar_necesidades_adicionales")
            actions.append("proporcionar_mas_valor")
        
        else:
            actions.append("resolver_problemas_específicos")
            actions.append("mejorar_experiencia")
        
        if nps.get("category") == "promotor":
            actions.append("aprovechar_momentum_positivo")
        
        return actions
    
    def _get_feedback_for_period(self, period: str) -> List[Dict]:
        """Obtiene feedback para un período específico"""
        # Este método obtendría feedback de la base de datos
        # Por ahora retorna datos mock
        return []
    
    def _calculate_satisfaction_metrics(self, feedback_data: List[Dict]) -> Dict:
        """Calcula métricas de satisfacción"""
        if not feedback_data:
            return {"avg_rating": 0, "total_responses": 0}
        
        ratings = [f.get("overall_rating", 3) for f in feedback_data]
        
        return {
            "avg_rating": sum(ratings) / len(ratings),
            "total_responses": len(feedback_data),
            "promoters": len([r for r in ratings if r >= 4]),
            "detractors": len([r for r in ratings if r <= 2]),
            "satisfaction_distribution": {
                "5_stars": ratings.count(5),
                "4_stars": ratings.count(4),
                "3_stars": ratings.count(3),
                "2_stars": ratings.count(2),
                "1_star": ratings.count(1)
            }
        }
    
    def _analyze_feedback_trends(self, feedback_data: List[Dict]) -> Dict:
        """Analiza tendencias en el feedback"""
        return {
            "trend": "stable",
            "improvement_areas": [],
            "positive_trends": []
        }
    
    def _identify_common_issues(self, feedback_data: List[Dict]) -> List[Dict]:
        """Identifica problemas comunes en el feedback"""
        return []
    
    async def _generate_improvement_recommendations(self, metrics: Dict, trends: Dict, issues: List[Dict]) -> List[Dict]:
        """Genera recomendaciones de mejora"""
        return [
            {
                "area": "experiencia_usuario",
                "recommendation": "Continuar monitoreando feedback",
                "priority": "media"
            }
        ]