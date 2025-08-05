"""
Sistema de Respuestas Proactivas Basadas en Patrones
Identifica patrones de comportamiento y genera respuestas anticipadas
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from app.infrastructure.openai.client import OpenAIClient
from memory.lead_memory import LeadMemoryManager

logger = logging.getLogger(__name__)

class ProactiveResponsesUseCase:
    """Genera respuestas proactivas basadas en patrones de comportamiento"""
    
    def __init__(self, openai_client: OpenAIClient, memory_manager: LeadMemoryManager):
        self.openai_client = openai_client
        self.memory_manager = memory_manager
        self.logger = logger
        
        # Patrones de comportamiento que activan respuestas proactivas
        self.behavior_patterns = {
            "abandono_inmediato": {
                "trigger": "usuario_no_responde_5min",
                "condition": lambda data: self._check_immediate_abandonment(data),
                "response_type": "re_engagement"
            },
            "pregunta_repetitiva": {
                "trigger": "misma_pregunta_3_veces",
                "condition": lambda data: self._check_repetitive_questions(data),
                "response_type": "clarification"
            },
            "interes_alto_sin_accion": {
                "trigger": "muchas_preguntas_sin_compra",
                "condition": lambda data: self._check_high_interest_no_action(data),
                "response_type": "push_gentle"
            },
            "confusion_evidente": {
                "trigger": "preguntas_confusas_seguidas",
                "condition": lambda data: self._check_confusion_pattern(data),
                "response_type": "simplification"
            },
            "decision_paralysis": {
                "trigger": "comparaciones_excesivas",
                "condition": lambda data: self._check_decision_paralysis(data),
                "response_type": "decision_help"
            },
            "momentum_positivo": {
                "trigger": "respuestas_positivas_consecutivas",
                "condition": lambda data: self._check_positive_momentum(data),
                "response_type": "accelerate"
            }
        }
    
    async def analyze_and_respond(self, user_id: str, current_message: str = None) -> Dict:
        """
        Analiza patrones y determina si generar respuesta proactiva
        
        Args:
            user_id: ID del usuario
            current_message: Mensaje actual (opcional)
        
        Returns:
            Dict con recomendación de respuesta proactiva o None
        """
        try:
            # 1. Obtener datos del usuario
            user_data = self._get_user_behavior_data(user_id)
            
            # 2. Analizar patrones
            detected_patterns = []
            for pattern_name, pattern_config in self.behavior_patterns.items():
                if pattern_config["condition"](user_data):
                    detected_patterns.append({
                        "name": pattern_name,
                        "type": pattern_config["response_type"],
                        "trigger": pattern_config["trigger"]
                    })
            
            # 3. Seleccionar patrón más relevante
            if not detected_patterns:
                return {"should_respond": False, "reason": "no_patterns_detected"}
            
            primary_pattern = self._select_primary_pattern(detected_patterns, user_data)
            
            # 4. Generar respuesta proactiva
            proactive_response = await self._generate_proactive_response(
                user_id, primary_pattern, user_data, current_message
            )
            
            # 5. Registrar patrón detectado
            await self._log_pattern_detection(user_id, primary_pattern)
            
            return {
                "should_respond": True,
                "pattern": primary_pattern,
                "response": proactive_response,
                "confidence": proactive_response.get("confidence", 0.7),
                "timing": proactive_response.get("suggested_timing", "immediate")
            }
            
        except Exception as e:
            self.logger.error(f"Error en análisis proactivo: {e}")
            return {"should_respond": False, "reason": "error", "error": str(e)}
    
    def _get_user_behavior_data(self, user_id: str) -> Dict:
        """Recopila datos de comportamiento del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            # Obtener historial de mensajes recientes
            message_history = getattr(user_memory, 'message_history', [])
            
            # Obtener emociones recientes
            emotion_history = getattr(user_memory, 'emotion_history', [])
            
            # Calcular métricas de comportamiento
            now = datetime.now()
            
            return {
                "user_id": user_id,
                "message_count": len(message_history),
                "recent_messages": message_history[-10:] if message_history else [],
                "recent_emotions": emotion_history[-5:] if emotion_history else [],
                "last_message_time": getattr(user_memory, 'last_interaction', None),
                "conversation_duration": self._calculate_conversation_duration(user_memory),
                "question_count": self._count_questions(message_history),
                "purchase_signals": getattr(user_memory, 'purchase_signals', 0),
                "current_emotion": getattr(user_memory, 'current_emotion', 'neutral'),
                "buyer_persona": getattr(user_memory, 'buyer_persona', None),
                "lead_score": getattr(user_memory, 'lead_score', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos de comportamiento: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    def _check_immediate_abandonment(self, data: Dict) -> bool:
        """Detecta abandono inmediato después de mensaje inicial"""
        if not data.get("last_message_time"):
            return False
            
        try:
            last_msg_time = datetime.fromisoformat(data["last_message_time"])
            time_diff = datetime.now() - last_msg_time
            
            # Abandono si no responde en 5 minutos después de mensaje inicial
            return (
                time_diff > timedelta(minutes=5) and
                data.get("message_count", 0) <= 2 and
                time_diff < timedelta(hours=1)  # Pero no muy antiguo
            )
        except:
            return False
    
    def _check_repetitive_questions(self, data: Dict) -> bool:
        """Detecta preguntas repetitivas"""
        recent_messages = data.get("recent_messages", [])
        if len(recent_messages) < 3:
            return False
        
        # Buscar patrones similares en mensajes recientes
        question_keywords = []
        for msg in recent_messages[-5:]:
            if "?" in msg or any(q_word in msg.lower() for q_word in ["cuanto", "cuando", "como", "donde", "que"]):
                # Extraer keywords principales
                words = [word.lower() for word in msg.split() if len(word) > 3]
                question_keywords.append(set(words))
        
        # Verificar similitud entre preguntas
        if len(question_keywords) >= 3:
            for i in range(len(question_keywords) - 2):
                similarity = len(question_keywords[i] & question_keywords[i+1] & question_keywords[i+2])
                if similarity >= 2:  # Al menos 2 palabras en común
                    return True
        
        return False
    
    def _check_high_interest_no_action(self, data: Dict) -> bool:
        """Detecta alto interés sin tomar acción"""
        return (
            data.get("question_count", 0) >= 5 and
            data.get("purchase_signals", 0) == 0 and
            data.get("conversation_duration", 0) > 10  # Más de 10 minutos
        )
    
    def _check_confusion_pattern(self, data: Dict) -> bool:
        """Detecta patrón de confusión"""
        recent_emotions = data.get("recent_emotions", [])
        if len(recent_emotions) < 3:
            return False
        
        # Buscar emociones de confusión/frustración consecutivas
        confusion_emotions = ["frustrado", "escéptico"]
        recent_emotion_types = [emotion.get("emotion") for emotion in recent_emotions[-3:]]
        
        confusion_count = sum(1 for emotion in recent_emotion_types if emotion in confusion_emotions)
        return confusion_count >= 2
    
    def _check_decision_paralysis(self, data: Dict) -> bool:
        """Detecta parálisis de decisión"""
        recent_messages = data.get("recent_messages", [])
        
        comparison_keywords = ["versus", "vs", "diferencia", "comparar", "mejor", "peor", "o"]
        comparison_count = 0
        
        for msg in recent_messages[-5:]:
            if any(keyword in msg.lower() for keyword in comparison_keywords):
                comparison_count += 1
        
        return (
            comparison_count >= 3 and
            data.get("purchase_signals", 0) == 0 and
            data.get("message_count", 0) >= 8
        )
    
    def _check_positive_momentum(self, data: Dict) -> bool:
        """Detecta momento positivo para acelerar"""
        recent_emotions = data.get("recent_emotions", [])
        if len(recent_emotions) < 2:
            return False
        
        positive_emotions = ["emocionado", "curioso", "decidido"]
        recent_emotion_types = [emotion.get("emotion") for emotion in recent_emotions[-3:]]
        
        positive_count = sum(1 for emotion in recent_emotion_types if emotion in positive_emotions)
        
        return (
            positive_count >= 2 and
            data.get("current_emotion") in positive_emotions and
            data.get("lead_score", 0) > 60
        )
    
    def _select_primary_pattern(self, patterns: List[Dict], user_data: Dict) -> Dict:
        """Selecciona el patrón más relevante para responder"""
        
        # Prioridades por tipo de patrón
        priority_order = {
            "abandono_inmediato": 10,
            "momentum_positivo": 9,
            "decision_paralysis": 8,
            "confusion_evidente": 7,
            "interes_alto_sin_accion": 6,
            "pregunta_repetitiva": 5
        }
        
        # Ordenar por prioridad
        patterns.sort(key=lambda p: priority_order.get(p["name"], 0), reverse=True)
        
        return patterns[0]
    
    async def _generate_proactive_response(self, user_id: str, pattern: Dict, user_data: Dict, current_message: str = None) -> Dict:
        """Genera respuesta proactiva personalizada"""
        
        pattern_name = pattern["name"]
        response_type = pattern["type"]
        
        # Templates base por tipo de patrón
        response_templates = {
            "re_engagement": await self._generate_reengagement_response(user_data),
            "clarification": await self._generate_clarification_response(user_data),
            "push_gentle": await self._generate_gentle_push_response(user_data),
            "simplification": await self._generate_simplification_response(user_data),
            "decision_help": await self._generate_decision_help_response(user_data),
            "accelerate": await self._generate_acceleration_response(user_data)
        }
        
        base_response = response_templates.get(response_type, {})
        
        # Personalizar según buyer persona
        personalized_response = await self._personalize_proactive_response(
            base_response, user_data, pattern_name
        )
        
        return {
            "message": personalized_response.get("message", ""),
            "confidence": personalized_response.get("confidence", 0.7),
            "suggested_timing": personalized_response.get("timing", "immediate"),
            "follow_up_actions": personalized_response.get("actions", []),
            "pattern_detected": pattern_name
        }
    
    async def _generate_reengagement_response(self, user_data: Dict) -> Dict:
        """Genera respuesta de re-engagement"""
        return {
            "message": f"""🤔 Veo que quizás te fuiste ocupado/a...

No hay problema, entiendo que liderar una empresa requiere estar en mil cosas a la vez.

💡 **¿Te ayudo con algo específico en 2 minutos?**
• Precio y detalles del curso
• Testimonios de otros CEOs
• Demo rápida de resultados

¿Por dónde empezamos?""",
            "confidence": 0.8,
            "timing": "immediate",
            "actions": ["offer_quick_info", "lower_barrier"]
        }
    
    async def _generate_clarification_response(self, user_data: Dict) -> Dict:
        """Genera respuesta de clarificación"""
        return {
            "message": f"""📋 Veo que tienes varias preguntas similares...

**Déjame aclararte todo de una vez:**

🎯 **Curso**: Experto en IA para Profesionales PyME
💰 **Inversión**: $4,500 MXN (pagos flexibles disponibles)
📅 **Duración**: 8 sesiones prácticas (12 horas total)
💻 **Modalidad**: 100% online con casos reales

¿Esto responde tus dudas principales o hay algo específico que quieres profundizar?""",
            "confidence": 0.85,
            "timing": "immediate",
            "actions": ["provide_summary", "ask_specific_question"]
        }
    
    async def _generate_gentle_push_response(self, user_data: Dict) -> Dict:
        """Genera empuje gentil hacia la acción"""
        return {
            "message": f"""🎯 Veo que tienes mucho interés en automatizar con IA...

**La buena noticia:** Estás haciendo las preguntas correctas.
**El siguiente paso:** Probablemente sea ver esto en acción.

💡 **Te propongo algo:**
• Agenda una demo de 15 min conmigo
• Te muestro exactamente cómo aplicarías esto en tu empresa
• Sin compromiso, solo para que veas el potencial real

¿Te parece bien hoy en la tarde o prefieres mañana?""",
            "confidence": 0.9,
            "timing": "immediate",
            "actions": ["schedule_demo", "show_value", "create_urgency"]
        }
    
    async def _generate_simplification_response(self, user_data: Dict) -> Dict:
        """Genera respuesta de simplificación"""
        return {
            "message": f"""🔄 Déjame simplificar esto...

**En 3 puntos claros:**

1️⃣ **Qué obtienes**: Automatizaciones que te ahorran 20+ horas/semana
2️⃣ **Cómo funciona**: 8 sesiones prácticas donde construyes tus propias herramientas
3️⃣ **Resultado**: Sistemas de IA funcionando en tu empresa desde la primera semana

**¿Cuál de estos 3 puntos quieres que desarrolle más?**""",
            "confidence": 0.8,
            "timing": "immediate",
            "actions": ["break_down_complexity", "focus_on_benefits"]
        }
    
    async def _generate_decision_help_response(self, user_data: Dict) -> Dict:
        """Genera ayuda para tomar decisión"""
        return {
            "message": f"""🤔 Te veo comparando opciones (excelente approach de CEO)...

**Te ayudo a decidir con 3 preguntas:**

1️⃣ **¿Cuál es tu mayor dolor de automatización ahora mismo?**
2️⃣ **¿Qué presupuesto mensual destinas a herramientas/capacitación?**
3️⃣ **¿Qué timeframe tienes para implementar IA en tu empresa?**

Con estas respuestas te doy una recomendación específica para TU situación.

**¿Empezamos por la pregunta 1?**""",
            "confidence": 0.9,
            "timing": "immediate",
            "actions": ["guided_decision", "personalize_recommendation"]
        }
    
    async def _generate_acceleration_response(self, user_data: Dict) -> Dict:
        """Genera respuesta para acelerar momentum positivo"""
        return {
            "message": f"""🚀 ¡Perfecto! Veo que estás convencido del valor...

**Momento ideal para tomar acción:**

💎 **Oferta especial para CEOs decisivos:**
• 15% descuento si confirmas hoy
• Acceso inmediato a templates premium
• Sesión 1-on-1 de estrategia incluida

💳 **Opciones de pago flexibles:**
• Pago único: $3,825 MXN (descuento aplicado)
• 2 pagos: $2,250 MXN c/u
• 3 pagos: $1,575 MXN c/u

**¿Con cuál opción arrancamos?**""",
            "confidence": 0.95,
            "timing": "immediate",
            "actions": ["create_offer", "provide_payment_options", "close_sale"]
        }
    
    async def _personalize_proactive_response(self, base_response: Dict, user_data: Dict, pattern: str) -> Dict:
        """Personaliza respuesta según buyer persona"""
        
        buyer_persona = user_data.get("buyer_persona")
        current_emotion = user_data.get("current_emotion", "neutral")
        
        # Ajustar tono según emoción actual
        if current_emotion == "frustrado":
            base_response["message"] = base_response["message"].replace("🚀", "🤝").replace("¡Perfecto!", "Entiendo tu situación")
        elif current_emotion == "ansioso":
            base_response["message"] = "⚡ " + base_response["message"]
        
        # Ajustar según buyer persona
        if buyer_persona == "CEO":
            base_response["message"] = base_response["message"].replace("empresas", "tu empresa").replace("profesionales", "líderes como tú")
        elif buyer_persona == "Operations Manager":
            base_response["message"] = base_response["message"].replace("automatizar", "optimizar operaciones")
        
        return base_response
    
    async def _log_pattern_detection(self, user_id: str, pattern: Dict):
        """Registra patrón detectado en memoria del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            if not hasattr(user_memory, 'pattern_history'):
                user_memory.pattern_history = []
            
            pattern_entry = {
                "pattern": pattern["name"],
                "type": pattern["type"],
                "detected_at": datetime.now().isoformat(),
                "trigger": pattern["trigger"]
            }
            
            user_memory.pattern_history.append(pattern_entry)
            
            # Mantener solo los últimos 15 patrones
            if len(user_memory.pattern_history) > 15:
                user_memory.pattern_history = user_memory.pattern_history[-15:]
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error guardando patrón detectado: {e}")
    
    def _calculate_conversation_duration(self, user_memory) -> int:
        """Calcula duración de conversación en minutos"""
        try:
            first_interaction = getattr(user_memory, 'first_interaction', None)
            last_interaction = getattr(user_memory, 'last_interaction', None)
            
            if not first_interaction or not last_interaction:
                return 0
            
            start_time = datetime.fromisoformat(first_interaction)
            end_time = datetime.fromisoformat(last_interaction)
            
            duration = (end_time - start_time).total_seconds() / 60
            return int(duration)
            
        except:
            return 0
    
    def _count_questions(self, message_history: List[str]) -> int:
        """Cuenta preguntas en el historial"""
        question_count = 0
        for message in message_history:
            if "?" in message or any(q_word in message.lower() for q_word in ["cuanto", "cuando", "como", "donde", "que", "cual", "quien"]):
                question_count += 1
        return question_count