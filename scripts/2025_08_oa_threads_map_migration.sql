-- Migración para integración de OpenAI Assistants API (Threads)
-- Tabla de mapeo entre números de WhatsApp y thread_id de OpenAI

-- Crear tabla de mapeo si no existe
CREATE TABLE IF NOT EXISTS public.oa_threads_map (
    user_phone text PRIMARY KEY,           -- Número de WhatsApp como "whatsapp:+1234567890"
    thread_id text NOT NULL,               -- Thread ID de OpenAI Assistants API
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Crear índice en thread_id para búsquedas reversas (opcional pero recomendado)
CREATE INDEX IF NOT EXISTS idx_oa_threads_map_thread_id 
ON public.oa_threads_map(thread_id);

-- Comentarios para documentación
COMMENT ON TABLE public.oa_threads_map IS 'Mapeo entre números de WhatsApp y Thread IDs de OpenAI Assistants API';
COMMENT ON COLUMN public.oa_threads_map.user_phone IS 'Número de WhatsApp en formato Twilio: whatsapp:+1234567890';
COMMENT ON COLUMN public.oa_threads_map.thread_id IS 'Thread ID único de OpenAI Assistants API';
COMMENT ON COLUMN public.oa_threads_map.created_at IS 'Timestamp de creación del mapeo';
COMMENT ON COLUMN public.oa_threads_map.updated_at IS 'Timestamp de última actualización del mapeo';