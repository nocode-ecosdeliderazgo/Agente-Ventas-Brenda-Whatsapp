#!/usr/bin/env python3
"""
Script de prueba específico para el flujo de anuncio de cursos.
Simula la recepción de códigos de cursos como #CursoIA1 y valida la respuesta completa.
"""
import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar componentes del sistema
from app.config import settings
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.infrastructure.openai.client import OpenAIClient
from app.application.usecases.process_incoming_message import ProcessIncomingMessageUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.application.usecases.tool_activation_use_case import ToolActivationUseCase
from app.application.usecases.course_announcement_use_case import CourseAnnouncementUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from memory.lead_memory import MemoryManager

def debug_print(message: str, function_name: str = "", file_name: str = "test_course_announcement.py"):
    """Print de debug visual para consola"""
    print(f"🔍 [{file_name}::{function_name}] {message}")

class CourseAnnouncementTester:
    """Tester específico para el flujo de anuncio de cursos"""
    
    def __init__(self):
        # Variables del sistema
        self.twilio_client = None
        self.memory_use_case = None
        self.intent_analyzer = None
        self.course_query_use_case = None
        self.intelligent_response_use_case = None
        self.process_message_use_case = None
        self.privacy_flow_use_case = None
        self.tool_activation_use_case = None
        self.course_announcement_use_case = None
        self.openai_client = None
        
        # Test cases definidos
        self.test_cases = [
            {
                "name": "Prueba #CursoIA1 - Usuario nuevo",
                "user_id": "test_user_001",
                "setup_user": True,
                "user_data": {
                    "name": "María García",
                    "role": "Gerente de Marketing Digital",
                    "privacy_accepted": True
                },
                "message": "#CursoIA1",
                "expected_responses": [
                    "Introducción a la Inteligencia Artificial para PyMEs",
                    "497",
                    "USD",
                    "8 sesiones",
                    "Principiante"
                ]
            },
            {
                "name": "Prueba #CursoIA2 - Usuario con rol diferente",
                "user_id": "test_user_002", 
                "setup_user": True,
                "user_data": {
                    "name": "Carlos Mendoza",
                    "role": "Director de Operaciones",
                    "privacy_accepted": True
                },
                "message": "#CursoIA2",
                "expected_responses": [
                    "IA Intermedia",
                    "797",
                    "USD",
                    "12 sesiones",
                    "Intermedio"
                ]
            },
            {
                "name": "Prueba código inexistente",
                "user_id": "test_user_003",
                "setup_user": True,
                "user_data": {
                    "name": "Ana López",
                    "role": "CEO",
                    "privacy_accepted": True
                },
                "message": "#CursoInexistente123",
                "expected_responses": [
                    "no encontrado",
                    "#CursoIA1",
                    "#CursoIA2",
                    "#CursoIA3"
                ]
            },
            {
                "name": "Prueba con mensaje mixto",
                "user_id": "test_user_004",
                "setup_user": True,
                "user_data": {
                    "name": "Roberto Silva",
                    "role": "Fundador",
                    "privacy_accepted": True
                },
                "message": "Hola, me interesa el #CursoIA1 para mi empresa",
                "expected_responses": [
                    "Introducción a la Inteligencia Artificial",
                    "PyMEs",
                    "497",
                    "8 sesiones"
                ]
            },
            {
                "name": "Prueba sin privacidad aceptada",
                "user_id": "test_user_005",
                "setup_user": True,
                "user_data": {
                    "name": "Usuario",
                    "role": "No disponible",
                    "privacy_accepted": False
                },
                "message": "#CursoIA1",
                "expected_responses": [
                    "privacidad",
                    "consentimiento",
                    "datos"
                ]
            }
        ]
        
    async def initialize_system(self):
        """Inicializa el sistema exactamente como en webhook.py"""
        debug_print("🚀 INICIANDO SISTEMA DE PRUEBAS DE ANUNCIO DE CURSOS...", "initialize_system")
        
        # Inicializar cliente Twilio simulado
        debug_print("Inicializando cliente Twilio simulado...", "initialize_system")
        self.twilio_client = ConsoleTwilioClient()
        debug_print("✅ Cliente Twilio simulado inicializado", "initialize_system")

        # Crear manager de memoria y caso de uso
        debug_print("Inicializando sistema de memoria...", "initialize_system")
        memory_manager = MemoryManager(memory_dir="memorias_test")
        self.memory_use_case = ManageUserMemoryUseCase(memory_manager)
        debug_print("✅ Sistema de memoria inicializado", "initialize_system")

        # Inicializar flujo de privacidad
        debug_print("🔐 Inicializando flujo de privacidad...", "initialize_system")
        self.privacy_flow_use_case = PrivacyFlowUseCase(self.memory_use_case, self.twilio_client)
        debug_print("✅ Flujo de privacidad inicializado", "initialize_system")

        # Inicializar sistema con OpenAI (opcional)
        try:
            debug_print("🤖 Inicializando cliente OpenAI...", "initialize_system")
            self.openai_client = OpenAIClient()
            debug_print("✅ Cliente OpenAI inicializado", "initialize_system")
            
            debug_print("🧠 Inicializando analizador de intención...", "initialize_system")
            self.intent_analyzer = AnalyzeMessageIntentUseCase(self.openai_client, self.memory_use_case)
            debug_print("✅ Analizador de intención inicializado", "initialize_system")
            
            # Sistema de cursos (sin base de datos por ahora)
            debug_print("📚 Inicializando sistema de cursos...", "initialize_system")
            self.course_query_use_case = None  # Sin base de datos
            debug_print("✅ Sistema de cursos en modo mock", "initialize_system")
            
            # Crear generador de respuestas inteligentes
            debug_print("🧩 Creando generador de respuestas inteligentes...", "initialize_system")
            self.intelligent_response_use_case = GenerateIntelligentResponseUseCase(
                self.intent_analyzer, self.twilio_client, self.openai_client, self.course_query_use_case
            )
            debug_print("✅ Generador de respuestas inteligentes creado", "initialize_system")
            
            # Inicializar sistema de herramientas
            debug_print("🛠️ Inicializando sistema de herramientas...", "initialize_system")
            self.tool_activation_use_case = ToolActivationUseCase()
            debug_print("✅ Sistema de herramientas inicializado", "initialize_system")
            
        except Exception as e:
            debug_print(f"⚠️ OpenAI no disponible: {e}", "initialize_system")
            self.openai_client = None
            self.intent_analyzer = None
            self.intelligent_response_use_case = None
            self.tool_activation_use_case = None
        
        # Inicializar sistema de anuncios de cursos
        debug_print("📚 Inicializando sistema de anuncios de cursos...", "initialize_system")
        self.course_announcement_use_case = CourseAnnouncementUseCase(
            self.course_query_use_case, self.memory_use_case, self.twilio_client
        )
        debug_print("✅ Sistema de anuncios de cursos inicializado", "initialize_system")
        
        # Crear caso de uso de procesamiento principal
        debug_print("⚙️ Creando procesador de mensajes principal...", "initialize_system")
        self.process_message_use_case = ProcessIncomingMessageUseCase(
            self.twilio_client, self.memory_use_case, self.intelligent_response_use_case, 
            self.privacy_flow_use_case, self.tool_activation_use_case, self.course_announcement_use_case
        )
        debug_print("✅ Procesador de mensajes principal creado", "initialize_system")
        
        debug_print("🎉 SISTEMA DE PRUEBAS INICIALIZADO CORRECTAMENTE", "initialize_system")
    
    def create_webhook_data(self, user_message: str, user_id: str) -> Dict[str, Any]:
        """Crea datos de webhook simulados"""
        return {
            'MessageSid': f"test_course_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'From': f'whatsapp:+{user_id}',
            'To': f'whatsapp:{settings.twilio_phone_number}',
            'Body': user_message,
            'AccountSid': 'test_account',
            'MessagingServiceSid': 'test_service',
            'NumMedia': '0',
            'ProfileName': 'Usuario Test',
            'WaId': user_id
        }
    
    async def setup_test_user(self, user_id: str, user_data: Dict[str, Any]):
        """Configura un usuario de prueba con datos específicos"""
        try:
            debug_print(f"🔧 Configurando usuario de prueba {user_id}...", "setup_test_user")
            
            # Obtener o crear memoria del usuario
            user_memory = await self.memory_use_case.get_user_memory(user_id)
            
            # Configurar datos del usuario
            user_memory.name = user_data.get('name', 'Usuario Test')
            user_memory.role = user_data.get('role', 'Test Role')
            user_memory.privacy_accepted = user_data.get('privacy_accepted', True)
            
            if user_memory.privacy_accepted:
                user_memory.privacy_requested = True
                user_memory.stage = "sales_agent"
                user_memory.current_flow = "none"
            else:
                user_memory.privacy_requested = False
                user_memory.stage = "first_contact"
                user_memory.current_flow = "privacy"
            
            # Guardar memoria
            await self.memory_use_case.save_user_memory(user_memory)
            
            debug_print(f"✅ Usuario {user_id} configurado: {user_memory.name} ({user_memory.role})", "setup_test_user")
            
        except Exception as e:
            debug_print(f"❌ Error configurando usuario {user_id}: {e}", "setup_test_user")
    
    async def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un caso de prueba específico"""
        try:
            debug_print(f"🧪 EJECUTANDO: {test_case['name']}", "run_test_case")
            
            user_id = test_case['user_id']
            message = test_case['message']
            expected_responses = test_case['expected_responses']
            
            # Configurar usuario si es necesario
            if test_case.get('setup_user'):
                await self.setup_test_user(user_id, test_case['user_data'])
            
            # Crear datos del webhook
            webhook_data = self.create_webhook_data(message, user_id)
            
            # Procesar mensaje
            debug_print(f"📨 Enviando mensaje: '{message}'", "run_test_case")
            result = await self.process_message_use_case.execute(webhook_data)
            
            # Validar resultado
            validation_result = self.validate_test_result(result, expected_responses, test_case)
            
            debug_print(f"📊 Resultado: {'✅ ÉXITO' if validation_result['success'] else '❌ FALLO'}", "run_test_case")
            
            return {
                'test_name': test_case['name'],
                'success': validation_result['success'],
                'result': result,
                'validation': validation_result,
                'expected': expected_responses,
                'actual_response': result.get('response_text', ''),
                'processing_type': result.get('processing_type', 'unknown')
            }
            
        except Exception as e:
            debug_print(f"💥 Error en caso de prueba: {e}", "run_test_case")
            return {
                'test_name': test_case['name'],
                'success': False,
                'error': str(e),
                'result': None
            }
    
    def validate_test_result(self, result: Dict[str, Any], expected_responses: List[str], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Valida el resultado de un caso de prueba"""
        try:
            if not result.get('success'):
                return {
                    'success': False,
                    'reason': 'processing_failed',
                    'details': result.get('error', 'Unknown error')
                }
            
            response_text = result.get('response_text', '').lower()
            processing_type = result.get('processing_type', '')
            
            # Validaciones específicas por tipo de procesamiento
            validation_details = []
            
            # Para casos que esperan flujo de privacidad
            if any('privacidad' in exp.lower() for exp in expected_responses):
                if processing_type == 'privacy_flow':
                    validation_details.append("✅ Flujo de privacidad activado correctamente")
                else:
                    validation_details.append("❌ Se esperaba flujo de privacidad")
                    return {
                        'success': False,
                        'reason': 'wrong_processing_type',
                        'expected': 'privacy_flow',
                        'actual': processing_type,
                        'details': validation_details
                    }
            
            # Para casos que esperan anuncio de curso
            elif any('#curso' in exp.lower() or 'ia' in exp.lower() for exp in expected_responses):
                if processing_type == 'course_announcement':
                    validation_details.append("✅ Flujo de anuncio de curso activado correctamente")
                    
                    # Validar recursos adicionales
                    additional_resources = result.get('additional_resources_sent', {})
                    if additional_resources.get('pdf_sent'):
                        validation_details.append("✅ PDF enviado")
                    if additional_resources.get('image_sent'):
                        validation_details.append("✅ Imagen enviada")
                    if additional_resources.get('follow_up_sent'):
                        validation_details.append("✅ Mensaje de seguimiento enviado")
                        
                else:
                    validation_details.append(f"❌ Se esperaba anuncio de curso, obtuvo: {processing_type}")
            
            # Validar contenido esperado en la respuesta
            matches = 0
            for expected in expected_responses:
                if expected.lower() in response_text:
                    matches += 1
                    validation_details.append(f"✅ Encontrado: '{expected}'")
                else:
                    validation_details.append(f"❌ No encontrado: '{expected}'")
            
            # Calcular éxito basado en coincidencias
            success_rate = matches / len(expected_responses) if expected_responses else 1
            is_success = success_rate >= 0.7  # 70% de coincidencias mínimas
            
            return {
                'success': is_success,
                'success_rate': success_rate,
                'matches': matches,
                'total_expected': len(expected_responses),
                'processing_type': processing_type,
                'details': validation_details
            }
            
        except Exception as e:
            return {
                'success': False,
                'reason': 'validation_error',
                'details': [f"Error validando: {e}"]
            }
    
    async def run_all_tests(self):
        """Ejecuta todos los casos de prueba"""
        print("\n" + "="*80)
        print("🧪 INICIANDO PRUEBAS DEL FLUJO DE ANUNCIO DE CURSOS")
        print("="*80)
        
        results = []
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n{'='*20} PRUEBA {i}/{len(self.test_cases)} {'='*20}")
            
            result = await self.run_test_case(test_case)
            results.append(result)
            
            # Mostrar resultado de la prueba
            self.print_test_result(result, i)
            
            # Pausa entre pruebas
            await asyncio.sleep(1)
        
        # Mostrar resumen final
        self.print_test_summary(results)
        
        return results
    
    def print_test_result(self, result: Dict[str, Any], test_number: int):
        """Imprime el resultado de una prueba individual"""
        test_name = result['test_name']
        success = result['success']
        
        status_icon = "✅" if success else "❌"
        print(f"\n{status_icon} PRUEBA {test_number}: {test_name}")
        
        if success:
            validation = result.get('validation', {})
            print(f"   📊 Tasa de éxito: {validation.get('success_rate', 0):.1%}")
            print(f"   🎯 Tipo de procesamiento: {result.get('processing_type', 'unknown')}")
            
            # Mostrar detalles de validación
            details = validation.get('details', [])
            for detail in details[:3]:  # Mostrar máximo 3 detalles
                print(f"   {detail}")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            validation = result.get('validation', {})
            if validation.get('details'):
                for detail in validation['details'][:2]:
                    print(f"   {detail}")
    
    def print_test_summary(self, results: List[Dict[str, Any]]):
        """Imprime resumen final de todas las pruebas"""
        print("\n" + "="*80)
        print("📊 RESUMEN FINAL DE PRUEBAS")
        print("="*80)
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"📈 Total de pruebas: {total_tests}")
        print(f"✅ Pruebas exitosas: {successful_tests}")
        print(f"❌ Pruebas fallidas: {failed_tests}")
        print(f"📊 Tasa de éxito: {successful_tests/total_tests:.1%}")
        
        # Mostrar detalles de pruebas fallidas
        if failed_tests > 0:
            print(f"\n❌ PRUEBAS FALLIDAS:")
            for result in results:
                if not result['success']:
                    print(f"   • {result['test_name']}: {result.get('error', 'Validation failed')}")
        
        # Mostrar tipos de procesamiento detectados
        processing_types = {}
        for result in results:
            if result['success']:
                proc_type = result.get('processing_type', 'unknown')
                processing_types[proc_type] = processing_types.get(proc_type, 0) + 1
        
        if processing_types:
            print(f"\n🔄 TIPOS DE PROCESAMIENTO DETECTADOS:")
            for proc_type, count in processing_types.items():
                print(f"   • {proc_type}: {count} veces")
        
        print("\n" + "="*80)

