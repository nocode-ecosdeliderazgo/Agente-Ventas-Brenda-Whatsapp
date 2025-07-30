# DOCUMENTACIÓN DE BASE DE DATOS - SISTEMA DE CURSOS DE IA

## 📋 Resumen Ejecutivo

Esta documentación describe la estructura completa de la base de datos del sistema de cursos de IA para "Aprenda y Aplique IA". La base de datos está diseñada para gestionar cursos, sesiones, actividades, recursos multimedia y bonos, proporcionando toda la información necesaria para que el agente Brenda pueda ofrecer recomendaciones personalizadas y respuestas contextuales.

## 🏗️ Arquitectura de la Base de Datos

### **Diagrama de Relaciones**
```
ai_courses (1) ←→ (N) ai_course_session
     ↑                        ↑
     │                        │
     │                        │
     │                        │
ai_tema_activity (N) ←→ (1) ai_course_session
     ↑
     │
     │
elements_url (N) ←→ (1) ai_tema_activity

bond (N) ←→ (1) ai_courses
```

## 📊 Tablas Principales

### 1. **`ai_courses` - Catálogo de Cursos**

**Propósito**: Tabla central que almacena información completa de cada curso de IA.

#### **Estructura de Columnas**
```sql
CREATE TABLE public.ai_courses (
  id_course uuid NOT NULL DEFAULT gen_random_uuid(),           -- PK único
  Name character varying,                                      -- Nombre del curso
  Short_description character varying,                         -- Descripción corta
  Long_descrption character varying,                          -- Descripción larga
  created_at timestamp with time zone NOT NULL DEFAULT now(), -- Fecha creación
  session_count smallint,                                     -- Número de sesiones
  total_duration_min bigint,                                  -- Duración total (minutos)
  Price character varying,                                     -- Precio (string)
  Currency character varying,                                  -- Moneda
  course_url character varying,                               -- URL del curso
  Purchase_url character varying,                             -- URL de compra
  level character varying,                                     -- Nivel (Beginner, Intermediate, etc.)
  language character varying,                                  -- Idioma del curso
  audience_category character varying,                         -- Categoría de audiencia
  status character varying,                                    -- Estado (Active, Upcoming, etc.)
  start_date timestamp without time zone,                     -- Fecha de inicio
  end_date timestamp without time zone,                       -- Fecha de fin
  roi character varying,                                      -- Descripción del ROI
  modality character varying NOT NULL,                        -- Modalidad (Online, In-person)
  CONSTRAINT ai_courses_pkey PRIMARY KEY (id_course)
);
```

#### **Datos de Ejemplo (Basado en Imágenes)**
```json
{
  "id_course": "11111111-1111-1111-1111-111111111111",
  "Name": "Experto en IA para Profesionales: Domina",
  "Short_description": "Capacitar a profesionales para optimizar",
  "Long_descrption": "En este curso aprenderás desde los funda",
  "created_at": "2025-07-26 20:16:20.924679+00",
  "session_count": 4,
  "total_duration_min": 12,
  "Price": "4000",
  "Currency": "USD",
  "level": "Intermediate",
  "language": "Spanish",
  "audience_category": "Professionals",
  "status": "Active",
  "modality": "Online"
}
```

### 2. **`ai_course_session` - Sesiones de Cursos**

**Propósito**: Define las sesiones individuales que componen cada curso.

#### **Estructura de Columnas**
```sql
CREATE TABLE public.ai_course_session (
  id_session uuid NOT NULL DEFAULT gen_random_uuid(),          -- PK único
  created_at timestamp with time zone NOT NULL DEFAULT now(), -- Fecha creación
  session_index smallint,                                     -- Índice/orden de la sesión
  title character varying,                                     -- Título de la sesión
  objective character varying,                                 -- Objetivo de aprendizaje
  duration_minutes bigint,                                     -- Duración en minutos
  scheduled_at timestamp without time zone,                   -- Fecha programada
  id_course_fk uuid,                                          -- FK a ai_courses
  CONSTRAINT ai_course_session_pkey PRIMARY KEY (id_session),
  CONSTRAINT ai_course_session_id_course_fk_fkey FOREIGN KEY (id_course_fk) REFERENCES public.ai_courses(id_course)
);
```

