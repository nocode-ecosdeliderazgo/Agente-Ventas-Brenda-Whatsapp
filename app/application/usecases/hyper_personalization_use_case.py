"""
Sistema de Personalización Hiper-avanzada
Perfiles detallados, adaptación de tono, contenido dinámico y A/B testing
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import random
from dataclasses import dataclass, asdict

from app.infrastructure.openai.client import OpenAIClient
from memory.lead_memory import LeadMemoryManager

logger = logging.getLogger(__name__)

@dataclass
class PersonalityProfile:
    """Perfil de personalidad del usuario"""
    communication_style: str  # direct, analytical, expressive, amiable
    decision_making_style: str  # quick, methodical, consensus, spontaneous
    information_preference: str  # detailed, summary, visual, social_proof
    risk_tolerance: str  # high, medium, low
    authority_orientation: str  # autonomous, collaborative, hierarchical
    confidence_score: float

@dataclass
class ABTestVariant:
    """Variante de A/B test"""
    variant_id: str
    message_type: str
    content: str
    tone: str
    length: str
    call_to_action: str
    created_at: str

@dataclass
class ConversionOptimization:
    """Optimización de conversión"""
    optimization_type: str
    current_performance: float
    target_performance: float
    recommended_changes: List[str]
    test_duration_days: int
    confidence_level: float

class HyperPersonalizationUseCase:
    """Sistema de personalización hiper-avanzada"""
    
    def __init__(self, openai_client: OpenAIClient, memory_manager: LeadMemoryManager):
        self.openai_client = openai_client
        self.memory_manager = memory_manager
        self.logger = logger
        
        # Perfiles de personalidad predefinidos
        self.personality_profiles = {
            "analytical_executive": PersonalityProfile(
                communication_style="analytical",
                decision_making_style="methodical",
                information_preference="detailed",
                risk_tolerance="medium",
                authority_orientation="autonomous",
                confidence_score=0.85
            ),
            "decisive_leader": PersonalityProfile(
                communication_style="direct",
                decision_making_style="quick",
                information_preference="summary",
                risk_tolerance="high",
                authority_orientation="autonomous",
                confidence_score=0.90
            ),
            "collaborative_manager": PersonalityProfile(
                communication_style="amiable",
                decision_making_style="consensus",
                information_preference="social_proof",
                risk_tolerance="medium",
                authority_orientation="collaborative",
                confidence_score=0.80
            ),
            "detail_oriented_specialist": PersonalityProfile(
                communication_style="analytical",
                decision_making_style="methodical",
                information_preference="detailed",
                risk_tolerance="low",
                authority_orientation="hierarchical",
                confidence_score=0.75
            ),
            "innovative_visionary": PersonalityProfile(
                communication_style="expressive",
                decision_making_style="spontaneous",
                information_preference="visual",
                risk_tolerance="high",
                authority_orientation="autonomous",
                confidence_score=0.88
            )
        }
        
        # Plantillas de mensajes por estilo
        self.message_templates = {
            "direct": {
                "greeting": "Vamos directo al punto:",
                "value_prop": "Te ahorro tiempo: esto te da {benefit} en {timeframe}.",
                "cta": "¿Decidimos ahora?",
                "objection": "Entiendo tu punto. La realidad es:"
            },
            "analytical": {
                "greeting": "Basándome en tu perfil empresarial:",
                "value_prop": "Los datos muestran que obtendrás {benefit} con un ROI de {roi}% en {timeframe}.",
                "cta": "¿Revisamos los números juntos?",
                "objection": "Analicemos esto paso a paso:"
            },
            "expressive": {
                "greeting": "¡Esto es emocionante para tu empresa!",
                "value_prop": "Imagínate: {benefit} transformando completamente tu operación en solo {timeframe}.",
                "cta": "¿Te sumas a esta transformación?",
                "objection": "Entiendo perfectamente tu preocupación:"
            },
            "amiable": {
                "greeting": "Me da mucho gusto poder ayudarte:",
                "value_prop": "Muchos líderes como tú han logrado {benefit} en aproximadamente {timeframe}.",
                "cta": "¿Te gustaría que conversemos más sobre esto?",
                "objection": "Claro, es completamente normal pensar en eso:"
            }
        }
        
        # Sistema de A/B testing
        self.ab_test_active = {}
        self.conversion_metrics = {}
    
    async def create_detailed_behavioral_profile(self, user_id: str) -> Dict:
        """
        Crea perfil comportamental detallado del usuario
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Dict con perfil comportamental completo
        """
        try:
            # 1. Obtener datos comportamentales
            behavioral_data = await self._gather_behavioral_data(user_id)
            
            # 2. Analizar personalidad con IA
            personality_analysis = await self._analyze_personality_with_ai(
                user_id, behavioral_data
            )
            
            # 3. Mapear a perfil de personalidad
            personality_profile = self._map_to_personality_profile(personality_analysis)
            
            # 4. Analizar patrones de comunicación
            communication_patterns = self._analyze_communication_patterns(behavioral_data)
            
            # 5. Identificar preferencias de contenido
            content_preferences = self._identify_content_preferences(behavioral_data)
            
            # 6. Calcular score de engagement personalizado
            engagement_score = self._calculate_personalized_engagement_score(
                behavioral_data, personality_profile
            )
            
            # 7. Crear perfil completo
            detailed_profile = {
                "user_id": user_id,
                "personality_profile": asdict(personality_profile),
                "communication_patterns": communication_patterns,
                "content_preferences": content_preferences,
                "engagement_score": engagement_score,
                "behavioral_insights": personality_analysis,
                "created_at": datetime.now().isoformat(),
                "confidence_level": personality_profile.confidence_score
            }
            
            # 8. Guardar perfil en memoria
            await self._save_behavioral_profile(user_id, detailed_profile)
            
            return detailed_profile
            
        except Exception as e:
            self.logger.error(f"Error creando perfil comportamental: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    async def adapt_tone_dynamically(self, user_id: str, message_content: str, context: Dict) -> str:
        """
        Adapta el tono del mensaje según la personalidad del usuario
        
        Args:
            user_id: ID del usuario
            message_content: Contenido del mensaje original
            context: Contexto adicional
        
        Returns:
            Mensaje adaptado al tono personal
        """
        try:
            # 1. Obtener perfil de personalidad
            profile = await self._get_user_personality_profile(user_id)
            
            # 2. Determinar estilo de comunicación apropiado
            communication_style = profile.get("communication_style", "analytical")
            
            # 3. Adaptar mensaje usando plantillas
            adapted_message = await self._adapt_message_to_style(
                message_content, communication_style, context
            )
            
            # 4. Ajustar según contexto emocional
            emotional_context = context.get("current_emotion", "neutral")
            final_message = self._adjust_for_emotional_context(
                adapted_message, emotional_context, communication_style
            )
            
            # 5. Registrar adaptación para aprendizaje
            await self._log_tone_adaptation(user_id, {
                "original_message": message_content,
                "adapted_message": final_message,
                "style_used": communication_style,
                "emotional_context": emotional_context,
                "timestamp": datetime.now().isoformat()
            })
            
            return final_message
            
        except Exception as e:
            self.logger.error(f"Error adaptando tono: {e}")
            return message_content  # Fallback al mensaje original
    
    async def generate_dynamic_content(self, user_id: str, content_type: str, context: Dict) -> Dict:
        """
        Genera contenido dinámico según el contexto del usuario
        
        Args:
            user_id: ID del usuario
            content_type: Tipo de contenido (offer, explanation, objection_handling, etc.)
            context: Contexto actual
        
        Returns:
            Dict con contenido personalizado
        """
        try:
            # 1. Obtener perfil y preferencias
            profile = await self._get_user_personality_profile(user_id)
            preferences = await self._get_content_preferences(user_id)
            
            # 2. Generar contenido base
            base_content = await self._generate_base_content(content_type, context)
            
            # 3. Personalizar según perfil
            personalized_content = await self._personalize_content_for_profile(
                base_content, profile, preferences
            )
            
            # 4. Adaptar según historial de respuesta
            response_history = await self._analyze_response_history(user_id)
            optimized_content = await self._optimize_content_based_on_history(
                personalized_content, response_history
            )
            
            # 5. Agregar elementos dinámicos específicos
            dynamic_elements = await self._add_dynamic_elements(
                user_id, optimized_content, context
            )
            
            return {
                "content_type": content_type,
                "personalized_content": dynamic_elements,
                "personalization_factors": {
                    "personality_style": profile.get("communication_style"),
                    "information_preference": profile.get("information_preference"),
                    "decision_style": profile.get("decision_making_style"),
                    "risk_tolerance": profile.get("risk_tolerance")
                },
                "optimization_applied": True,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generando contenido dinámico: {e}")
            return {"content_type": content_type, "error": str(e)}
    
    async def run_ab_test_message(self, user_id: str, message_type: str, context: Dict) -> Dict:
        """
        Ejecuta A/B testing automático de mensajes
        
        Args:
            user_id: ID del usuario
            message_type: Tipo de mensaje a testear
            context: Contexto actual
        
        Returns:
            Dict con variante seleccionada y datos del test
        """
        try:
            # 1. Verificar si hay test activo para este tipo de mensaje
            active_test = self._get_active_ab_test(message_type)
            
            # 2. Si no hay test activo, crear uno nuevo
            if not active_test:
                active_test = await self._create_new_ab_test(message_type, context)
            
            # 3. Seleccionar variante para este usuario
            selected_variant = await self._select_variant_for_user(
                user_id, active_test, context
            )
            
            # 4. Generar mensaje según variante
            test_message = await self._generate_message_from_variant(
                selected_variant, context
            )
            
            # 5. Registrar exposición al test
            await self._log_ab_test_exposure(user_id, active_test, selected_variant)
            
            return {
                "test_id": active_test["test_id"],
                "variant_id": selected_variant["variant_id"],
                "message": test_message,
                "test_type": message_type,
                "expected_metric": active_test["primary_metric"],
                "user_segment": self._classify_user_segment(user_id),
                "exposure_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error en A/B testing: {e}")
            # Fallback a mensaje estándar
            return await self.generate_dynamic_content(user_id, message_type, context)
    
    async def optimize_conversion_continuously(self, user_id: str) -> ConversionOptimization:
        """
        Optimiza conversiones de forma continua basada en datos históricos
        
        Args:
            user_id: ID del usuario
        
        Returns:
            ConversionOptimization con recomendaciones
        """
        try:
            # 1. Analizar performance actual
            current_performance = await self._analyze_current_performance(user_id)
            
            # 2. Identificar oportunidades de mejora
            improvement_opportunities = await self._identify_improvement_opportunities(
                user_id, current_performance
            )
            
            # 3. Calcular performance objetivo
            target_performance = self._calculate_target_performance(
                current_performance, improvement_opportunities
            )
            
            # 4. Generar recomendaciones específicas
            recommendations = await self._generate_conversion_recommendations(
                user_id, current_performance, improvement_opportunities
            )
            
            # 5. Estimar duración y confianza del test
            test_params = self._calculate_test_parameters(
                current_performance, target_performance
            )
            
            optimization = ConversionOptimization(
                optimization_type="continuous_improvement",
                current_performance=current_performance["conversion_rate"],
                target_performance=target_performance,
                recommended_changes=recommendations,
                test_duration_days=test_params["duration_days"],
                confidence_level=test_params["confidence_level"]
            )
            
            # 6. Guardar optimización en memoria
            await self._save_conversion_optimization(user_id, optimization)
            
            return optimization
            
        except Exception as e:
            self.logger.error(f"Error en optimización continua: {e}")
            return ConversionOptimization(
                optimization_type="fallback",
                current_performance=0.1,
                target_performance=0.15,
                recommended_changes=["continue_current_approach"],
                test_duration_days=7,
                confidence_level=0.5
            )
    
    # Métodos auxiliares privados
    
    async def _gather_behavioral_data(self, user_id: str) -> Dict:
        """Recopila datos comportamentales del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            return {
                "message_history": getattr(user_memory, 'message_history', []),
                "emotion_history": getattr(user_memory, 'emotion_history', []),
                "interaction_patterns": getattr(user_memory, 'interaction_patterns', {}),
                "response_times": self._calculate_response_times(user_memory),
                "engagement_metrics": self._calculate_engagement_metrics(user_memory),
                "decision_indicators": self._extract_decision_indicators(user_memory),
                "communication_preferences": self._analyze_communication_preferences(user_memory)
            }
            
        except Exception as e:
            self.logger.error(f"Error recopilando datos comportamentales: {e}")
            return {}
    
    async def _analyze_personality_with_ai(self, user_id: str, behavioral_data: Dict) -> Dict:
        """Analiza personalidad usando IA"""
        try:
            # Preparar datos para análisis
            message_sample = behavioral_data.get("message_history", [])[-10:]  # Últimos 10
            emotion_pattern = behavioral_data.get("emotion_history", [])[-5:]   # Últimas 5
            
            prompt = f"""Analiza la personalidad y estilo de comunicación de este usuario empresarial basándote en sus mensajes y patrones emocionales:

MENSAJES DEL USUARIO:
{json.dumps(message_sample, indent=2)}

PATRONES EMOCIONALES:
{json.dumps(emotion_pattern, indent=2)}

MÉTRICAS DE ENGAGEMENT:
{json.dumps(behavioral_data.get("engagement_metrics", {}), indent=2)}

Clasifica al usuario en estas dimensiones:

1. ESTILO DE COMUNICACIÓN:
   - direct (directo, sin rodeos)
   - analytical (analítico, basado en datos)
   - expressive (expresivo, emocional)
   - amiable (amigable, colaborativo)

2. ESTILO DE TOMA DE DECISIONES:
   - quick (rápido, intuitivo)
   - methodical (metódico, paso a paso)
   - consensus (busca consenso)
   - spontaneous (espontáneo)

3. PREFERENCIA DE INFORMACIÓN:
   - detailed (información detallada)
   - summary (resúmenes ejecutivos)
   - visual (gráficos, imágenes)
   - social_proof (testimonios, casos)

4. TOLERANCIA AL RIESGO:
   - high (alto, innovador)
   - medium (medio, calculado)
   - low (bajo, conservador)

5. ORIENTACIÓN DE AUTORIDAD:
   - autonomous (toma decisiones solo)
   - collaborative (decide en equipo)
   - hierarchical (consulta superiores)

Responde en formato JSON:
{{
    "communication_style": "analytical",
    "decision_making_style": "methodical",
    "information_preference": "detailed",
    "risk_tolerance": "medium",
    "authority_orientation": "autonomous",
    "confidence_score": 0.85,
    "key_traits": ["detail_oriented", "data_driven", "systematic"],
    "communication_triggers": ["numbers", "proof", "step_by_step"],
    "reasoning": "Explicación breve del análisis"
}}"""

            response = await self.openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis = json.loads(response.get('content', '{}'))
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error en análisis de personalidad con IA: {e}")
            return {
                "communication_style": "analytical",
                "decision_making_style": "methodical",
                "information_preference": "detailed",
                "risk_tolerance": "medium",
                "authority_orientation": "autonomous",
                "confidence_score": 0.5
            }
    
    def _map_to_personality_profile(self, analysis: Dict) -> PersonalityProfile:
        """Mapea análisis a perfil de personalidad"""
        return PersonalityProfile(
            communication_style=analysis.get("communication_style", "analytical"),
            decision_making_style=analysis.get("decision_making_style", "methodical"),
            information_preference=analysis.get("information_preference", "detailed"),
            risk_tolerance=analysis.get("risk_tolerance", "medium"),
            authority_orientation=analysis.get("authority_orientation", "autonomous"),
            confidence_score=analysis.get("confidence_score", 0.5)
        )
    
    def _analyze_communication_patterns(self, behavioral_data: Dict) -> Dict:
        """Analiza patrones de comunicación"""
        message_history = behavioral_data.get("message_history", [])
        
        if not message_history:
            return {"pattern": "insufficient_data"}
        
        patterns = {
            "avg_message_length": sum(len(msg) for msg in message_history) / len(message_history),
            "question_frequency": sum(1 for msg in message_history if "?" in msg) / len(message_history),
            "urgency_indicators": sum(1 for msg in message_history if any(word in msg.lower() for word in ["urgente", "rápido", "ya", "pronto"])),
            "politeness_level": sum(1 for msg in message_history if any(word in msg.lower() for word in ["por favor", "gracias", "disculpe"])) / len(message_history),
            "technical_terms": sum(1 for msg in message_history if any(word in msg.lower() for word in ["api", "sistema", "integración", "automatización"])),
            "decision_language": sum(1 for msg in message_history if any(word in msg.lower() for word in ["decidir", "comprar", "adquirir", "implementar"]))
        }
        
        return patterns
    
    def _identify_content_preferences(self, behavioral_data: Dict) -> Dict:
        """Identifica preferencias de contenido"""
        message_history = behavioral_data.get("message_history", [])
        engagement_metrics = behavioral_data.get("engagement_metrics", {})
        
        preferences = {
            "prefers_detailed_explanations": False,
            "responds_to_social_proof": False,
            "values_data_and_metrics": False,
            "prefers_quick_summaries": False,
            "responds_to_urgency": False
        }
        
        if not message_history:
            return preferences
        
        # Analizar preferencias basadas en patrones de mensaje
        detail_requests = sum(1 for msg in message_history if any(word in msg.lower() for word in ["detalles", "explicar", "cómo funciona", "más información"]))
        preferences["prefers_detailed_explanations"] = detail_requests > len(message_history) * 0.3
        
        social_requests = sum(1 for msg in message_history if any(word in msg.lower() for word in ["testimonios", "casos", "referencias", "otros clientes"]))
        preferences["responds_to_social_proof"] = social_requests > 0
        
        data_requests = sum(1 for msg in message_history if any(word in msg.lower() for word in ["datos", "estadísticas", "números", "roi", "resultados"]))
        preferences["values_data_and_metrics"] = data_requests > len(message_history) * 0.2
        
        urgency_indicators = sum(1 for msg in message_history if any(word in msg.lower() for word in ["urgente", "rápido", "ya", "cuando"]))
        preferences["responds_to_urgency"] = urgency_indicators > len(message_history) * 0.3
        
        # Preferencia por resúmenes si mensajes son cortos
        avg_length = sum(len(msg) for msg in message_history) / len(message_history)
        preferences["prefers_quick_summaries"] = avg_length < 80
        
        return preferences
    
    def _calculate_personalized_engagement_score(self, behavioral_data: Dict, profile: PersonalityProfile) -> float:
        """Calcula score de engagement personalizado"""
        base_engagement = behavioral_data.get("engagement_metrics", {}).get("base_score", 0.5)
        
        # Ajustar según personalidad
        personality_multiplier = 1.0
        
        if profile.communication_style == "expressive":
            personality_multiplier += 0.1  # Más engagement esperado
        elif profile.communication_style == "analytical":
            personality_multiplier += 0.05  # Engagement más medido
        
        if profile.decision_making_style == "quick":
            personality_multiplier += 0.1  # Decisiones rápidas = más engagement
        
        if profile.risk_tolerance == "high":
            personality_multiplier += 0.05  # Mayor disposición a interactuar
        
        personalized_score = min(1.0, base_engagement * personality_multiplier)
        return personalized_score
    
    async def _get_user_personality_profile(self, user_id: str) -> Dict:
        """Obtiene perfil de personalidad del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            stored_profile = getattr(user_memory, 'personality_profile', None)
            
            if stored_profile:
                return stored_profile
            
            # Si no existe, crear uno nuevo
            profile = await self.create_detailed_behavioral_profile(user_id)
            return profile.get("personality_profile", {})
            
        except Exception as e:
            self.logger.error(f"Error obteniendo perfil de personalidad: {e}")
            # Fallback a perfil analítico
            return asdict(self.personality_profiles["analytical_executive"])
    
    async def _adapt_message_to_style(self, message: str, style: str, context: Dict) -> str:
        """Adapta mensaje al estilo de comunicación"""
        try:
            template = self.message_templates.get(style, self.message_templates["analytical"])
            
            # Usar IA para adaptación inteligente
            prompt = f"""Adapta este mensaje al estilo de comunicación '{style}':

