#!/usr/bin/env python3
"""
Script de prueba para verificar el flujo del anuncio de cursos.
"""
import sys
import asyncio
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from app.application.usecases.course_announcement_use_case import CourseAnnouncementUseCase
from app.application.usecases.manage_user_memory import ManageUserMemoryUseCase
from app.application.usecases.query_course_information import QueryCourseInformationUseCase
from app.infrastructure.twilio.client import TwilioWhatsAppClient
from app.domain.entities.message import IncomingMessage
from memory.lead_memory import LeadMemory, MemoryManager
from datetime import datetime

async def test_course_announcement_flow():
    """Prueba el flujo completo del anuncio de cursos."""
    
    print("🧪 INICIANDO PRUEBA DEL FLUJO DE ANUNCIO DE CURSOS")
    print("=" * 60)
    
    # Inicializar componentes
    memory_manager = MemoryManager()
    memory_use_case = ManageUserMemoryUseCase(memory_manager)
    course_query_use_case = QueryCourseInformationUseCase()
    twilio_client = TwilioWhatsAppClient()
    
    # Crear caso de uso
    course_announcement_use_case = CourseAnnouncementUseCase(
        course_query_use_case=course_query_use_case,
        memory_use_case=memory_use_case,
        twilio_client=twilio_client
    )
    
    # Simular mensaje con código de curso
    test_message = IncomingMessage(
        message_sid="TEST_SID_123",
        from_number="+5215614686075",
        to_number="+14155238886",
        body="#Experto_IA_GPT_Gemini #ADSIM_05",
        timestamp=None,
        raw_data={}
    )
    
    user_id = "5215614686075"
    
    print(f"📝 Mensaje de prueba: {test_message.body}")
    print(f"👤 Usuario: {user_id}")
    print("=" * 60)
    
    # Verificar si debe manejar el anuncio
    should_handle = course_announcement_use_case.should_handle_course_announcement(test_message)
    print(f"🔍 ¿Debe manejar anuncio? {should_handle}")
    
    if should_handle:
        print("✅ Código de curso detectado correctamente")
        
        # Extraer código de curso
        course_code = course_announcement_use_case.extract_course_code(test_message.body)
        print(f"📋 Código extraído: {course_code}")
        
        # Procesar anuncio
        print("\n🚀 Procesando anuncio...")
        result = await course_announcement_use_case.handle_course_announcement(
            user_id, test_message
        )
        
        print(f"\n📊 Resultado del procesamiento:")
        print(f"✅ Éxito: {result.get('success', False)}")
        print(f"📚 Código del curso: {result.get('course_code', 'N/A')}")
        print(f"📖 Nombre del curso: {result.get('course_name', 'N/A')}")
        print(f"📤 Respuesta enviada: {result.get('response_sent', False)}")
        print(f"💬 Texto de respuesta: {result.get('response_text', 'N/A')[:100]}...")
        
        # Verificar recursos adicionales
        additional_resources = result.get('additional_resources_sent', {})
        print(f"📄 PDF enviado: {additional_resources.get('pdf_sent', False)}")
        print(f"🖼️ Imagen enviada: {additional_resources.get('image_sent', False)}")
        print(f"📝 Seguimiento enviado: {additional_resources.get('follow_up_sent', False)}")
        
    else:
        print("❌ No se detectó código de curso válido")
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBA COMPLETADA")

if __name__ == "__main__":
    asyncio.run(test_course_announcement_flow()) 