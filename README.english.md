<p align="center">
  | <a href="https://github.com/OsOsorioP/EasyJobs/blob/main/README.md" target="_blank">español</a> |
</p>

# EasyJobs

![React](https://img.shields.io/badge/React-313131?style=flat&logo=react)
![Vite](https://img.shields.io/badge/Vite-313131?style=flat&logo=vite)
![pnpm](https://img.shields.io/badge/pnpm-313131?style=flat&logo=pnpm)
![FastAPI](https://img.shields.io/badge/FastAPI-313131?style=flat&logo=fastapi)
![uv](https://img.shields.io/badge/uv-313131?style=flat&logo=uv)
![LangChain](https://img.shields.io/badge/LangChain-313131?style=flat&logo=langchain)
![Qdrant](https://img.shields.io/badge/Qdrant-313131?style=flat&logo=qdrant)
![Postgres](https://img.shields.io/badge/Postgres-313131?style=flat&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-313131?style=flat&logo=docker)
![Status](https://img.shields.io/badge/Status-development-success)

**EasyJobs** is an AI-driven recruiting platform for managing candidates, processing profiles at scale, and searching for semantic information with the help of LLMs. The project combines microfrontends, microservices, and a gateway to provide a complete flow from data capture to insight generation.

## What the platform offers

- Full candidate management with authentication and role-based access control
- Mass data ingestion from CSV files and batches of PDF resumes
- Structured information extraction through AI
- Semantic search over profiles indexed in Qdrant
- Automatic insight generation to support recruiting decisions
- Two decoupled user experiences: a main app and a specialized intelligence microfrontend

## General architecture

The system is organized in layers:

- Frontends: two independent applications built with React + Vite
  - Host: main experience for users and business operations
  - Intelligence: specialized experience for search, ETL, and insights
- Backend: decoupled microservices for identity, candidates, and intelligence
- Gateway: single entry point for routing requests and validating authentication
- Data: PostgreSQL by domain and Qdrant for vector search

## Repository structure

- [docs/arquitecture.md](docs/arquitecture.md): overview of the architecture
- [docs/runbook.md](docs/runbook.md): quick start guide
- [services/README.md](services/README.md): technical details of the microservices
- [docker-compose.yml](docker-compose.yml): local infrastructure with the main services
- [web/](web/README.md): technical details of the microfrontends

## Quick start

### Prerequisites

- Docker Desktop and Docker Compose
- Node.js 20+
- pnpm
- uv
- Git

### 1. Start the backend infrastructure

From the project root:

```bash
docker compose up --build -d
```

### 2. Install and run the frontends

```bash
cd web
pnpm install
```

In separate terminals:

```bash
cd web
pnpm --filter host dev
```

```bash
cd web
pnpm --filter intelligence preview
```

### 3. Expected access points

- Host app: http://localhost:3000
- Intelligence app: http://localhost:5001
- Gateway: http://localhost:8080
- Backend services:
  - Candidate: http://localhost:8000/health
  - Identity: http://localhost:8001/health
  - Intelligence: http://localhost:8002/health

## Recommended documentation

1. Review [docs/arquitecture.md](docs/arquitecture.md) to understand the architecture
2. Follow [docs/runbook.md](docs/runbook.md) to set up the local environment
3. Check [services/README.md](services/README.md) for service details

## Contribution

Contributions are made from the develop branch. It is recommended to work with small changes and keep the documentation aligned with the implementation.