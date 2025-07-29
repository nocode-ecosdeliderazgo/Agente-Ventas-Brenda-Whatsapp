"""
Personalize Response Use Case

This use case creates highly personalized responses based on buyer persona detection,
user context, and conversation history.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from app.infrastructure.openai.client import OpenAIClient
from app.application.usecases.extract_user_info_use_case import ExtractUserInfoUseCase
from memory.lead_memory import LeadMemory
from prompts.personalization_prompts import (
    get_personalized_system_prompt,
    get_personalized_response_prompt,
    get_buyer_persona_examples,
    get_communication_approach_info
)

logger = logging.getLogger(__name__)

@dataclass
class PersonalizationResult:
    """Result of personalization process"""
    personalized_response: str
    buyer_persona_detected: str
    personalization_confidence: float
    applied_personalizations: List[str]
    response_metadata: Dict[str, Any]

class PersonalizeResponseUseCase:
    """
    Creates personalized responses based on comprehensive user analysis.
    """
    
    def __init__(
        self, 
        openai_client: OpenAIClient,
        extract_user_info_use_case: ExtractUserInfoUseCase
    ):
        self.openai_client = openai_client
        self.extract_user_info_use_case = extract_user_info_use_case

    async def generate_personalized_response(
        self,
        user_message: str,
        user_memory: LeadMemory,
        conversation_intent: str = "general",
        force_insight_extraction: bool = False
    ) -> PersonalizationResult:
        """
        Generates a highly personalized response based on user context.
        
        Args:
            user_message: The user's message
            user_memory: Current user memory
            conversation_intent: Detected conversation intent
            force_insight_extraction: Force re-extraction of user insights
            
        Returns:
            PersonalizationResult with personalized response and metadata
        """
        try:
            # 1. Update user insights if needed
            updated_memory = await self._ensure_user_insights(user_memory, [user_message], force_insight_extraction)
            
            # 2. Get personalization context
            personalization_context = updated_memory.get_personalization_context()
            
            # 3. Determine personalization strategy
            personalization_strategy = self._determine_personalization_strategy(
                personalization_context, conversation_intent
            )
            
            # 4. Generate personalized response
            personalized_response = await self._generate_ai_personalized_response(
                user_message, personalization_context, conversation_intent, personalization_strategy
            )
            
            # 5. Apply post-processing personalizations
            enhanced_response = self._apply_post_processing_personalizations(
                personalized_response, personalization_context, personalization_strategy
            )
            
            # 6. Calculate personalization confidence
            confidence_score = self._calculate_personalization_confidence(personalization_context)
            
            # 7. Track applied personalizations
            applied_personalizations = self._get_applied_personalizations(personalization_strategy)
            
            return PersonalizationResult(
                personalized_response=enhanced_response,
                buyer_persona_detected=personalization_context['user_profile']['buyer_persona'],
                personalization_confidence=confidence_score,
                applied_personalizations=applied_personalizations,
                response_metadata={
                    'personalization_strategy': personalization_strategy,
                    'user_context_used': personalization_context,
                    'conversation_intent': conversation_intent
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating personalized response: {e}")
            return self._generate_fallback_response(user_message, user_memory)

    async def _ensure_user_insights(
        self, 
        user_memory: LeadMemory, 
        recent_messages: List[str],
        force_extraction: bool = False
    ) -> LeadMemory:
        """Ensures user insights are up-to-date"""
        
        # Check if insights need updating
        needs_update = (
            force_extraction or
            user_memory.buyer_persona_match == "unknown" or
            user_memory.insights_confidence < 0.5 or
            user_memory.last_insights_update != "2024-07-29"  # Today's date
        )
        
        if needs_update:
            logger.info(f"Extracting/updating user insights for {user_memory.user_id}")
            
            # Extract new insights
            insights = await self.extract_user_info_use_case.extract_insights_from_conversation(
                user_memory, recent_messages
            )
            
            # Update memory with insights
            updated_memory = await self.extract_user_info_use_case.update_user_memory_with_insights(
                user_memory, insights
            )
            
            return updated_memory
        
        return user_memory

    def _determine_personalization_strategy(
        self, 
        personalization_context: Dict[str, Any],
        conversation_intent: str
    ) -> Dict[str, Any]:
        """Determines the personalization strategy to apply"""
        
        user_profile = personalization_context['user_profile']
        communication_context = personalization_context['communication_context']
        
        buyer_persona = user_profile['buyer_persona']
        professional_level = user_profile['professional_level']
        decision_making_power = user_profile['decision_making_power']
        urgency_signals = communication_context['urgency_signals']
        
        strategy = {
            'primary_approach': 'general_business',
            'technical_level': 'basic',
            'urgency_handling': 'standard',
            'roi_focus': 'general',
            'example_types': ['general'],
            'personalization_depth': 'medium'
        }
        
        # Determine primary approach based on buyer persona
        persona_approaches = {
            'lucia_copypro': 'creative_roi_focused',
            'marcos_multitask': 'efficiency_operational',
            'sofia_visionaria': 'strategic_executive',
            'ricardo_rh_agil': 'people_development',
            'daniel_data_innovador': 'technical_analytical'
        }
        
        strategy['primary_approach'] = persona_approaches.get(buyer_persona, 'general_business')
        
        # Adjust technical level
        if user_profile['technical_level'] in ['intermediate', 'advanced'] or buyer_persona == 'daniel_data_innovador':
            strategy['technical_level'] = 'advanced'
        elif professional_level in ['senior', 'executive']:
            strategy['technical_level'] = 'business_focused'
        
        # Handle urgency
        if urgency_signals:
            strategy['urgency_handling'] = 'high_priority'
        
        # ROI focus
        roi_focuses = {
            'lucia_copypro': 'marketing_roi',
            'marcos_multitask': 'operational_efficiency',
            'sofia_visionaria': 'strategic_growth',
            'ricardo_rh_agil': 'people_development',
            'daniel_data_innovador': 'technical_capabilities'
        }
        strategy['roi_focus'] = roi_focuses.get(buyer_persona, 'general')
        
        # Example types
        example_mappings = {
            'lucia_copypro': ['marketing_campaigns', 'content_creation', 'lead_generation'],
            'marcos_multitask': ['process_optimization', 'cost_reduction', 'quality_improvement'],
            'sofia_visionaria': ['competitive_advantage', 'scalability', 'market_leadership'],
            'ricardo_rh_agil': ['talent_development', 'training_efficiency', 'employee_retention'],
            'daniel_data_innovador': ['advanced_analytics', 'ml_implementation', 'data_automation']
        }
        strategy['example_types'] = example_mappings.get(buyer_persona, ['general'])
        
        # Personalization depth
        if personalization_context['metadata']['insights_confidence'] > 0.7:
            strategy['personalization_depth'] = 'high'
        elif personalization_context['metadata']['insights_confidence'] > 0.4:
            strategy['personalization_depth'] = 'medium'
        else:
            strategy['personalization_depth'] = 'low'
        
        return strategy

    async def _generate_ai_personalized_response(
        self,
        user_message: str,
        personalization_context: Dict[str, Any],
        conversation_intent: str,
        personalization_strategy: Dict[str, Any]
    ) -> str:
        """Generates AI response with personalization"""
        
        # Build personalized system prompt
        system_prompt = get_personalized_system_prompt(personalization_context)
        
        # Build personalized response prompt
        response_prompt = get_personalized_response_prompt(
            user_message, personalization_context, conversation_intent
        )
        
        # Add strategy-specific instructions
        strategy_instructions = self._build_strategy_instructions(personalization_strategy)
        
        # Generate response with OpenAI
        messages = [
            {"role": "system", "content": f"{system_prompt}\n\n{strategy_instructions}"},
            {"role": "user", "content": response_prompt}
        ]
        
        response = await self.openai_client.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            max_tokens=600,
            temperature=0.3  # Lower temperature for more consistent personalized responses
        )
        
        return response

    def _build_strategy_instructions(self, strategy: Dict[str, Any]) -> str:
        """Builds strategy-specific instructions for AI"""
        
        instructions = f"""
