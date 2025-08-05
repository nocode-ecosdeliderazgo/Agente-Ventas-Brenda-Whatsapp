"""
Sistema de Ventas Avanzadas
Calificación automática de leads, ofertas personalizadas, descuentos dinámicos,
recordatorios de pagos y upselling inteligente
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

from app.infrastructure.openai.client import OpenAIClient
from memory.lead_memory import LeadMemoryManager

logger = logging.getLogger(__name__)

@dataclass
class LeadQualification:
    """Calificación automática de lead"""
    user_id: str
    qualification: str  # hot, warm, cold
    score: int  # 0-100
    factors: List[str]
    priority_level: str  # high, medium, low
    recommended_actions: List[str]
    next_follow_up: str
    confidence: float
    qualified_at: str

@dataclass
class PersonalizedOffer:
    """Oferta personalizada"""
    offer_id: str
    user_id: str
    offer_type: str  # standard, premium, custom
    original_price: float
    discount_percentage: float
    final_price: float
    bonuses_included: List[str]
    urgency_factors: List[str]
    valid_until: str
    personalization_factors: List[str]
    created_at: str

@dataclass
class PaymentReminder:
    """Recordatorio de pago"""
    reminder_id: str
    user_id: str
    reminder_type: str  # initial, follow_up, final, recovery
    payment_amount: float
    days_overdue: int
    tone: str  # gentle, firm, urgent
    message: str
    scheduled_at: str
    sent_at: Optional[str]

@dataclass
class UpsellOpportunity:
    """Oportunidad de upselling"""
    opportunity_id: str
    user_id: str
    base_purchase: str
    recommended_addon: str
    upsell_value: float
    probability: float
    timing: str  # immediate, post_onboarding, renewal
    reasoning: List[str]
    created_at: str

class AdvancedSalesSystemUseCase:
    """Sistema avanzado de ventas con IA"""
    
    def __init__(self, openai_client: OpenAIClient, memory_manager: LeadMemoryManager):
        self.openai_client = openai_client
        self.memory_manager = memory_manager
        self.logger = logger
        
        # Factores de calificación de leads
        self.qualification_factors = {
            "hot": {
                "min_score": 80,
                "factors": [
                    "multiple_purchase_signals",
                    "budget_confirmed",
                    "decision_maker_identified",
                    "timeline_defined",
                    "high_engagement"
                ]
            },
            "warm": {
                "min_score": 60,
                "factors": [
                    "some_purchase_signals",
                    "budget_discussed",
                    "engaged_in_conversation",
                    "information_gathered"
                ]
            },
            "cold": {
                "min_score": 0,
                "factors": [
                    "minimal_engagement",
                    "no_purchase_signals",
                    "budget_concerns",
                    "low_interaction"
                ]
            }
        }
        
        # Tipos de ofertas personalizadas
        self.offer_templates = {
            "executive_premium": {
                "base_discount": 15,
                "bonuses": ["executive_onboarding", "priority_support", "custom_implementation"],
                "urgency_period_days": 7
            },
            "startup_friendly": {
                "base_discount": 20,
                "bonuses": ["payment_plan", "startup_resources", "community_access"],
                "urgency_period_days": 5
            },
            "enterprise_custom": {
                "base_discount": 10,
                "bonuses": ["team_training", "custom_integration", "dedicated_success_manager"],
                "urgency_period_days": 14
            },
            "limited_time": {
                "base_discount": 25,
                "bonuses": ["immediate_access", "bonus_materials"],
                "urgency_period_days": 3
            }
        }
        
        # Sistema de descuentos dinámicos
        self.dynamic_discount_rules = {
            "high_engagement": {"discount": 5, "condition": lambda data: data.get("engagement_score", 0) > 0.8},
            "quick_decision": {"discount": 10, "condition": lambda data: data.get("days_in_funnel", 0) <= 2},
            "multiple_courses_interest": {"discount": 15, "condition": lambda data: len(data.get("courses_viewed", [])) > 1},
            "referral_source": {"discount": 8, "condition": lambda data: data.get("referral_source") is not None},
            "return_customer": {"discount": 12, "condition": lambda data: data.get("previous_purchases", 0) > 0},
            "bulk_purchase": {"discount": 20, "condition": lambda data: data.get("team_size", 0) > 10}
        }
    
    async def qualify_lead_automatically(self, user_id: str) -> LeadQualification:
        """
        Califica lead automáticamente basado en comportamiento y datos
        
        Args:
            user_id: ID del usuario
        
        Returns:
            LeadQualification con calificación completa
        """
        try:
            # 1. Obtener datos del usuario
            user_data = await self._gather_lead_data(user_id)
            
            # 2. Calcular score de calificación
            qualification_score = await self._calculate_qualification_score(user_data)
            
            # 3. Determinar calificación (hot/warm/cold)
            qualification_level = self._determine_qualification_level(qualification_score)
            
            # 4. Identificar factores que influyen en la calificación
            influencing_factors = await self._identify_qualification_factors(
                user_data, qualification_level
            )
            
            # 5. Determinar prioridad y acciones recomendadas
            priority_actions = self._determine_priority_actions(
                qualification_level, qualification_score, influencing_factors
            )
            
            # 6. Calcular próximo follow-up
            next_followup = self._calculate_next_followup_timing(
                qualification_level, user_data
            )
            
            # 7. Calcular confianza en la calificación
            confidence = self._calculate_qualification_confidence(
                qualification_score, influencing_factors, user_data
            )
            
            qualification = LeadQualification(
                user_id=user_id,
                qualification=qualification_level,
                score=qualification_score,
                factors=influencing_factors,
                priority_level=priority_actions["priority"],
                recommended_actions=priority_actions["actions"],
                next_follow_up=next_followup,
                confidence=confidence,
                qualified_at=datetime.now().isoformat()
            )
            
            # 8. Guardar calificación en memoria
            await self._save_lead_qualification(user_id, qualification)
            
            return qualification
            
        except Exception as e:
            self.logger.error(f"Error calificando lead: {e}")
            return LeadQualification(
                user_id=user_id,
                qualification="cold",
                score=30,
                factors=["error_in_qualification"],
                priority_level="low",
                recommended_actions=["manual_review"],
                next_follow_up="24_hours",
                confidence=0.3,
                qualified_at=datetime.now().isoformat()
            )
    
    async def create_personalized_offer(self, user_id: str, base_course: str, context: Dict) -> PersonalizedOffer:
        """
        Crea oferta personalizada basada en el perfil del usuario
        
        Args:
            user_id: ID del usuario
            base_course: Curso base para la oferta
            context: Contexto adicional
        
        Returns:
            PersonalizedOffer personalizada
        """
        try:
            # 1. Obtener perfil del usuario
            user_profile = await self._get_comprehensive_user_profile(user_id)
            
            # 2. Determinar tipo de oferta apropiada
            offer_type = await self._determine_offer_type(user_profile, context)
            
            # 3. Calcular descuento dinámico
            dynamic_discount = await self._calculate_dynamic_discount(user_profile)
            
            # 4. Seleccionar bonos apropiados
            personalized_bonuses = await self._select_personalized_bonuses(
                user_profile, offer_type
            )
            
            # 5. Crear factores de urgencia apropiados
            urgency_factors = await self._create_urgency_factors(
                user_profile, offer_type
            )
            
            # 6. Calcular precios
            original_price = await self._get_course_price(base_course)
            final_price = original_price * (1 - dynamic_discount / 100)
            
            # 7. Determinar validez de la oferta
            validity_period = self._calculate_offer_validity(offer_type, user_profile)
            
            offer = PersonalizedOffer(
                offer_id=f"offer_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                offer_type=offer_type,
                original_price=original_price,
                discount_percentage=dynamic_discount,
                final_price=final_price,
                bonuses_included=personalized_bonuses,
                urgency_factors=urgency_factors,
                valid_until=(datetime.now() + timedelta(days=validity_period)).isoformat(),
                personalization_factors=await self._extract_personalization_factors(user_profile),
                created_at=datetime.now().isoformat()
            )
            
            # 8. Guardar oferta en memoria
            await self._save_personalized_offer(user_id, offer)
            
            return offer
            
        except Exception as e:
            self.logger.error(f"Error creando oferta personalizada: {e}")
            return await self._create_fallback_offer(user_id, base_course)
    
    async def generate_dynamic_discount(self, user_id: str) -> Dict:
        """
        Genera descuento dinámico basado en múltiples factores
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Dict con detalles del descuento dinámico
        """
        try:
            # 1. Obtener datos del usuario
            user_data = await self._gather_lead_data(user_id)
            
            # 2. Evaluar reglas de descuento
            applicable_discounts = []
            total_discount = 0
            
            for rule_name, rule_config in self.dynamic_discount_rules.items():
                if rule_config["condition"](user_data):
                    discount_amount = rule_config["discount"]
                    applicable_discounts.append({
                        "rule": rule_name,
                        "discount": discount_amount,
                        "reason": self._get_discount_reason(rule_name)
                    })
                    total_discount += discount_amount
            
            # 3. Aplicar límites máximos
            max_discount = self._get_max_discount_limit(user_data)
            final_discount = min(total_discount, max_discount)
            
            # 4. Calcular tiempo de validez del descuento
            discount_validity = self._calculate_discount_validity(applicable_discounts)
            
            return {
                "user_id": user_id,
                "total_discount_percentage": final_discount,
                "applicable_rules": applicable_discounts,
                "discount_breakdown": {
                    "base_discount": 0,
                    "behavioral_bonus": sum(d["discount"] for d in applicable_discounts),
                    "cap_applied": total_discount > max_discount
                },
                "validity": {
                    "valid_until": (datetime.now() + timedelta(hours=discount_validity)).isoformat(),
                    "urgency_level": "high" if discount_validity <= 24 else "medium"
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generando descuento dinámico: {e}")
            return {"user_id": user_id, "total_discount_percentage": 0, "error": str(e)}
    
    async def create_payment_reminder(self, user_id: str, payment_context: Dict) -> PaymentReminder:
        """
        Crea recordatorio de pago personalizado
        
        Args:
            user_id: ID del usuario
            payment_context: Contexto del pago
        
        Returns:
            PaymentReminder personalizado
        """
        try:
            # 1. Analizar situación del pago
            payment_status = await self._analyze_payment_status(user_id, payment_context)
            
            # 2. Determinar tipo de recordatorio apropiado
            reminder_type = self._determine_reminder_type(payment_status)
            
            # 3. Calcular tono apropiado
            reminder_tone = await self._calculate_reminder_tone(
                user_id, payment_status, reminder_type
            )
            
            # 4. Generar mensaje personalizado
            reminder_message = await self._generate_reminder_message(
                user_id, payment_status, reminder_tone, reminder_type
            )
            
            # 5. Determinar timing del recordatorio
            reminder_timing = self._calculate_reminder_timing(
                payment_status, reminder_type
            )
            
            reminder = PaymentReminder(
                reminder_id=f"reminder_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                reminder_type=reminder_type,
                payment_amount=payment_context.get("amount", 0),
                days_overdue=payment_status.get("days_overdue", 0),
                tone=reminder_tone,
                message=reminder_message,
                scheduled_at=reminder_timing,
                sent_at=None
            )
            
            # 6. Programar envío del recordatorio
            await self._schedule_payment_reminder(reminder)
            
            return reminder
            
        except Exception as e:
            self.logger.error(f"Error creando recordatorio de pago: {e}")
            return PaymentReminder(
                reminder_id=f"fallback_{user_id}",
                user_id=user_id,
                reminder_type="gentle",
                payment_amount=0,
                days_overdue=0,
                tone="professional",
                message="Recordatorio de pago pendiente",
                scheduled_at=datetime.now().isoformat(),
                sent_at=None
            )
    
    async def identify_upsell_opportunities(self, user_id: str) -> List[UpsellOpportunity]:
        """
        Identifica oportunidades de upselling inteligente
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Lista de oportunidades de upselling
        """
        try:
            # 1. Obtener historial de compras y comportamiento
            user_profile = await self._get_comprehensive_user_profile(user_id)
            
            # 2. Analizar patrones de compra
            purchase_patterns = await self._analyze_purchase_patterns(user_profile)
            
            # 3. Identificar productos/servicios complementarios
            complementary_offerings = await self._identify_complementary_offerings(
                user_profile, purchase_patterns
            )
            
            # 4. Calcular probabilidad de aceptación para cada oportunidad
            opportunities = []
            
            for offering in complementary_offerings:
                probability = await self._calculate_upsell_probability(
                    user_profile, offering
                )
                
                if probability > 0.3:  # Umbral mínimo de probabilidad
                    timing = await self._determine_optimal_upsell_timing(
                        user_profile, offering
                    )
                    
                    reasoning = await self._generate_upsell_reasoning(
                        user_profile, offering
                    )
                    
                    opportunity = UpsellOpportunity(
                        opportunity_id=f"upsell_{user_id}_{offering['id']}_{int(datetime.now().timestamp())}",
                        user_id=user_id,
                        base_purchase=user_profile.get("latest_purchase", "unknown"),
                        recommended_addon=offering["name"],
                        upsell_value=offering["price"],
                        probability=probability,
                        timing=timing,
                        reasoning=reasoning,
                        created_at=datetime.now().isoformat()
                    )
                    
                    opportunities.append(opportunity)
            
            # 5. Ordenar por probabilidad y valor
            opportunities.sort(
                key=lambda x: x.probability * x.upsell_value, 
                reverse=True
            )
            
            # 6. Guardar oportunidades en memoria
            await self._save_upsell_opportunities(user_id, opportunities)
            
            return opportunities[:5]  # Top 5 oportunidades
            
        except Exception as e:
            self.logger.error(f"Error identificando oportunidades de upselling: {e}")
            return []
    
    # Métodos auxiliares privados
    
    async def _gather_lead_data(self, user_id: str) -> Dict:
        """Recopila datos completos del lead"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            # Calcular métricas derivadas
            engagement_score = self._calculate_current_engagement_score(user_memory)
            days_in_funnel = self._calculate_days_in_funnel(user_memory)
            purchase_signals = self._count_purchase_signals(user_memory)
            
            return {
                "user_id": user_id,
                "lead_score": getattr(user_memory, 'lead_score', 0),
                "interaction_count": getattr(user_memory, 'interaction_count', 0),
                "engagement_score": engagement_score,
                "days_in_funnel": days_in_funnel,
                "purchase_signals": purchase_signals,
                "buyer_persona": getattr(user_memory, 'buyer_persona_match', 'unknown'),
                "current_emotion": getattr(user_memory, 'current_emotion', 'neutral'),
                "message_history": getattr(user_memory, 'message_history', []),
                "emotion_history": getattr(user_memory, 'emotion_history', []),
                "pain_points": getattr(user_memory, 'pain_points', []),
                "budget_indicators": getattr(user_memory, 'budget_indicators', []),
                "decision_making_power": getattr(user_memory, 'decision_making_power', 'unknown'),
                "company_size": getattr(user_memory, 'company_size', 'unknown'),
                "industry_sector": getattr(user_memory, 'industry_sector', 'unknown'),
                "urgency_signals": getattr(user_memory, 'urgency_signals', []),
                "previous_purchases": getattr(user_memory, 'previous_purchases', 0),
                "referral_source": getattr(user_memory, 'referral_source', None),
                "courses_viewed": getattr(user_memory, 'courses_viewed', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error recopilando datos del lead: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    async def _calculate_qualification_score(self, user_data: Dict) -> int:
        """Calcula score de calificación de 0-100"""
        score = 0
        
        # Factores de scoring
        scoring_factors = {
            "lead_score": {"weight": 0.3, "max_value": 100},
            "engagement_score": {"weight": 0.2, "max_value": 1},
            "purchase_signals": {"weight": 0.25, "max_value": 10},
            "interaction_count": {"weight": 0.1, "max_value": 20},
            "decision_making_power": {"weight": 0.15, "values": {"decision_maker": 100, "budget_holder": 80, "influencer": 50, "unknown": 20}}
        }
        
        # Calcular score ponderado
        for factor, config in scoring_factors.items():
            value = user_data.get(factor, 0)
            weight = config["weight"]
            
            if "max_value" in config:
                normalized_value = min(value / config["max_value"], 1.0)
                score += normalized_value * weight * 100
            elif "values" in config:
                mapped_value = config["values"].get(value, 0)
                score += (mapped_value / 100) * weight * 100
        
        # Bonificaciones por factores específicos
        bonuses = {
            "buyer_persona_executive": 10 if user_data.get("buyer_persona") in ["sofia_visionaria", "daniel_data_innovador"] else 0,
            "budget_indicators_positive": 15 if len(user_data.get("budget_indicators", [])) > 0 else 0,
            "urgency_signals": 10 if len(user_data.get("urgency_signals", [])) > 2 else 0,
            "short_sales_cycle": 10 if user_data.get("days_in_funnel", 30) <= 7 else 0
        }
        
        total_bonus = sum(bonuses.values())
        final_score = min(100, int(score + total_bonus))
        
        return final_score
    
    def _determine_qualification_level(self, score: int) -> str:
        """Determina nivel de calificación basado en score"""
        if score >= self.qualification_factors["hot"]["min_score"]:
            return "hot"
        elif score >= self.qualification_factors["warm"]["min_score"]:
            return "warm"
        else:
            return "cold"
    
    async def _identify_qualification_factors(self, user_data: Dict, qualification_level: str) -> List[str]:
        """Identifica factores que influyen en la calificación"""
        factors = []
        
        # Factores basados en datos
        if user_data.get("purchase_signals", 0) >= 3:
            factors.append("multiple_purchase_signals")
        
        if user_data.get("engagement_score", 0) > 0.7:
            factors.append("high_engagement")
        
        if user_data.get("decision_making_power") in ["decision_maker", "budget_holder"]:
            factors.append("decision_maker_identified")
        
        if len(user_data.get("budget_indicators", [])) > 0:
            factors.append("budget_discussed")
        
        if user_data.get("days_in_funnel", 30) <= 7:
            factors.append("timeline_defined")
        
        if user_data.get("interaction_count", 0) >= 10:
            factors.append("engaged_in_conversation")
        
        # Factores específicos por nivel
        level_factors = self.qualification_factors.get(qualification_level, {}).get("factors", [])
        factors.extend([f for f in level_factors if f not in factors])
        
        return factors[:8]  # Máximo 8 factores
    
    def _determine_priority_actions(self, qualification: str, score: int, factors: List[str]) -> Dict:
        """Determina prioridad y acciones recomendadas"""
        if qualification == "hot":
            return {
                "priority": "high",
                "actions": [
                    "immediate_sales_contact",
                    "present_premium_offer",
                    "schedule_demo_call",
                    "provide_contract_details"
                ]
            }
        elif qualification == "warm":
            return {
                "priority": "medium",
                "actions": [
                    "nurture_with_value_content",
                    "address_specific_objections",
                    "provide_social_proof",
                    "create_urgency"
                ]
            }
        else:
            return {
                "priority": "low",
                "actions": [
                    "educational_content",
                    "build_relationship",
                    "identify_pain_points",
                    "qualify_further"
                ]
            }
    
    def _calculate_next_followup_timing(self, qualification: str, user_data: Dict) -> str:
        """Calcula timing del próximo follow-up"""
        timing_map = {
            "hot": "immediate",  # Dentro de 1 hora
            "warm": "24_hours",
            "cold": "72_hours"
        }
        
        base_timing = timing_map.get(qualification, "24_hours")
        
        # Ajustar por urgencia
        urgency_signals = len(user_data.get("urgency_signals", []))
        if urgency_signals > 2:
            return "immediate"
        elif urgency_signals > 0 and base_timing != "immediate":
            return "12_hours"
        
        return base_timing
    
    def _calculate_qualification_confidence(self, score: int, factors: List[str], user_data: Dict) -> float:
        """Calcula confianza en la calificación"""
        base_confidence = 0.6
        
        # Más factores = mayor confianza
        factor_bonus = min(0.3, len(factors) * 0.05)
        
        # Más interacciones = mayor confianza
        interaction_bonus = min(0.1, user_data.get("interaction_count", 0) * 0.01)
        
        # Score extremos = mayor confianza
        if score >= 90 or score <= 20:
            score_bonus = 0.1
        else:
            score_bonus = 0.0
        
        total_confidence = base_confidence + factor_bonus + interaction_bonus + score_bonus
        return min(0.95, total_confidence)
    
    async def _get_comprehensive_user_profile(self, user_id: str) -> Dict:
        """Obtiene perfil completo del usuario"""
        user_data = await self._gather_lead_data(user_id)
        
        # Agregar datos adicionales para ofertas
        user_memory = self.memory_manager.get_user_memory(user_id)
        
        additional_data = {
            "personality_profile": getattr(user_memory, 'personality_profile', {}),
            "assessment_history": getattr(user_memory, 'assessment_history', []),
            "preference_history": getattr(user_memory, 'preference_history', {}),
            "communication_style": getattr(user_memory, 'communication_style', 'professional'),
            "response_patterns": getattr(user_memory, 'response_patterns', {}),
            "conversion_indicators": getattr(user_memory, 'conversion_indicators', [])
        }
        
        return {**user_data, **additional_data}
    
    async def _determine_offer_type(self, user_profile: Dict, context: Dict) -> str:
        """Determina tipo de oferta apropiada"""
        buyer_persona = user_profile.get("buyer_persona", "unknown")
        company_size = user_profile.get("company_size", "unknown")
        decision_power = user_profile.get("decision_making_power", "unknown")
        
        # Lógica de determinación de oferta
        if buyer_persona in ["sofia_visionaria", "daniel_data_innovador"] and decision_power == "decision_maker":
            return "executive_premium"
        elif company_size in ["startup", "small"]:
            return "startup_friendly"
        elif company_size in ["large", "enterprise"]:
            return "enterprise_custom"
        elif context.get("urgency_level") == "high":
            return "limited_time"
        else:
            return "executive_premium"  # Default
    
    async def _calculate_dynamic_discount(self, user_profile: Dict) -> float:
        """Calcula descuento dinámico"""
        base_discount = 0
        
        # Aplicar reglas de descuento dinámico
        for rule_name, rule_config in self.dynamic_discount_rules.items():
            if rule_config["condition"](user_profile):
                base_discount += rule_config["discount"]
        
        # Límites por tipo de usuario
        max_discount = 30  # Default
        if user_profile.get("buyer_persona") in ["sofia_visionaria"]:
            max_discount = 20  # Ejecutivos menos sensibles al precio
        elif user_profile.get("company_size") == "startup":
            max_discount = 35  # Startups más sensibles al precio
        
        return min(base_discount, max_discount)
    
    async def _select_personalized_bonuses(self, user_profile: Dict, offer_type: str) -> List[str]:
        """Selecciona bonos personalizados"""
        base_bonuses = self.offer_templates.get(offer_type, {}).get("bonuses", [])
        
        # Bonos adicionales basados en perfil
        additional_bonuses = []
        
        if user_profile.get("buyer_persona") == "daniel_data_innovador":
            additional_bonuses.extend(["advanced_analytics_module", "api_access"])
        
        if user_profile.get("company_size") in ["large", "enterprise"]:
            additional_bonuses.extend(["team_licenses", "enterprise_features"])
        
        if len(user_profile.get("pain_points", [])) > 3:
            additional_bonuses.append("personalized_consultation")
        
        return base_bonuses + additional_bonuses[:2]  # Máximo 2 bonos adicionales
    
    async def _create_urgency_factors(self, user_profile: Dict, offer_type: str) -> List[str]:
        """Crea factores de urgencia apropiados"""
        urgency_factors = []
        
        # Factores base por tipo de oferta
        if offer_type == "limited_time":
            urgency_factors.extend(["limited_spots", "price_increase_soon"])
        
        # Factores basados en perfil
        if user_profile.get("days_in_funnel", 0) > 14:
            urgency_factors.append("extended_consideration_discount")
        
        if len(user_profile.get("urgency_signals", [])) > 2:
            urgency_factors.append("immediate_implementation_needed")
        
        if user_profile.get("current_emotion") == "decidido":
            urgency_factors.append("momentum_capture")
        
        return urgency_factors
    
    async def _get_course_price(self, course_name: str) -> float:
        """Obtiene precio del curso"""
        # Precios base - en producción vendrían de BD
        course_prices = {
            "Experto en IA para Profesionales": 4500.0,
            "IA Avanzada para Empresas": 6500.0,
            "Automatización Empresarial": 3500.0
        }
        
        return course_prices.get(course_name, 4500.0)
    
    def _calculate_offer_validity(self, offer_type: str, user_profile: Dict) -> int:
        """Calcula período de validez de la oferta en días"""
        base_validity = self.offer_templates.get(offer_type, {}).get("urgency_period_days", 7)
        
        # Ajustar por perfil del usuario
        if user_profile.get("decision_making_style") == "quick":
            return max(3, base_validity - 2)
        elif user_profile.get("decision_making_style") == "methodical":
            return base_validity + 7
        
        return base_validity
    
    async def _extract_personalization_factors(self, user_profile: Dict) -> List[str]:
        """Extrae factores de personalización utilizados"""
        factors = []
        
        if user_profile.get("buyer_persona") != "unknown":
            factors.append(f"buyer_persona_{user_profile['buyer_persona']}")
        
        if user_profile.get("company_size") != "unknown":
            factors.append(f"company_size_{user_profile['company_size']}")
        
        if user_profile.get("engagement_score", 0) > 0.7:
            factors.append("high_engagement")
        
        if len(user_profile.get("purchase_signals", [])) > 2:
            factors.append("strong_purchase_intent")
        
        return factors
    
    # Métodos adicionales simplificados
    
    def _calculate_current_engagement_score(self, user_memory) -> float:
        """Calcula score de engagement actual"""
        interaction_count = getattr(user_memory, 'interaction_count', 0)
        return min(1.0, interaction_count / 15)
    
    def _calculate_days_in_funnel(self, user_memory) -> int:
        """Calcula días en el funnel"""
        first_interaction = getattr(user_memory, 'first_interaction', None)
        if not first_interaction:
            return 0
        
        try:
            first_time = datetime.fromisoformat(first_interaction)
            return (datetime.now() - first_time).days
        except:
            return 0
    
    def _count_purchase_signals(self, user_memory) -> int:
        """Cuenta señales de compra"""
        return getattr(user_memory, 'purchase_signals', 0)
    
    def _get_discount_reason(self, rule_name: str) -> str:
        """Obtiene razón del descuento"""
        reasons = {
            "high_engagement": "Alto nivel de participación",
            "quick_decision": "Decisión rápida",
            "multiple_courses_interest": "Interés en múltiples cursos",
            "referral_source": "Referencia de cliente",
            "return_customer": "Cliente recurrente",
            "bulk_purchase": "Compra para equipo"
        }
        return reasons.get(rule_name, "Descuento especial")
    
    def _get_max_discount_limit(self, user_data: Dict) -> int:
        """Obtiene límite máximo de descuento"""
        if user_data.get("buyer_persona") in ["sofia_visionaria"]:
            return 25  # Ejecutivos - límite menor
        elif user_data.get("company_size") == "startup":
            return 40  # Startups - límite mayor
        else:
            return 30  # Default
    
    def _calculate_discount_validity(self, discounts: List[Dict]) -> int:
        """Calcula validez del descuento en horas"""
        if len(discounts) >= 3:
            return 12  # Muchos descuentos = urgencia alta
        elif len(discounts) >= 2:
            return 24  # Algunos descuentos = urgencia media
        else:
            return 48  # Pocos descuentos = urgencia baja
    
    async def _save_lead_qualification(self, user_id: str, qualification: LeadQualification):
        """Guarda calificación en memoria"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            if not hasattr(user_memory, 'lead_qualifications'):
                user_memory.lead_qualifications = []
            
            user_memory.lead_qualifications.append(asdict(qualification))
            
            # Mantener solo las últimas 5
            if len(user_memory.lead_qualifications) > 5:
                user_memory.lead_qualifications = user_memory.lead_qualifications[-5:]
            
            # Actualizar calificación actual
            user_memory.current_qualification = qualification.qualification
            user_memory.current_lead_score = qualification.score
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error guardando calificación: {e}")
    
    async def _save_personalized_offer(self, user_id: str, offer: PersonalizedOffer):
        """Guarda oferta personalizada en memoria"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            if not hasattr(user_memory, 'personalized_offers'):
                user_memory.personalized_offers = []
            
            user_memory.personalized_offers.append(asdict(offer))
            
            # Mantener solo las últimas 3
            if len(user_memory.personalized_offers) > 3:
                user_memory.personalized_offers = user_memory.personalized_offers[-3:]
            
            # Actualizar oferta actual
            user_memory.current_offer = asdict(offer)
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error guardando oferta personalizada: {e}")
    
    # Métodos simplificados para otras funcionalidades
    
    async def _create_fallback_offer(self, user_id: str, base_course: str) -> PersonalizedOffer:
        """Crea oferta de fallback"""
        return PersonalizedOffer(
            offer_id=f"fallback_{user_id}",
            user_id=user_id,
            offer_type="standard",
            original_price=4500.0,
            discount_percentage=10.0,
            final_price=4050.0,
            bonuses_included=["basic_support"],
            urgency_factors=["limited_time"],
            valid_until=(datetime.now() + timedelta(days=7)).isoformat(),
            personalization_factors=["fallback_offer"],
            created_at=datetime.now().isoformat()
        )
    
    async def _analyze_payment_status(self, user_id: str, context: Dict) -> Dict:
        """Analiza estado del pago"""
        return {
            "status": "pending",
            "days_overdue": context.get("days_overdue", 0),
            "amount": context.get("amount", 0),
            "previous_reminders": 0
        }
    
    def _determine_reminder_type(self, payment_status: Dict) -> str:
        """Determina tipo de recordatorio"""
        days_overdue = payment_status.get("days_overdue", 0)
        
        if days_overdue <= 1:
            return "initial"
        elif days_overdue <= 7:
            return "follow_up"
        elif days_overdue <= 14:
            return "final"
        else:
            return "recovery"
    
    async def _calculate_reminder_tone(self, user_id: str, payment_status: Dict, reminder_type: str) -> str:
        """Calcula tono del recordatorio"""
        if reminder_type == "initial":
            return "gentle"
        elif reminder_type == "follow_up":
            return "professional"
        elif reminder_type == "final":
            return "firm"
        else:
            return "urgent"
    
    async def _generate_reminder_message(self, user_id: str, payment_status: Dict, tone: str, reminder_type: str) -> str:
        """Genera mensaje del recordatorio"""
        amount = payment_status.get("amount", 0)
        
        if tone == "gentle":
            return f"Recordatorio amigable: Tienes un pago pendiente de ${amount:,.2f}. ¿Necesitas ayuda con el proceso?"
        elif tone == "professional":
            return f"Recordatorio: Tu pago de ${amount:,.2f} está pendiente. Por favor procede con el pago cuando tengas oportunidad."
        elif tone == "firm":
            return f"Pago pendiente: ${amount:,.2f}. Es importante que regularices tu situación para mantener tu acceso al programa."
        else:
            return f"URGENTE: Pago vencido de ${amount:,.2f}. Contacta con nosotros inmediatamente para evitar suspensión del servicio."
    
    def _calculate_reminder_timing(self, payment_status: Dict, reminder_type: str) -> str:
        """Calcula timing del recordatorio"""
        now = datetime.now()
        
        if reminder_type == "initial":
            scheduled_time = now + timedelta(hours=24)
        elif reminder_type == "follow_up":
            scheduled_time = now + timedelta(hours=12)
        else:
            scheduled_time = now + timedelta(hours=6)
        
        return scheduled_time.isoformat()
    
    async def _schedule_payment_reminder(self, reminder: PaymentReminder):
        """Programa envío del recordatorio"""
        # En producción, esto se integraría con un sistema de colas/scheduler
        self.logger.info(f"Recordatorio programado para {reminder.scheduled_at}")
    
    async def _analyze_purchase_patterns(self, user_profile: Dict) -> Dict:
        """Analiza patrones de compra"""
        return {
            "purchase_frequency": "first_time",
            "price_sensitivity": "medium",
            "feature_preference": "standard"
        }
    
    async def _identify_complementary_offerings(self, user_profile: Dict, patterns: Dict) -> List[Dict]:
        """Identifica ofertas complementarias"""
        return [
            {"id": "advanced_ai", "name": "IA Avanzada", "price": 2000.0},
            {"id": "automation_plus", "name": "Automatización Plus", "price": 1500.0}
        ]
    
    async def _calculate_upsell_probability(self, user_profile: Dict, offering: Dict) -> float:
        """Calcula probabilidad de upselling"""
        base_prob = 0.3
        
        if user_profile.get("engagement_score", 0) > 0.7:
            base_prob += 0.2
        
        if user_profile.get("current_qualification") == "hot":
            base_prob += 0.3
        
        return min(1.0, base_prob)
    
    async def _determine_optimal_upsell_timing(self, user_profile: Dict, offering: Dict) -> str:
        """Determina timing óptimo para upselling"""
        if user_profile.get("current_qualification") == "hot":
            return "immediate"
        else:
            return "post_onboarding"
    
    async def _generate_upsell_reasoning(self, user_profile: Dict, offering: Dict) -> List[str]:
        """Genera razonamiento para upselling"""
        return [
            "Complementa perfectamente su compra actual",
            "Alto engagement sugiere interés en funcionalidades avanzadas",
            "Perfil de usuario coincide con usuarios típicos de este producto"
        ]
    
    async def _save_upsell_opportunities(self, user_id: str, opportunities: List[UpsellOpportunity]):
        """Guarda oportunidades de upselling"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            if not hasattr(user_memory, 'upsell_opportunities'):
                user_memory.upsell_opportunities = []
            
            # Convertir a dict para guardado
            opportunities_dict = [asdict(opp) for opp in opportunities]
            user_memory.upsell_opportunities = opportunities_dict
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error guardando oportunidades de upselling: {e}")