#### **Datos de Ejemplo (Basado en Imágenes)**
```json
[
  {
    "id_session": "22222222-2222-2222-2222-222222222222",
    "session_index": 1,
    "title": "Descubriendo la IA para Profesi",
    "objective": "Comprender la importancia de la IA y farr",
    "duration_minutes": 180,
    "scheduled_at": null
  },
  {
    "id_session": "33333333-3333-3333-3333-333333333333",
    "session_index": 2,
    "title": "Dominando la Comunicación co",
    "objective": "Dominar técnicas avanzadas de promptin",
    "duration_minutes": 180,
    "scheduled_at": null
  },
  {
    "id_session": "44444444-4444-4444-4444-444444444444",
    "session_index": 3,
    "title": "IMPULSO con ChatGPT para PY",
    "objective": "Aplicar el modelo IMPULSO para resolver",
    "duration_minutes": 180,
    "scheduled_at": null
  },
  {
    "id_session": "55555555-5555-5555-5555-555555555555",
    "session_index": 4,
    "title": "Estrategia y Proyecto Integradoı",
    "objective": "Diseñar e implementar un plan IA real y r",
    "duration_minutes": 180,
    "scheduled_at": null
  }
]
```

### 3. **`ai_tema_activity` - Actividades y Temas**

**Propósito**: Almacena las actividades y temas específicos dentro de cada sesión.

#### **Estructura de Columnas**
```sql
CREATE TABLE public.ai_tema_activity (
  id_activity uuid NOT NULL DEFAULT gen_random_uuid(),         -- PK único
  created_at timestamp with time zone NOT NULL DEFAULT now(), -- Fecha creación
  id_course_fk uuid NOT NULL DEFAULT gen_random_uuid(),      -- FK a ai_courses
  id_session_fk uuid NOT NULL DEFAULT gen_random_uuid(),     -- FK a ai_course_session
  item_session integer NOT NULL,                              -- Orden dentro de la sesión
  item_type text NOT NULL,                                    -- Tipo: "subtema" o "actividad"
  title_item character varying NOT NULL,                      -- Título del elemento
  CONSTRAINT ai_tema_activity_pkey PRIMARY KEY (id_activity),
  CONSTRAINT ai_tema_activity_id_session_fk_fkey FOREIGN KEY (id_session_fk) REFERENCES public.ai_course_session(id_session),
  CONSTRAINT ai_tema_activity_id_course_fk_fkey FOREIGN KEY (id_course_fk) REFERENCES public.ai_courses(id_course)
);
```

#### **Datos de Ejemplo (Basado en Imágenes)**
```json
[
  {
    "id_activity": "aaaaaaa1-0000-0000-0000-aaaaaaaaaaa111111",
    "id_session_fk": "22222222-2222-2222-2222-222222222222",
    "item_session": 1,
    "item_type": "subtema",
    "title_item": "Introducción a la IA y casos de negocio re"
  },
  {
    "id_activity": "bbbbbbb1-0000-0000-0000-bbbbbbbbb111111",
    "id_session_fk": "22222222-2222-2222-2222-222222222222",
    "item_session": 2,
    "item_type": "actividad",
    "title_item": "Configuración de cuentas en ChatGPT y ("
  },
  {
    "id_activity": "ccccccc1-0000-0000-0000-ccccccccc111111",
    "id_session_fk": "22222222-2222-2222-2222-222222222222",
    "item_session": 3,
    "item_type": "subtema",
    "title_item": "Comparación de fortalezas: ChatGPT vs."
  },
  {
    "id_activity": "ddddddd1-0000-0000-0000-ddddddddd111111",
    "id_session_fk": "22222222-2222-2222-2222-222222222222",
    "item_session": 4,
    "item_type": "actividad",
    "title_item": "Ejercicio guiado: actualizar tu CV con pro"
  }
]
```

### 4. **`bond` - Bonos y Beneficios**