ESTRATEGIA DE PERSONALIZACIÓN APLICADA:
- Enfoque principal: {strategy['primary_approach']}
- Nivel técnico: {strategy['technical_level']}
- Manejo de urgencia: {strategy['urgency_handling']}
- Enfoque de ROI: {strategy['roi_focus']}
- Profundidad de personalización: {strategy['personalization_depth']}

TIPOS DE EJEMPLOS A USAR: {', '.join(strategy['example_types'])}

INSTRUCCIONES ESPECÍFICAS:
"""
        
        # Add approach-specific instructions
        approach_instructions = {
            'creative_roi_focused': "Usa lenguaje creativo pero cuantificado. Enfócate en resultados de marketing medibles.",
            'efficiency_operational': "Sé directo y orientado a resultados. Enfócate en eficiencia y reducción de costos.",
            'strategic_executive': "Usa perspectiva estratégica. Enfócate en ventaja competitiva y crecimiento.",
            'people_development': "Enfócate en impacto en las personas y desarrollo de talento.",
            'technical_analytical': "Usa terminología técnica apropiada. Enfócate en capacidades y especificaciones.",
            'general_business': "Mantén enfoque profesional general orientado a valor de negocio."
        }
        
        instructions += approach_instructions.get(strategy['primary_approach'], "Mantén enfoque profesional.")
        
        # Add urgency handling
        if strategy['urgency_handling'] == 'high_priority':
            instructions += "\n- IMPORTANTE: El usuario muestra señales de urgencia. Responde con prioridad y ofrece acción inmediata."
        
        return instructions

    def _apply_post_processing_personalizations(
        self,
        response: str,
        personalization_context: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> str:
        """Applies final personalizations to the response"""
        
        enhanced_response = response
        
        # Add personalized greeting if it's a first interaction
        if personalization_context['communication_context']['interaction_count'] <= 1:
            buyer_persona = personalization_context['user_profile']['buyer_persona']
            if buyer_persona != 'unknown':
                enhanced_response = self._add_personalized_greeting(enhanced_response, buyer_persona)
        
        # Add personalized signature/closing
        enhanced_response = self._add_personalized_closing(enhanced_response, strategy)
        
        return enhanced_response

    def _add_personalized_greeting(self, response: str, buyer_persona: str) -> str:
        """Adds personalized greeting based on buyer persona"""
        
        persona_greetings = {
            'lucia_copypro': "Como especialista en marketing digital,",
            'marcos_multitask': "Entiendo los desafíos operativos que enfrentas,",
            'sofia_visionaria': "Como líder visionario,",
            'ricardo_rh_agil': "Sabiendo tu enfoque en desarrollo de talento,",
            'daniel_data_innovador': "Con tu background en análisis de datos,"
        }
        
        greeting = persona_greetings.get(buyer_persona, "")
        if greeting and not response.lower().startswith("como"):
            return f"{greeting} {response.lower()}"
        
        return response

    def _add_personalized_closing(self, response: str, strategy: Dict[str, Any]) -> str:
        """Adds personalized closing based on strategy"""
        
        closings = {
            'creative_roi_focused': "\n\n¿Te gustaría ver ejemplos específicos de campañas optimizadas con IA?",
            'efficiency_operational': "\n\n¿Quieres que analicemos qué procesos de tu operación podrían automatizarse?",
            'strategic_executive': "\n\n¿Te interesa discutir cómo esto se alinea con tu visión estratégica?",
            'people_development': "\n\n¿Te gustaría ver cómo otros líderes han desarrollado sus equipos con IA?",
            'technical_analytical': "\n\n¿Quieres revisar las especificaciones técnicas de implementación?",
            'general_business': "\n\n¿Te gustaría conocer más detalles sobre cómo aplicar esto en tu empresa?"
        }
        
        closing = closings.get(strategy['primary_approach'], "")
        
        # Avoid duplicate closings
        if closing and not any(phrase in response.lower() for phrase in ['te gustaría', '¿quieres', '¿te interesa']):
            return response + closing
        
        return response

    def _calculate_personalization_confidence(self, personalization_context: Dict[str, Any]) -> float:
        """Calculates confidence in personalization quality"""
        
        confidence = 0.0
        
        # Base confidence from insights
        confidence += personalization_context['metadata']['insights_confidence'] * 0.4
        
        # Buyer persona detection
        if personalization_context['user_profile']['buyer_persona'] != 'unknown':
            confidence += 0.3
        
        # Profile completeness
        profile_fields = ['professional_level', 'company_size', 'industry_sector']
        complete_fields = sum(1 for field in profile_fields 
                             if personalization_context['user_profile'][field] != 'unknown')
        confidence += (complete_fields / len(profile_fields)) * 0.2
        
        # Interaction history
        if personalization_context['communication_context']['interaction_count'] > 3:
            confidence += 0.1
        
        return min(confidence, 1.0)

    def _get_applied_personalizations(self, strategy: Dict[str, Any]) -> List[str]:
        """Gets list of applied personalizations for tracking"""
        
        personalizations = []
        
        if strategy['primary_approach'] != 'general_business':
            personalizations.append(f"buyer_persona_approach_{strategy['primary_approach']}")
        
        if strategy['technical_level'] != 'basic':
            personalizations.append(f"technical_level_{strategy['technical_level']}")
        
        if strategy['urgency_handling'] == 'high_priority':
            personalizations.append("urgency_prioritized")
        
        if strategy['roi_focus'] != 'general':
            personalizations.append(f"roi_focus_{strategy['roi_focus']}")
        
        if strategy['personalization_depth'] == 'high':
            personalizations.append("deep_personalization")
        
        return personalizations

    def _generate_fallback_response(self, user_message: str, user_memory: LeadMemory) -> PersonalizationResult:
        """Generates fallback response when personalization fails"""
        
        fallback_response = f"""¡Hola{', ' + user_memory.name if user_memory.name else ''}! 

