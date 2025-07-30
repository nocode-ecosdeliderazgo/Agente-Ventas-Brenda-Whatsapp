"""
Configuración centralizada para mapeos de hashtags de campañas.
UN SOLO ARCHIVO para evitar desorden como en Telegram.
"""

from typing import Optional

# Mapeos centralizados para detección (UN SOLO ARCHIVO)
COURSE_HASHTAG_MAPPING = {
    'Experto_IA_GPT_Gemini': '11111111-1111-1111-1111-111111111111',
    'EXPERTO_IA_GPT_GEMINI': '11111111-1111-1111-1111-111111111111',
    'Exerto_IA_GPT_Gemini': '11111111-1111-1111-1111-111111111111',  # Error común de ortografía
    'EXPERTO_IA_GPT_GEMINI': '11111111-1111-1111-1111-111111111111',
    'experto_ia_gpt_gemini': '11111111-1111-1111-1111-111111111111',  # Minúsculas
    'ExpertoIA': '11111111-1111-1111-1111-111111111111',  # Versión corta
    'IA_GPT_Gemini': '11111111-1111-1111-1111-111111111111',  # Versión media
    'GPT_Gemini': '11111111-1111-1111-1111-111111111111'  # Versión muy corta
}

CAMPAIGN_HASHTAG_MAPPING = {
    'ADSIM_05': 'facebook_campaign_2025',
    'ADSFACE_02': 'facebook_ads_2025',
    'anuncio:facebook_2025': 'facebook_campaign_2025'
}

# Función centralizada para obtener mapeo
def get_course_id_from_hashtag(hashtag: str) -> Optional[str]:
    """Obtiene ID del curso desde hashtag (centralizado)"""
    return COURSE_HASHTAG_MAPPING.get(hashtag)

def get_campaign_name_from_hashtag(hashtag: str) -> Optional[str]:
    """Obtiene nombre de campaña desde hashtag (centralizado)"""
    return CAMPAIGN_HASHTAG_MAPPING.get(hashtag)

def is_course_hashtag(hashtag: str) -> bool:
    """Verifica si un hashtag corresponde a un curso"""
    return hashtag in COURSE_HASHTAG_MAPPING

def is_campaign_hashtag(hashtag: str) -> bool:
    """Verifica si un hashtag corresponde a una campaña"""
    return hashtag in CAMPAIGN_HASHTAG_MAPPING 