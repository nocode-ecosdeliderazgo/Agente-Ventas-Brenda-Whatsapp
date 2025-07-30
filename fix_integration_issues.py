#!/usr/bin/env python3
"""
Script para detectar y corregir problemas de integración entre Fases 1 y 2
"""

import os
import sys
import importlib
from typing import List, Dict, Any

def debug_print(message: str, function_name: str = ""):
    """Print de debug visual"""
    print(f"🔧 [{function_name}] {message}")

class IntegrationFixer:
    """Clase para detectar y corregir problemas de integración"""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
    
    def check_imports_and_dependencies(self):
        """Verificar que todas las dependencias estén disponibles"""
        debug_print("🔍 Verificando imports y dependencias", "CHECK_IMPORTS")
        
        required_modules = [
            "app.application.usecases.anti_hallucination_use_case",
            "app.application.usecases.personalize_response_use_case", 
            "app.application.usecases.extract_user_info_use_case",
            "app.application.usecases.validate_response_use_case",
            "app.infrastructure.openai.client",
            "app.infrastructure.database.client",
            "app.infrastructure.database.repositories.course_repository",
            "memory.lead_memory",
            "app.domain.entities.message"
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                importlib.import_module(module)
                debug_print(f"✅ {module}", "CHECK_IMPORTS")
            except ImportError as e:
                missing_modules.append(module)
                debug_print(f"❌ {module}: {e}", "CHECK_IMPORTS")
        
        if missing_modules:
            self.issues_found.append(f"Missing modules: {missing_modules}")
            debug_print(f"⚠️ Módulos faltantes: {len(missing_modules)}", "CHECK_IMPORTS")
        else:
            debug_print("✅ Todos los módulos están disponibles", "CHECK_IMPORTS")
        
        return len(missing_modules) == 0
    
    def check_memory_structure(self):
        """Verificar que la estructura de memoria sea compatible con ambas fases"""
        debug_print("🔍 Verificando estructura de memoria", "CHECK_MEMORY")
        
        try:
            from memory.lead_memory import LeadMemory
            
            # Crear instancia de prueba
            test_memory = LeadMemory(
                user_id="test_user",
                name="Test User",
                role="Test Role"
            )
            
            # Verificar campos de FASE 1
            fase_1_fields = [
                'user_id', 'name', 'role', 'interaction_count'
            ]
            
            # Verificar campos de FASE 2
            fase_2_fields = [
                'buyer_persona_match', 'professional_level', 'company_size',
                'industry_sector', 'technical_level', 'decision_making_power',
                'budget_indicators', 'urgency_signals', 'insights_confidence',
                'response_style_preference'
            ]
            
            missing_fase_1_fields = []
            missing_fase_2_fields = []
            
            for field in fase_1_fields:
                if not hasattr(test_memory, field):
                    missing_fase_1_fields.append(field)
            
            for field in fase_2_fields:
                if not hasattr(test_memory, field):
                    missing_fase_2_fields.append(field)
            
            if missing_fase_1_fields:
                debug_print(f"⚠️ Campos FASE 1 faltantes: {missing_fase_1_fields}", "CHECK_MEMORY")
                self.issues_found.append(f"Missing FASE 1 fields: {missing_fase_1_fields}")
            
            if missing_fase_2_fields:
                debug_print(f"⚠️ Campos FASE 2 faltantes: {missing_fase_2_fields}", "CHECK_MEMORY")
                self.issues_found.append(f"Missing FASE 2 fields: {missing_fase_2_fields}")
            
            if not missing_fase_1_fields and not missing_fase_2_fields:
                debug_print("✅ Estructura de memoria compatible", "CHECK_MEMORY")
                return True
            else:
                return False
                
        except Exception as e:
            debug_print(f"❌ Error verificando memoria: {e}", "CHECK_MEMORY")
            self.issues_found.append(f"Memory structure error: {e}")
            return False
    
    def check_generate_intelligent_response_integration(self):
        """Verificar que generate_intelligent_response.py tenga la integración correcta"""
        debug_print("🔍 Verificando integración en generate_intelligent_response.py", "CHECK_INTEGRATION")
        
        try:
            file_path = "app/application/usecases/generate_intelligent_response.py"
            
            if not os.path.exists(file_path):
                debug_print(f"❌ Archivo no encontrado: {file_path}", "CHECK_INTEGRATION")
                self.issues_found.append(f"File not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar imports necesarios
            required_imports = [
                "from app.application.usecases.anti_hallucination_use_case import AntiHallucinationUseCase",
                "from app.application.usecases.personalize_response_use_case import PersonalizeResponseUseCase",
                "from app.application.usecases.extract_user_info_use_case import ExtractUserInfoUseCase",
                "from app.application.usecases.validate_response_use_case import ValidateResponseUseCase"
            ]
            
            missing_imports = []
            for import_line in required_imports:
                if import_line not in content:
                    missing_imports.append(import_line)
            
            # Verificar inicialización en __init__
            required_init_patterns = [
                "self.anti_hallucination_use_case = AntiHallucinationUseCase",
                "self.personalize_response_use_case = PersonalizeResponseUseCase",
                "self.extract_user_info_use_case = ExtractUserInfoUseCase"
            ]
            
            missing_init_patterns = []
            for pattern in required_init_patterns:
                if pattern not in content:
                    missing_init_patterns.append(pattern)
            
            # Verificar métodos de integración
            required_methods = [
                "_should_use_advanced_personalization",
                "_should_use_ai_generation"
            ]
            
            missing_methods = []
            for method in required_methods:
                if f"def {method}" not in content:
                    missing_methods.append(method)
            
            # Verificar flujo de decisión en _generate_contextual_response
            decision_flow_patterns = [
                "should_use_personalization = self._should_use_advanced_personalization",
                "personalization_result = await self.personalize_response_use_case.generate_personalized_response",
                "safe_response_result = await self.anti_hallucination_use_case.generate_safe_response"
            ]
            
            missing_decision_patterns = []
            for pattern in decision_flow_patterns:
                if pattern not in content:
                    missing_decision_patterns.append(pattern)
            
            # Reportar problemas
            if missing_imports:
                debug_print(f"⚠️ Imports faltantes: {len(missing_imports)}", "CHECK_INTEGRATION")
                self.issues_found.append(f"Missing imports: {missing_imports}")
            
            if missing_init_patterns:
                debug_print(f"⚠️ Inicializaciones faltantes: {len(missing_init_patterns)}", "CHECK_INTEGRATION")
                self.issues_found.append(f"Missing init patterns: {missing_init_patterns}")
            
            if missing_methods:
                debug_print(f"⚠️ Métodos faltantes: {len(missing_methods)}", "CHECK_INTEGRATION")
                self.issues_found.append(f"Missing methods: {missing_methods}")
            
            if missing_decision_patterns:
                debug_print(f"⚠️ Patrones de decisión faltantes: {len(missing_decision_patterns)}", "CHECK_INTEGRATION")
                self.issues_found.append(f"Missing decision patterns: {missing_decision_patterns}")
            
            if not any([missing_imports, missing_init_patterns, missing_methods, missing_decision_patterns]):
                debug_print("✅ Integración en generate_intelligent_response.py correcta", "CHECK_INTEGRATION")
                return True
            else:
                return False
                
        except Exception as e:
            debug_print(f"❌ Error verificando integración: {e}", "CHECK_INTEGRATION")
            self.issues_found.append(f"Integration check error: {e}")
            return False
    
    def check_prompts_availability(self):
        """Verificar que los prompts necesarios estén disponibles"""
        debug_print("🔍 Verificando disponibilidad de prompts", "CHECK_PROMPTS")
        
        required_prompt_files = [
            "prompts/anti_hallucination_prompts.py",
            "prompts/personalization_prompts.py"
        ]
        
        missing_files = []
        
        for file_path in required_prompt_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
                debug_print(f"❌ Archivo no encontrado: {file_path}", "CHECK_PROMPTS")
            else:
                debug_print(f"✅ {file_path}", "CHECK_PROMPTS")
        
        if missing_files:
            self.issues_found.append(f"Missing prompt files: {missing_files}")
            debug_print(f"⚠️ Archivos de prompts faltantes: {len(missing_files)}", "CHECK_PROMPTS")
            return False
        else:
            debug_print("✅ Todos los archivos de prompts están disponibles", "CHECK_PROMPTS")
            return True
    
    def run_comprehensive_check(self):
        """Ejecutar verificación completa"""
        debug_print("🚀 Iniciando verificación completa de integración", "MAIN")
        
        checks = [
            ("Imports y dependencias", self.check_imports_and_dependencies),
            ("Estructura de memoria", self.check_memory_structure),
            ("Integración en generate_intelligent_response.py", self.check_generate_intelligent_response_integration),
            ("Disponibilidad de prompts", self.check_prompts_availability)
        ]
        
        passed_checks = 0
        total_checks = len(checks)
        
        for check_name, check_function in checks:
            debug_print(f"🔍 Ejecutando: {check_name}", "MAIN")
            try:
                if check_function():
                    passed_checks += 1
                    debug_print(f"✅ {check_name}: PASÓ", "MAIN")
                else:
                    debug_print(f"❌ {check_name}: FALLÓ", "MAIN")
            except Exception as e:
                debug_print(f"❌ {check_name}: ERROR - {e}", "MAIN")
                self.issues_found.append(f"{check_name} error: {e}")
        
        # Resumen
        print("\n" + "="*60)
        debug_print(f"📊 RESUMEN DE VERIFICACIÓN", "MAIN")
        debug_print(f"✅ Checks pasados: {passed_checks}/{total_checks}", "MAIN")
        
        if self.issues_found:
            debug_print(f"⚠️ Problemas encontrados: {len(self.issues_found)}", "MAIN")
            for i, issue in enumerate(self.issues_found, 1):
                debug_print(f"  {i}. {issue}", "MAIN")
        else:
            debug_print("🎉 No se encontraron problemas de integración", "MAIN")
        
        return passed_checks == total_checks
    
    def generate_fix_report(self):
        """Generar reporte de problemas y soluciones"""
        if not self.issues_found:
            debug_print("✅ No se requieren correcciones", "REPORT")
            return
        
        debug_print("📋 GENERANDO REPORTE DE CORRECCIONES", "REPORT")
        
        report = []
        report.append("# REPORTE DE PROBLEMAS DE INTEGRACIÓN FASES 1 Y 2")
        report.append("")
        report.append("## Problemas Encontrados:")
        
        for i, issue in enumerate(self.issues_found, 1):
            report.append(f"{i}. {issue}")
        
        report.append("")
        report.append("## Acciones Recomendadas:")
        
        # Sugerir acciones basadas en los problemas encontrados
        if any("Missing modules" in issue for issue in self.issues_found):
            report.append("- Verificar que todos los archivos de casos de uso estén creados")
            report.append("- Asegurar que las rutas de importación sean correctas")
        
        if any("Missing FASE" in issue for issue in self.issues_found):
            report.append("- Actualizar la clase LeadMemory con los campos faltantes")
            report.append("- Verificar que la estructura de memoria sea compatible")
        
        if any("Missing imports" in issue for issue in self.issues_found):
            report.append("- Agregar los imports faltantes en generate_intelligent_response.py")
            report.append("- Verificar que los casos de uso estén disponibles")
        
        if any("Missing decision patterns" in issue for issue in self.issues_found):
            report.append("- Revisar el flujo de decisión en _generate_contextual_response")
            report.append("- Asegurar que la integración de fases esté implementada")
        
        # Guardar reporte
        report_file = "INTEGRATION_ISSUES_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        debug_print(f"📄 Reporte guardado en: {report_file}", "REPORT")

def main():
    """Función principal"""
    print("🔧 VERIFICACIÓN Y CORRECCIÓN DE INTEGRACIÓN FASES 1 Y 2")
    print("="*60)
    
    fixer = IntegrationFixer()
    
    # Ejecutar verificación completa
    success = fixer.run_comprehensive_check()
    
    # Generar reporte si hay problemas
    if not success:
        fixer.generate_fix_report()
        debug_print("⚠️ Se encontraron problemas. Revisa el reporte generado.", "MAIN")
    else:
        debug_print("🎉 Integración verificada correctamente", "MAIN")

if __name__ == "__main__":
    main() 