MENSAJE ORIGINAL:
{message}

ESTILO OBJETIVO: {style}
CONTEXTO: {json.dumps(context, indent=2)}

PLANTILLAS DE ESTILO:
{json.dumps(template, indent=2)}

Adapta el mensaje manteniendo:
1. El contenido core y la información clave
2. El call-to-action apropiado
3. El tono según el estilo '{style}'

Responde solo con el mensaje adaptado:"""

            response = await self.openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.4
            )
            
            adapted = response.get('content', message).strip()
            return adapted
            
        except Exception as e:
            self.logger.error(f"Error adaptando mensaje: {e}")
            return message
    
    def _adjust_for_emotional_context(self, message: str, emotion: str, style: str) -> str:
        """Ajusta mensaje según contexto emocional"""
        adjustments = {
            "frustrado": {
                "prefix": "Entiendo que esto puede ser confuso. ",
                "tone_modifier": "empático y claro"
            },
            "emocionado": {
                "prefix": "¡Perfecto! ",
                "tone_modifier": "entusiasta"
            },
            "ansioso": {
                "prefix": "Te doy la información clave rápidamente: ",
                "tone_modifier": "directo y eficiente"
            },
            "escéptico": {
                "prefix": "Es completamente normal tener dudas. ",
                "tone_modifier": "basado en evidencia"
            }
        }
        
        adjustment = adjustments.get(emotion, {"prefix": "", "tone_modifier": ""})
        
        if adjustment["prefix"]:
            return adjustment["prefix"] + message
        
        return message
    
    async def _save_behavioral_profile(self, user_id: str, profile: Dict):
        """Guarda perfil comportamental en memoria"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            user_memory.personality_profile = profile
            user_memory.last_profile_update = datetime.now().isoformat()
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error guardando perfil comportamental: {e}")
    
    async def _log_tone_adaptation(self, user_id: str, adaptation_data: Dict):
        """Registra adaptación de tono para aprendizaje"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            if not hasattr(user_memory, 'tone_adaptation_history'):
                user_memory.tone_adaptation_history = []
            
            user_memory.tone_adaptation_history.append(adaptation_data)
            
            # Mantener solo los últimos 20 registros
            if len(user_memory.tone_adaptation_history) > 20:
                user_memory.tone_adaptation_history = user_memory.tone_adaptation_history[-20:]
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error registrando adaptación de tono: {e}")
    
    # Métodos para A/B testing (simplificados)
    
    def _get_active_ab_test(self, message_type: str) -> Optional[Dict]:
        """Obtiene test A/B activo para tipo de mensaje"""
        return self.ab_test_active.get(message_type)
    
    async def _create_new_ab_test(self, message_type: str, context: Dict) -> Dict:
        """Crea nuevo test A/B"""
        test_id = f"ab_test_{message_type}_{int(datetime.now().timestamp())}"
        
        # Crear variantes de test
        variants = await self._generate_test_variants(message_type, context)
        
        new_test = {
            "test_id": test_id,
            "message_type": message_type,
            "variants": variants,
            "primary_metric": "response_rate",
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.ab_test_active[message_type] = new_test
        return new_test
    
    async def _generate_test_variants(self, message_type: str, context: Dict) -> List[ABTestVariant]:
        """Genera variantes para testing"""
        variants = []
        
        # Variante A: Estilo directo
        variants.append(ABTestVariant(
            variant_id="variant_a_direct",
            message_type=message_type,
            content="template_direct",
            tone="direct",
            length="short",
            call_to_action="strong",
            created_at=datetime.now().isoformat()
        ))
        
        # Variante B: Estilo analítico
        variants.append(ABTestVariant(
            variant_id="variant_b_analytical",
            message_type=message_type,
            content="template_analytical",
            tone="analytical",
            length="medium",
            call_to_action="data_driven",
            created_at=datetime.now().isoformat()
        ))
        
        return variants
    
    async def _select_variant_for_user(self, user_id: str, test: Dict, context: Dict) -> Dict:
        """Selecciona variante para usuario específico"""
        variants = test.get("variants", [])
        
        if not variants:
            return {}
        
        # Selección basada en perfil del usuario
        profile = await self._get_user_personality_profile(user_id)
        communication_style = profile.get("communication_style", "analytical")
        
        # Mapear estilo a variante preferida
        if communication_style == "direct":
            preferred_variant = next((v for v in variants if "direct" in v.variant_id), variants[0])
        else:
            preferred_variant = next((v for v in variants if "analytical" in v.variant_id), variants[0])
        
        return asdict(preferred_variant)
    
    # Métodos adicionales simplificados para el sistema completo
    
    def _calculate_response_times(self, user_memory) -> Dict:
        """Calcula tiempos de respuesta del usuario"""
        return {"avg_response_time_minutes": 15, "response_consistency": "medium"}
    
    def _calculate_engagement_metrics(self, user_memory) -> Dict:
        """Calcula métricas de engagement"""
        interaction_count = getattr(user_memory, 'interaction_count', 0)
        return {
            "base_score": min(1.0, interaction_count / 10),
            "consistency": "medium",
            "trend": "increasing" if interaction_count > 5 else "stable"
        }
    
    def _extract_decision_indicators(self, user_memory) -> List[str]:
        """Extrae indicadores de decisión"""
        return ["asks_detailed_questions", "mentions_budget", "requests_timeline"]
    
    def _analyze_communication_preferences(self, user_memory) -> Dict:
        """Analiza preferencias de comunicación"""
        return {
            "prefers_short_messages": True,
            "responds_to_data": True,
            "values_social_proof": False
        }
    
    async def _generate_base_content(self, content_type: str, context: Dict) -> str:
        """Genera contenido base"""
        return f"Contenido base para {content_type}"
    
    async def _personalize_content_for_profile(self, content: str, profile: Dict, preferences: Dict) -> str:
        """Personaliza contenido según perfil"""
        return content + " [personalizado]"
    
    async def _analyze_response_history(self, user_id: str) -> Dict:
        """Analiza historial de respuestas"""
        return {"response_rate": 0.8, "engagement_pattern": "consistent"}
    
    async def _optimize_content_based_on_history(self, content: str, history: Dict) -> str:
        """Optimiza contenido basado en historial"""
        return content + " [optimizado]"
    
    async def _add_dynamic_elements(self, user_id: str, content: str, context: Dict) -> str:
        """Agrega elementos dinámicos"""
        return content + " [elementos dinámicos]"
    
    async def _get_content_preferences(self, user_id: str) -> Dict:
        """Obtiene preferencias de contenido"""
        return {"format": "detailed", "examples": True, "data": True}
    
    async def _generate_message_from_variant(self, variant: Dict, context: Dict) -> str:
        """Genera mensaje desde variante de test"""
        return f"Mensaje de variante {variant.get('variant_id', 'unknown')}"
    
    async def _log_ab_test_exposure(self, user_id: str, test: Dict, variant: Dict):
        """Registra exposición a test A/B"""
        self.logger.info(f"Usuario {user_id} expuesto a variante {variant.get('variant_id')}")
    
    def _classify_user_segment(self, user_id: str) -> str:
        """Clasifica segmento del usuario"""
        return "high_value_prospect"
    
    async def _analyze_current_performance(self, user_id: str) -> Dict:
        """Analiza performance actual"""
        return {
            "conversion_rate": 0.15,
            "engagement_rate": 0.65,
            "response_rate": 0.80
        }
    
    async def _identify_improvement_opportunities(self, user_id: str, performance: Dict) -> List[str]:
        """Identifica oportunidades de mejora"""
        return ["improve_call_to_action", "add_social_proof", "optimize_timing"]
    
    def _calculate_target_performance(self, current: Dict, opportunities: List[str]) -> float:
        """Calcula performance objetivo"""
        base_rate = current.get("conversion_rate", 0.1)
        improvement_factor = len(opportunities) * 0.05
        return min(0.5, base_rate + improvement_factor)
    
    async def _generate_conversion_recommendations(self, user_id: str, current: Dict, opportunities: List[str]) -> List[str]:
        """Genera recomendaciones de conversión"""
        return [
            "Personalizar mensaje según estilo de comunicación",
            "Agregar elementos de urgencia apropiados",
            "Incluir prueba social relevante",
            "Optimizar timing de follow-up"
        ]
    
    def _calculate_test_parameters(self, current: Dict, target: float) -> Dict:
        """Calcula parámetros del test"""
        return {
            "duration_days": 14,
            "confidence_level": 0.85,
            "minimum_sample_size": 100
        }
    
    async def _save_conversion_optimization(self, user_id: str, optimization: ConversionOptimization):
        """Guarda optimización de conversión"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            if not hasattr(user_memory, 'conversion_optimizations'):
                user_memory.conversion_optimizations = []
            
            user_memory.conversion_optimizations.append(asdict(optimization))
            
            # Mantener solo las últimas 5
            if len(user_memory.conversion_optimizations) > 5:
                user_memory.conversion_optimizations = user_memory.conversion_optimizations[-5:]
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error guardando optimización de conversión: {e}")