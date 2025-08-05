"""
Herramientas de Diagnóstico Digital
Evaluación de madurez digital, gaps de automatización, ROI personalizado y competencias
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from app.infrastructure.openai.client import OpenAIClient
from memory.lead_memory import LeadMemoryManager

logger = logging.getLogger(__name__)

class DiagnosticToolsUseCase:
    """Herramientas de diagnóstico y evaluación para empresas"""
    
    def __init__(self, openai_client: OpenAIClient, memory_manager: LeadMemoryManager):
        self.openai_client = openai_client
        self.memory_manager = memory_manager
        self.logger = logger
        
        # Sectores industriales y sus características
        self.industry_profiles = {
            "retail": {
                "name": "Retail y E-commerce",
                "automation_opportunities": ["inventario", "atención_cliente", "marketing", "logística"],
                "avg_savings_percentage": 25,
                "priority_tools": ["chatbots", "crm_automation", "inventory_management"]
            },
            "manufacturing": {
                "name": "Manufactura",
                "automation_opportunities": ["control_calidad", "mantenimiento", "planificación", "reportes"],
                "avg_savings_percentage": 35,
                "priority_tools": ["predictive_maintenance", "quality_control", "production_planning"]
            },
            "services": {
                "name": "Servicios Profesionales",
                "automation_opportunities": ["facturación", "seguimiento_clientes", "reportes", "scheduling"],
                "avg_savings_percentage": 30,
                "priority_tools": ["crm", "project_management", "automated_reporting"]
            },
            "healthcare": {
                "name": "Salud y Bienestar",
                "automation_opportunities": ["citas", "historiales", "seguimiento", "comunicación"],
                "avg_savings_percentage": 40,
                "priority_tools": ["appointment_scheduling", "patient_communication", "data_analysis"]
            },
            "education": {
                "name": "Educación",
                "automation_opportunities": ["evaluaciones", "comunicación", "contenido", "administración"],
                "avg_savings_percentage": 28,
                "priority_tools": ["learning_management", "automated_grading", "communication"]
            },
            "finance": {
                "name": "Finanzas y Seguros",
                "automation_opportunities": ["reportes", "análisis_riesgo", "atención_cliente", "compliance"],
                "avg_savings_percentage": 45,
                "priority_tools": ["risk_analysis", "automated_reporting", "compliance_monitoring"]
            }
        }
    
    async def run_digital_maturity_assessment(self, user_id: str, responses: Dict[str, str]) -> Dict:
        """
        Evalúa la madurez digital de la empresa
        
        Args:
            user_id: ID del usuario
            responses: Respuestas del assessment
        
        Returns:
            Dict con evaluación completa de madurez digital
        """
        try:
            # 1. Calcular puntuaciones por área
            area_scores = self._calculate_maturity_scores(responses)
            
            # 2. Determinar nivel general de madurez
            overall_maturity = self._determine_maturity_level(area_scores)
            
            # 3. Identificar fortalezas y debilidades
            strengths_weaknesses = self._analyze_strengths_weaknesses(area_scores)
            
            # 4. Generar recomendaciones específicas
            recommendations = await self._generate_maturity_recommendations(
                overall_maturity, area_scores, user_id
            )
            
            # 5. Crear plan de mejora
            improvement_plan = self._create_improvement_plan(
                overall_maturity, area_scores
            )
            
            # 6. Guardar resultados en memoria
            await self._save_assessment_results(user_id, {
                "type": "digital_maturity",
                "overall_score": overall_maturity["score"],
                "level": overall_maturity["level"],
                "area_scores": area_scores,
                "completed_at": datetime.now().isoformat()
            })
            
            return {
                "assessment_type": "digital_maturity",
                "overall_maturity": overall_maturity,
                "area_breakdown": area_scores,
                "strengths": strengths_weaknesses["strengths"],
                "improvement_areas": strengths_weaknesses["weaknesses"],
                "recommendations": recommendations,
                "improvement_plan": improvement_plan,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error en assessment de madurez digital: {e}")
            return {"error": str(e), "assessment_type": "digital_maturity"}
    
    async def analyze_automation_gaps(self, user_id: str, company_info: Dict) -> Dict:
        """
        Analiza gaps de automatización en la empresa
        
        Args:
            user_id: ID del usuario
            company_info: Información de la empresa
        
        Returns:
            Dict con análisis de gaps y oportunidades
        """
        try:
            industry = company_info.get("industry", "services")
            company_size = company_info.get("size", "medium")
            current_tools = company_info.get("current_tools", [])
            pain_points = company_info.get("pain_points", [])
            
            # 1. Obtener perfil de industria
            industry_profile = self.industry_profiles.get(industry, self.industry_profiles["services"])
            
            # 2. Analizar herramientas actuales vs recomendadas
            tool_gap_analysis = self._analyze_tool_gaps(current_tools, industry_profile)
            
            # 3. Identificar procesos sin automatizar
            process_gaps = self._identify_process_gaps(pain_points, industry_profile)
            
            # 4. Calcular impacto potencial
            impact_analysis = self._calculate_automation_impact(
                company_size, industry_profile, tool_gap_analysis, process_gaps
            )
            
            # 5. Priorizar oportunidades
            prioritized_opportunities = self._prioritize_opportunities(
                tool_gap_analysis, process_gaps, impact_analysis
            )
            
            # 6. Generar roadmap de implementación
            implementation_roadmap = await self._generate_automation_roadmap(
                prioritized_opportunities, company_info
            )
            
            # 7. Guardar análisis
            await self._save_assessment_results(user_id, {
                "type": "automation_gaps",
                "industry": industry,
                "gaps_identified": len(prioritized_opportunities),
                "potential_savings": impact_analysis.get("total_savings", 0),
                "completed_at": datetime.now().isoformat()
            })
            
            return {
                "assessment_type": "automation_gaps",
                "industry_profile": industry_profile,
                "current_state": {
                    "tools_in_use": current_tools,
                    "identified_pain_points": pain_points
                },
                "gap_analysis": {
                    "tool_gaps": tool_gap_analysis,
                    "process_gaps": process_gaps
                },
                "impact_analysis": impact_analysis,
                "opportunities": prioritized_opportunities,
                "implementation_roadmap": implementation_roadmap,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error en análisis de gaps: {e}")
            return {"error": str(e), "assessment_type": "automation_gaps"}
    
    async def calculate_personalized_roi(self, user_id: str, business_params: Dict) -> Dict:
        """
        Calcula ROI personalizado para la inversión en IA
        
        Args:
            user_id: ID del usuario
            business_params: Parámetros del negocio
        
        Returns:
            Dict con cálculo detallado de ROI
        """
        try:
            # Extraer parámetros
            annual_revenue = business_params.get("annual_revenue", 5000000)  # 5M default
            employees = business_params.get("employees", 25)
            avg_hourly_cost = business_params.get("avg_hourly_cost", 500)
            industry = business_params.get("industry", "services")
            current_efficiency = business_params.get("current_efficiency", 70)  # %
            
            # 1. Calcular tiempo perdido actual
            time_waste_analysis = self._calculate_time_waste(
                employees, avg_hourly_cost, industry
            )
            
            # 2. Proyectar ahorros con IA
            automation_savings = self._project_automation_savings(
                time_waste_analysis, industry, current_efficiency
            )
            
            # 3. Calcular costos de implementación
            implementation_costs = self._calculate_implementation_costs(
                employees, industry
            )
            
            # 4. Proyecciones financieras
            financial_projections = self._generate_financial_projections(
                automation_savings, implementation_costs, annual_revenue
            )
            
            # 5. Análisis de sensibilidad
            sensitivity_analysis = self._perform_sensitivity_analysis(
                financial_projections, automation_savings
            )
            
            # 6. Recomendaciones de inversión
            investment_recommendations = await self._generate_investment_recommendations(
                financial_projections, business_params
            )
            
            # 7. Guardar cálculo
            await self._save_assessment_results(user_id, {
                "type": "roi_calculation",
                "projected_roi": financial_projections.get("roi_12_months", 0),
                "annual_savings": automation_savings.get("annual_savings", 0),
                "payback_period": financial_projections.get("payback_months", 0),
                "completed_at": datetime.now().isoformat()
            })
            
            return {
                "assessment_type": "personalized_roi",
                "business_parameters": business_params,
                "current_state": {
                    "time_waste": time_waste_analysis,
                    "annual_cost_of_inefficiency": time_waste_analysis.get("annual_cost", 0)
                },
                "automation_potential": automation_savings,
                "investment_analysis": {
                    "implementation_costs": implementation_costs,
                    "financial_projections": financial_projections
                },
                "sensitivity_analysis": sensitivity_analysis,
                "recommendations": investment_recommendations,
                "summary": {
                    "roi_12_months": financial_projections.get("roi_12_months", 0),
                    "payback_period_months": financial_projections.get("payback_months", 0),
                    "net_benefit_year_1": financial_projections.get("net_benefit_year_1", 0)
                },
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculando ROI personalizado: {e}")
            return {"error": str(e), "assessment_type": "personalized_roi"}
    
    async def assess_ai_competencies(self, user_id: str, team_info: Dict) -> Dict:
        """
        Evalúa competencias actuales del equipo en IA
        
        Args:
            user_id: ID del usuario
            team_info: Información del equipo
        
        Returns:
            Dict con evaluación de competencias
        """
        try:
            # 1. Evaluar competencias por área
            competency_scores = self._evaluate_team_competencies(team_info)
            
            # 2. Identificar brechas de habilidades
            skill_gaps = self._identify_skill_gaps(competency_scores)
            
            # 3. Recomendar capacitación específica
            training_recommendations = await self._recommend_training_programs(
                skill_gaps, team_info
            )
            
            # 4. Crear plan de desarrollo
            development_plan = self._create_team_development_plan(
                competency_scores, skill_gaps
            )
            
            # 5. Evaluar readiness para IA
            ai_readiness = self._assess_ai_readiness(
                competency_scores, team_info
            )
            
            # 6. Guardar evaluación
            await self._save_assessment_results(user_id, {
                "type": "ai_competencies",
                "overall_readiness": ai_readiness.get("level", "low"),
                "team_size": team_info.get("size", 0),
                "key_gaps": len(skill_gaps),
                "completed_at": datetime.now().isoformat()
            })
            
            return {
                "assessment_type": "ai_competencies",
                "team_profile": team_info,
                "competency_evaluation": competency_scores,
                "skill_gaps": skill_gaps,
                "ai_readiness": ai_readiness,
                "training_recommendations": training_recommendations,
                "development_plan": development_plan,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error en assessment de competencias: {e}")
            return {"error": str(e), "assessment_type": "ai_competencies"}
    
    def recommend_tools_by_sector(self, industry: str, company_size: str, budget_range: str) -> Dict:
        """
        Recomienda herramientas específicas por sector
        
        Args:
            industry: Industria de la empresa
            company_size: Tamaño de la empresa
            budget_range: Rango de presupuesto
        
        Returns:
            Dict con recomendaciones de herramientas
        """
        try:
            industry_profile = self.industry_profiles.get(industry, self.industry_profiles["services"])
            
            # Base de herramientas por categoría
            tool_categories = {
                "chatbots": {
                    "low": ["ChatGPT API", "Botpress", "Rasa"],
                    "medium": ["Dialogflow", "Microsoft Bot Framework", "Amazon Lex"],
                    "high": ["Custom NLP Solutions", "Enterprise Conversational AI"]
                },
                "crm_automation": {
                    "low": ["HubSpot Free", "Zoho CRM", "Pipedrive"],
                    "medium": ["Salesforce Essentials", "Monday.com", "ActiveCampaign"],
                    "high": ["Salesforce Enterprise", "Microsoft Dynamics", "Custom CRM"]
                },
                "automated_reporting": {
                    "low": ["Google Data Studio", "Power BI", "Tableau Public"],
                    "medium": ["Tableau Pro", "Looker", "Qlik Sense"],
                    "high": ["Custom BI Solutions", "Enterprise Analytics Platforms"]
                },
                "inventory_management": {
                    "low": ["inFlow", "Zoho Inventory", "Ordoro"],
                    "medium": ["TradeGecko", "Cin7", "NetSuite"],
                    "high": ["SAP", "Oracle WMS", "Custom Solutions"]
                }
            }
            
            # Seleccionar herramientas según presupuesto
            recommended_tools = []
            priority_tools = industry_profile.get("priority_tools", [])
            
            for tool_category in priority_tools:
                if tool_category in tool_categories:
                    tools = tool_categories[tool_category].get(budget_range, [])
                    if tools:
                        recommended_tools.append({
                            "category": tool_category,
                            "tools": tools,
                            "priority": "high" if tool_category in priority_tools[:2] else "medium"
                        })
            
            # Calcular inversión estimada
            investment_estimates = self._calculate_tool_investment(
                recommended_tools, budget_range, company_size
            )
            
            # Crear plan de implementación
            implementation_timeline = self._create_tool_implementation_timeline(
                recommended_tools
            )
            
            return {
                "industry": industry_profile["name"],
                "company_size": company_size,
                "budget_range": budget_range,
                "recommended_tools": recommended_tools,
                "investment_estimates": investment_estimates,
                "implementation_timeline": implementation_timeline,
                "expected_benefits": {
                    "automation_opportunities": industry_profile["automation_opportunities"],
                    "avg_savings_percentage": industry_profile["avg_savings_percentage"]
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error en recomendación de herramientas: {e}")
            return {"error": str(e)}
    
    # Métodos auxiliares privados
    
    def _calculate_maturity_scores(self, responses: Dict[str, str]) -> Dict:
        """Calcula puntuaciones de madurez por área"""
        
        areas = {
            "strategy": ["digital_strategy", "ai_adoption_plan", "leadership_commitment"],
            "technology": ["current_tools", "integration_level", "data_quality"],
            "processes": ["process_documentation", "automation_level", "efficiency_metrics"],
            "people": ["digital_skills", "training_programs", "change_readiness"],
            "culture": ["innovation_mindset", "data_driven_decisions", "collaboration_tools"]
        }
        
        area_scores = {}
        
        for area, questions in areas.items():
            scores = []
            for question in questions:
                response = responses.get(question, "1")
                try:
                    score = int(response)  # Asume escala 1-5
                    scores.append(score)
                except:
                    scores.append(3)  # Default medio
            
            area_scores[area] = {
                "score": sum(scores) / len(scores) if scores else 3,
                "max_score": 5,
                "percentage": (sum(scores) / len(scores) / 5 * 100) if scores else 60
            }
        
        return area_scores
    
    def _determine_maturity_level(self, area_scores: Dict) -> Dict:
        """Determina nivel general de madurez"""
        
        overall_score = sum(area["score"] for area in area_scores.values()) / len(area_scores)
        overall_percentage = overall_score / 5 * 100
        
        if overall_percentage >= 80:
            level = "Avanzado"
            description = "Empresa líder en transformación digital"
        elif overall_percentage >= 60:
            level = "Intermedio"
            description = "Buen progreso en digitalización, oportunidades de mejora"
        elif overall_percentage >= 40:
            level = "Básico"
            description = "Fundamentos establecidos, necesita acelerar transformación"
        else:
            level = "Inicial"
            description = "Gran potencial de mejora en todas las áreas"
        
        return {
            "score": overall_score,
            "percentage": overall_percentage,
            "level": level,
            "description": description
        }
    
    def _analyze_strengths_weaknesses(self, area_scores: Dict) -> Dict:
        """Analiza fortalezas y debilidades"""
        
        sorted_areas = sorted(area_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        strengths = []
        weaknesses = []
        
        for area, score_data in sorted_areas:
            if score_data["percentage"] >= 70:
                strengths.append({
                    "area": area,
                    "score": score_data["score"],
                    "percentage": score_data["percentage"]
                })
            elif score_data["percentage"] <= 50:
                weaknesses.append({
                    "area": area,
                    "score": score_data["score"],
                    "percentage": score_data["percentage"]
                })
        
        return {"strengths": strengths, "weaknesses": weaknesses}
    
    async def _generate_maturity_recommendations(self, maturity: Dict, area_scores: Dict, user_id: str) -> List[Dict]:
        """Genera recomendaciones basadas en madurez"""
        
        recommendations = []
        
        # Recomendar mejoras para áreas débiles
        for area, score_data in area_scores.items():
            if score_data["percentage"] <= 60:
                recommendations.append({
                    "area": area,
                    "priority": "high" if score_data["percentage"] <= 40 else "medium",
                    "recommendation": f"Mejorar {area}: implementar mejores prácticas y herramientas",
                    "expected_impact": "Aumento de 15-25% en eficiencia"
                })
        
        return recommendations[:5]  # Top 5 recomendaciones
    
    def _create_improvement_plan(self, maturity: Dict, area_scores: Dict) -> Dict:
        """Crea plan de mejora estructurado"""
        
        phases = {
            "phase_1": {
                "name": "Fundamentos (Meses 1-3)",
                "focus": "Establecer bases sólidas",
                "actions": []
            },
            "phase_2": {
                "name": "Implementación (Meses 4-8)",
                "focus": "Desplegar soluciones clave",
                "actions": []
            },
            "phase_3": {
                "name": "Optimización (Meses 9-12)",
                "focus": "Refinar y escalar",
                "actions": []
            }
        }
        
        # Asignar acciones según áreas débiles
        weak_areas = [area for area, score in area_scores.items() if score["percentage"] <= 60]
        
        for i, area in enumerate(weak_areas[:6]):  # Max 6 áreas
            phase_key = f"phase_{(i // 2) + 1}"
            phases[phase_key]["actions"].append(f"Mejorar {area}")
        
        return phases
    
    def _analyze_tool_gaps(self, current_tools: List[str], industry_profile: Dict) -> Dict:
        """Analiza gaps en herramientas actuales"""
        
        recommended_tools = set(industry_profile.get("priority_tools", []))
        current_tool_categories = set()
        
        # Mapear herramientas actuales a categorías
        tool_mapping = {
            "excel": "spreadsheet_tools",
            "google_sheets": "spreadsheet_tools",
            "salesforce": "crm_automation",
            "hubspot": "crm_automation",
            "zapier": "workflow_automation",
            "chatgpt": "ai_tools"
        }
        
        for tool in current_tools:
            category = tool_mapping.get(tool.lower(), "other")
            current_tool_categories.add(category)
        
        missing_categories = recommended_tools - current_tool_categories
        
        return {
            "current_categories": list(current_tool_categories),
            "recommended_categories": list(recommended_tools),
            "missing_categories": list(missing_categories),
            "coverage_percentage": (len(current_tool_categories) / len(recommended_tools) * 100) if recommended_tools else 100
        }
    
    def _identify_process_gaps(self, pain_points: List[str], industry_profile: Dict) -> List[Dict]:
        """Identifica procesos sin automatizar"""
        
        automation_opportunities = industry_profile.get("automation_opportunities", [])
        
        gaps = []
        for opportunity in automation_opportunities:
            # Verificar si el pain point indica gap en esta área
            related_pain_points = [p for p in pain_points if opportunity.lower() in p.lower()]
            
            if related_pain_points:
                gaps.append({
                    "process": opportunity,
                    "related_pain_points": related_pain_points,
                    "automation_potential": "high",
                    "estimated_savings": "15-30%"
                })
        
        return gaps
    
    def _calculate_automation_impact(self, company_size: str, industry_profile: Dict, tool_gaps: Dict, process_gaps: List[Dict]) -> Dict:
        """Calcula impacto potencial de automatización"""
        
        # Factores de empresa
        size_multipliers = {"small": 0.8, "medium": 1.0, "large": 1.2}
        size_multiplier = size_multipliers.get(company_size, 1.0)
        
        # Calcular ahorros base
        avg_savings_pct = industry_profile.get("avg_savings_percentage", 25)
        
        # Ajustar por gaps identificados
        gap_impact = len(process_gaps) * 5  # 5% por gap
        total_savings_pct = min(50, avg_savings_pct + gap_impact) * size_multiplier
        
        # Estimar ahorros monetarios (ejemplo base: $100k anuales)
        base_annual_cost = 100000 * size_multiplier
        annual_savings = base_annual_cost * (total_savings_pct / 100)
        
        return {
            "total_savings_percentage": total_savings_pct,
            "annual_savings": annual_savings,
            "monthly_savings": annual_savings / 12,
            "gaps_identified": len(process_gaps),
            "implementation_complexity": "medium" if len(process_gaps) <= 3 else "high"
        }
    
    def _prioritize_opportunities(self, tool_gaps: Dict, process_gaps: List[Dict], impact: Dict) -> List[Dict]:
        """Prioriza oportunidades de automatización"""
        
        opportunities = []
        
        # Agregar oportunidades de herramientas
        for missing_category in tool_gaps.get("missing_categories", []):
            opportunities.append({
                "type": "tool_implementation",
                "category": missing_category,
                "priority": "high",
                "estimated_effort": "medium",
                "expected_roi": "3-6 months"
            })
        
        # Agregar oportunidades de procesos
        for gap in process_gaps:
            opportunities.append({
                "type": "process_automation",
                "process": gap["process"],
                "priority": "high" if "high" in gap.get("automation_potential", "") else "medium",
                "estimated_effort": "low" if len(gap.get("related_pain_points", [])) == 1 else "medium",
                "expected_roi": "2-4 months"
            })
        
        # Ordenar por prioridad
        priority_order = {"high": 3, "medium": 2, "low": 1}
        opportunities.sort(key=lambda x: priority_order.get(x["priority"], 1), reverse=True)
        
        return opportunities[:8]  # Top 8 oportunidades
    
    async def _generate_automation_roadmap(self, opportunities: List[Dict], company_info: Dict) -> Dict:
        """Genera roadmap de implementación"""
        
        quarters = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}
        
        # Distribuir oportunidades por trimestres
        for i, opportunity in enumerate(opportunities):
            quarter = f"Q{(i // 2) + 1}"
            if quarter in quarters:
                quarters[quarter].append(opportunity)
        
        return {
            "timeline": quarters,
            "total_opportunities": len(opportunities),
            "estimated_duration": "12 months",
            "success_metrics": [
                "Reducción 25% tiempo procesos manuales",
                "Aumento 30% productividad equipo",
                "ROI positivo en 6 meses"
            ]
        }
    
    async def _save_assessment_results(self, user_id: str, results: Dict):
        """Guarda resultados de assessment en memoria del usuario"""
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            if not hasattr(user_memory, 'assessment_history'):
                user_memory.assessment_history = []
            
            user_memory.assessment_history.append(results)
            
            # Mantener solo los últimos 10 assessments
            if len(user_memory.assessment_history) > 10:
                user_memory.assessment_history = user_memory.assessment_history[-10:]
            
            # Actualizar stats del usuario
            user_memory.last_assessment = results["type"]
            user_memory.last_assessment_date = results["completed_at"]
            
            self.memory_manager.save_lead_memory(user_id, user_memory)
            
        except Exception as e:
            self.logger.error(f"Error guardando resultados de assessment: {e}")
    
    # Continúan los métodos para ROI y competencias...
    
    def _calculate_time_waste(self, employees: int, hourly_cost: float, industry: str) -> Dict:
        """Calcula tiempo desperdiciado actual"""
        
        # Factores por industria
        waste_factors = {
            "retail": 0.25,
            "manufacturing": 0.30,
            "services": 0.35,
            "healthcare": 0.20,
            "education": 0.25,
            "finance": 0.40
        }
        
        waste_factor = waste_factors.get(industry, 0.30)
        
        # Cálculos
        hours_per_week = 40
        weeks_per_year = 50
        total_hours_year = employees * hours_per_week * weeks_per_year
        wasted_hours_year = total_hours_year * waste_factor
        annual_waste_cost = wasted_hours_year * hourly_cost
        
        return {
            "total_annual_hours": total_hours_year,
            "wasted_hours_annual": wasted_hours_year,
            "waste_percentage": waste_factor * 100,
            "annual_cost": annual_waste_cost,
            "monthly_cost": annual_waste_cost / 12,
            "weekly_cost": annual_waste_cost / 52
        }
    
    def _project_automation_savings(self, time_waste: Dict, industry: str, current_efficiency: int) -> Dict:
        """Proyecta ahorros con automatización"""
        
        # Potencial de automatización por industria
        automation_potential = {
            "retail": 0.60,
            "manufacturing": 0.70,
            "services": 0.65,
            "healthcare": 0.50,
            "education": 0.55,
            "finance": 0.75
        }
        
        potential = automation_potential.get(industry, 0.60)
        
        # Ajustar por eficiencia actual
        efficiency_factor = (100 - current_efficiency) / 100
        adjusted_potential = potential * efficiency_factor
        
        # Calcular ahorros
        recoverable_waste = time_waste["annual_cost"] * adjusted_potential
        
        return {
            "automation_potential_percentage": adjusted_potential * 100,
            "recoverable_annual_cost": recoverable_waste,
            "annual_savings": recoverable_waste * 0.8,  # 80% del potencial
            "monthly_savings": recoverable_waste * 0.8 / 12,
            "hours_saved_annually": time_waste["wasted_hours_annual"] * adjusted_potential * 0.8,
            "productivity_increase_percentage": adjusted_potential * 80
        }
    
    def _calculate_implementation_costs(self, employees: int, industry: str) -> Dict:
        """Calcula costos de implementación"""
        
        # Costos base por empleado
        base_cost_per_employee = 500
        
        # Factores por industria
        industry_factors = {
            "retail": 0.8,
            "manufacturing": 1.2,
            "services": 1.0,
            "healthcare": 1.5,
            "education": 0.9,
            "finance": 1.3
        }
        
        factor = industry_factors.get(industry, 1.0)
        
        # Cálculos
        software_costs = employees * base_cost_per_employee * factor
        training_costs = employees * 200  # $200 per employee
        consulting_costs = software_costs * 0.3  # 30% of software costs
        
        total_implementation = software_costs + training_costs + consulting_costs
        
        return {
            "software_licensing": software_costs,
            "training_and_onboarding": training_costs,
            "consulting_and_setup": consulting_costs,
            "total_implementation": total_implementation,
            "annual_maintenance": total_implementation * 0.2  # 20% annual maintenance
        }
    
    def _generate_financial_projections(self, savings: Dict, costs: Dict, annual_revenue: float) -> Dict:
        """Genera proyecciones financieras"""
        
        annual_savings = savings.get("annual_savings", 0)
        implementation_cost = costs.get("total_implementation", 0)
        annual_maintenance = costs.get("annual_maintenance", 0)
        
        # Net benefit first year
        net_benefit_year_1 = annual_savings - implementation_cost - annual_maintenance
        
        # ROI calculations
        total_investment = implementation_cost + annual_maintenance
        roi_12_months = (net_benefit_year_1 / total_investment * 100) if total_investment > 0 else 0
        
        # Payback period in months
        monthly_net_savings = (annual_savings - annual_maintenance) / 12
        payback_months = (implementation_cost / monthly_net_savings) if monthly_net_savings > 0 else 999
        
        # Revenue impact
        revenue_impact_percentage = (annual_savings / annual_revenue * 100) if annual_revenue > 0 else 0
        
        return {
            "net_benefit_year_1": net_benefit_year_1,
            "roi_12_months": roi_12_months,
            "payback_months": min(payback_months, 60),  # Cap at 5 years
            "revenue_impact_percentage": revenue_impact_percentage,
            "break_even_month": payback_months,
            "year_2_net_benefit": annual_savings - annual_maintenance,
            "year_3_net_benefit": annual_savings - annual_maintenance
        }
    
    def _perform_sensitivity_analysis(self, projections: Dict, savings: Dict) -> Dict:
        """Realiza análisis de sensibilidad"""
        
        base_roi = projections.get("roi_12_months", 0)
        base_savings = savings.get("annual_savings", 0)
        
        scenarios = {
            "conservative": {
                "savings_multiplier": 0.7,
                "roi": base_roi * 0.7,
                "description": "Escenario conservador (70% de ahorros proyectados)"
            },
            "realistic": {
                "savings_multiplier": 1.0,
                "roi": base_roi,
                "description": "Escenario realista (ahorros proyectados completos)"
            },
            "optimistic": {
                "savings_multiplier": 1.3,
                "roi": base_roi * 1.3,
                "description": "Escenario optimista (130% de ahorros proyectados)"
            }
        }
        
        return scenarios
    
    async def _generate_investment_recommendations(self, projections: Dict, business_params: Dict) -> List[Dict]:
        """Genera recomendaciones de inversión"""
        
        roi = projections.get("roi_12_months", 0)
        payback_months = projections.get("payback_months", 999)
        
        recommendations = []
        
        if roi > 200 and payback_months < 6:
            recommendations.append({
                "type": "strong_recommendation",
                "message": "Inversión altamente recomendada - ROI excelente y payback rápido",
                "priority": "immediate"
            })
        elif roi > 100 and payback_months < 12:
            recommendations.append({
                "type": "positive_recommendation", 
                "message": "Inversión recomendada - ROI sólido y payback aceptable",
                "priority": "high"
            })
        elif roi > 50:
            recommendations.append({
                "type": "conditional_recommendation",
                "message": "Inversión viable - considerar factores adicionales",
                "priority": "medium"
            })
        else:
            recommendations.append({
                "type": "caution_recommendation",
                "message": "Revisar parámetros - ROI puede ser insuficiente",
                "priority": "low"
            })
        
        return recommendations
    
    def _evaluate_team_competencies(self, team_info: Dict) -> Dict:
        """Evalúa competencias actuales del equipo"""
        
        competency_areas = {
            "technical_skills": team_info.get("technical_level", 3),
            "ai_familiarity": team_info.get("ai_experience", 2),
            "data_literacy": team_info.get("data_skills", 3),
            "change_adaptability": team_info.get("change_readiness", 4),
            "learning_agility": team_info.get("learning_willingness", 4)
        }
        
        scores = {}
        for area, score in competency_areas.items():
            scores[area] = {
                "current_level": score,
                "target_level": 4,
                "gap": max(0, 4 - score),
                "percentage": (score / 5) * 100
            }
        
        return scores
    
    def _identify_skill_gaps(self, competency_scores: Dict) -> List[Dict]:
        """Identifica brechas de habilidades"""
        
        gaps = []
        
        for area, scores in competency_scores.items():
            if scores["gap"] > 1:  # Gap significativo
                gaps.append({
                    "skill_area": area,
                    "current_level": scores["current_level"],
                    "target_level": scores["target_level"],
                    "gap_size": scores["gap"],
                    "priority": "high" if scores["gap"] > 2 else "medium"
                })
        
        return gaps
    
    async def _recommend_training_programs(self, skill_gaps: List[Dict], team_info: Dict) -> List[Dict]:
        """Recomienda programas de capacitación"""
        
        recommendations = []
        
        training_mapping = {
            "technical_skills": {
                "program": "Fundamentos Técnicos para IA",
                "duration": "4 semanas",
                "cost": "$500/persona"
            },
            "ai_familiarity": {
                "program": "Introducción a IA Empresarial",
                "duration": "3 semanas", 
                "cost": "$400/persona"
            },
            "data_literacy": {
                "program": "Análisis de Datos para Profesionales",
                "duration": "6 semanas",
                "cost": "$600/persona"
            }
        }
        
        for gap in skill_gaps:
            skill_area = gap["skill_area"]
            if skill_area in training_mapping:
                training = training_mapping[skill_area]
                recommendations.append({
                    "skill_gap": skill_area,
                    "recommended_program": training["program"],
                    "duration": training["duration"],
                    "estimated_cost": training["cost"],
                    "priority": gap["priority"]
                })
        
        return recommendations
    
    def _create_team_development_plan(self, competency_scores: Dict, skill_gaps: List[Dict]) -> Dict:
        """Crea plan de desarrollo del equipo"""
        
        phases = {
            "immediate": {"duration": "1-2 months", "focus": [], "goals": []},
            "short_term": {"duration": "3-6 months", "focus": [], "goals": []},
            "long_term": {"duration": "6-12 months", "focus": [], "goals": []}
        }
        
        # Distribuir gaps por fases según prioridad
        for gap in skill_gaps:
            if gap["priority"] == "high":
                phases["immediate"]["focus"].append(gap["skill_area"])
            elif gap["priority"] == "medium":
                phases["short_term"]["focus"].append(gap["skill_area"])
            else:
                phases["long_term"]["focus"].append(gap["skill_area"])
        
        # Agregar goals genéricos
        phases["immediate"]["goals"] = ["Establecer fundamentos", "Reducir gaps críticos"]
        phases["short_term"]["goals"] = ["Desarrollar competencias intermedias", "Aplicar conocimientos"]
        phases["long_term"]["goals"] = ["Alcanzar experticia", "Liderar implementación"]
        
        return phases
    
    def _assess_ai_readiness(self, competency_scores: Dict, team_info: Dict) -> Dict:
        """Evalúa preparación del equipo para IA"""
        
        # Calcular score promedio
        avg_score = sum(scores["current_level"] for scores in competency_scores.values()) / len(competency_scores)
        
        # Factores adicionales
        team_size = team_info.get("size", 5)
        leadership_support = team_info.get("leadership_support", 3)
        
        # Ajustar score
        adjusted_score = (avg_score + leadership_support) / 2
        
        if adjusted_score >= 4:
            level = "high"
            description = "Equipo listo para implementación IA"
        elif adjusted_score >= 3:
            level = "medium"
            description = "Equipo requiere capacitación básica"
        else:
            level = "low"
            description = "Equipo necesita desarrollo significativo"
        
        return {
            "level": level,
            "score": adjusted_score,
            "description": description,
            "readiness_percentage": (adjusted_score / 5) * 100,
            "key_strengths": [area for area, scores in competency_scores.items() if scores["current_level"] >= 4],
            "critical_gaps": [area for area, scores in competency_scores.items() if scores["current_level"] <= 2]
        }
    
    def _calculate_tool_investment(self, recommended_tools: List[Dict], budget_range: str, company_size: str) -> Dict:
        """Calcula inversión estimada en herramientas"""
        
        # Costos base por herramienta
        base_costs = {
            "low": {"monthly": 50, "setup": 200},
            "medium": {"monthly": 200, "setup": 1000},
            "high": {"monthly": 800, "setup": 5000}
        }
        
        # Multiplicadores por tamaño de empresa
        size_multipliers = {"small": 0.8, "medium": 1.0, "large": 1.5}
        
        costs = base_costs.get(budget_range, base_costs["medium"])
        multiplier = size_multipliers.get(company_size, 1.0)
        
        monthly_cost = costs["monthly"] * len(recommended_tools) * multiplier
        setup_cost = costs["setup"] * len(recommended_tools) * multiplier
        annual_cost = monthly_cost * 12 + setup_cost
        
        return {
            "setup_cost": setup_cost,
            "monthly_recurring": monthly_cost,
            "annual_total": annual_cost,
            "cost_per_tool": costs,
            "total_tools": len(recommended_tools)
        }
    
    def _create_tool_implementation_timeline(self, recommended_tools: List[Dict]) -> Dict:
        """Crea timeline de implementación de herramientas"""
        
        timeline = {"month_1": [], "month_2": [], "month_3": [], "month_4": []}
        
        # Distribuir herramientas por prioridad
        high_priority = [tool for tool in recommended_tools if tool.get("priority") == "high"]
        medium_priority = [tool for tool in recommended_tools if tool.get("priority") == "medium"]
        
        # Asignar por meses
        for i, tool in enumerate(high_priority[:2]):
            timeline[f"month_{i+1}"].append(tool)
        
        for i, tool in enumerate(medium_priority[:2]):
            month_key = f"month_{i+3}"
            if month_key in timeline:
                timeline[month_key].append(tool)
        
        return timeline