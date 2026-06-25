# Runbook rápido de inicio

Esta guía resume la forma más directa de levantar el proyecto en desarrollo: primero los microfrontends y después los microservicios backend con Docker.

## Requisitos previos

- Docker Desktop y Docker Compose
- Node.js 20+ y pnpm
- Git

## 1. Preparar variables de entorno

Desde la raíz del proyecto:

```bash
cp .env.example .env
```

Edita el archivo `.env` y deja al menos estas variables con valores válidos:

- `JWT_SECRET_KEY`
- `COHERE_API_KEY` (si vas a probar la parte de inteligencia)
- `GROQ_API_KEY` (si vas a probar la parte de inteligencia)

También los .env para los microfrontends, crea .env en cada frontend y solamente coloca el url del gateway: ```

```
VITE_API_URL=http://localhost:8080
```

## 2. Levantar los microfrontends

Instala dependencias del monorepo web:

```bash
cd web
pnpm install
```

Inicia el host y el microfrontend de inteligencia en terminales separadas:

```bash
# Terminal 1
cd web
pnpm --filter host dev
```

```bash
# Terminal 2
cd web
pnpm --filter intelligence build
pnpm --filter intelligence preview
```

Puntos de acceso esperados:

- Host: http://localhost:3000
- Intelligence: http://localhost:5001

## 3. Levantar los microservicios con Docker

Desde la raíz del proyecto:

```bash
docker compose up --build -d
```

Esto levanta:

- PostgreSQL en el puerto 5432
- Qdrant en el puerto 6333
- Identity en el puerto 8001
- Candidate en el puerto 8000
- Intelligence en el puerto 8002
- Gateway en el puerto 8080

Puedes verificar el estado de los contenedores con:

```bash
docker compose ps
```

Y revisar logs si algo falla:

```bash
docker compose logs -f <servicio>
```

## 4. Comprobar que todo quedó arriba

- Frontend host: http://localhost:3000
- Frontend intelligence: http://localhost:5001
- Gateway: http://localhost:8080
- Health checks de los servicios:
  - http://localhost:8000/health
  - http://localhost:8001/health
  - http://localhost:8002/health

## 5. Deteener todo

```bash
docker compose down
```

Si necesitas reconstruir imágenes desde cero:

```bash
docker compose down -v
docker compose up --build -d
```

## Nota rápida

El orden recomendado es este porque los microfrontends se pueden probar de forma independiente y luego el backend queda preparado para recibir peticiones a través del gateway.
