# Esquema condensado de la base de datos de **Brenda Bot**

> Última actualización: 2025‑08‑03

| Tabla                   | Descripción                                                           | Claves y columnas clave                                                                                                                                                          |
| ----------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ai\_courses**         | Catálogo maestro de cursos de IA                                      | **id\_course** (uuid, PK), name, short\_description, *long\_description*, price, currency, session\_count, total\_duration\_min, level, modality, status, start\_date, end\_date |
| **ai\_course\_session** | Sesiones cronológicas de cada curso                                   | **id\_session** (uuid, PK), session\_index (smallint), title, objective, duration\_minutes, scheduled\_at, **id\_course\_fk** → ai\_courses                                      |
| **ai\_tema\_activity**  | Actividades o sub‑temas dentro de una sesión                          | **id\_activity** (uuid, PK), item\_type (quiz / demo / task), title\_item, **id\_session\_fk**, **id\_course\_fk**                                                               |
| **bond**                | Bonos y recursos extra ligados a un curso                             | **id\_bond** (bigint, PK), content, type\_bond, **id\_courses\_fk**, bond\_url, active                                                                                           |
| **elements\_url**       | Recursos multimedia (videos, docs) referenciados a sesión o actividad | **id\_element** (uuid, PK), item\_type, url\_test, description\_url, **id\_session\_fk**, id\_activity\_fk                                                                       |

### Relaciones principales

```
ai_courses 1 ────< ai_course_session 1 ────< ai_tema_activity
   |                                \
   |                                 > ai_course_session has many elements_url
   |
   > ai_courses 1 ────< bond
   > ai_courses 1 ────< elements_url (opcional via sesión/actividad)
```

### Consultas típicas existentes

```sql
-- 1) Obtener resumen de catálogo
SELECT id_course, name, price, currency, level, modality
FROM ai_courses
WHERE status = 'active';

-- 2) Detalle completo de un curso
SELECT *
FROM ai_courses           c
LEFT JOIN ai_course_session  s ON s.id_course_fk = c.id_course
LEFT JOIN ai_tema_activity  a ON a.id_course_fk = c.id_course
LEFT JOIN bond               b ON b.id_courses_fk = c.id_course
LEFT JOIN elements_url       e ON e.id_course_fk = c.id_course OR e.id_session_fk = s.id_session;

-- 3) Búsqueda por texto
SELECT id_course, name, short_description
FROM ai_courses
WHERE to_tsvector('spanish', name || ' ' || short_description) @@ plainto_tsquery('spanish', :query);
```

### Índices recomendados

```sql
CREATE INDEX idx_ai_courses_name_tsv ON ai_courses USING gin (to_tsvector('spanish', name));
CREATE INDEX idx_ai_course_session_course_fk ON ai_course_session (id_course_fk);
CREATE INDEX idx_ai_tema_activity_session_fk ON ai_tema_activity (id_session_fk);
```

### Reglas de permisos sugeridas para la herramienta `tool_db.query`

| Tabla               | Solo SELECT | Filtros permitidos                 | Comentario                               |
| ------------------- | ----------- | ---------------------------------- | ---------------------------------------- |
| ai\_courses         | ✅           | name ILIKE, level, modality, price | Nunca exponer CLABE u otra data sensible |
| ai\_course\_session | ✅           | id\_course\_fk                     | Limitar a 20 filas                       |
| ai\_tema\_activity  | ✅           | id\_session\_fk                    | —                                        |
| bond                | ✅           | id\_courses\_fk, active=true       | —                                        |
| elements\_url       | ✅           | id\_session\_fk, item\_type        | —                                        |

> **Nota**: el agente **solo** debe consultar columnas listadas arriba; cualquier columna nueva deberá añadirse explícitamente en el prompt de permisos.

---

### Uso de ejemplo de la herramienta (pseudo‑JSON)

```json
{
  "tool": "tool_db.query",
  "table": "ai_courses",
  "filters": {"level": "intermedio", "modality": "online"},
  "limit": 3
}
```

---

¡Listo para adjuntar a Claude o cualquier otra IA como contexto de esquema!