**Propósito**: Almacena los bonos, beneficios y recursos adicionales asociados a cada curso.

#### **Estructura de Columnas**
```sql
CREATE TABLE public.bond (
  id_bond bigint GENERATED ALWAYS AS IDENTITY NOT NULL,       -- PK auto-increment
  created_at timestamp with time zone NOT NULL DEFAULT now(), -- Fecha creación
  content text NOT NULL,                                      -- Descripción del bono
  type_bond character varying NOT NULL,                       -- Tipo: "bonus"
  id_courses_fk uuid,                                         -- FK a ai_courses
  emisor character varying NOT NULL,                          -- Emisor del bono
  CONSTRAINT bond_pkey PRIMARY KEY (id_bond),
  CONSTRAINT Bond_id_courses_fk_fkey FOREIGN KEY (id_courses_fk) REFERENCES public.ai_courses(id_course)
);
```

#### **Datos de Ejemplo (Basado en Imágenes)**
```json
[
  {
    "id_bond": 1,
    "content": "Workbook interactivo en Coda.io con plantillas y actividades colaborativas preconfiguradas. Copia tu propio espacio y personaliza tu aprendizaje.",
    "type_bond": "bonus",
    "id_courses_fk": "11111111-1111-1111-1111-111111111111",
    "emisor": "Ecos de liderazgo"
  },
  {
    "id_bond": 2,
    "content": "Acceso 100% online a las grabaciones de todas las sesiones (4 masterclasses de 3h cada una), disponibles hasta el cierre del curso.",
    "type_bond": "bonus",
    "id_courses_fk": "11111111-1111-1111-1111-111111111111",
    "emisor": "Ecos de liderazgo"
  },
  {
    "id_bond": 3,
    "content": "Soporte en Telegram con nuestro agente de Aprende y Aplica IA, para resolver dudas y compartir casos reales.",
    "type_bond": "bonus",
    "id_courses_fk": "11111111-1111-1111-1111-111111111111",
    "emisor": "Ecos de liderazgo"
  },
  {
    "id_bond": 4,
    "content": "Acceso vitalicio a la comunidad privada de alumnos, donde podrás intercambiar experiencias y seguir aprendiendo junto a otros profesionales.",
    "type_bond": "bonus",
    "id_courses_fk": "11111111-1111-1111-1111-111111111111",
    "emisor": "Ecos de liderazgo"
  },
  {
    "id_bond": 5,
    "content": "Bolsa de empleo especializada en oportunidades para expertos en IA, con ofertas exclusivas para la comunidad.",
    "type_bond": "bonus",
    "id_courses_fk": "11111111-1111-1111-1111-111111111111",
    "emisor": "Ecos de liderazgo"
  },
  {
    "id_bond": 6,
    "content": "Biblioteca de prompts avanzada, con más de 100 ejemplos comentados y plantillas para distintos casos de uso empresariales.",
    "type_bond": "bonus",
    "id_courses_fk": "11111111-1111-1111-1111-111111111111",
    "emisor": "Ecos de liderazgo"
  },
  {
    "id_bond": 7,
    "content": "Insignia digital y banner para LinkedIn que certifica tu condición de "Experto en IA para Profesionales", lista para compartir en redes.",
    "type_bond": "bonus",
    "id_courses_fk": "11111111-1111-1111-1111-111111111111",
    "emisor": "Ecos de liderazgo"
  },
  {
    "id_bond": 8,
    "content": "Descuento exclusivo (10%) en packs de integración de ChatGPT y Gemini, para que implementes automatizaciones de inmediato.",
    "type_bond": "bonus",
    "id_courses_fk": "11111111-1111-1111-1111-111111111111",
    "emisor": "Ecos de liderazgo"
  },
  {
    "id_bond": 9,
    "content": "1 sesiones trimestrales de Q&A en vivo con Ernesto Hernández, resolviendo dudas y compartiendo tendencias.",
    "type_bond": "bonus",
    "id_courses_fk": "11111111-1111-1111-1111-111111111111",
    "emisor": "Ecos de liderazgo"
  },
  {
    "id_bond": 10,
    "content": "Suscripción anual al boletín "AI Trends", con análisis de mercado, casos de éxito y herramientas emergentes.",
    "type_bond": "bonus",
    "id_courses_fk": "11111111-1111-1111-1111-111111111111",
    "emisor": "Ecos de liderazgo"
  }
]
```

