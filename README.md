<p align="center">
  | <a href="https://github.com/OsOsorioP/EasyJobs/blob/main/README.english.md" target="_blank">english</a> |
</p>

# EasyJobs

![React](https://img.shields.io/badge/React-313131?style=flat&logo=react)
![Vite](https://img.shields.io/badge/Vite-313131?style=flat&logo=vite)
![Vite](https://img.shields.io/badge/pnpm-313131?style=flat&logo=pnpm)
![FastAPI](https://img.shields.io/badge/FastAPI-313131?style=flat&logo=fastapi)
![FastAPI](https://img.shields.io/badge/uv-313131?style=flat&logo=uv)
![LangChain](https://img.shields.io/badge/LangChain-313131?style=flat&logo=langchain)
![Qdrant](https://img.shields.io/badge/Qdrant-313131?style=flat&logo=qdrant)
![Postgres](https://img.shields.io/badge/Postgres-313131?style=flat&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-313131?style=flat&logo=docker)
![Status](https://img.shields.io/badge/Status-development-success)

**EasyJobs** es una plataforma de reclutamiento impulsada por inteligencia artificial para gestionar candidatos, procesar perfiles de forma masiva y buscar información semántica con ayuda de LLMs. El proyecto combina microfrontends, microservicios y un gateway para ofrecer un flujo completo desde la captura de datos hasta la generación de insights.

## Qué ofrece la plataforma

- Gestión completa de candidatos con autenticación y control por roles
- Ingesta masiva de datos desde CSV y lotes de CVs en PDF
- Extracción estructurada de información mediante IA
- Búsqueda semántica sobre perfiles indexados en Qdrant
- Generación de insights automáticos para apoyar decisiones de reclutamiento
- Dos experiencias de usuario desacopladas: una app principal y un microfrontend especializado en inteligencia

## Arquitectura general

El sistema está organizado en capas:

- Frontends: dos aplicaciones independientes construidas con React + Vite
  - Host: experiencia principal para usuarios y operaciones de negocio
  - Intelligence: experiencia especializada para búsqueda, ETL e insights
- Backend: microservicios desacoplados para identidad, candidatos e inteligencia
- Gateway: punto único de entrada para enrutar peticiones y validar autenticación
- Datos: PostgreSQL por dominio y Qdrant para búsquedas vectoriales

## Estructura del repositorio

- [docs/arquitecture.md](docs/arquitecture.md): visión general de la arquitectura
- [docs/runbook.md](docs/runbook.md): guía rápida de inicio
- [services/README.md](services/README.md): detalle técnico de los microservicios
- [docker-compose.yml](docker-compose.yml): infraestructura local con los servicios principales
- [web/](web/README.md): detalle técnico de microfrontends

## Inicio rápido

### Requisitos previos

- Docker Desktop y Docker Compose
- Node.js 20+
- pnpm
- uv
- Git

### 1. Levantar infraestructura backend

Desde la raíz del proyecto:

```bash
docker compose up --build -d
```

### 2. Instalar y ejecutar los frontends

```bash
cd web
pnpm install
```

En terminales separadas:

```bash
cd web
pnpm --filter host dev
```

```bash
cd web
pnpm --filter intelligence preview
```

### 3. Accesos esperados

- Host app: http://localhost:3000
- Intelligence app: http://localhost:5001
- Gateway: http://localhost:8080
- Servicios backend:
  - Candidate: http://localhost:8000/health
  - Identity: http://localhost:8001/health
  - Intelligence: http://localhost:8002/health

## Documentación recomendada

1. Revisar [docs/arquitecture.md](docs/arquitecture.md) para entender la arquitectura
2. Seguir [docs/runbook.md](docs/runbook.md) para levantar el entorno local
3. Consultar [services/README.md](services/README.md) para detalles de los servicios

## Contribución

Las contribuciones se realizan desde la rama develop. Se recomienda trabajar con cambios pequeños y mantener la documentación alineada con la implementación.
