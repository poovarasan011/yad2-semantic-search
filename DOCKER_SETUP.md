# Docker Setup Guide

This guide explains how to set up and run the semantic search engine using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- `.env` file configured (see `.env.example`)

## Quick Start

1. **Create `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` file** with your configuration:
   ```env
   POSTGRES_USER=user
   POSTGRES_PASSWORD=password
   POSTGRES_DB=yad2_search
   POSTGRES_PORT=5432
   QDRANT_PORT=6333
   BACKEND_PORT=8000
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Check service status**:
   ```bash
   docker-compose ps
   ```

5. **View logs**:
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f backend
   ```

## Services

### 1. PostgreSQL Database (`db`)
- **Container**: `yad2_postgres`
- **Port**: Configured via `POSTGRES_PORT` (default: 5432)
- **Data**: Persisted in `postgres_data` volume
- **Initialization**: Runs `infra/postgres/init.sql` on first start

### 2. Qdrant Vector Database (`vector_db`)
- **Container**: `yad2_qdrant`
- **Port**: Configured via `QDRANT_PORT` (default: 6333)
- **Data**: Persisted in `qdrant_data` volume
- **Web UI**: Available at `http://localhost:6333/dashboard`

### 3. FastAPI Backend (`backend`)
- **Container**: `yad2_backend`
- **Port**: Configured via `BACKEND_PORT` (default: 8000)
- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Auto-restart**: Yes

### 4. ETL Pipeline (`etl`)
- **Container**: `yad2_etl`
- **Auto-restart**: No (run on-demand)
- **Usage**: Trigger via API or run manually

## Common Commands

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d db vector_db backend
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### Run ETL Pipeline
```bash
# Option 1: Via API (recommended)
curl -X POST http://localhost:8000/api/v1/ingest

# Option 2: Run ETL container manually
docker-compose run --rm etl python main.py
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f db
docker-compose logs -f vector_db
```

### Rebuild Services
```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build backend
```

### Access Containers
```bash
# PostgreSQL
docker exec -it yad2_postgres psql -U user -d yad2_search

# Backend container
docker exec -it yad2_backend bash

# ETL container
docker exec -it yad2_etl bash
```

## Environment Variables

All environment variables are loaded from `.env` file. Key variables:

- **Database**: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`
- **Qdrant**: `QDRANT_PORT`, `QDRANT_COLLECTION_NAME`, `QDRANT_VECTOR_SIZE`
- **Backend**: `BACKEND_PORT`, `LOG_LEVEL`, `DEBUG`
- **Embeddings**: `EMBEDDING_MODEL_NAME`, `EMBEDDING_DEVICE`, `EMBEDDING_BATCH_SIZE`

## Network Configuration

All services are connected via the `yad2_network` bridge network. Services communicate using service names:

- Backend → PostgreSQL: `db:5432`
- Backend → Qdrant: `vector_db:6333`
- ETL → PostgreSQL: `db:5432`
- ETL → Qdrant: `vector_db:6333`

## Volumes

- **`postgres_data`**: PostgreSQL database files
- **`qdrant_data`**: Qdrant vector database files
- **Project root** (read-only): Mounted at `/workspace` for `.env` file access

## Troubleshooting

### Services won't start
1. Check if ports are already in use:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

2. Check logs:
   ```bash
   docker-compose logs
   ```

### Database connection errors
1. Ensure PostgreSQL is running:
   ```bash
   docker-compose ps db
   ```

2. Check database credentials in `.env` match container settings

3. Wait for database to be ready (can take 10-20 seconds on first start)

### Backend can't find .env file
- Ensure `.env` file exists in project root
- Check that project root is mounted at `/workspace` in container

### Import errors in ETL
- Ensure project root is mounted at `/workspace`
- Check `PYTHONPATH` includes `/workspace`

## Development vs Production

### Development
- Use `docker-compose up` for local development
- Mount volumes for live code reloading (not configured by default)
- Enable debug logging: `DEBUG=true` in `.env`

### Production
- Use specific image tags instead of `latest`
- Set up proper secrets management (not `.env` file)
- Configure resource limits
- Use reverse proxy (nginx/traefik)
- Enable HTTPS

## Next Steps

1. **Ingest data**: Run ETL pipeline to populate databases
2. **Test API**: Visit `http://localhost:8000/docs` for interactive API docs
3. **Search**: Try semantic search endpoint: `GET /api/v1/search?query=דירה 2 חדרים`