### 5. **`elements_url` - Recursos Multimedia**

**Propósito**: Almacena URLs y recursos multimedia asociados a sesiones y actividades.

#### **Estructura de Columnas**
```sql
CREATE TABLE public.elements_url (
  id_element uuid NOT NULL DEFAULT gen_random_uuid(),          -- PK único
  created_at timestamp with time zone NOT NULL DEFAULT now(), -- Fecha creación
  id_session_fk uuid NOT NULL DEFAULT gen_random_uuid(),     -- FK a ai_course_session
  id_activity_fk uuid DEFAULT gen_random_uuid(),             -- FK a ai_tema_activity
  item_type character varying NOT NULL,                       -- Tipo: "video" o "document"
  url_test character varying NOT NULL,                        -- URL del recurso
  description_url character varying NOT NULL,                 -- Descripción del recurso
  CONSTRAINT elements_url_pkey PRIMARY KEY (id_element),
  CONSTRAINT Elements_url_id_activity_fk_fkey FOREIGN KEY (id_activity_fk) REFERENCES public.ai_tema_activity(id_activity),
  CONSTRAINT Elements_url_id_session_fk_fkey FOREIGN KEY (id_session_fk) REFERENCES public.ai_course_session(id_session)
);
```

#### **Datos de Ejemplo (Basado en SQL)**
```json
[
  {
    "id_element": "66666662-0000-0000-0000-666666666661",
    "id_session_fk": "22222222-2222-2222-2222-222222222222",
    "id_activity_fk": "aaaaaaa1-0000-0000-0000-aaaaaaaaaaa1",
    "item_type": "video",
    "url_test": "https://example.com/grabacion/sesion1",
    "description_url": "Grabación Sesión 1: Descubriendo la IA para Profesionales"
  },
  {
    "id_element": "66666662-0000-0000-0000-666666666662",
    "id_session_fk": "22222222-2222-2222-2222-222222222222",
    "id_activity_fk": "aaaaaaa1-0000-0000-0000-aaaaaaaaaaa2",
    "item_type": "document",
    "url_test": "https://coda.io/workbook-plantilla",
    "description_url": "Plantilla Coda.io: Workbook interactivo para prácticas de la sesión 1"
  },
  {
    "id_element": "77777773-0000-0000-0000-777777777771",
    "id_session_fk": "33333333-3333-3333-3333-333333333333",
    "id_activity_fk": "bbbbbbb2-0000-0000-0000-bbbbbbbbbbb1",
    "item_type": "video",
    "url_test": "https://example.com/grabacion/sesion2",
    "description_url": "Grabación Sesión 2: Dominando la Comunicación con IA"
  },
  {
    "id_element": "77777773-0000-0000-0000-777777777772",
    "id_session_fk": "33333333-3333-3333-3333-333333333333",
    "id_activity_fk": "bbbbbbb2-0000-0000-0000-bbbbbbbbbbb2",
    "item_type": "document",
    "url_test": "https://coda.io/plantilla-agente-gpt",
    "description_url": "Guía paso a paso: Construcción de tu agente GPT/Gemini"
  },
  {
    "id_element": "88888884-0000-0000-0000-888888888881",
    "id_session_fk": "44444444-4444-4444-4444-444444444444",
    "id_activity_fk": "ccccccc3-0000-0000-0000-ccccccccc3c1",
    "item_type": "video",
    "url_test": "https://example.com/grabacion/sesion3",
    "description_url": "Grabación Sesión 3: IMPULSO con ChatGPT para PYMES"
  },
  {
    "id_element": "88888884-0000-0000-0000-888888888882",
    "id_session_fk": "44444444-4444-4444-4444-444444444444",
    "id_activity_fk": "ccccccc3-0000-0000-0000-ccccccccc3c2",
    "item_type": "document",
    "url_test": "https://coda.io/casos-impulso-pymes",
    "description_url": "Ejercicios interactivos: Reto de negocio con modelo IMPULSO"
  },
  {
    "id_element": "99999995-0000-0000-0000-999999999991",
    "id_session_fk": "55555555-5555-5555-5555-555555555555",
    "id_activity_fk": "ddddddd4-0000-0000-0000-ddddddddd4d1",
    "item_type": "video",
    "url_test": "https://example.com/grabacion/sesion4",
    "description_url": "Grabación Sesión 4: Estrategia y Proyecto Integrador"
  },
  {
    "id_element": "99999995-0000-0000-0000-999999999992",
    "id_session_fk": "55555555-5555-5555-5555-555555555555",
    "id_activity_fk": "ddddddd4-0000-0000-0000-ddddddddd4d2",
    "item_type": "document",
    "url_test": "https://coda.io/plantilla-plan-ia",
    "description_url": "Plantilla Coda.io: Bosquejo de plan de IA y métricas de impacto"
  }
]
```

