# Testing Guide

This directory contains unit and integration tests for the semantic search engine.

## Test Structure

```
tests/
├── unit/           # Unit tests (fast, isolated, mocked dependencies)
│   ├── test_api_*.py          # FastAPI endpoint tests
│   ├── test_db_*.py           # Database tests
│   ├── test_embedding_*.py    # Embedding service tests
│   └── ...
├── integration/    # Integration tests (slower, real dependencies)
│   └── test_docker_setup.py   # Docker container tests
├── conftest.py     # Shared pytest fixtures
└── pytest.ini      # Pytest configuration
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run only unit tests
```bash
pytest tests/unit/
```

### Run only integration tests
```bash
pytest tests/integration/ -m integration
```

### Run specific test file
```bash
pytest tests/unit/test_api_search.py
```

### Run with coverage
```bash
pytest --cov=backend/app --cov-report=html
```

### Run with verbose output
```bash
pytest -v
```

## Test Markers

Tests are marked with categories:

- `@pytest.mark.unit` - Unit tests (default)
- `@pytest.mark.integration` - Integration tests (require Docker)
- `@pytest.mark.e2e` - End-to-end tests

Run tests by marker:
```bash
pytest -m unit
pytest -m integration
```

## Unit Tests

Unit tests are fast and test individual components in isolation using mocks.

### FastAPI Endpoint Tests

- **Location**: `tests/unit/test_api_*.py`
- **What they test**:
  - Endpoint request/response handling
  - Parameter validation
  - Error handling
  - Response schemas

- **Dependencies**: All external dependencies are mocked

### Example: Running API tests
```bash
pytest tests/unit/test_api_search.py -v
```

## Integration Tests

Integration tests verify that multiple components work together.

### Docker Setup Tests

- **Location**: `tests/integration/test_docker_setup.py`
- **What they test**:
  - Docker containers start correctly
  - Services are accessible
  - Volumes and networks are created
  - Environment variables are configured

- **Requirements**:
  - Docker must be running
  - `docker-compose` must be available
  - Services defined in `docker-compose.dev.yml`

### Running Docker Integration Tests

1. **Start Docker services** (tests will do this automatically, but you can manually start):
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Run integration tests**:
   ```bash
   pytest tests/integration/test_docker_setup.py -m integration -v
   ```

3. **Cleanup** (tests will do this automatically, but you can manually stop):
   ```bash
   docker-compose -f docker-compose.dev.yml down
   ```

## Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `test_settings` - Test configuration
- `test_db_session` - In-memory SQLite database session
- `qdrant_manager_mock` - Mocked Qdrant manager

## Writing New Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_my_endpoint(client):
    response = client.get("/api/v1/my-endpoint")
    assert response.status_code == 200
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
def test_service_connectivity():
    # Test real service connectivity
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

- Unit tests: Fast, no external dependencies
- Integration tests: Require Docker, can be run in CI with Docker support

## Troubleshooting

### Tests fail with import errors
- Ensure you're running tests from the project root
- Check that `backend/` is in Python path (handled by `conftest.py`)

### Integration tests fail
- Ensure Docker is running: `docker ps`
- Check that ports aren't already in use
- Verify `docker-compose.dev.yml` exists and is valid

### Tests are slow
- Unit tests should be fast (< 1 second total)
- Integration tests are slower (require Docker startup)
- Use `-m unit` to skip integration tests during development

