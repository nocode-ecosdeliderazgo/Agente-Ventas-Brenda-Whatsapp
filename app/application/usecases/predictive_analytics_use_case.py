"""
Sistema de Análisis Predictivo
Predicción de comportamiento del usuario y optimización de timing
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
from dataclasses import dataclass

from app.infrastructure.openai.client import OpenAIClient
from memory.lead_memory import LeadMemoryManager

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Resultado de una predicción"""
    prediction_type: str
    probability: float
    confidence: float
    factors: List[str]
    recommended_action: str
    timing: str
    generated_at: str

class PredictiveAnalyticsUseCase:
    """Sistema de análisis predictivo para optimización de conversaciones"""
    
    def __init__(self, openai_client: OpenAIClient, memory_manager: LeadMemoryManager):
        self.openai_client = openai_client
        self.memory_manager = memory_manager
        self.logger = logger
        
        # Modelos predictivos basados en reglas (se pueden mejorar con ML)
        self.prediction_models = {
            "abandonment": self._predict_abandonment,
            "optimal_sale_timing": self._predict_optimal_sale_timing,
            "purchase_patterns": self._analyze_purchase_patterns,
            "follow_up_timing": self._predict_follow_up_timing,
            "message_optimization": self._predict_message_optimization
        }
        
        # Factores de riesgo de abandono
        self.abandonment_factors = {
            "response_delay": {"weight": 0.3, "threshold": 300},  # 5 min
            "negative_emotions": {"weight": 0.25, "threshold": 2},
            "question_repetition": {"weight": 0.2, "threshold": 3},
            "low_engagement": {"weight": 0.15, "threshold": 0.3},
            "session_duration": {"weight": 0.1, "threshold": 1800}  # 30 min
        }
        
        # Factores de momento óptimo de venta
        self.sale_timing_factors = {
            "positive_emotion_streak": {"weight": 0.3, "min_value": 2},
            "high_engagement": {"weight": 0.25, "min_value": 0.7},
            "purchase_signals": {"weight": 0.2, "min_value": 2},
            "question_to_interest_ratio": {"weight": 0.15, "min_value": 0.6},
            "time_in_funnel": {"weight": 0.1, "optimal_range": (2, 7)}  # días
        }
    
    async def run_predictive_analysis(self, user_id: str) -> Dict[str, PredictionResult]:
        """
        Ejecuta análisis predictivo completo para un usuario
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Dict con todas las predicciones
        """
        try:
            predictions = {}
            
            # Ejecutar todos los modelos predictivos
            for model_name, model_function in self.prediction_models.items():
                try:
                    prediction = await model_function(user_id)
                    predictions[model_name] = prediction
                except Exception as e:
                    self.logger.error(f"Error en modelo {model_name}: {e}")
                    predictions[model_name] = PredictionResult(
                        prediction_type=model_name,
                        probability=0.5,
                        confidence=0.0,
                        factors=[],
                        recommended_action="continue_normal_flow",
                        timing="immediate",
                        generated_at=datetime.now().isoformat()
                    )
            
            # Guardar predicciones en memoria
            await self._save_predictions_to_memory(user_id, predictions)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error en análisis predictivo: {e}")
            return {}
    
    async def _predict_abandonment(self, user_id: str) -> PredictionResult:
        """Predice probabilidad de abandono de conversación"""
        
        user_data = self._get_user_behavioral_data(user_id)
        
        # Calcular factores de riesgo
        risk_factors = []
        total_risk_score = 0.0
        
        # 1. Delay en respuesta
        last_response_delay = user_data.get("last_response_delay_seconds", 0)
        if last_response_delay > self.abandonment_factors["response_delay"]["threshold"]:
            risk_score = min(1.0, last_response_delay / 600)  # Max a 10 min
            total_risk_score += risk_score * self.abandonment_factors["response_delay"]["weight"]
            risk_factors.append(f"respuesta_demorada_{int(last_response_delay/60)}min")
        
        # 2. Emociones negativas consecutivas
        negative_emotion_count = self._count_recent_negative_emotions(user_data)
        if negative_emotion_count >= self.abandonment_factors["negative_emotions"]["threshold"]:
            risk_score = min(1.0, negative_emotion_count / 5)
            total_risk_score += risk_score * self.abandonment_factors["negative_emotions"]["weight"]
            risk_factors.append(f"emociones_negativas_{negative_emotion_count}")
        
        # 3. Repetición de preguntas
        question_repetition = self._analyze_question_repetition(user_data)
        if question_repetition >= self.abandonment_factors["question_repetition"]["threshold"]:
            risk_score = min(1.0, question_repetition / 5)
            total_risk_score += risk_score * self.abandonment_factors["question_repetition"]["weight"]
            risk_factors.append(f"preguntas_repetitivas_{question_repetition}")
        
        # 4. Bajo engagement
        engagement_score = self._calculate_engagement_score(user_data)
        if engagement_score < self.abandonment_factors["low_engagement"]["threshold"]:
            risk_score = 1.0 - engagement_score
            total_risk_score += risk_score * self.abandonment_factors["low_engagement"]["weight"]
            risk_factors.append(f"bajo_engagement_{engagement_score:.2f}")
        
        # 5. Duración de sesión excesiva
        session_duration = user_data.get("session_duration_seconds", 0)
        if session_duration > self.abandonment_factors["session_duration"]["threshold"]:
            risk_score = min(1.0, session_duration / 3600)  # Max a 1 hora
            total_risk_score += risk_score * self.abandonment_factors["session_duration"]["weight"]
            risk_factors.append(f"sesion_larga_{int(session_duration/60)}min")
        
        # Determinar probabilidad y acción recomendada
        abandonment_probability = min(1.0, total_risk_score)
        
        if abandonment_probability >= 0.7:
            recommended_action = "immediate_intervention"
            timing = "immediate"
        elif abandonment_probability >= 0.5:
            recommended_action = "proactive_engagement"
            timing = "within_5_minutes"
        elif abandonment_probability >= 0.3:
            recommended_action = "gentle_nudge"
            timing = "within_15_minutes"
        else:
            recommended_action = "continue_normal_flow"
            timing = "normal"
        
        confidence = self._calculate_prediction_confidence(risk_factors, user_data)
        
        return PredictionResult(
            prediction_type="abandonment",
            probability=abandonment_probability,
            confidence=confidence,
            factors=risk_factors,
            recommended_action=recommended_action,
            timing=timing,
            generated_at=datetime.now().isoformat()
        )
    
    async def _predict_optimal_sale_timing(self, user_id: str) -> PredictionResult:
        """Predice el momento óptimo para presentar oferta de venta"""
        
        user_data = self._get_user_behavioral_data(user_id)
        
        # Calcular factores positivos para venta
        positive_factors = []
        total_readiness_score = 0.0
        
        # 1. Racha de emociones positivas
        positive_streak = self._count_positive_emotion_streak(user_data)
        if positive_streak >= self.sale_timing_factors["positive_emotion_streak"]["min_value"]:
            factor_score = min(1.0, positive_streak / 5)
            total_readiness_score += factor_score * self.sale_timing_factors["positive_emotion_streak"]["weight"]
            positive_factors.append(f"emociones_positivas_{positive_streak}")
        
        # 2. Alto engagement
        engagement_score = self._calculate_engagement_score(user_data)
        if engagement_score >= self.sale_timing_factors["high_engagement"]["min_value"]:
            factor_score = engagement_score
            total_readiness_score += factor_score * self.sale_timing_factors["high_engagement"]["weight"]
            positive_factors.append(f"alto_engagement_{engagement_score:.2f}")
        
        # 3. Señales de compra
        purchase_signals = user_data.get("purchase_signals_count", 0)
        if purchase_signals >= self.sale_timing_factors["purchase_signals"]["min_value"]:
            factor_score = min(1.0, purchase_signals / 5)
            total_readiness_score += factor_score * self.sale_timing_factors["purchase_signals"]["weight"]
            positive_factors.append(f"señales_compra_{purchase_signals}")
        
        # 4. Ratio preguntas/interés
        question_interest_ratio = self._calculate_question_interest_ratio(user_data)
        if question_interest_ratio >= self.sale_timing_factors["question_to_interest_ratio"]["min_value"]:
            factor_score = question_interest_ratio
            total_readiness_score += factor_score * self.sale_timing_factors["question_to_interest_ratio"]["weight"]
            positive_factors.append(f"ratio_interes_{question_interest_ratio:.2f}")
        
        # 5. Tiempo en funnel óptimo
        days_in_funnel = user_data.get("days_in_funnel", 0)
        optimal_range = self.sale_timing_factors["time_in_funnel"]["optimal_range"]
        if optimal_range[0] <= days_in_funnel <= optimal_range[1]:
            factor_score = 1.0 - abs(days_in_funnel - np.mean(optimal_range)) / optimal_range[1]
            total_readiness_score += factor_score * self.sale_timing_factors["time_in_funnel"]["weight"]
            positive_factors.append(f"timing_optimo_{days_in_funnel}dias")
        
        # Determinar momento óptimo
        sale_readiness = min(1.0, total_readiness_score)
        
        if sale_readiness >= 0.8:
            recommended_action = "present_premium_offer"
            timing = "immediate"
        elif sale_readiness >= 0.6:
            recommended_action = "present_standard_offer"
            timing = "within_1_hour"
        elif sale_readiness >= 0.4:
            recommended_action = "warm_up_for_sale"
            timing = "within_24_hours"
        else:
            recommended_action = "continue_nurturing"
            timing = "wait_for_signals"
        
        confidence = self._calculate_prediction_confidence(positive_factors, user_data)
        
        return PredictionResult(
            prediction_type="optimal_sale_timing",
            probability=sale_readiness,
            confidence=confidence,
            factors=positive_factors,
            recommended_action=recommended_action,
            timing=timing,
            generated_at=datetime.now().isoformat()
        )
    
    async def _analyze_purchase_patterns(self, user_id: str) -> PredictionResult:
        """Analiza patrones de compra del usuario"""
        
        user_data = self._get_user_behavioral_data(user_id)
        
        # Analizar patrones específicos
        patterns = []
        pattern_strength = 0.0
        
        # 1. Patrón de investigación previa
        research_intensity = self._calculate_research_intensity(user_data)
        if research_intensity > 0.7:
            patterns.append("investigador_intensivo")
            pattern_strength += 0.3
        
        # 2. Patrón de decisión rápida
        decision_speed = self._calculate_decision_speed(user_data)
        if decision_speed > 0.8:
            patterns.append("decision_rapida")
            pattern_strength += 0.25
        elif decision_speed < 0.3:
            patterns.append("decision_lenta")
            pattern_strength += 0.2
        
        # 3. Patrón de sensibilidad al precio
        price_sensitivity = self._analyze_price_sensitivity(user_data)
        if price_sensitivity > 0.7:
            patterns.append("sensible_precio")
            pattern_strength += 0.2
        
        # 4. Patrón de búsqueda de validación social
        social_validation = self._analyze_social_validation_seeking(user_data)
        if social_validation > 0.6:
            patterns.append("busca_validacion")
            pattern_strength += 0.15
        
        # 5. Patrón de urgencia
        urgency_pattern = self._analyze_urgency_pattern(user_data)
        if urgency_pattern > 0.5:
            patterns.append("urgencia_alta")
            pattern_strength += 0.1
        
        # Determinar acción recomendada basada en patrones
        if "investigador_intensivo" in patterns:
            recommended_action = "provide_detailed_information"
        elif "decision_rapida" in patterns:
            recommended_action = "present_immediate_offer"
        elif "sensible_precio" in patterns:
            recommended_action = "emphasize_value_and_roi"
        elif "busca_validacion" in patterns:
            recommended_action = "show_social_proof"
        else:
            recommended_action = "balanced_approach"
        
        confidence = min(0.9, pattern_strength + 0.1)
        
        return PredictionResult(
            prediction_type="purchase_patterns",
            probability=pattern_strength,
            confidence=confidence,
            factors=patterns,
            recommended_action=recommended_action,
            timing="immediate",
            generated_at=datetime.now().isoformat()
        )
    
    async def _predict_follow_up_timing(self, user_id: str) -> PredictionResult:
        """Predice el timing óptimo para follow-up"""
        
        user_data = self._get_user_behavioral_data(user_id)
        
        # Factores para timing de follow-up
        timing_factors = []
        timing_score = 0.0
        
        # 1. Último engagement del usuario
        last_interaction_hours = user_data.get("hours_since_last_interaction", 0)
        
        if last_interaction_hours < 2:
            timing_score += 0.1
            timing_factors.append("interaccion_reciente")
            recommended_timing = "wait_2_hours"
        elif 2 <= last_interaction_hours <= 24:
            timing_score += 0.8
            timing_factors.append("timing_optimo")
            recommended_timing = "immediate"
        elif 24 < last_interaction_hours <= 72:
            timing_score += 0.6
            timing_factors.append("reactivacion_necesaria")
            recommended_timing = "immediate"
        else:
            timing_score += 0.3
            timing_factors.append("reengagement_critico")
            recommended_timing = "immediate"
        
        # 2. Día de la semana y hora
        current_time = datetime.now()
        weekday = current_time.weekday()  # 0=Monday, 6=Sunday
        hour = current_time.hour
        
        # Horario business optimal (9-18, Lunes-Viernes)
        if 0 <= weekday <= 4 and 9 <= hour <= 18:
            timing_score += 0.3
            timing_factors.append("horario_business")
        elif 0 <= weekday <= 4 and (19 <= hour <= 21):
            timing_score += 0.2
            timing_factors.append("horario_tarde")
        else:
            timing_score += 0.1
            timing_factors.append("horario_suboptimo")
        
        # 3. Historial de respuesta del usuario
        response_pattern = self._analyze_user_response_pattern(user_data)
        if response_pattern.get("responsive_to_followup", False):
            timing_score += 0.2
            timing_factors.append("responsive_seguimiento")
        
        # 4. Etapa del funnel
        funnel_stage = user_data.get("funnel_stage", "awareness")
        if funnel_stage in ["consideration", "intent"]:
            timing_score += 0.2
            timing_factors.append("etapa_avanzada")
        
        # Determinar acción específica
        if timing_score >= 0.8:
            recommended_action = "immediate_personalized_followup"
        elif timing_score >= 0.6:
            recommended_action = "scheduled_followup"
        elif timing_score >= 0.4:
            recommended_action = "gentle_check_in"
        else:
            recommended_action = "wait_for_better_timing"
        
        confidence = min(0.9, timing_score)
        
        return PredictionResult(
            prediction_type="follow_up_timing",
            probability=timing_score,
            confidence=confidence,
            factors=timing_factors,
            recommended_action=recommended_action,
            timing=recommended_timing,
            generated_at=datetime.now().isoformat()
        )
    
    async def _predict_message_optimization(self, user_id: str) -> PredictionResult:
        """Predice optimizaciones para mensajes futuros"""
        
        user_data = self._get_user_behavioral_data(user_id)
        
        # Analizar preferencias de comunicación
        optimization_factors = []
        optimization_score = 0.0
        
        # 1. Análisis de longitud de mensaje preferida
        preferred_length = self._analyze_preferred_message_length(user_data)
        optimization_factors.append(f"longitud_preferida_{preferred_length}")
        
        # 2. Análisis de tono efectivo
        effective_tone = self._analyze_effective_tone(user_data)
        optimization_factors.append(f"tono_efectivo_{effective_tone}")
        
        # 3. Análisis de timing de respuesta
        response_timing = self._analyze_response_timing_effectiveness(user_data)
        optimization_factors.append(f"timing_efectivo_{response_timing}")
        
        # 4. Análisis de tipo de contenido que funciona
        effective_content = self._analyze_effective_content_types(user_data)
        optimization_factors.extend(effective_content)
        
        # Calcular score de optimización
        optimization_score = len(optimization_factors) * 0.2
        
        # Determinar recomendaciones específicas
        recommendations = []
        if preferred_length == "short":
            recommendations.append("usar_mensajes_concisos")
        elif preferred_length == "long":
            recommendations.append("proporcionar_detalles_completos")
        
        if effective_tone == "formal":
            recommendations.append("mantener_tono_profesional")
        elif effective_tone == "casual":
            recommendations.append("usar_tono_conversacional")
        
        recommended_action = "optimize_" + "_".join(recommendations[:2])
        
        confidence = min(0.8, optimization_score)
        
        return PredictionResult(
            prediction_type="message_optimization",
            probability=optimization_score,
            confidence=confidence,
            factors=optimization_factors,
            recommended_action=recommended_action,
            timing="apply_to_next_message",
            generated_at=datetime.now().isoformat()
        )
    
    # Métodos auxiliares para cálculos específicos
    
    def _get_user_behavioral_data(self, user_id: str) -> Dict:
        """Obtiene datos comportamentales del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            # Calcular métricas derivadas
            now = datetime.now()
            
            # Tiempo desde última interacción
            last_interaction = getattr(user_memory, 'last_interaction', None)
            hours_since_last = 0
            if last_interaction:
                last_time = datetime.fromisoformat(last_interaction)
                hours_since_last = (now - last_time).total_seconds() / 3600
            
            # Días en funnel
            first_interaction = getattr(user_memory, 'first_interaction', None)
            days_in_funnel = 0
            if first_interaction:
                first_time = datetime.fromisoformat(first_interaction)
                days_in_funnel = (now - first_time).days
            
            return {
                "user_id": user_id,
                "interaction_count": getattr(user_memory, 'interaction_count', 0),
                "lead_score": getattr(user_memory, 'lead_score', 0),
                "current_emotion": getattr(user_memory, 'current_emotion', 'neutral'),
                "emotion_history": getattr(user_memory, 'emotion_history', []),
                "message_history": getattr(user_memory, 'message_history', []),
                "buyer_persona": getattr(user_memory, 'buyer_persona_match', 'unknown'),
                "purchase_signals_count": getattr(user_memory, 'purchase_signals', 0),
                "hours_since_last_interaction": hours_since_last,
                "days_in_funnel": days_in_funnel,
                "session_duration_seconds": self._calculate_session_duration(user_memory),
                "last_response_delay_seconds": self._calculate_last_response_delay(user_memory),
                "funnel_stage": getattr(user_memory, 'stage', 'first_contact'),
                "conversation_history": getattr(user_memory, 'conversation_history', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos comportamentales: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    def _count_recent_negative_emotions(self, user_data: Dict) -> int:
        """Cuenta emociones negativas recientes"""
        emotion_history = user_data.get("emotion_history", [])
        negative_emotions = {"frustrado", "escéptico"}
        
        count = 0
        for emotion_entry in emotion_history[-5:]:  # Últimas 5 emociones
            if emotion_entry.get("emotion") in negative_emotions:
                count += 1
        
        return count
    
    def _count_positive_emotion_streak(self, user_data: Dict) -> int:
        """Cuenta racha de emociones positivas"""
        emotion_history = user_data.get("emotion_history", [])
        positive_emotions = {"emocionado", "curioso", "decidido"}
        
        streak = 0
        for emotion_entry in reversed(emotion_history[-10:]):  # Últimas 10, en reversa
            if emotion_entry.get("emotion") in positive_emotions:
                streak += 1
            else:
                break
        
        return streak
    
    def _analyze_question_repetition(self, user_data: Dict) -> int:
        """Analiza repetición de preguntas"""
        message_history = user_data.get("message_history", [])
        
        questions = []
        for message in message_history[-10:]:  # Últimos 10 mensajes
            if "?" in message or any(word in message.lower() for word in ["cuanto", "cuando", "como", "donde", "que"]):
                # Extraer keywords principales
                words = set(word.lower() for word in message.split() if len(word) > 3)
                questions.append(words)
        
        # Buscar similitudes
        repetitions = 0
        for i in range(len(questions)):
            for j in range(i + 1, len(questions)):
                if len(questions[i] & questions[j]) >= 2:  # Al menos 2 palabras comunes
                    repetitions += 1
        
        return repetitions
    
    def _calculate_engagement_score(self, user_data: Dict) -> float:
        """Calcula score de engagement"""
        interaction_count = user_data.get("interaction_count", 0)
        days_in_funnel = max(1, user_data.get("days_in_funnel", 1))
        
        # Interacciones por día
        interactions_per_day = interaction_count / days_in_funnel
        
        # Normalizar a 0-1
        engagement_score = min(1.0, interactions_per_day / 5)  # 5 interacciones/día = máximo
        
        return engagement_score
    
    def _calculate_question_interest_ratio(self, user_data: Dict) -> float:
        """Calcula ratio de preguntas vs interés mostrado"""
        message_history = user_data.get("message_history", [])
        
        if not message_history:
            return 0.0
        
        question_count = 0
        interest_signals = 0
        
        interest_keywords = ["interesante", "me gusta", "perfecto", "excelente", "quiero", "necesito"]
        
        for message in message_history:
            message_lower = message.lower()
            if "?" in message or any(word in message_lower for word in ["cuanto", "cuando", "como"]):
                question_count += 1
            
            if any(keyword in message_lower for keyword in interest_keywords):
                interest_signals += 1
        
        if question_count == 0:
            return 0.0
        
        return min(1.0, interest_signals / question_count)
    
    def _calculate_research_intensity(self, user_data: Dict) -> float:
        """Calcula intensidad de investigación"""
        interaction_count = user_data.get("interaction_count", 0)
        days_in_funnel = max(1, user_data.get("days_in_funnel", 1))
        
        # Muchas interacciones en poco tiempo = investigación intensiva
        intensity = (interaction_count / days_in_funnel) / 10  # Normalizar
        
        return min(1.0, intensity)
    
    def _calculate_decision_speed(self, user_data: Dict) -> float:
        """Calcula velocidad de decisión"""
        days_in_funnel = user_data.get("days_in_funnel", 0)
        purchase_signals = user_data.get("purchase_signals_count", 0)
        
        if purchase_signals == 0:
            return 0.0
        
        # Señales de compra rápidas = decisión rápida
        speed = purchase_signals / max(1, days_in_funnel)
        
        return min(1.0, speed)
    
    def _analyze_price_sensitivity(self, user_data: Dict) -> float:
        """Analiza sensibilidad al precio"""
        message_history = user_data.get("message_history", [])
        
        price_mentions = 0
        total_messages = len(message_history)
        
        price_keywords = ["precio", "costo", "caro", "barato", "descuento", "oferta"]
        
        for message in message_history:
            if any(keyword in message.lower() for keyword in price_keywords):
                price_mentions += 1
        
        if total_messages == 0:
            return 0.0
        
        return min(1.0, price_mentions / total_messages * 2)  # Amplificar
    
    def _analyze_social_validation_seeking(self, user_data: Dict) -> float:
        """Analiza búsqueda de validación social"""
        message_history = user_data.get("message_history", [])
        
        validation_mentions = 0
        total_messages = len(message_history)
        
        validation_keywords = ["testimonios", "referencias", "casos", "otros clientes", "experiencias", "recomendaciones"]
        
        for message in message_history:
            if any(keyword in message.lower() for keyword in validation_keywords):
                validation_mentions += 1
        
        if total_messages == 0:
            return 0.0
        
        return min(1.0, validation_mentions / total_messages * 3)  # Amplificar más
    
    def _analyze_urgency_pattern(self, user_data: Dict) -> float:
        """Analiza patrones de urgencia"""
        message_history = user_data.get("message_history", [])
        
        urgency_mentions = 0
        total_messages = len(message_history)
        
        urgency_keywords = ["urgente", "rápido", "pronto", "ya", "inmediato", "cuando puedo empezar"]
        
        for message in message_history:
            if any(keyword in message.lower() for keyword in urgency_keywords):
                urgency_mentions += 1
        
        if total_messages == 0:
            return 0.0
        
        return min(1.0, urgency_mentions / total_messages * 4)  # Mayor amplificación
    
    def _analyze_user_response_pattern(self, user_data: Dict) -> Dict:
        """Analiza patrones de respuesta del usuario"""
        # Análisis simplificado - se puede expandir con datos históricos
        interaction_count = user_data.get("interaction_count", 0)
        
        return {
            "responsive_to_followup": interaction_count > 5,
            "average_response_time": "medium",
            "preferred_communication_frequency": "daily"
        }
    
    def _analyze_preferred_message_length(self, user_data: Dict) -> str:
        """Analiza longitud de mensaje preferida"""
        message_history = user_data.get("message_history", [])
        
        if not message_history:
            return "medium"
        
        # Analizar longitud promedio de mensajes del usuario
        avg_length = sum(len(msg) for msg in message_history) / len(message_history)
        
        if avg_length < 50:
            return "short"
        elif avg_length > 150:
            return "long"
        else:
            return "medium"
    
    def _analyze_effective_tone(self, user_data: Dict) -> str:
        """Analiza tono efectivo para el usuario"""
        buyer_persona = user_data.get("buyer_persona", "unknown")
        
        # Mapeo simple por buyer persona
        if buyer_persona in ["sofia_visionaria", "daniel_data_innovador"]:
            return "formal"
        elif buyer_persona in ["lucia_copypro", "marcos_multitask"]:
            return "casual"
        else:
            return "professional"
    
    def _analyze_response_timing_effectiveness(self, user_data: Dict) -> str:
        """Analiza efectividad del timing de respuesta"""
        hours_since_last = user_data.get("hours_since_last_interaction", 0)
        
        if hours_since_last < 1:
            return "immediate"
        elif hours_since_last < 24:
            return "same_day"
        else:
            return "delayed"
    
    def _analyze_effective_content_types(self, user_data: Dict) -> List[str]:
        """Analiza tipos de contenido efectivos"""
        content_types = []
        
        # Basado en buyer persona y comportamiento
        buyer_persona = user_data.get("buyer_persona", "unknown")
        interaction_count = user_data.get("interaction_count", 0)
        
        if buyer_persona == "daniel_data_innovador":
            content_types.extend(["datos_estadisticos", "casos_tecnicos"])
        elif buyer_persona == "sofia_visionaria":
            content_types.extend(["vision_estrategica", "roi_executive"])
        elif interaction_count > 8:
            content_types.extend(["contenido_detallado", "casos_profundos"])
        else:
            content_types.extend(["contenido_visual", "ejemplos_simples"])
        
        return content_types
    
    def _calculate_session_duration(self, user_memory) -> int:
        """Calcula duración de sesión en segundos"""
        try:
            first_interaction = getattr(user_memory, 'first_interaction', None)
            last_interaction = getattr(user_memory, 'last_interaction', None)
            
            if not first_interaction or not last_interaction:
                return 0
            
            start_time = datetime.fromisoformat(first_interaction)
            end_time = datetime.fromisoformat(last_interaction)
            
            duration = (end_time - start_time).total_seconds()
            return int(duration)
            
        except:
            return 0
    
    def _calculate_last_response_delay(self, user_memory) -> int:
        """Calcula delay de última respuesta en segundos"""
        try:
            last_interaction = getattr(user_memory, 'last_interaction', None)
            
            if not last_interaction:
                return 0
            
            last_time = datetime.fromisoformat(last_interaction)
            delay = (datetime.now() - last_time).total_seconds()
            
            return int(delay)
            
        except:
            return 0
    
    def _calculate_prediction_confidence(self, factors: List[str], user_data: Dict) -> float:
        """Calcula confianza en la predicción"""
        base_confidence = 0.5
        
        # Más factores = mayor confianza
        factor_bonus = min(0.3, len(factors) * 0.1)
        
        # Más datos = mayor confianza
        interaction_bonus = min(0.2, user_data.get("interaction_count", 0) * 0.02)
        
        total_confidence = base_confidence + factor_bonus + interaction_bonus
        
        return min(0.95, total_confidence)
    
    async def _save_predictions_to_memory(self, user_id: str, predictions: Dict[str, PredictionResult]):
        """Guarda predicciones en memoria del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            if not hasattr(user_memory, 'prediction_history'):
                user_memory.prediction_history = []
            
            # Convertir predicciones a dict para guardado
            prediction_entry = {
                "predictions": {
                    name: {
                        "type": pred.prediction_type,
                        "probability": pred.probability,
                        "confidence": pred.confidence,
                        "factors": pred.factors,
                        "recommended_action": pred.recommended_action,
                        "timing": pred.timing,
                        "generated_at": pred.generated_at
                    }
                    for name, pred in predictions.items()
                },
                "generated_at": datetime.now().isoformat()
            }
            
            user_memory.prediction_history.append(prediction_entry)
            
            # Mantener solo las últimas 10 predicciones
            if len(user_memory.prediction_history) > 10:
                user_memory.prediction_history = user_memory.prediction_history[-10:]
            
            # Actualizar predicciones actuales
            user_memory.current_predictions = prediction_entry["predictions"]
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error guardando predicciones en memoria: {e}")
    
    def get_prediction_summary(self, user_id: str) -> Dict:
        """Obtiene resumen de predicciones actuales"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            current_predictions = getattr(user_memory, 'current_predictions', {})
            
            summary = {
                "user_id": user_id,
                "total_predictions": len(current_predictions),
                "high_priority_actions": [],
                "immediate_actions": [],
                "prediction_overview": {}
            }
            
            for name, prediction in current_predictions.items():
                # Resumen por predicción
                summary["prediction_overview"][name] = {
                    "probability": prediction.get("probability", 0),
                    "confidence": prediction.get("confidence", 0),
                    "action": prediction.get("recommended_action", ""),
                    "timing": prediction.get("timing", "")
                }
                
                # Acciones de alta prioridad
                if prediction.get("probability", 0) > 0.7:
                    summary["high_priority_actions"].append({
                        "type": name,
                        "action": prediction.get("recommended_action", ""),
                        "probability": prediction.get("probability", 0)
                    })
                
                # Acciones inmediatas
                if prediction.get("timing") in ["immediate", "within_5_minutes"]:
                    summary["immediate_actions"].append({
                        "type": name,
                        "action": prediction.get("recommended_action", ""),
                        "timing": prediction.get("timing", "")
                    })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de predicciones: {e}")
            return {"user_id": user_id, "error": str(e)}