## 🎯 Información Clave para Prompts del Agente

### **Datos Críticos para Personalización**

#### **1. Información del Curso**
- **Nombre**: "Experto en IA para Profesionales: Domina"
- **Duración**: 4 sesiones, 12 horas totales
- **Precio**: $4000 USD
- **Nivel**: Intermediate
- **Audiencia**: Professionals
- **Modalidad**: Online
- **Estado**: Active

#### **2. Estructura del Curso**
```
Sesión 1: Descubriendo la IA para Profesionales (180 min)
├── Subtema: Introducción a la IA y casos de negocio
├── Actividad: Configuración de cuentas en ChatGPT
├── Subtema: Comparación de fortalezas: ChatGPT vs.
└── Actividad: Ejercicio guiado: actualizar tu CV

Sesión 2: Dominando la Comunicación con IA (180 min)
├── Subtema: Técnicas avanzadas de prompting
└── Actividad: Creación de tu primer agente GPT/Gemin

Sesión 3: IMPULSO con ChatGPT para PyMEs (180 min)
├── Subtema: Introducción al modelo IMPULSO para PY
└── Actividad: Caso práctico: resolver un reto de negoci

Sesión 4: Estrategia y Proyecto Integrado (180 min)
├── Subtema: Diseño de la estrategia IA para tu empres
└── Actividad: Ejercicio individual: bosquejo de tu plan d
```

#### **3. Bonos Incluidos (10 bonos totales)**
1. **Workbook interactivo en Coda.io** - Plantillas y actividades colaborativas preconfiguradas. Copia tu propio espacio y personaliza tu aprendizaje.
2. **Acceso 100% online a grabaciones** - 4 masterclasses de 3h cada una, disponibles hasta el cierre del curso.
3. **Soporte en Telegram** - Agente de Aprende y Aplica IA para dudas y casos reales.
4. **Comunidad privada vitalicia** - Intercambio de experiencias con otros profesionales.
5. **Bolsa de empleo especializada** - Oportunidades exclusivas para expertos en IA.
6. **Biblioteca de prompts avanzada** - Más de 100 ejemplos comentados para casos empresariales.
7. **Insignia digital LinkedIn** - Certificación "Experto en IA para Profesionales".
8. **Descuento exclusivo 10%** - En packs de integración ChatGPT y Gemini.
9. **Sesiones Q&A trimestrales** - En vivo con Ernesto Hernández, tendencias y dudas.
10. **Suscripción anual "AI Trends"** - Análisis de mercado, casos de éxito y herramientas.

#### **4. Recursos Multimedia**
- **Videos**: Grabaciones de cada sesión (4 masterclasses de 3h cada una)
- **Documentos**: Plantillas Coda.io, guías paso a paso, ejercicios interactivos
- **Plataformas**: Coda.io, Telegram, LinkedIn, YouTube
- **Recursos por sesión**:
  - **Sesión 1**: Grabación + Plantilla Coda.io para prácticas
  - **Sesión 2**: Grabación + Guía construcción agente GPT/Gemini
  - **Sesión 3**: Grabación + Ejercicios modelo IMPULSO para PyMEs
  - **Sesión 4**: Grabación + Plantilla plan IA y métricas de impacto