class ConsoleTwilioClient(TwilioWhatsAppClient):
    """Cliente Twilio simulado para las pruebas"""
    
    def __init__(self):
        self.sent_messages = []
        
    async def send_message(self, message):
        """Simula el envío de mensaje via Twilio"""
        message_data = {
            'to_number': message.to_number,
            'body': message.body,
            'message_type': message.message_type.value,
            'timestamp': datetime.now().isoformat(),
            'message_sid': f"test_msg_{len(self.sent_messages)}"
        }
        
        self.sent_messages.append(message_data)
        
        print(f"📱 [TWILIO SIMULADO] Mensaje enviado:")
        print(f"   Para: {message.to_number}")
        print(f"   Contenido: {message.body[:100]}{'...' if len(message.body) > 100 else ''}")
        print(f"   SID: {message_data['message_sid']}")
        
        return {
            'success': True,
            'message_sid': message_data['message_sid'],
            'error': None
        }

async def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del flujo de anuncio de cursos...")
    
    # Verificar configuración
    try:
        print("🔧 Verificando configuración...")
        print(f"   OpenAI API Key: {'✅ Configurado' if settings.openai_api_key else '❌ No configurado'}")
        print(f"   Twilio Phone: {'✅ Configurado' if settings.twilio_phone_number else '❌ No configurado'}")
        print(f"   Environment: {settings.app_environment}")
        
        if not settings.openai_api_key:
            print("⚠️  ADVERTENCIA: OpenAI API Key no configurada. Las pruebas seguirán con datos mock.")
            
    except Exception as e:
        print(f"⚠️  Error verificando configuración: {e}")
    
    # Crear y ejecutar tester
    tester = CourseAnnouncementTester()
    
    try:
        # Inicializar sistema
        await tester.initialize_system()
        
        # Ejecutar todas las pruebas
        results = await tester.run_all_tests()
        
        # Determinar código de salida
        successful_tests = sum(1 for r in results if r['success'])
        if successful_tests == len(results):
            print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
            sys.exit(0)
        else:
            print("⚠️  Algunas pruebas fallaron. Revisar resultados arriba.")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Error ejecutando pruebas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())