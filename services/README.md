# Microservicios

Sistema diseñado para gestionar perfiles de candidatos, procesar grandes volúmenes de datos, realizar búsquedas semánticas y generar información valiosa mediante IA para los flujos de trabajo de reclutamiento.

La plataforma combina operaciones CRUD tradicionales con capacidades de IA modernas, como búsqueda vectorial, incrustaciones, clasificación de candidatos y análisis automatizado de perfiles.

## Arquitectura
El backend está construido utilizando FastAPI y sigue una arquitectura de microservicios compuesta por cuatro servicios independientes:
```
```

## Services

### Api Gateway
La puerta de enlace API actúa como punto de entrada único para todas las solicitudes de los clientes.

Responsabilidades:
- Enrutamiento de solicitudes
- Validación de autenticación
- Agregación de API
- Configuración de CORS
- Limitación de velocidad
- Registro centralizado

### Identity Service
Gestiona la autenticación y autorización en toda la plataforma.

Responsabilidades:
- Registro de usuarios
- Inicio de sesión de usuarios
- Generación y validación de tokens JWT
- Control de acceso basado en roles
- Gestión de perfiles de usuario

### Candidate Service
Servicio empresarial principal responsable de la gestión de candidatos.

Responsabilidades:
- Operaciones CRUD de candidatos
- Gestión de la experiencia
- Registros académicos
- Gestión de habilidades
- Almacenamiento de perfiles de candidatos

Funciones principales:
- Crear perfiles de candidatos
- Actualizar información de candidatos
- Eliminar registros de candidatos
- Buscar metadatos de candidatos

### Intelligence Service
Ofrece capacidades avanzadas de procesamiento de datos e inteligencia artificial.

Responsabilidades:
1. Procesamiento ETL
    - Ingesta masiva de datos
    - Procesamiento de archivos CSV y Excel
    - Normalización de datos
    - Validación de datos
2. Búsqueda semántica
    - Generación de incrustaciones de texto
    - Indexación vectorial
    - Búsqueda de similitud
    - Capacidades de búsqueda híbrida
3. Análisis mediante IA
    - Resumen de perfiles de candidatos
    - Alineación de candidatos con puestos de trabajo
    - Clasificación de candidatos
    - Recomendaciones automatizadas
    - Generación de información para la selección de personal
4. Tecnologías:
    - Modelos de lenguaje a gran escala (LLM)
    - Base de datos vectorial
    - Modelos de incrustación
    - Procesamiento en segundo plano

## Stack Tech

### Backend
- FastAPI
- Python 3.12+
- SQLAlchemy
- Pydantic

### Bases de datos
- PostgreSQL
- Base de datos vectorial (Qdrant)

### IA y búsqueda
- API de OpenAI
- Modelos de incrustación
- Búsqueda semántica

### Infrastructure
- Docker
- Docker Compose
- Nginx / API Gateway