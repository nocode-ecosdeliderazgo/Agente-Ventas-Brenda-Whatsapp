"""
Sistema de Detección de Emociones del Usuario
Analiza el tono emocional de los mensajes para personalizar respuestas
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import re

from app.infrastructure.openai.client import OpenAIClient
from memory.lead_memory import LeadMemoryManager

logger = logging.getLogger(__name__)

class EmotionDetectionUseCase:
    """Detecta emociones y estado emocional del usuario"""
    
    def __init__(self, openai_client: OpenAIClient, memory_manager: LeadMemoryManager):
        self.openai_client = openai_client
        self.memory_manager = memory_manager
        self.logger = logger
        
        # Patrones de emociones básicas
        self.emotion_patterns = {
            "frustrado": [
                "no entiendo", "no funciona", "es complicado", "difícil", 
                "perdí tiempo", "cansado", "aburrido", "molesto"
            ],
            "emocionado": [
                "excelente", "perfecto", "increíble", "genial", "me encanta",
                "fantástico", "maravilloso", "impresionante"
            ],
            "ansioso": [
                "urgente", "rápido", "pronto", "cuando", "ya", "necesito ya",
                "no puedo esperar", "cuánto falta"
            ],
            "escéptico": [
                "seguro", "confiable", "realmente funciona", "garantía",
                "pruebas", "evidencia", "dudas", "no estoy convencido"
            ],
            "curioso": [
                "interesante", "cómo funciona", "más detalles", "cuéntame más",
                "ejemplo", "qué pasa si", "y si", "me gustaría saber"
            ],
            "decidido": [
                "quiero comprarlo", "me apunto", "vamos a hacerlo", "decidido",
                "adelante", "sí, hagámoslo", "cuenta conmigo"
            ]
        }
    
    async def detect_emotion(self, user_id: str, message: str, conversation_history: List[str] = None) -> Dict:
        """
        Detecta la emoción principal del usuario en el mensaje
        
        Args:
            user_id: ID del usuario
            message: Mensaje a analizar
            conversation_history: Historial reciente de conversación
        
        Returns:
            Dict con emoción detectada, confianza y recomendaciones
        """
        try:
            # 1. Análisis por patrones (rápido)
            pattern_emotion = self._detect_emotion_by_patterns(message)
            
            # 2. Análisis con IA (más preciso)
            ai_emotion = await self._detect_emotion_with_ai(message, conversation_history)
            
            # 3. Combinar resultados
            final_emotion = self._combine_emotion_results(pattern_emotion, ai_emotion)
            
            # 4. Guardar en memoria del usuario
            await self._save_emotion_to_memory(user_id, final_emotion)
            
            # 5. Generar recomendaciones de respuesta
            recommendations = self._generate_response_recommendations(final_emotion)
            
            return {
                "emotion": final_emotion["emotion"],
                "confidence": final_emotion["confidence"],
                "intensity": final_emotion["intensity"],
                "recommendations": recommendations,
                "detected_at": datetime.now().isoformat(),
                "method": final_emotion["method"]
            }
            
        except Exception as e:
            self.logger.error(f"Error detectando emoción: {e}")
            return {
                "emotion": "neutral",
                "confidence": 0.5,
                "intensity": "medium",
                "recommendations": {"tone": "professional", "approach": "informative"},
                "detected_at": datetime.now().isoformat(),
                "method": "fallback"
            }
    
    def _detect_emotion_by_patterns(self, message: str) -> Dict:
        """Detecta emoción usando patrones de texto"""
        message_lower = message.lower()
        emotion_scores = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in message_lower:
                    score += 1
            
            if score > 0:
                emotion_scores[emotion] = score
        
        if not emotion_scores:
            return {"emotion": "neutral", "confidence": 0.6, "intensity": "medium", "method": "pattern"}
        
        # Emoción con mayor score
        top_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        confidence = min(0.8, 0.5 + (top_emotion[1] * 0.1))
        
        return {
            "emotion": top_emotion[0],
            "confidence": confidence,
            "intensity": "high" if top_emotion[1] > 2 else "medium",
            "method": "pattern"
        }
    
    async def _detect_emotion_with_ai(self, message: str, conversation_history: List[str] = None) -> Dict:
        """Detecta emoción usando OpenAI"""
        try:
            context = ""
            if conversation_history:
                context = f"Historial reciente: {' | '.join(conversation_history[-3:])}\n\n"
            
            prompt = f"""Analiza la emoción del siguiente mensaje del usuario:

{context}Mensaje actual: "{message}"

Clasifica la emoción principal en una de estas categorías:
- frustrado: Usuario molesto, confundido o cansado
- emocionado: Usuario muy positivo y entusiasmado
- ansioso: Usuario tiene prisa o urgencia
- escéptico: Usuario tiene dudas o necesita convencerse
- curioso: Usuario busca información y está interesado
- decidido: Usuario está listo para tomar acción
- neutral: Sin emociones fuertes detectables

