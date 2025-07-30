"""
Caso de uso para mapear curso y campaña desde hashtags.
"""
from typing import Dict, Any, Optional
from app.config.campaign_config import (
    get_course_id_from_hashtag, 
    get_campaign_name_from_hashtag
)


class MapCampaignCourseUseCase:
    """Caso de uso para mapear curso y campaña desde hashtags"""
    
    async def execute(self, hashtags_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el mapeo de curso y campaña desde hashtags
        
        Args:
            hashtags_info: Información de hashtags detectados
            
        Returns:
            Dict con información mapeada de curso y campaña
        """
        try:
            course_id = hashtags_info.get('course_id')
            campaign_name = hashtags_info.get('campaign_name')
            
            # Validar que ambos hashtags estén presentes
            if not course_id or not campaign_name:
                return {
                    'success': False,
                    'error': 'Faltan hashtags de curso o campaña',
                    'course_id': None,
                    'campaign_name': None,
                    'mapping_complete': False
                }
            
            # Obtener información de campaña
            campaign_info = await self._get_campaign_info(course_id, campaign_name)
            
            return {
                'success': True,
                'course_id': course_id,
                'campaign_name': campaign_name,
                'campaign_info': campaign_info,
                'mapping_complete': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'course_id': None,
                'campaign_name': None,
                'mapping_complete': False
            }
    
    async def _get_campaign_info(self, course_id: str, campaign_name: str) -> Dict[str, Any]:
        """Obtiene información completa de campaña"""
        return {
            'course_id': course_id,
            'campaign_name': campaign_name,
            'platform': 'facebook',  # Por defecto
            'status': 'active'
        } 