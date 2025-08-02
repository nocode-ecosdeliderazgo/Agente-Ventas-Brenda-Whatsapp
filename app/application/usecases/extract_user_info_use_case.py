"""
Extract User Information Use Case

This use case intelligently extracts and analyzes user information from conversations
to build detailed buyer persona profiles for enhanced personalization.
"""

import logging
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from app.infrastructure.openai.client import OpenAIClient
from memory.lead_memory import LeadMemory

logger = logging.getLogger(__name__)

@dataclass
class UserInsights:
    """Insights extracted from user interactions"""
    professional_level: str = "unknown"  # junior, mid-level, senior, executive
    company_size: str = "unknown"  # startup, small, medium, large, enterprise
    industry_sector: str = "unknown"  # marketing, operations, tech, consulting, etc.
    pain_points: List[str] = None
    automation_needs: List[str] = None
    budget_indicators: List[str] = None
    urgency_signals: List[str] = None
    technical_level: str = "unknown"  # beginner, intermediate, advanced
    decision_making_power: str = "unknown"  # influencer, decision_maker, budget_holder
    buyer_persona_match: str = "unknown"  # lucia_copypro, marcos_multitask, etc.
    confidence_score: float = 0.0

class ExtractUserInfoUseCase:
    """
    Intelligently extracts and analyzes user information for personalization.
    """
    
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        
        # Buyer persona patterns for detection
        self.buyer_persona_patterns = {
            'lucia_copypro': {
                'keywords': ['marketing', 'campaña', 'contenido', 'social media', 'agencia', 'clientes', 'leads'],
                'roles': ['marketing manager', 'digital marketing', 'content manager', 'social media manager'],
                'pain_points': ['crear contenido', 'campañas', 'leads', 'clientes', 'creatividad'],
                'automation_needs': ['contenido automático', 'campañas', 'reportes', 'análisis']
            },
            'marcos_multitask': {
                'keywords': ['operaciones', 'procesos', 'eficiencia', 'productividad', 'equipos', 'manufacturar'],
                'roles': ['operations manager', 'gerente operaciones', 'director operativo', 'jefe producción'],
                'pain_points': ['procesos manuales', 'eficiencia', 'costos', 'tiempo', 'recursos'],
                'automation_needs': ['automatizar procesos', 'reportes', 'inventarios', 'calidad']
            },
            'sofia_visionaria': {
                'keywords': ['ceo', 'fundador', 'empresa', 'crecimiento', 'estrategia', 'competencia', 'innovación'],
                'roles': ['ceo', 'founder', 'director general', 'presidente', 'cofundador'],
                'pain_points': ['competencia', 'crecimiento', 'innovación', 'costos', 'escalabilidad'],
                'automation_needs': ['decisiones estratégicas', 'análisis mercado', 'innovación', 'competitividad']
            },
            'ricardo_rh_agil': {
                'keywords': ['recursos humanos', 'talento', 'capacitación', 'empleados', 'reclutamiento', 'training'],
                'roles': ['hr manager', 'recursos humanos', 'people operations', 'talent manager', 'rrhh'],
                'pain_points': ['capacitación', 'talento', 'retención', 'productividad empleados', 'skills'],
                'automation_needs': ['capacitación automática', 'evaluaciones', 'onboarding', 'desarrollo']
            },
            'daniel_data_innovador': {
                'keywords': ['datos', 'análisis', 'business intelligence', 'reportes', 'métricas', 'insights'],
                'roles': ['data analyst', 'business intelligence', 'innovation manager', 'analista datos'],
                'pain_points': ['análisis datos', 'reportes', 'insights', 'decisiones basadas datos'],
                'automation_needs': ['reportes automáticos', 'análisis predictivo', 'dashboards', 'insights']
            }
        }
        
        # Company size indicators
        self.company_size_indicators = {
            'startup': ['startup', 'emprendimiento', 'comenzando', 'founding', 'incubadora'],
            'small': ['pequeña empresa', 'pyme', 'pocos empleados', '5-20 empleados', 'negocio familiar'],
            'medium': ['mediana empresa', '20-200 empleados', 'several departments', 'growing company'],
            'large': ['gran empresa', 'corporativo', '200+ empleados', 'multinacional'],
            'enterprise': ['enterprise', 'corporación', '1000+ empleados', 'fortune 500']
        }
        
        # Budget indicators
        self.budget_indicators = {
            'low': ['presupuesto limitado', 'económico', 'barato', 'sin mucho dinero', 'ajustado'],
            'medium': ['inversión razonable', 'presupuesto moderado', 'valor por dinero'],
            'high': ['dispuesto invertir', 'presupuesto amplio', 'ROI importante', 'inversión significativa'],
            'premium': ['mejor opción', 'premium', 'sin restricciones presupuesto', 'top tier']
        }

    async def extract_insights_from_conversation(
        self, 
        user_memory: LeadMemory,
        recent_messages: List[str] = None
    ) -> UserInsights:
        """
        Extracts comprehensive user insights from conversation history.
        
        Args:
            user_memory: Current user memory with conversation history
            recent_messages: Recent messages for immediate analysis
            
        Returns:
            UserInsights: Extracted insights about the user
        """
        try:
            # Combine all available text for analysis
            conversation_text = self._prepare_conversation_text(user_memory, recent_messages)
            
            if not conversation_text.strip():
                return UserInsights()
            
            # Use AI for intelligent extraction
            insights = await self._ai_extract_insights(conversation_text, user_memory)
            
            # Enhance with pattern-based detection
            enhanced_insights = self._enhance_with_patterns(insights, conversation_text)
            
            # Calculate confidence score
            enhanced_insights.confidence_score = self._calculate_confidence_score(enhanced_insights, conversation_text)
            
            logger.info(f"Extracted insights for user {user_memory.user_id}: persona={enhanced_insights.buyer_persona_match}, confidence={enhanced_insights.confidence_score:.2f}")
            
            return enhanced_insights
            
        except Exception as e:
            logger.error(f"Error extracting user insights: {e}")
            return UserInsights()

    def _prepare_conversation_text(self, user_memory: LeadMemory, recent_messages: List[str] = None) -> str:
        """Prepares conversation text for analysis"""
        text_parts = []
        
        # Add basic user info
        if user_memory.name:
            text_parts.append(f"Nombre: {user_memory.name}")
        if user_memory.role:
            text_parts.append(f"Rol: {user_memory.role}")
        
        # Add conversation history
        if hasattr(user_memory, 'conversation_history') and user_memory.conversation_history:
            for msg in user_memory.conversation_history[-10:]:  # Last 10 messages
                if isinstance(msg, dict) and msg.get('user_message'):
                    text_parts.append(msg['user_message'])
        
        # Add recent messages
        if recent_messages:
            text_parts.extend(recent_messages[-5:])  # Last 5 recent messages
        
        # Add existing insights
        if hasattr(user_memory, 'interests') and user_memory.interests:
            text_parts.append(f"Intereses: {', '.join(user_memory.interests)}")
        if hasattr(user_memory, 'pain_points') and user_memory.pain_points:
            text_parts.append(f"Pain points: {', '.join(user_memory.pain_points)}")
        
        return " ".join(text_parts)

    async def _ai_extract_insights(self, conversation_text: str, user_memory: LeadMemory) -> UserInsights:
        """Uses AI to extract insights from conversation"""
        
        extraction_prompt = f"""
Analiza la siguiente conversación de un usuario interesado en cursos de IA para empresas PyME y extrae información clave para personalización.

CONVERSACIÓN:
{conversation_text}

INSTRUCCIONES:
Extrae la siguiente información y responde en formato JSON:

1. professional_level: junior, mid-level, senior, executive
2. company_size: startup, small, medium, large, enterprise  
3. industry_sector: marketing, operations, tech, consulting, healthcare, education, retail, finance, manufacturing, other
4. pain_points: lista de problemas/desafíos mencionados
5. automation_needs: lista de procesos que quiere automatizar
6. budget_indicators: lista de indicadores de presupuesto mencionados
7. urgency_signals: lista de señales de urgencia/prisa
8. technical_level: beginner, intermediate, advanced
9. decision_making_power: influencer, decision_maker, budget_holder
10. buyer_persona_match: lucia_copypro, marcos_multitask, sofia_visionaria, ricardo_rh_agil, daniel_data_innovador, unknown

BUYER PERSONAS DE REFERENCIA:
- lucia_copypro: Marketing Digital Manager (Agencies)
- marcos_multitask: Operations Manager (Manufacturing PyMEs)
- sofia_visionaria: CEO/Founder (Professional Services)
- ricardo_rh_agil: Head of Talent & Learning (Scale-ups)
- daniel_data_innovador: Senior Innovation/BI Analyst (Corporates)

Responde solo con JSON válido, sin explicaciones adicionales.
"""

        try:
            response = await self.openai_client.chat_completion(
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de buyer personas para empresas PyME. Extrae información relevante para personalización de respuestas."},
                    {"role": "user", "content": extraction_prompt}
                ],
                model="gpt-4o-mini",
                max_tokens=500,
                temperature=0.1
            )
            
            # Parse JSON response
            insights_data = json.loads(response)
            
            return UserInsights(
                professional_level=insights_data.get('professional_level', 'unknown'),
                company_size=insights_data.get('company_size', 'unknown'),
                industry_sector=insights_data.get('industry_sector', 'unknown'),
                pain_points=insights_data.get('pain_points', []),
                automation_needs=insights_data.get('automation_needs', []),
                budget_indicators=insights_data.get('budget_indicators', []),
                urgency_signals=insights_data.get('urgency_signals', []),
                technical_level=insights_data.get('technical_level', 'unknown'),
                decision_making_power=insights_data.get('decision_making_power', 'unknown'),
                buyer_persona_match=insights_data.get('buyer_persona_match', 'unknown')
            )
            
        except Exception as e:
            logger.error(f"Error in AI insight extraction: {e}")
            return UserInsights()

    def _enhance_with_patterns(self, insights: UserInsights, conversation_text: str) -> UserInsights:
        """Enhances AI insights with pattern-based detection"""
        
        text_lower = conversation_text.lower()
        
        # Enhance buyer persona detection
        if insights.buyer_persona_match == 'unknown':
            persona_scores = {}
            
            for persona, patterns in self.buyer_persona_patterns.items():
                score = 0
                
                # Check keywords
                for keyword in patterns['keywords']:
                    if keyword in text_lower:
                        score += 2
                
                # Check roles
                for role in patterns['roles']:
                    if role in text_lower:
                        score += 3
                
                # Check pain points
                for pain in patterns['pain_points']:
                    if pain in text_lower:
                        score += 1
                
                persona_scores[persona] = score
            
            # Select highest scoring persona
            if persona_scores:
                best_persona = max(persona_scores, key=persona_scores.get)
                if persona_scores[best_persona] >= 3:  # Minimum confidence threshold
                    insights.buyer_persona_match = best_persona
        
        # Enhance company size detection
        if insights.company_size == 'unknown':
            for size, indicators in self.company_size_indicators.items():
                if any(indicator in text_lower for indicator in indicators):
                    insights.company_size = size
                    break
        
        # Enhance budget indicators
        if not insights.budget_indicators:
            for budget_level, indicators in self.budget_indicators.items():
                matching_indicators = [ind for ind in indicators if ind in text_lower]
                if matching_indicators:
                    insights.budget_indicators = matching_indicators
                    break
        
        return insights

    def _calculate_confidence_score(self, insights: UserInsights, conversation_text: str) -> float:
        """Calculates confidence score for extracted insights"""
        
        score = 0.0
        max_score = 10.0
        
        # Score based on available information
        if insights.buyer_persona_match != 'unknown':
            score += 2.0
        if insights.professional_level != 'unknown':
            score += 1.5
        if insights.company_size != 'unknown':
            score += 1.0
        if insights.industry_sector != 'unknown':
            score += 1.0
        if insights.pain_points:
            score += min(len(insights.pain_points) * 0.5, 2.0)
        if insights.automation_needs:
            score += min(len(insights.automation_needs) * 0.5, 1.5)
        if insights.technical_level != 'unknown':
            score += 0.5
        if insights.decision_making_power != 'unknown':
            score += 0.5
        
        return min(score / max_score, 1.0)

    async def update_user_memory_with_insights(self, user_memory: LeadMemory, insights: UserInsights) -> LeadMemory:
        """
        Updates user memory with extracted insights.
        
        Args:
            user_memory: Current user memory
            insights: Extracted insights
            
        Returns:
            Updated user memory
        """
        try:
            # Update basic info
            if not hasattr(user_memory, 'professional_level'):
                user_memory.professional_level = insights.professional_level
            if not hasattr(user_memory, 'company_size'):
                user_memory.company_size = insights.company_size
            if not hasattr(user_memory, 'industry_sector'):
                user_memory.industry_sector = insights.industry_sector
            
            # Update or merge lists
            if insights.pain_points:
                if not hasattr(user_memory, 'pain_points') or not user_memory.pain_points:
                    user_memory.pain_points = insights.pain_points
                else:
                    # Merge unique pain points
                    user_memory.pain_points = list(set(user_memory.pain_points + insights.pain_points))
            
            if insights.automation_needs:
                if not hasattr(user_memory, 'automation_needs') or not user_memory.automation_needs:
                    user_memory.automation_needs = insights.automation_needs
                else:
                    user_memory.automation_needs = list(set(user_memory.automation_needs + insights.automation_needs))
            
            # Update advanced attributes
            if not hasattr(user_memory, 'buyer_persona_match'):
                user_memory.buyer_persona_match = insights.buyer_persona_match
            if not hasattr(user_memory, 'technical_level'):
                user_memory.technical_level = insights.technical_level
            if not hasattr(user_memory, 'decision_making_power'):
                user_memory.decision_making_power = insights.decision_making_power
            
            # Add insights metadata
            user_memory.insights_confidence = insights.confidence_score
            user_memory.last_insights_update = "2024-07-29"  # Current date
            
            logger.info(f"Updated user memory with insights: persona={insights.buyer_persona_match}, confidence={insights.confidence_score:.2f}")
            
            return user_memory
            
        except Exception as e:
            logger.error(f"Error updating user memory with insights: {e}")
            return user_memory

    def get_personalization_context(self, user_memory: LeadMemory) -> Dict[str, Any]:
        """
        Generates personalization context for response generation.
        
        Args:
            user_memory: User memory with insights
            
        Returns:
            Dict with personalization context
        """
        context = {
            'buyer_persona': getattr(user_memory, 'buyer_persona_match', 'unknown'),
            'professional_level': getattr(user_memory, 'professional_level', 'unknown'),
            'company_size': getattr(user_memory, 'company_size', 'unknown'),
            'industry_sector': getattr(user_memory, 'industry_sector', 'unknown'),
            'pain_points': getattr(user_memory, 'pain_points', []),
            'automation_needs': getattr(user_memory, 'automation_needs', []),
            'technical_level': getattr(user_memory, 'technical_level', 'unknown'),
            'decision_making_power': getattr(user_memory, 'decision_making_power', 'unknown'),
            'confidence_score': getattr(user_memory, 'insights_confidence', 0.0)
        }
        
        return context