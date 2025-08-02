"""
Detector de hashtags para infraestructura.
"""
import re
from typing import List, Dict, Any
from app.config.campaign_config import (
    get_course_id_from_hashtag, 
    get_campaign_name_from_hashtag,
    is_course_hashtag,
    is_campaign_hashtag
)


class HashtagDetector:
    """Detector de hashtags para infraestructura"""
    
    def __init__(self):
        self.hashtag_pattern = r'#([a-zA-Z0-9_]+)'
    
    def detect_hashtags(self, message_text: str) -> Dict[str, Any]:
        """
        Detecta hashtags en un mensaje
        
        Args:
            message_text: Texto del mensaje
            
        Returns:
            Dict con información de hashtags detectados
        """
        try:
            # Extraer hashtags del mensaje
            hashtags = self._extract_hashtags(message_text)
            
            # Clasificar hashtags
            course_hashtags = []
            campaign_hashtags = []
            
            for hashtag_text in hashtags:
                # Normalizar hashtag (sin #)
                clean_hashtag = hashtag_text.replace('#', '')
                
                if is_course_hashtag(clean_hashtag):
                    course_id = get_course_id_from_hashtag(clean_hashtag)
                    course_hashtags.append({
                        'text': hashtag_text,
                        'type': 'course',
                        'mapped_value': course_id
                    })
                elif is_campaign_hashtag(clean_hashtag):
                    campaign_name = get_campaign_name_from_hashtag(clean_hashtag)
                    campaign_hashtags.append({
                        'text': hashtag_text,
                        'type': 'campaign',
                        'mapped_value': campaign_name
                    })
            
            # Determinar si es un anuncio
            is_ad = len(course_hashtags) > 0 and len(campaign_hashtags) > 0
            
            return {
                'is_ad': is_ad,
                'course_hashtags': course_hashtags,
                'campaign_hashtags': campaign_hashtags,
                'all_hashtags': course_hashtags + campaign_hashtags,
                'course_id': course_hashtags[0]['mapped_value'] if course_hashtags else None,
                'campaign_name': campaign_hashtags[0]['mapped_value'] if campaign_hashtags else None
            }
            
        except Exception as e:
            return {
                'is_ad': False,
                'error': str(e),
                'course_hashtags': [],
                'campaign_hashtags': [],
                'all_hashtags': [],
                'course_id': None,
                'campaign_name': None
            }
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extrae hashtags de un texto"""
        return re.findall(self.hashtag_pattern, text)
    
    def _validate_hashtag_format(self, hashtag: str) -> bool:
        """Valida formato de hashtag"""
        return bool(re.match(r'^#[a-zA-Z0-9_]+$', hashtag)) 