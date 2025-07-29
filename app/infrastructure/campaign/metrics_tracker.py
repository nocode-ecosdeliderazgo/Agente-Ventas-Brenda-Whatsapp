"""
Tracker de métricas para campañas (opcional).
"""
from typing import Dict, Any, Optional
from datetime import datetime


class MetricsTracker:
    """Tracker de métricas para campañas"""
    
    def __init__(self):
        self.metrics = {}
    
    def track_ad_interaction(self, user_id: str, course_id: str, 
                           campaign_name: str, interaction_type: str) -> Dict[str, Any]:
        """
        Registra interacción con anuncio
        
        Args:
            user_id: ID del usuario
            course_id: ID del curso
            campaign_name: Nombre de la campaña
            interaction_type: Tipo de interacción
            
        Returns:
            Dict con información de métrica registrada
        """
        try:
            metric_key = f"{user_id}_{course_id}_{campaign_name}"
            
            metric_data = {
                'user_id': user_id,
                'course_id': course_id,
                'campaign_name': campaign_name,
                'interaction_type': interaction_type,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
            self.metrics[metric_key] = metric_data
            
            return {
                'success': True,
                'metric_key': metric_key,
                'tracked': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tracked': False
            }
    
    def get_campaign_metrics(self, campaign_name: str) -> Dict[str, Any]:
        """
        Obtiene métricas de una campaña específica
        
        Args:
            campaign_name: Nombre de la campaña
            
        Returns:
            Dict con métricas de la campaña
        """
        try:
            campaign_metrics = [
                metric for metric in self.metrics.values()
                if metric.get('campaign_name') == campaign_name
            ]
            
            return {
                'success': True,
                'campaign_name': campaign_name,
                'total_interactions': len(campaign_metrics),
                'metrics': campaign_metrics
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'campaign_name': campaign_name,
                'total_interactions': 0,
                'metrics': []
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Obtiene todas las métricas registradas
        
        Returns:
            Dict con todas las métricas
        """
        try:
            return {
                'success': True,
                'total_metrics': len(self.metrics),
                'metrics': list(self.metrics.values())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'total_metrics': 0,
                'metrics': []
            } 