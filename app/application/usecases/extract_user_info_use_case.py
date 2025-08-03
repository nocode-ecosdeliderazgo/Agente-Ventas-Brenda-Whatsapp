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
        
        # 🆕 Enhanced buyer persona patterns with advanced matching
        self.buyer_persona_patterns = {
            'lucia_copypro': {
                'primary_keywords': ['marketing digital', 'content marketing', 'social media', 'campaigns', 'agencia marketing'],
                'secondary_keywords': ['marketing', 'campaña', 'contenido', 'creativo', 'diseño', 'clientes', 'leads', 'brand'],
                'industry_context': ['agencia', 'publicidad', 'comunicación', 'medios', 'creative', 'branding'],
                'specific_roles': ['marketing manager', 'digital marketing manager', 'content manager', 'social media manager', 
                                 'creative director', 'brand manager', 'community manager', 'growth marketing'],
                'pain_indicators': ['crear contenido', 'generar ideas', 'campañas efectivas', 'engagement', 'conversión',
                                  'crear posts', 'contenido viral', 'creatividad bloqueada', 'tiempo contenido'],
                'automation_signals': ['automatizar posts', 'generar contenido', 'análisis campañas', 'reportes automáticos',
                                     'programar publicaciones', 'ideas automáticas', 'copywriting'],
                'business_context': ['20-100 empleados', 'agencia pequeña', 'freelance', 'marketing team', 'cliente b2b'],
                'urgency_signals': ['campaña urgente', 'deadline', 'cliente esperando', 'resultados rápidos'],
                'weight_multipliers': {'primary_keywords': 4, 'specific_roles': 3, 'pain_indicators': 2, 'industry_context': 2}
            },
            'marcos_multitask': {
                'primary_keywords': ['operaciones', 'procesos empresariales', 'efficiency', 'productividad operativa', 'manufactura'],
                'secondary_keywords': ['producción', 'calidad', 'inventarios', 'logística', 'cadena suministro', 'equipos'],
                'industry_context': ['manufactura', 'industrial', 'producción', 'fábrica', 'planta', 'almacén', 'logística'],
                'specific_roles': ['operations manager', 'gerente de operaciones', 'director operativo', 'jefe de producción',
                                 'plant manager', 'production manager', 'process improvement', 'lean manager'],
                'pain_indicators': ['procesos manuales', 'ineficiencias', 'costos operativos', 'tiempo perdido', 'errores humanos',
                                  'reportes manuales', 'control inventario', 'seguimiento producción'],
                'automation_signals': ['automatizar procesos', 'streamline operations', 'reportes automáticos', 
                                     'control automático', 'optimizar workflows', 'reducir manual work'],
                'business_context': ['50-200 empleados', 'empresa manufacturera', 'pyme industrial', 'planta producción'],
                'urgency_signals': ['reducir costos ya', 'eficiencia inmediata', 'competencia', 'presión resultados'],
                'weight_multipliers': {'primary_keywords': 4, 'specific_roles': 3, 'pain_indicators': 3, 'industry_context': 2}
            },
            'sofia_visionaria': {
                'primary_keywords': ['ceo', 'founder', 'director general', 'estrategia empresarial', 'crecimiento empresa'],
                'secondary_keywords': ['liderazgo', 'visión', 'innovación', 'competitividad', 'escalabilidad', 'transformación'],
                'industry_context': ['servicios profesionales', 'consultoría', 'tecnología', 'startups', 'scale-up'],
                'specific_roles': ['ceo', 'chief executive', 'founder', 'co-founder', 'director general', 'presidente',
                                 'managing director', 'executive director', 'dueño empresa', 'emprendedor'],
                'pain_indicators': ['competencia feroz', 'crecimiento estancado', 'falta innovación', 'decisiones lentas',
                                  'escalabilidad limitada', 'dependencia personal', 'ventaja competitiva', 'diferenciación'],
                'automation_signals': ['decisiones basadas datos', 'análisis estratégico', 'insights mercado',
                                     'automatizar decisiones', 'inteligencia competitiva', 'predictive analytics'],
                'business_context': ['30-150 empleados', 'servicios profesionales', 'consultoría', 'b2b services'],
                'urgency_signals': ['transformación digital urgente', 'competencia avanza', 'oportunidad mercado'],
                'weight_multipliers': {'primary_keywords': 5, 'specific_roles': 4, 'pain_indicators': 2, 'urgency_signals': 3}
            },
            'ricardo_rh_agil': {
                'primary_keywords': ['recursos humanos', 'people operations', 'talent management', 'rrhh', 'gestión talento'],
                'secondary_keywords': ['empleados', 'capacitación', 'training', 'desarrollo', 'reclutamiento', 'onboarding'],
                'industry_context': ['scale-up', 'tecnología', 'servicios', 'crecimiento rápido', 'startup'],
                'specific_roles': ['hr manager', 'people operations', 'talent manager', 'hr director', 'chief people officer',
                                 'learning & development', 'talent acquisition', 'hr business partner'],
                'pain_indicators': ['retención talento', 'capacitación escalable', 'onboarding lento', 'skills gap',
                                  'cultura empresa', 'engagement empleados', 'desarrollo profesional'],
                'automation_signals': ['training automático', 'onboarding digital', 'evaluaciones automáticas',
                                     'desarrollo personalizado', 'learning paths', 'skill assessment'],
                'business_context': ['100-300 empleados', 'crecimiento rápido', 'tech company', 'scale-up'],
                'urgency_signals': ['retención crítica', 'skills shortage', 'crecimiento acelerado', 'talent war'],
                'weight_multipliers': {'primary_keywords': 4, 'specific_roles': 3, 'pain_indicators': 3, 'urgency_signals': 2}
            },
            'daniel_data_innovador': {
                'primary_keywords': ['business intelligence', 'data analysis', 'analytics', 'data science', 'insights'],
                'secondary_keywords': ['datos', 'métricas', 'reportes', 'dashboards', 'kpis', 'análisis', 'estadísticas'],
                'industry_context': ['tecnología', 'fintech', 'e-commerce', 'saas', 'digital', 'corporativo'],
                'specific_roles': ['data analyst', 'business intelligence', 'data scientist', 'analytics manager',
                                 'insights analyst', 'bi developer', 'data manager', 'innovation analyst'],
                'pain_indicators': ['datos dispersos', 'reportes manuales', 'falta insights', 'decisiones sin datos',
                                  'análisis lento', 'dashboards estáticos', 'datos no confiables'],
                'automation_signals': ['reportes automáticos', 'análisis predictivo', 'ai insights', 'automated dashboards',
                                     'data pipelines', 'machine learning', 'predictive models'],
                'business_context': ['200+ empleados', 'data-driven', 'tecnología', 'corporativo', 'digital transformation'],
                'urgency_signals': ['competitive intelligence', 'data-driven decisions', 'real-time insights'],
                'weight_multipliers': {'primary_keywords': 4, 'specific_roles': 3, 'pain_indicators': 2, 'automation_signals': 3}
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

🎯 BUYER PERSONAS ESPECÍFICOS (prioriza exactitud sobre generalización):

**lucia_copypro** - Marketing Digital Manager (20-100 empleados)
• Keywords clave: "marketing digital", "content marketing", "social media", "campaigns", "agencia"
• Roles específicos: marketing manager, content manager, social media manager, creative director
• Pain points: crear contenido, generar ideas, campañas efectivas, engagement, conversión
• Contexto: agencias, publicidad, medios, creative, branding

**marcos_multitask** - Operations Manager (50-200 empleados)  
• Keywords clave: "operaciones", "procesos empresariales", "efficiency", "productividad operativa", "manufactura"
• Roles específicos: operations manager, gerente de operaciones, director operativo, plant manager
• Pain points: procesos manuales, ineficiencias, costos operativos, reportes manuales
• Contexto: manufactura, industrial, producción, fábrica, logística

**sofia_visionaria** - CEO/Founder (30-150 empleados)
• Keywords clave: "ceo", "founder", "director general", "estrategia empresarial", "crecimiento empresa"
• Roles específicos: ceo, founder, director general, managing director, dueño empresa
• Pain points: competencia feroz, crecimiento estancado, falta innovación, escalabilidad
• Contexto: servicios profesionales, consultoría, startups, scale-up

**ricardo_rh_agil** - Head of Talent (100-300 empleados)
• Keywords clave: "recursos humanos", "people operations", "talent management", "rrhh"
• Roles específicos: hr manager, people operations, talent manager, chief people officer
• Pain points: retención talento, capacitación escalable, skills gap, engagement empleados
• Contexto: scale-up, tecnología, crecimiento rápido, startup

**daniel_data_innovador** - BI/Data Analyst (200+ empleados)
• Keywords clave: "business intelligence", "data analysis", "analytics", "data science"
• Roles específicos: data analyst, business intelligence, data scientist, analytics manager
• Pain points: datos dispersos, reportes manuales, falta insights, decisiones sin datos
• Contexto: tecnología, fintech, corporativo, digital transformation

⚠️ CRITERIOS ESTRICTOS: Solo asignar buyer_persona_match si hay evidencia CLARA y ESPECÍFICA. 
Si hay dudas, usar "unknown". Mejor precisión que recall.

Responde SOLO con JSON válido, sin markdown ni explicaciones.
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
        """🆕 Enhanced AI insights with advanced pattern-based detection"""
        
        text_lower = conversation_text.lower()
        
        # Enhance buyer persona detection with advanced scoring
        if insights.buyer_persona_match == 'unknown':
            persona_scores = {}
            persona_details = {}
            
            for persona, patterns in self.buyer_persona_patterns.items():
                score = 0.0
                matches = {'categories': [], 'total_matches': 0}
                
                # Weight multipliers for different categories
                multipliers = patterns.get('weight_multipliers', {})
                
                # Check primary keywords (highest weight)
                primary_matches = [kw for kw in patterns.get('primary_keywords', []) if kw in text_lower]
                if primary_matches:
                    weight = multipliers.get('primary_keywords', 4)
                    score += len(primary_matches) * weight
                    matches['categories'].append(f"primary_keywords({len(primary_matches)})")
                    matches['total_matches'] += len(primary_matches)
                
                # Check specific roles (high weight)
                role_matches = [role for role in patterns.get('specific_roles', []) if role in text_lower]
                if role_matches:
                    weight = multipliers.get('specific_roles', 3)
                    score += len(role_matches) * weight
                    matches['categories'].append(f"specific_roles({len(role_matches)})")
                    matches['total_matches'] += len(role_matches)
                
                # Check industry context
                industry_matches = [ctx for ctx in patterns.get('industry_context', []) if ctx in text_lower]
                if industry_matches:
                    weight = multipliers.get('industry_context', 2)
                    score += len(industry_matches) * weight
                    matches['categories'].append(f"industry_context({len(industry_matches)})")
                    matches['total_matches'] += len(industry_matches)
                
                # Check pain indicators
                pain_matches = [pain for pain in patterns.get('pain_indicators', []) if pain in text_lower]
                if pain_matches:
                    weight = multipliers.get('pain_indicators', 2)
                    score += len(pain_matches) * weight
                    matches['categories'].append(f"pain_indicators({len(pain_matches)})")
                    matches['total_matches'] += len(pain_matches)
                
                # Check automation signals
                automation_matches = [sig for sig in patterns.get('automation_signals', []) if sig in text_lower]
                if automation_matches:
                    weight = multipliers.get('automation_signals', 2)
                    score += len(automation_matches) * weight
                    matches['categories'].append(f"automation_signals({len(automation_matches)})")
                    matches['total_matches'] += len(automation_matches)
                
                # Check business context
                business_matches = [ctx for ctx in patterns.get('business_context', []) if ctx in text_lower]
                if business_matches:
                    weight = multipliers.get('business_context', 1)
                    score += len(business_matches) * weight
                    matches['categories'].append(f"business_context({len(business_matches)})")
                    matches['total_matches'] += len(business_matches)
                
                # Check urgency signals (bonus multiplier)
                urgency_matches = [sig for sig in patterns.get('urgency_signals', []) if sig in text_lower]
                if urgency_matches:
                    weight = multipliers.get('urgency_signals', 2)
                    score += len(urgency_matches) * weight
                    matches['categories'].append(f"urgency_signals({len(urgency_matches)})")
                    matches['total_matches'] += len(urgency_matches)
                
                # Check secondary keywords (lower weight)
                secondary_matches = [kw for kw in patterns.get('secondary_keywords', []) if kw in text_lower]
                if secondary_matches:
                    weight = multipliers.get('secondary_keywords', 1)
                    score += len(secondary_matches) * weight
                    matches['categories'].append(f"secondary_keywords({len(secondary_matches)})")
                    matches['total_matches'] += len(secondary_matches)
                
                # Apply contextual bonuses
                if matches['total_matches'] >= 3:  # Multiple category matches
                    score *= 1.2  # 20% bonus
                
                if len(matches['categories']) >= 3:  # Diverse category matches
                    score *= 1.1  # 10% bonus
                
                persona_scores[persona] = score
                persona_details[persona] = matches
            
            # Select highest scoring persona with improved threshold
            if persona_scores:
                best_persona = max(persona_scores, key=persona_scores.get)
                best_score = persona_scores[best_persona]
                
                # Dynamic threshold based on match quality
                min_threshold = 6.0  # Minimum score required
                confidence_threshold = 8.0  # High confidence score
                
                if best_score >= min_threshold:
                    insights.buyer_persona_match = best_persona
                    
                    # Log matching details for debugging
                    matches_info = persona_details[best_persona]
                    logger.info(f"🎯 Buyer persona match: {best_persona} (score: {best_score:.1f})")
                    logger.info(f"   Matches: {', '.join(matches_info['categories'])}")
                    logger.info(f"   Confidence: {'HIGH' if best_score >= confidence_threshold else 'MEDIUM'}")
                else:
                    logger.info(f"🤔 No strong buyer persona match (best: {best_persona} with {best_score:.1f}, need {min_threshold})")
        
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