# memory/ - Documentación de Memoria Persistente

Esta carpeta contiene toda la lógica relacionada con la memoria persistente de usuarios/leads para el bot Brenda.

## Componentes principales
- **lead_memory.py**: Define la estructura de datos (LeadMemory) y el gestor de memoria (MemoryManager).

## Responsabilidades
- Almacenar y recuperar información relevante de cada usuario (nombre, curso, historial, intereses, etc.).
- Garantizar la persistencia de datos entre sesiones (usando archivos JSON o base de datos).
- Implementar auto-corrección de datos corruptos y backups automáticos.
- Proveer métodos para actualizar, leer y validar la memoria de cada usuario.

## Buenas prácticas
- No almacenar información sensible sin cifrado.
- Realizar backups antes de modificar archivos de memoria.
- Validar la estructura de los datos al cargar la memoria.
- Mantener la lógica de memoria separada de la lógica de negocio y de canal.

## Ejemplo de uso
```python
from memory.lead_memory import LeadMemory, MemoryManager
```

## Notas
- Si se requiere migrar la memoria a una base de datos, este módulo debe ser el único punto de acceso.
- Toda actualización de memoria debe pasar por el MemoryManager. 