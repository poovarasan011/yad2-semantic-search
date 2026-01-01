# Yad2 Semantic Search Engine

A semantic search engine powered by **ML embeddings and vector search** for real estate listings. Built with state-of-the-art multilingual language models, this system transforms natural language queries in Hebrew into high-dimensional vector embeddings to find semantically relevant listings. Instead of rigid filters, users can search with natural language phrases like "דירה 2 חדרים קרוב לאוניברסיטה" (2-room apartment near the university) and receive intelligently ranked, contextually relevant results.

## 🎯 Motivation

Traditional search interfaces force users to navigate complex filter menus and dropdowns, making it difficult to express nuanced search intent. This project solves that problem by enabling **natural language search** - users simply describe what they're looking for in plain Hebrew, and the system understands the semantic meaning behind their query.

**Key Value Propositions:**
- **No More Rigid Filters**: Express search intent naturally instead of selecting predefined options
- **Semantic Understanding**: Finds listings based on meaning and context, not just keyword matching
- **Better User Experience**: Faster and more intuitive than traditional filter-based search
- **Multilingual Support**: Optimized for Hebrew text while supporting multilingual queries

The system currently focuses on real estate listings (apartments) but is designed to be extensible to other listing types and domains.

## ✨ Key Features

- **Semantic Search**: Natural language queries in Hebrew with multilingual embeddings
- **Hybrid Search**: Combines semantic (vector) search with structured filters (price, rooms, location, features)
- **Multivector Embeddings**: Uses separate embeddings for structured data and free-text descriptions for improved relevance
- **ETL Pipeline**: Automated data ingestion pipeline with Prefect orchestration
- **RESTful API**: FastAPI backend with auto-generated OpenAPI documentation
- **Streamlit UI**: Interactive web interface for searching and browsing results
- **Dockerized**: Full containerization with Docker Compose for easy deployment
- **Production-Ready**: Error handling, logging, health checks, and comprehensive test coverage

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- (Optional) Virtual environment

### 1. Clone and Setup

```bash
git clone <repository-url>
cd semantic_search_engine

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=yad2_search
POSTGRES_PORT=5432

# Qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=apartments

# Embedding Model
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-base
EMBEDDING_DEVICE=cpu

# API
API_V1_PREFIX=/api/v1
BACKEND_PORT=8000
```

### 3. Start Services

**Option A: Docker Compose (Recommended for Development)**

```bash
# Start databases only (for local development)
docker-compose -f docker-compose.dev.yml up -d

# Or start everything (databases + backend + ETL)
docker-compose up -d
```

**Option B: Development Mode (Databases in Docker, Backend Locally)**

```bash
# Start databases
docker-compose -f docker-compose.dev.yml up -d

# Run backend locally
cd backend
uvicorn app.main:app --reload
```

### 4. Ingest Data

```bash
# Option 1: Via API endpoint
curl -X POST http://localhost:8000/api/v1/ingest

# Option 2: Run ETL pipeline directly
cd etl
python main.py
```

### 5. Use the Search API

```bash
# Search endpoint
curl "http://localhost:8000/api/v1/search?query=דירה%202%20חדרים%20בתל%20אביב&limit=10"

# With filters
curl "http://localhost:8000/api/v1/search?query=דירה&price_max=8000&rooms_min=2.0&city=תל%20אביב"

# API documentation
open http://localhost:8000/docs
```

### 6. (Optional) Launch Streamlit UI

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Visit `http://localhost:8501` to use the interactive search interface.

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.11+ | Core development language |
| **Backend Framework** | FastAPI | High-performance async API |
| **Vector Database** | Qdrant | Semantic search and vector storage |
| **Relational Database** | PostgreSQL | Structured data storage (ground truth) |
| **Embeddings** | HuggingFace sentence-transformers | Multilingual text embeddings (multilingual-e5-base) |
| **ETL Orchestration** | Prefect | Pipeline management and scheduling |
| **Scraping** | Mock Scraper (Yad2 scraper in progress) | Data extraction |
| **Frontend** | Streamlit | Interactive search UI |
| **Containerization** | Docker & Docker Compose | Deployment and development environments |
| **Testing** | pytest | Unit and integration testing |
| **ORM** | SQLAlchemy | Database abstraction |
| **Configuration** | Pydantic Settings | Environment-based configuration |

## 📁 Project Structure

```
semantic_search_engine/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── services/ # Business logic (embedding, search)
│   │   ├── db/       # Database models and connections
│   │   └── core/     # Configuration and logging
│   └── Dockerfile
├── etl/              # ETL pipeline
│   ├── scrapers/     # Data extraction
│   ├── processors/   # Data cleaning and vectorization
│   ├── loaders/      # Database loading
│   └── Dockerfile
├── frontend/         # Streamlit UI
├── infra/            # Infrastructure configs (PostgreSQL, Qdrant)
├── tests/            # Test suite (unit + integration)
├── experiments/      # R&D and experimentation code
└── docker-compose.yml
```

## 📚 Additional Documentation

- [Docker Setup Guide](DOCKER_SETUP.md) - Detailed Docker configuration and usage
- [Testing Documentation](tests/README.md) - How to run tests
- [Frontend README](frontend/README.md) - Streamlit UI setup and usage

## 🔧 Development

```bash
# Run tests
pytest tests/unit/ -v

# Run integration tests (requires Docker)
pytest tests/integration/ -v

# Check code quality
pytest --cov=backend --cov=etl tests/
```