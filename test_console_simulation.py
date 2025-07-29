#!/usr/bin/env python3
"""
Script de simulación en consola para probar el sistema Brenda sin depender de WhatsApp/Twilio.
Replica exactamente el comportamiento del webhook pero en modo interactivo por consola.
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
from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.generate_intelligent_response import GenerateIntelligentResponseUseCase
from app.application.usecases.privacy_flow_use_case import PrivacyFlowUseCase
from app.application.usecases.analyze_message_intent import AnalyzeMessageIntentUseCase
from app.application.usecases.process_incoming_message import ProcessIncomingMessageUseCase
from app.infrastructure.openai.client import OpenAIClient
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from memory.lead_memory import MemoryManager, LeadMemory

class ConsoleTwilioClient(TwilioWhatsAppClient):
    """Cliente Twilio simulado para consola que hereda de TwilioWhatsAppClient"""
    
    def __init__(self):
        self.sent_messages = []
        
    async def send_message(self, message: OutgoingMessage) -> Dict[str, Any]:
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
    
    def get_sent_messages(self) -> List[Dict[str, Any]]:
        """Obtiene todos los mensajes enviados"""
        return self.sent_messages

class ConsoleSimulation:
    """Simulador de conversación en consola para el sistema Brenda"""
    
    def __init__(self):
        # Inicializar componentes del sistema
        self.memory_manager = MemoryManager()
        self.memory_use_case = ManageUserMemoryUseCase(self.memory_manager)
        self.openai_client = OpenAIClient()
        self.twilio_client = ConsoleTwilioClient()
        
        # Inicializar casos de uso
        self.analyze_intent_use_case = AnalyzeMessageIntentUseCase(
            openai_client=self.openai_client,
            memory_use_case=self.memory_use_case
        )
        
        self.intelligent_response_use_case = GenerateIntelligentResponseUseCase(
            intent_analyzer=self.analyze_intent_use_case,
            twilio_client=self.twilio_client,
            openai_client=self.openai_client
        )
        
        self.privacy_flow_use_case = PrivacyFlowUseCase(
            memory_use_case=self.memory_use_case,
            twilio_client=self.twilio_client
        )
        
        # Inicializar procesador principal
        self.processor = ProcessIncomingMessageUseCase(
            twilio_client=self.twilio_client,
            memory_use_case=self.memory_use_case,
            intelligent_response_use_case=self.intelligent_response_use_case,
            privacy_flow_use_case=self.privacy_flow_use_case
        )
        
        self.user_id = "console_user_001"
        self.conversation_count = 0
        
    def print_header(self):
        """Imprime el header del simulador"""
        print("\n" + "="*80)
        print("🤖 BRENDA - SIMULADOR DE CONVERSACIÓN EN CONSOLA")
        print("="*80)
        print("📱 Simulando WhatsApp sin dependencias de Twilio")
        print("🧠 Sistema inteligente con OpenAI GPT-4o-mini")
        print("💾 Memoria de usuario persistente")
        print("🔒 Flujo de privacidad obligatorio")
        print("🎯 Análisis de intención PyME-específico")
        print("🎁 Sistema de bonos inteligente")
        print("="*80)
        print("💬 Escribe tu mensaje y presiona Enter")
        print("🛑 Escribe 'salir' para terminar la conversación")
        print("="*80)
        
    def print_debug_separator(self):
        """Imprime separador para los debug prints"""
        print("\n" + "#"*80)
        print("🔍 DEBUG PRINTS DEL SISTEMA")
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
        
    def create_incoming_message(self, user_message: str) -> IncomingMessage:
        """Crea un mensaje entrante simulado"""
        webhook_data = {
            'From': 'whatsapp:+1234567890',  # Número simulado con prefijo WhatsApp
            'To': f'whatsapp:{settings.twilio_phone_number}',
            'Body': user_message,
            'MessageSid': "console_sim_" + str(self.conversation_count),
            'Timestamp': datetime.now().isoformat()
        }
        
        return IncomingMessage.from_twilio_webhook(webhook_data)
        
    def save_conversation_log(self, user_message: str, agent_response: str):
        """Guarda el log de la conversación"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "conversation_count": self.conversation_count
        }
        
        # Crear directorio de logs si no existe
        os.makedirs("logs", exist_ok=True)
        
        # Guardar en archivo de log
        log_file = f"logs/conversation_log_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️  Error guardando log: {e}")
            
    async def process_message(self, user_message: str):
        """Procesa un mensaje del usuario"""
        try:
            # Crear mensaje entrante simulado
            incoming_message = self.create_incoming_message(user_message)
            
            # Mostrar separador de debug
            self.print_debug_separator()
            
            # Procesar mensaje con el sistema real
            print("🔄 Procesando mensaje con sistema inteligente...")
            
            # Crear datos de webhook simulados
            webhook_data = {
                'From': incoming_message.from_number,
                'To': incoming_message.to_number,
                'Body': incoming_message.body,
                'MessageSid': incoming_message.message_sid,
                'Timestamp': incoming_message.timestamp.isoformat()
            }
            
            result = await self.processor.execute(webhook_data)
            
            # Mostrar separador de respuesta
            self.print_response_separator()
            
            # Mostrar respuesta del agente
            if result and result.get('success'):
                response_text = result.get('response_text', '')
                if response_text:
                    self.print_agent_response(response_text)
                    self.save_conversation_log(user_message, response_text)
                else:
                    self.print_agent_response("Lo siento, no pude procesar tu mensaje.")
            else:
                self.print_agent_response("Ocurrió un error procesando tu mensaje. Inténtalo de nuevo.")
                
        except Exception as e:
            print(f"💥 Error procesando mensaje: {e}")
            self.print_agent_response("Ocurrió un error procesando tu mensaje. Inténtalo de nuevo.")
            
    async def run_simulation(self):
        """Ejecuta la simulación de conversación"""
        self.print_header()
        
        print("\n🎯 ESPERANDO TU PRIMER MENSAJE...")
        print("💡 Sugerencia: Prueba con 'Hola' para iniciar el flujo de privacidad")
        
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
                self.conversation_count += 1
                
                # Mostrar mensaje del usuario
                self.print_user_message(user_message)
                
                # Procesar mensaje
                await self.process_message(user_message)
                
                # Esperar siguiente mensaje
                print(f"\n🎯 ESPERANDO TU SIGUIENTE MENSAJE... (Conversación #{self.conversation_count})")
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego! Conversación interrumpida por el usuario.")
                break
            except Exception as e:
                print(f"\n💥 Error inesperado: {e}")
                print("🔄 Continuando con la conversación...")

def main():
    """Función principal"""
    print("🚀 Iniciando simulador de conversación Brenda...")
    
    # Verificar configuración
    try:
        print("🔧 Verificando configuración...")
        print(f"   OpenAI API Key: {'✅ Configurado' if settings.openai_api_key else '❌ No configurado'}")
        print(f"   Twilio Phone: {'✅ Configurado' if settings.twilio_phone_number else '❌ No configurado'}")
        print(f"   Environment: {settings.app_environment}")
        
        if not settings.openai_api_key:
            print("⚠️  ADVERTENCIA: OpenAI API Key no configurada. Algunas funcionalidades pueden no funcionar.")
            
    except Exception as e:
        print(f"⚠️  Error verificando configuración: {e}")
    
    # Crear y ejecutar simulador
    simulator = ConsoleSimulation()
    
    try:
        # Ejecutar simulación
        asyncio.run(simulator.run_simulation())
    except Exception as e:
        print(f"💥 Error ejecutando simulación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 