Gracias por tu interés en nuestros cursos de IA aplicada para empresas.

Me gustaría entender mejor tus necesidades específicas para poder ayudarte de la mejor manera. 

¿Podrías contarme un poco sobre tu rol y los desafíos principales que enfrentas en tu empresa?

¡Estoy aquí para ayudarte! 😊"""
        
        return PersonalizationResult(
            personalized_response=fallback_response,
            buyer_persona_detected="unknown",
            personalization_confidence=0.0,
            applied_personalizations=["fallback_response"],
            response_metadata={"fallback_reason": "personalization_error"}
        )

    async def analyze_conversation_patterns(self, user_memory: LeadMemory) -> Dict[str, Any]:
        """
        Analyzes conversation patterns for continuous personalization improvement.
        
        Args:
            user_memory: User memory with conversation history
            
        Returns:
            Analysis of conversation patterns and recommendations
        """
        
        analysis = {
            'conversation_progression': 'unknown',
            'engagement_level': 'unknown',
            'personalization_effectiveness': 0.0,
            'recommendations': []
        }
        
        try:
            # Analyze interaction count vs stage progression
            if user_memory.interaction_count > 5 and user_memory.stage == 'first_contact':
                analysis['conversation_progression'] = 'slow'
                analysis['recommendations'].append('increase_personalization_depth')
            elif user_memory.interaction_count <= 3 and user_memory.stage in ['course_selection', 'sales_agent']:
                analysis['conversation_progression'] = 'fast'
                analysis['recommendations'].append('maintain_current_approach')
            else:
                analysis['conversation_progression'] = 'normal'
            
            # Analyze engagement based on lead score progression
            if user_memory.lead_score > 70:
                analysis['engagement_level'] = 'high'
            elif user_memory.lead_score > 50:
                analysis['engagement_level'] = 'medium'
            else:
                analysis['engagement_level'] = 'low'
                analysis['recommendations'].append('try_different_approach')
            
            # Calculate personalization effectiveness
            if hasattr(user_memory, 'insights_confidence'):
                base_effectiveness = user_memory.insights_confidence
                
                # Adjust based on conversation progression
                if analysis['conversation_progression'] == 'fast':
                    base_effectiveness += 0.2
                elif analysis['conversation_progression'] == 'slow':
                    base_effectiveness -= 0.1
                
                analysis['personalization_effectiveness'] = min(base_effectiveness, 1.0)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns: {e}")
            return analysis