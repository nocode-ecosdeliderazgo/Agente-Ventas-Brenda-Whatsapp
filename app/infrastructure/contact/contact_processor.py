#!/usr/bin/env python3
"""
Procesador de contacto para manejar solicitudes de asesores.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.domain.entities.contact_request import ContactRequest


class ContactProcessor:
    """
    Procesador para manejar solicitudes de contacto con asesores.
    """
    
    def __init__(self):
        """Inicializa el procesador de contacto."""
        self.pending_requests: List[ContactRequest] = []
        self.assigned_requests: List[ContactRequest] = []
        self.completed_requests: List[ContactRequest] = []
    
    async def process_contact_request(self, contact_request: ContactRequest) -> Dict[str, Any]:
        """
        Procesa una nueva solicitud de contacto.
        
        Args:
            contact_request: Solicitud de contacto a procesar
            
        Returns:
            Dict con el resultado del procesamiento
        """
        try:
            print(f"📞 PROCESANDO SOLICITUD DE CONTACTO")
            print(f"   ID: {contact_request.request_id}")
            print(f"   Usuario: {contact_request.user_name}")
            print(f"   Motivo: {contact_request.contact_reason}")
            
            # Agregar a la lista de solicitudes pendientes
            self.pending_requests.append(contact_request)
            
            # Determinar prioridad
            priority_score = contact_request.get_priority_score()
            is_urgent = contact_request.is_urgent()
            
            # Simular asignación de asesor (en producción esto sería más complejo)
            assignment_result = await self._assign_advisor(contact_request)
            
            return {
                'success': True,
                'request_id': contact_request.request_id,
                'priority_score': priority_score,
                'is_urgent': is_urgent,
                'assigned_advisor': assignment_result.get('advisor_id'),
                'advisor_name': assignment_result.get('advisor_name'),
                'estimated_response_time': assignment_result.get('response_time'),
                'status': 'pending'
            }
            
        except Exception as e:
            print(f"❌ Error procesando solicitud de contacto: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': 'error'
            }
    
    async def _assign_advisor(self, contact_request: ContactRequest) -> Dict[str, Any]:
        """
        Asigna un asesor a la solicitud.
        
        Args:
            contact_request: Solicitud de contacto
            
        Returns:
            Dict con información del asesor asignado
        """
        # Simulación de asignación de asesor
        # En producción, esto sería más complejo con base de datos de asesores
        
        advisors = [
            {'id': 'ADV_001', 'name': 'María González', 'specialties': ['tecnología', 'implementación']},
            {'id': 'ADV_002', 'name': 'Carlos Rodríguez', 'specialties': ['finanzas', 'empresas grandes']},
            {'id': 'ADV_003', 'name': 'Ana Martínez', 'specialties': ['salud', 'educación']},
            {'id': 'ADV_004', 'name': 'Luis Pérez', 'specialties': ['startups', 'pymes']}
        ]
        
        # Determinar asesor basado en industria y urgencia
        selected_advisor = self._select_advisor(contact_request, advisors)
        
        # Calcular tiempo de respuesta estimado
        if contact_request.is_urgent():
            response_time = "30-60 minutos"
        else:
            response_time = "2-4 horas"
        
        # Simular asignación
        contact_request.assign_advisor(selected_advisor['id'], selected_advisor['name'])
        
        # Mover de pendientes a asignadas
        if contact_request in self.pending_requests:
            self.pending_requests.remove(contact_request)
        self.assigned_requests.append(contact_request)
        
        return {
            'advisor_id': selected_advisor['id'],
            'advisor_name': selected_advisor['name'],
            'response_time': response_time,
            'specialties': selected_advisor['specialties']
        }
    
    def _select_advisor(self, contact_request: ContactRequest, advisors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Selecciona el asesor más adecuado para la solicitud.
        
        Args:
            contact_request: Solicitud de contacto
            advisors: Lista de asesores disponibles
            
        Returns:
            Asesor seleccionado
        """
        industry = contact_request.industry.lower() if contact_request.industry else ''
        company_size = contact_request.company_size.lower() if contact_request.company_size else ''
        
        # Buscar asesor por especialidad
        for advisor in advisors:
            for specialty in advisor['specialties']:
                if specialty in industry or specialty in company_size:
                    return advisor
        
        # Si no hay coincidencia específica, seleccionar por defecto
        if 'grande' in company_size or 'enterprise' in company_size:
            return advisors[1]  # Carlos para empresas grandes
        elif 'startup' in company_size or 'pequeña' in company_size:
            return advisors[3]  # Luis para startups/pymes
        else:
            return advisors[0]  # María por defecto
    
    async def get_pending_requests(self) -> List[ContactRequest]:
        """
        Obtiene todas las solicitudes pendientes.
        
        Returns:
            Lista de solicitudes pendientes
        """
        return self.pending_requests.copy()
    
    async def get_assigned_requests(self) -> List[ContactRequest]:
        """
        Obtiene todas las solicitudes asignadas.
        
        Returns:
            Lista de solicitudes asignadas
        """
        return self.assigned_requests.copy()
    
    async def get_urgent_requests(self) -> List[ContactRequest]:
        """
        Obtiene todas las solicitudes urgentes.
        
        Returns:
            Lista de solicitudes urgentes
        """
        urgent_requests = []
        
        for request in self.pending_requests + self.assigned_requests:
            if request.is_urgent():
                urgent_requests.append(request)
        
        return urgent_requests
    
    async def mark_request_as_completed(self, request_id: str, satisfaction_score: Optional[int] = None) -> bool:
        """
        Marca una solicitud como completada.
        
        Args:
            request_id: ID de la solicitud
            satisfaction_score: Puntuación de satisfacción opcional
            
        Returns:
            True si se marcó como completada
        """
        # Buscar en solicitudes asignadas
        for request in self.assigned_requests:
            if request.request_id == request_id:
                request.mark_as_completed(satisfaction_score)
                self.assigned_requests.remove(request)
                self.completed_requests.append(request)
                return True
        
        # Buscar en solicitudes pendientes (caso raro)
        for request in self.pending_requests:
            if request.request_id == request_id:
                request.mark_as_completed(satisfaction_score)
                self.pending_requests.remove(request)
                self.completed_requests.append(request)
                return True
        
        return False
    
    async def get_request_by_id(self, request_id: str) -> Optional[ContactRequest]:
        """
        Obtiene una solicitud por ID.
        
        Args:
            request_id: ID de la solicitud
            
        Returns:
            Solicitud encontrada o None
        """
        all_requests = self.pending_requests + self.assigned_requests + self.completed_requests
        
        for request in all_requests:
            if request.request_id == request_id:
                return request
        
        return None
    
    async def get_user_requests(self, user_id: str) -> List[ContactRequest]:
        """
        Obtiene todas las solicitudes de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de solicitudes del usuario
        """
        user_requests = []
        all_requests = self.pending_requests + self.assigned_requests + self.completed_requests
        
        for request in all_requests:
            if request.user_id == user_id:
                user_requests.append(request)
        
        return user_requests
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del procesador de contacto.
        
        Returns:
            Dict con estadísticas
        """
        total_requests = len(self.pending_requests) + len(self.assigned_requests) + len(self.completed_requests)
        
        urgent_count = 0
        for request in self.pending_requests + self.assigned_requests:
            if request.is_urgent():
                urgent_count += 1
        
        avg_priority_score = 0
        if total_requests > 0:
            all_requests = self.pending_requests + self.assigned_requests + self.completed_requests
            total_score = sum(request.get_priority_score() for request in all_requests)
            avg_priority_score = total_score / total_requests
        
        return {
            'total_requests': total_requests,
            'pending_requests': len(self.pending_requests),
            'assigned_requests': len(self.assigned_requests),
            'completed_requests': len(self.completed_requests),
            'urgent_requests': urgent_count,
            'average_priority_score': round(avg_priority_score, 2),
            'completion_rate': round(len(self.completed_requests) / total_requests * 100, 2) if total_requests > 0 else 0
        }
    
    async def cleanup_old_requests(self, days_old: int = 30) -> int:
        """
        Limpia solicitudes antiguas.
        
        Args:
            days_old: Días de antigüedad para limpiar
            
        Returns:
            Número de solicitudes eliminadas
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        removed_count = 0
        
        # Limpiar solicitudes completadas antiguas
        old_completed = []
        for request in self.completed_requests:
            if request.completed_at and request.completed_at < cutoff_date:
                old_completed.append(request)
                removed_count += 1
        
        for request in old_completed:
            self.completed_requests.remove(request)
        
        return removed_count 