## 🤖 Adaptación para Prompts del Agente

### **Información para Incluir en Prompts**

#### **1. Detalles del Curso**
```python
course_info = {
    "name": "Experto en IA para Profesionales: Domina",
    "duration": "4 sesiones (12 horas totales)",
    "price": "$4000 USD",
    "level": "Intermediate",
    "audience": "Professionals",
    "modality": "Online",
    "roi": "Optimización de procesos profesionales con IA"
}
```

#### **2. Estructura Detallada**
```python
sessions = [
    {
        "title": "Descubriendo la IA para Profesionales",
        "objective": "Comprender la importancia de la IA y fundamentos",
        "duration": "180 minutos",
        "activities": [
            "Introducción a la IA y casos de negocio",
            "Configuración de cuentas en ChatGPT",
            "Comparación de fortalezas: ChatGPT vs. otras herramientas",
            "Ejercicio guiado: actualizar tu CV con prompts"
        ]
    },
    # ... más sesiones
]
```

#### **3. Bonos y Beneficios**
```python
bonuses = [
    "Workbook interactivo en Coda.io",
    "Acceso 100% online a grabaciones",
    "Soporte continuo en Telegram",
    "Comunidad privada vitalicia",
    "Bolsa de empleo especializada",
    "Biblioteca de prompts avanzada",
    "Insignia digital y banner para LinkedIn",
    "Descuento exclusivo del 10% en packs adicionales",
    "Sesión trimestral de Q&A en vivo",
    "Suscripción anual al boletín 'AI Trends'"
]
```

### **Ejemplos de Prompts Adaptados**

#### **1. Recomendación de Curso**
```
"Basándome en tu rol de {user_role}, te recomiendo nuestro curso 'Experto en IA para Profesionales: Domina'. 

Este curso de 4 sesiones (12 horas) está diseñado específicamente para profesionales como tú que buscan optimizar sus procesos con IA.

**Lo que aprenderás:**
• Fundamentos de IA aplicada a casos de negocio reales
• Técnicas avanzadas de prompting para ChatGPT
• Modelo IMPULSO para resolver retos empresariales
• Estrategia IA personalizada para tu empresa

**Inversión:** $4000 USD con acceso vitalicio a todos los recursos.

**Bonos incluidos:** 10 beneficios adicionales como workbook interactivo, comunidad privada, bolsa de empleo especializada y más."
```

#### **2. Detalle de Sesiones**
```
"El curso está estructurado en 4 sesiones prácticas:

**Sesión 1: Descubriendo la IA para Profesionales (3 horas)**
- Introducción a la IA y casos de negocio reales
- Configuración de cuentas en ChatGPT
- Comparación de herramientas de IA
- Ejercicio práctico: actualizar tu CV con prompts

**Sesión 2: Dominando la Comunicación con IA (3 horas)**
- Técnicas avanzadas de prompting
- Creación de tu primer agente GPT/Gemini

**Sesión 3: IMPULSO con ChatGPT para PyMEs (3 horas)**
- Modelo IMPULSO para resolver retos empresariales
- Caso práctico aplicado a tu sector

**Sesión 4: Estrategia y Proyecto Integrado (3 horas)**
- Diseño de estrategia IA para tu empresa
- Ejercicio individual: bosquejo de tu plan de implementación"
```

#### **3. Bonos y Valor Agregado**
```
"Además del curso completo, incluyes acceso a:

🎁 **10 Bonos Exclusivos:**
• Workbook interactivo en Coda.io para ejercicios prácticos
• Acceso 100% online a todas las grabaciones
• Soporte continuo en Telegram con nuestro equipo
• Comunidad privada vitalicia de profesionales
• Bolsa de empleo especializada en oportunidades de IA
• Biblioteca de prompts avanzada con más de 100 templates
• Insignia digital y banner para LinkedIn que certifique tus habilidades
• Descuento exclusivo del 10% en packs adicionales
• Sesión trimestral de Q&A en vivo con expertos
• Suscripción anual al boletín 'AI Trends' con las últimas novedades

**Valor total:** Más de $2000 USD en bonos adicionales incluidos."
```

