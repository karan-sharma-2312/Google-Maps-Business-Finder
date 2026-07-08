# Business Intelligence AI Agent

Production-grade AI-powered business discovery and intelligence platform built in progressive phases.

## 1. Vision

This project discovers businesses from public sources, enriches them with website, SEO, and AI analysis, and exposes the results through APIs, dashboard, exports, and automation.

Primary delivery path:

1. Localhost-first development
2. Containerized deployment
3. CI/CD and cloud readiness
4. Apify Actor migration
5. SaaS and monetization readiness

## 2. Architecture Principles

We will follow:

- Clean Architecture
- Domain-Driven Design (DDD)
- SOLID principles
- Repository pattern
- Service layer pattern
- Dependency Injection
- Async-first I/O (scraping, networking, APIs)

### 2.1 Layered Structure (Conceptual)

- app: application entry points and wiring
- api: FastAPI routes, request/response contracts
- cli: Typer commands for local operations
- core: shared primitives (errors, base classes, constants)
- config: environment-aware settings and dependency configuration
- database: SQLAlchemy setup, sessions, migration integration
- models: persistence entities and ORM mappings
- schemas: Pydantic request/response and domain DTOs
- repositories: persistence abstraction and data access logic
- services: business logic orchestration
- scrapers/extractors/parsers: data acquisition pipeline
- ai: LLM providers, prompts, AI strategies
- tasks/scheduler/notifications: asynchronous and scheduled workflows
- middleware/authentication/authorization: API cross-cutting concerns
- analytics/exports/cache/storage: data products and infrastructure adapters
- tests: unit, integration, API, and scraper tests
- docs/scripts: documentation and automation scripts

## 3. Delivery Strategy

We will implement in strict phases. Each phase must pass local checks before moving forward.

### Phase 1-3 (Current)

Project bootstrap:

- Repository initialization
- Folder structure
- Environment configuration
- Logging setup
- CLI bootstrap
- Dependency management
- Documentation baseline

### Upcoming phases

- Phase 4-6: Data enrichment and scoring (SEO, AI, lead generation)
- Phase 7-12: Product features (dashboard, APIs, DB, scheduler, notifications, exports)
- Phase 13-17: Quality and operations (tests, Docker, CI/CD, security, monitoring)
- Phase 18-23: Extensibility and commercialization (plugins, agents, Apify, cloud, monetization)

## 4. Local-First Definition of Done

Before cloud or Apify migration, localhost must support:

- Deterministic setup from source
- Configurable environment profiles
- Stable scraping and parsing pipeline
- Reproducible database migrations
- Tested API surface
- Operational logging and error handling

## 5. Engineering Guardrails

All source files will enforce:

- Type hints and docstrings
- Clear separation of concerns
- Retry and timeout policies for network calls
- Structured logging
- No hardcoded secrets
- Testability by design

## 6. Mentor Mode Contract

For every file we create:

1. Explain why it exists
2. Explain how it works
3. Explain how it integrates with other files
4. Generate production-ready content
5. Keep progressing phase-by-phase with clear explanations

## 7. Phase 1 Status

Implemented in this repository:

- Git repository initialized
- Python virtual environment created (`.venv`)
- Enterprise directory scaffold created
- Environment template created (`.env.example`)
- Typed settings module and dependency accessor
- Centralized structured logging setup
- Typer CLI bootstrap
- FastAPI entrypoint and modular system routes
- Tooling baseline (`pyproject.toml`, `.pre-commit-config.yaml`)
- Bootstrap automation script (`scripts/bootstrap.ps1`)

## 8. Phase 2 Status (Google Maps Scraper)

Implemented in this repository:

- Canonical business schema with required fields (`app/schemas/business.py`)
- Async Playwright scraper (`app/scrapers/google_maps/scraper.py`)
- Parsing helpers for ratings/reviews/coordinates (`app/scrapers/google_maps/parser.py`)
- Service orchestration and JSON export (`app/services/google_maps_discovery_service.py`)
- CLI command for discovery (`google-maps-discover`)
- Unit tests for parser logic (`tests/unit/test_google_maps_parser.py`)

## 9. Phase 3 Status (Website Analyzer)

Implemented in this repository:

- Website analysis schema (`app/schemas/website_analysis.py`)
- Requests + BeautifulSoup extractor (`app/extractors/website_extractor.py`)
- Website analysis service (`app/services/website_analyzer_service.py`)
- CLI command for website analysis (`website-analyze`)
- Unit tests for extractor helper logic (`tests/unit/test_website_extractor.py`)

## 10. Local Setup (Beginner Friendly)

### Option A: One-command bootstrap (recommended on Windows)

```powershell
./scripts/bootstrap.ps1
```

### Option B: Manual setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pre-commit install
```

Create your env file:

```powershell
Copy-Item .env.example .env
```

## 11. Run the Project Locally

Start API server:

```powershell
.\.venv\Scripts\python.exe run.py
```

Run CLI examples:

```powershell
.\.venv\Scripts\python.exe -m app.cli.main version
.\.venv\Scripts\python.exe -m app.cli.main show-config
.\.venv\Scripts\python.exe -m app.cli.main init-dirs
.\.venv\Scripts\python.exe -m app.cli.main google-maps-discover --query "coffee shop" --location "new york" --max-results 10
.\.venv\Scripts\python.exe -m app.cli.main website-analyze --url "https://example.com"
```

System endpoints:

- `GET /system/health`
- `GET /system/ready`

## 12. Phase 4-9 Status

Implemented in this repository:

- SEO analyzer schema, extractor, and service
- REST API routes for discovery, website analysis, SEO analysis, and statistics
- Async database engine, ORM models, table initialization, and repositories
- Search and export history persistence with summary statistics endpoint
- API key authentication dependency
- In-memory per-IP rate limiting middleware

## 13. Phase 10-12 Status

Implemented in this repository:

- Celery application configuration scaffold
- Scheduler job stubs for daily/weekly runs
- Notification dispatcher strategy interface
- JSON export flows in service and API layers

## 14. Phase 13-17 Status

Implemented in this repository:

- Unit tests for parser and extractor layers
- API tests for system and statistics endpoints
- Dockerfile and docker-compose stack
- GitHub Actions CI workflow for lint/type/test
- Security baseline via API key + rate limiting

## 15. Phase 18-23 Status

Implemented in this repository:

- Plugin interface and plugin manager scaffold
- LangGraph-ready business research agent scaffold
- Frontend dashboard starter under frontend/index.html
- Apify migration simulation adapter script
- Deployment and monetization documentation

## 16. Run Commands

Backend API:

```powershell
.\.venv\Scripts\python.exe run.py
```

CLI commands:

```powershell
.\.venv\Scripts\python.exe -m app.cli.main google-maps-discover --query "coffee shop" --location "new york" --max-results 10
.\.venv\Scripts\python.exe -m app.cli.main website-analyze --url "https://example.com"
.\.venv\Scripts\python.exe -m app.cli.main seo-analyze --url "https://example.com"
```

Tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

Docker:

```powershell
docker compose up --build
```

## 17. Notes

- Set API_KEY in .env to protect non-system endpoints.
- Frontend dashboard file is at frontend/index.html and calls localhost API.
- Full production hardening still requires cloud secrets, TLS, and external monitoring integration.