Responde SOLO con este formato JSON:
{{"emotion": "categoria", "confidence": 0.85, "intensity": "high|medium|low", "reasons": ["razón1", "razón2"]}}"""

            response = await self.openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            # Parsear respuesta JSON
            import json
            result = json.loads(response.get('content', '{}'))
            result["method"] = "ai"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error en detección IA: {e}")
            return {"emotion": "neutral", "confidence": 0.5, "intensity": "medium", "method": "ai_fallback"}
    
    def _combine_emotion_results(self, pattern_result: Dict, ai_result: Dict) -> Dict:
        """Combina resultados de patrones y IA para mayor precisión"""
        
        # Si ambos detectan la misma emoción, aumentar confianza
        if pattern_result["emotion"] == ai_result["emotion"]:
            return {
                "emotion": pattern_result["emotion"],
                "confidence": min(0.95, (pattern_result["confidence"] + ai_result["confidence"]) / 1.5),
                "intensity": max(pattern_result["intensity"], ai_result["intensity"]),
                "method": "combined"
            }
        
        # Si difieren, tomar el de mayor confianza
        if pattern_result["confidence"] > ai_result["confidence"]:
            return pattern_result
        else:
            return ai_result
    
    async def _save_emotion_to_memory(self, user_id: str, emotion_data: Dict):
        """Guarda la emoción detectada en la memoria del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            # Crear array de emociones si no existe
            if not hasattr(user_memory, 'emotion_history'):
                user_memory.emotion_history = []
            
            # Agregar nueva emoción
            emotion_entry = {
                "emotion": emotion_data["emotion"],
                "confidence": emotion_data["confidence"],
                "intensity": emotion_data["intensity"],
                "timestamp": datetime.now().isoformat(),
                "method": emotion_data["method"]
            }
            
            user_memory.emotion_history.append(emotion_entry)
            
            # Mantener solo las últimas 10 emociones
            if len(user_memory.emotion_history) > 10:
                user_memory.emotion_history = user_memory.emotion_history[-10:]
            
            # Actualizar emoción actual
            user_memory.current_emotion = emotion_data["emotion"]
            user_memory.emotion_confidence = emotion_data["confidence"]
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error guardando emoción en memoria: {e}")
    
    def _generate_response_recommendations(self, emotion_data: Dict) -> Dict:
        """Genera recomendaciones de respuesta basadas en la emoción"""
        
        emotion = emotion_data["emotion"]
        intensity = emotion_data["intensity"]
        
        recommendations = {
            "frustrado": {
                "tone": "empático",
                "approach": "solución_inmediata",
                "priority": "alta",
                "suggestions": [
                    "Ofrecer ayuda específica",
                    "Simplificar explicaciones",
                    "Proporcionar alternativas fáciles"
                ]
            },
            "emocionado": {
                "tone": "entusiasta",
                "approach": "aprovechar_momentum",
                "priority": "muy_alta",
                "suggestions": [
                    "Presentar oferta inmediatamente",
                    "Compartir casos de éxito",
                    "Acelerar proceso de venta"
                ]
            },
            "ansioso": {
                "tone": "directo",
                "approach": "respuesta_rápida",
                "priority": "alta",
                "suggestions": [
                    "Dar timeframes específicos",
                    "Priorizar información clave",
                    "Ofrecer contacto directo"
                ]
            },
            "escéptico": {
                "tone": "profesional",
                "approach": "evidencia_social",
                "priority": "media",
                "suggestions": [
                    "Mostrar testimonios",
                    "Proporcionar datos concretos",
                    "Ofrecer garantías"
                ]
            },
            "curioso": {
                "tone": "informativo",
                "approach": "educacional",
                "priority": "media",
                "suggestions": [
                    "Compartir contenido detallado",
                    "Ofrecer demos",
                    "Proporcionar recursos adicionales"
                ]
            },
            "decidido": {
                "tone": "directo",
                "approach": "cierre_inmediato",
                "priority": "muy_alta",
                "suggestions": [
                    "Presentar opción de compra",
                    "Facilitar proceso de pago",
                    "Confirmar detalles"
                ]
            }
        }
        
        return recommendations.get(emotion, {
            "tone": "profesional",
            "approach": "informativo",
            "priority": "media",
            "suggestions": ["Continuar conversación normal"]
        })
    
    def get_emotion_trend(self, user_id: str, days: int = 7) -> Dict:
        """Analiza tendencia emocional del usuario en los últimos días"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            if not hasattr(user_memory, 'emotion_history'):
                return {"trend": "no_data", "dominant_emotion": "neutral"}
            
            # Filtrar emociones de los últimos días
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_emotions = []
            
            for emotion_entry in user_memory.emotion_history:
                emotion_date = datetime.fromisoformat(emotion_entry["timestamp"])
                if emotion_date >= cutoff_date:
                    recent_emotions.append(emotion_entry["emotion"])
            
            if not recent_emotions:
                return {"trend": "no_recent_data", "dominant_emotion": "neutral"}
            
            # Calcular emoción dominante
            emotion_counts = {}
            for emotion in recent_emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
            
            # Determinar tendencia (últimas vs primeras emociones)
            if len(recent_emotions) >= 3:
                early_emotions = recent_emotions[:len(recent_emotions)//2]
                late_emotions = recent_emotions[len(recent_emotions)//2:]
                
                # Clasificar emociones en positivas/negativas
                positive_emotions = {"emocionado", "curioso", "decidido"}
                
                early_positive = sum(1 for e in early_emotions if e in positive_emotions)
                late_positive = sum(1 for e in late_emotions if e in positive_emotions)
                
                if late_positive > early_positive:
                    trend = "improving"
                elif late_positive < early_positive:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            return {
                "trend": trend,
                "dominant_emotion": dominant_emotion,
                "emotion_distribution": emotion_counts,
                "total_interactions": len(recent_emotions)
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando tendencia emocional: {e}")
            return {"trend": "error", "dominant_emotion": "neutral"}