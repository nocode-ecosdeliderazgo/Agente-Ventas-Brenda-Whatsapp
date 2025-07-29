#!/usr/bin/env python3
"""
Simulador del webhook de WhatsApp que replica exactamente el comportamiento real.
Incluye acceso a base de datos y todas las dependencias del sistema.
"""
import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar componentes del sistema (exactamente como en webhook.py)
from app.config import settings
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.database.client import DatabaseClient
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.application.usecases.process_incoming_message import ProcessIncomingMessageUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.application.usecases.tool_activation_use_case import ToolActivationUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.application.usecases.detect_ad_hashtags_use_case import DetectAdHashtagsUseCase
from app.application.usecases.process_ad_flow_use_case import ProcessAdFlowUseCase
from memory.lead_memory import MemoryManager

def debug_print(message: str, function_name: str = "", file_name: str = "webhook_simulation.py"):
    """Print de debug visual para consola"""
    print(f"🔍 [{file_name}::{function_name}] {message}")

class WebhookSimulation:
    """Simulador que replica exactamente el comportamiento del webhook real"""
    
    def __init__(self):
        # Variables globales (exactamente como en webhook.py)
        self.twilio_client = None
        self.memory_use_case = None
        self.intent_analyzer = None
        self.course_query_use_case = None
        self.intelligent_response_use_case = None
        self.process_message_use_case = None
        self.privacy_flow_use_case = None
        self.tool_activation_use_case = None
        self.detect_ad_hashtags_use_case = None
        self.process_ad_flow_use_case = None
        self.openai_client = None
        self.db_client = None
        self.course_repository = None
        
    async def initialize_system(self):
        """Inicializa el sistema exactamente como en webhook.py"""
        debug_print("🚀 INICIANDO SISTEMA BOT BRENDA...", "initialize_system", "webhook_simulation.py")
        
        # Inicializar cliente Twilio
        debug_print("Inicializando cliente Twilio...", "initialize_system", "webhook_simulation.py")
        self.twilio_client = ConsoleTwilioClient()
        debug_print("✅ Cliente Twilio inicializado correctamente", "initialize_system", "webhook_simulation.py")

        # Crear manager de memoria y caso de uso
        debug_print("Inicializando sistema de memoria...", "initialize_system", "webhook_simulation.py")
        memory_manager = MemoryManager(memory_dir="memorias")
        self.memory_use_case = ManageUserMemoryUseCase(memory_manager)
        debug_print("✅ Sistema de memoria inicializado correctamente", "initialize_system", "webhook_simulation.py")

        # Inicializar flujo de privacidad
        debug_print("🔐 Inicializando flujo de privacidad...", "initialize_system", "webhook_simulation.py")
        self.privacy_flow_use_case = PrivacyFlowUseCase(self.memory_use_case, self.twilio_client)
        debug_print("✅ Flujo de privacidad inicializado correctamente", "initialize_system", "webhook_simulation.py")

        # Inicializar sistema con OpenAI
        try:
            debug_print("🤖 Inicializando cliente OpenAI...", "initialize_system", "webhook_simulation.py")
            self.openai_client = OpenAIClient()
            debug_print("✅ Cliente OpenAI inicializado correctamente", "initialize_system", "webhook_simulation.py")
            
            # Inicializar base de datos y repositorio de cursos
            debug_print("🗄️ Inicializando cliente de base de datos...", "initialize_system", "webhook_simulation.py")
            self.db_client = DatabaseClient()
            self.course_repository = CourseRepository()
            debug_print("✅ Cliente de base de datos inicializado correctamente", "initialize_system", "webhook_simulation.py")
            
            debug_print("🧠 Inicializando analizador de intención...", "initialize_system", "webhook_simulation.py")
            self.intent_analyzer = AnalyzeMessageIntentUseCase(self.openai_client, self.memory_use_case)
            debug_print("✅ Analizador de intención inicializado correctamente", "initialize_system", "webhook_simulation.py")
            
            # Inicializar sistema de cursos con base de datos
            debug_print("📚 Inicializando sistema de cursos PostgreSQL...", "initialize_system", "webhook_simulation.py")
            self.course_query_use_case = QueryCourseInformationUseCase()
            course_db_initialized = await self.course_query_use_case.initialize()
            
            if course_db_initialized:
                debug_print("✅ Sistema de cursos PostgreSQL inicializado correctamente", "initialize_system", "webhook_simulation.py")
            else:
                debug_print("⚠️ Sistema de cursos PostgreSQL no disponible, usando modo básico", "initialize_system", "webhook_simulation.py")
                self.course_query_use_case = None
            
            # Crear generador de respuestas inteligentes
            debug_print("🧩 Creando generador de respuestas inteligentes...", "initialize_system", "webhook_simulation.py")
            self.intelligent_response_use_case = GenerateIntelligentResponseUseCase(
                self.intent_analyzer, 
                self.twilio_client, 
                self.openai_client, 
                self.db_client,
                self.course_repository,
                self.course_query_use_case
            )
            debug_print("✅ Generador de respuestas inteligentes creado", "initialize_system", "webhook_simulation.py")
            
            # Inicializar sistema de herramientas de conversión
            debug_print("🛠️ Inicializando sistema de herramientas de conversión...", "initialize_system", "webhook_simulation.py")
            self.tool_activation_use_case = ToolActivationUseCase()
            debug_print("✅ Sistema de herramientas inicializado correctamente", "initialize_system", "webhook_simulation.py")
            
            # Inicializar sistema de flujo de anuncios
            debug_print("📢 Inicializando sistema de flujo de anuncios...", "initialize_system", "webhook_simulation.py")
            self.detect_ad_hashtags_use_case = DetectAdHashtagsUseCase()
            self.process_ad_flow_use_case = ProcessAdFlowUseCase(
                self.memory_use_case, 
                self.privacy_flow_use_case, 
                self.course_query_use_case
            )
            debug_print("✅ Sistema de flujo de anuncios inicializado correctamente", "initialize_system", "webhook_simulation.py")
            
            # Crear caso de uso de procesamiento con capacidades inteligentes
            debug_print("⚙️ Creando procesador de mensajes principal...", "initialize_system", "webhook_simulation.py")
            self.process_message_use_case = ProcessIncomingMessageUseCase(
                self.twilio_client, self.memory_use_case, self.intelligent_response_use_case, 
                self.privacy_flow_use_case, self.tool_activation_use_case,
                detect_ad_hashtags_use_case=self.detect_ad_hashtags_use_case,
                process_ad_flow_use_case=self.process_ad_flow_use_case
            )
            debug_print("✅ Procesador de mensajes principal creado", "initialize_system", "webhook_simulation.py")
            
            if self.course_query_use_case:
                debug_print("🎉 SISTEMA COMPLETO: OpenAI + Memoria + PostgreSQL inicializado correctamente", "initialize_system", "webhook_simulation.py")
            else:
                debug_print("🎉 SISTEMA BÁSICO: OpenAI + Memoria local inicializado correctamente", "initialize_system", "webhook_simulation.py")
                
        except Exception as e:
            debug_print(f"❌ Error inicializando sistema: {e}", "initialize_system", "webhook_simulation.py")
            raise
    
    def create_webhook_data(self, user_message: str, user_id: str = "console_user_001") -> Dict[str, Any]:
        """Crea datos de webhook simulados exactamente como los envía Twilio"""
        return {
            'MessageSid': f"console_sim_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'From': f'whatsapp:+{user_id}',
            'To': f'whatsapp:{settings.twilio_phone_number}',
            'Body': user_message,
            'AccountSid': 'console_sim_account',
            'MessagingServiceSid': 'console_sim_service',
            'NumMedia': '0',
            'ProfileName': 'Usuario Consola',
            'WaId': user_id
        }
    
    async def process_webhook_message(self, user_message: str, user_id: str = "console_user_001"):
        """Procesa un mensaje exactamente como lo hace el webhook real"""
        try:
            debug_print(f"📨 MENSAJE RECIBIDO!\n📱 Desde: whatsapp:+{user_id}\n💬 Texto: '{user_message}'", "process_webhook_message", "webhook_simulation.py")
            
            # Preparar datos del webhook (exactamente como en webhook.py)
            debug_print("📦 Preparando datos del webhook...", "process_webhook_message", "webhook_simulation.py")
            webhook_data = self.create_webhook_data(user_message, user_id)
            debug_print("✅ Datos del webhook preparados correctamente", "process_webhook_message", "webhook_simulation.py")
            
            # Procesar mensaje de forma síncrona (exactamente como en webhook.py)
            debug_print("🚀 INICIANDO PROCESAMIENTO SÍNCRONO...", "process_webhook_message", "webhook_simulation.py")
            result = await self.process_message_use_case.execute(webhook_data)
            debug_print(f"📊 Resultado del procesamiento: {result}", "process_webhook_message", "webhook_simulation.py")
            
            if result['success'] and result['processed']:
                debug_print(
                    f"✅ MENSAJE PROCESADO EXITOSAMENTE!\n"
                    f"📤 Respuesta enviada: {result['response_sent']}\n"
                    f"🔗 SID respuesta: {result.get('response_sid', 'N/A')}", 
                    "process_webhook_message", "webhook_simulation.py"
                )
                return result
            else:
                debug_print(f"⚠️ MENSAJE NO PROCESADO: {result}", "process_webhook_message", "webhook_simulation.py")
                return result
                
        except Exception as e:
            debug_print(f"💥 ERROR EN WEBHOOK: {e}", "process_webhook_message", "webhook_simulation.py")
            return {'success': False, 'error': str(e)}
    
    def print_header(self):
        """Imprime el header del simulador"""
        print("\n" + "="*80)
        print("🤖 BRENDA - SIMULADOR DE WEBHOOK COMPLETO")
        print("="*80)
        print("📱 Replicando exactamente el comportamiento del webhook real")
        print("🧠 Sistema inteligente con OpenAI GPT-4o-mini")
        print("💾 Memoria de usuario persistente")
        print("🔒 Flujo de privacidad obligatorio")
        print("🎯 Análisis de intención PyME-específico")
        print("🎁 Sistema de bonos inteligente")
        print("📚 Acceso a base de datos PostgreSQL")
        print("="*80)
        print("💬 Escribe tu mensaje y presiona Enter")
        print("🛑 Escribe 'salir' para terminar la conversación")
        print("="*80)
        
    def print_debug_separator(self):
        """Imprime separador para los debug prints"""
        print("\n" + "#"*80)
        print("🔍 DEBUG PRINTS DEL SISTEMA (WEBHOOK SIMULATION)")
        print("#"*80)
        
    def print_response_separator(self):
        """Imprime separador para la respuesta final"""
        print("\n" + "#"*80)
        print("🤖 RESPUESTA FINAL DE BRENDA")
        print("#"*80)
        
    def print_user_message(self, message: str):
        """Imprime el mensaje del usuario"""
        print(f"\n👤 USUARIO ({datetime.now().strftime('%H:%M:%S')}):")
        print(f"   {message}")
        
    def print_agent_response(self, response: str):
        """Imprime la respuesta del agente"""
        print(f"\n🤖 BRENDA ({datetime.now().strftime('%H:%M:%S')}):")
        print(f"   {response}")
        
    def save_conversation_log(self, user_message: str, agent_response: str, conversation_count: int):
        """Guarda el log de la conversación"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "conversation_count": conversation_count,
            "system": "webhook_simulation"
        }
        
        # Crear directorio de logs si no existe
        os.makedirs("logs", exist_ok=True)
        
        # Guardar en archivo de log
        log_file = f"logs/webhook_simulation_log_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️  Error guardando log: {e}")
            
    async def run_simulation(self):
        """Ejecuta la simulación del webhook"""
        self.print_header()
        
        print("\n🎯 ESPERANDO TU PRIMER MENSAJE...")
        print("💡 Sugerencia: Prueba con 'Hola' para iniciar el flujo de privacidad")
        
        conversation_count = 0
        
        while True:
            try:
                # Esperar mensaje del usuario
                user_message = input("\n👤 Tú: ").strip()
                
                # Verificar si quiere salir
                if user_message.lower() in ['salir', 'exit', 'quit', 's']:
                    print("\n👋 ¡Hasta luego! Gracias por probar el sistema Brenda.")
                    break
                    
                # Verificar mensaje vacío
                if not user_message:
                    print("⚠️  Por favor, escribe un mensaje.")
                    continue
                    
                # Incrementar contador de conversación
                conversation_count += 1
                
                # Mostrar mensaje del usuario
                self.print_user_message(user_message)
                
                # Mostrar separador de debug
                self.print_debug_separator()
                
                # Procesar mensaje exactamente como el webhook
                result = await self.process_webhook_message(user_message)
                
                # Mostrar separador de respuesta
                self.print_response_separator()
                
                # Mostrar respuesta del agente
                if result and result.get('success'):
                    response_text = result.get('response_text', '')
                    if response_text:
                        self.print_agent_response(response_text)
                        self.save_conversation_log(user_message, response_text, conversation_count)
                    else:
                        self.print_agent_response("Lo siento, no pude procesar tu mensaje.")
                else:
                    self.print_agent_response("Ocurrió un error procesando tu mensaje. Inténtalo de nuevo.")
                
                # Esperar siguiente mensaje
                print(f"\n🎯 ESPERANDO TU SIGUIENTE MENSAJE... (Conversación #{conversation_count})")
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego! Conversación interrumpida por el usuario.")
                break
            except Exception as e:
                print(f"\n💥 Error inesperado: {e}")
                print("🔄 Continuando con la conversación...")

class ConsoleTwilioClient(TwilioWhatsAppClient):
    """Cliente Twilio simulado para consola"""
    
    def __init__(self):
        self.sent_messages = []
        
    async def send_message(self, message):
        """Simula el envío de mensaje via Twilio"""
        message_data = {
            'to_number': message.to_number,
            'body': message.body,
            'message_type': message.message_type.value,
            'timestamp': datetime.now().isoformat(),
            'message_sid': f"console_sim_{len(self.sent_messages)}"
        }
        
        self.sent_messages.append(message_data)
        
        print(f"📱 [TWILIO SIMULADO] Enviando mensaje:")
        print(f"   Para: {message.to_number}")
        print(f"   Mensaje: {message.body}")
        print(f"   SID: {message_data['message_sid']}")
        
        return {
            'success': True,
            'message_sid': message_data['message_sid'],
            'error': None
        }

async def main():
    """Función principal"""
    print("🚀 Iniciando simulador de webhook Brenda...")
    
    # Verificar configuración
    try:
        print("🔧 Verificando configuración...")
        print(f"   OpenAI API Key: {'✅ Configurado' if settings.openai_api_key else '❌ No configurado'}")
        print(f"   Twilio Phone: {'✅ Configurado' if settings.twilio_phone_number else '❌ No configurado'}")
        print(f"   Database URL: {'✅ Configurado' if settings.database_url else '❌ No configurado'}")
        print(f"   Environment: {settings.app_environment}")
        
        if not settings.openai_api_key:
            print("⚠️  ADVERTENCIA: OpenAI API Key no configurada. Algunas funcionalidades pueden no funcionar.")
            
    except Exception as e:
        print(f"⚠️  Error verificando configuración: {e}")
    
    # Crear y ejecutar simulador
    simulator = WebhookSimulation()
    
    try:
        # Inicializar sistema (exactamente como en webhook.py)
        await simulator.initialize_system()
        
        # Ejecutar simulación
        await simulator.run_simulation()
    except Exception as e:
        print(f"💥 Error ejecutando simulación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 