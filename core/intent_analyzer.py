from openai import AsyncOpenAI
from memory.lead_memory import LeadMemory
from typing import Dict, Any, List

class IntentAnalyzer:
    """
    Sistema de clasificación inteligente de intenciones del usuario.
    """
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
    # TODO: Implementar método analyze_intent adaptado a WhatsApp 