## 📊 Queries Útiles para el Agente

### **1. Obtener Información del Curso**
```sql
SELECT 
    Name, Short_description, Long_descrption, 
    session_count, total_duration_min, Price, Currency,
    level, language, audience_category, status, roi, modality
FROM ai_courses 
WHERE id_course = '11111111-1111-1111-1111-111111111111';
```

### **2. Obtener Sesiones del Curso**
```sql
SELECT 
    session_index, title, objective, duration_minutes
FROM ai_course_session 
WHERE id_course_fk = '11111111-1111-1111-1111-111111111111'
ORDER BY session_index;
```

### **3. Obtener Actividades de una Sesión**
```sql
SELECT 
    item_session, item_type, title_item
FROM ai_tema_activity 
WHERE id_session_fk = '22222222-2222-2222-2222-222222222222'
ORDER BY item_session;
```

### **4. Obtener Bonos del Curso**
```sql
SELECT 
    content, emisor
FROM bond 
WHERE id_courses_fk = '11111111-1111-1111-1111-111111111111'
AND type_bond = 'bonus';
```

### **5. Obtener Recursos Multimedia**
```sql
SELECT 
    item_type, url_test, description_url
FROM elements_url 
WHERE id_session_fk = '22222222-2222-2222-2222-222222222222'
ORDER BY created_at;
```

## 🎯 Recomendaciones para Prompts

### **1. Personalización por Rol**
- **Marketing Digital**: Enfatizar casos de negocio y ROI
- **Operaciones**: Enfatizar optimización de procesos
- **Ventas**: Enfatizar herramientas de comunicación
- **CEO/Founder**: Enfatizar estrategia y transformación digital

### **2. Enfoque en Valor**
- **Precio**: $4000 USD (mencionar como inversión, no gasto)
- **ROI**: Optimización de procesos profesionales
- **Bonos**: $2000+ USD en valor adicional
- **Duración**: 12 horas (4 sesiones de 3 horas)

### **3. Estructura de Respuesta**
1. **Identificación de necesidad** basada en rol
2. **Presentación del curso** con detalles específicos
3. **Estructura de sesiones** con objetivos claros
4. **Bonos y beneficios** como valor agregado
5. **Call to action** para más información

---

## ⚡ Actualizaciones Recientes (Julio 2025)

### **🔧 Mejoras en Sistema de Respuestas Inteligentes**
- ✅ **Acceso correcto a BD**: Flujo de anuncios accede perfectamente a la base de datos
- ⚡ **Validación de roles**: Previene almacenamiento de roles inválidos como "Hola"
- 🤖 **Optimización OpenAI**: Sistema usa respuestas directas vs templates genéricos
- ⏳ **Pendiente validación**: Testing completo de mejoras en respuestas con datos de BD

### **🎯 Sistema de Bonos Contextual Actualizado**
- ✅ **10 bonos reales**: Todos los bonos están cargados en la tabla `bond`
- ⚡ **Activación inteligente**: Bonos presentados según contexto del usuario
- 🎁 **Presentación mejorada**: Formato adaptado para WhatsApp Business
- ⏳ **Pendiente validación**: Confirmar activación contextual con mejoras recientes

### **📊 Estado de Integración Actual**
- ✅ **Flujo de anuncios**: Perfecta integración con base de datos funcionando
- ✅ **Consultas de cursos**: Queries funcionando correctamente
- ✅ **Recursos multimedia**: URLs y contenido disponible en `elements_url`
- ⚡ **Respuestas inteligentes**: Mejoradas para usar datos reales de BD

---

**Estado**: ⚡ **FUNCIONAL CON MEJORAS RECIENTES**  
**Fecha**: Julio 2025 (Actualizado)  
**Propósito**: Adaptación completa del agente Brenda con base de datos PostgreSQL e integración inteligente de bonos contextuales 