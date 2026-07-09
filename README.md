# Google Maps Business Finder

Google Maps Business Finder is a Python service that helps you discover local businesses and quickly analyze their websites.

It supports three practical workflows:

- Google Maps discovery: find businesses by query + location.
- Website analysis: extract contact, social, and technology signals from a URL.
- SEO analysis: compute on-page SEO score with actionable issues.

You can run it as:

- A local API (FastAPI)
- A local CLI (Typer)
- An Apify Actor

## What This Is Used For

Use this project when you need a repeatable lead research workflow for:

- Local business prospecting
- Agency outreach list building
- Website quality checks before outreach
- SEO quick-audits at scale
- Automation pipelines that need structured JSON output

## Core Capabilities

- Async Google Maps scraping pipeline (query/location/max results)
- Website extraction (emails, phones, social links, analytics IDs, schema types)
- SEO extraction (score, issues, title/meta/headings, sitemap, canonical, broken links)
- API routes with optional API key auth and per-IP rate limiting
- CLI commands for day-to-day local usage
- Data persistence and history tracking
- JSON exports for each workflow
- Apify actor input/output/dataset schemas

## Project Entry Points

- API app: [run.py](run.py)
- CLI app: [app/cli/main.py](app/cli/main.py)
- Actor runtime: [scripts/apify_actor.py](scripts/apify_actor.py)
- API router composition: [app/api/router.py](app/api/router.py)
- Runtime settings: [app/config/settings.py](app/config/settings.py)

## Quick Start (Windows PowerShell)

### 1. Create environment and install dependencies

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Create a minimal `.env`

This repository currently has no `.env.example`, so create `.env` manually:

```env
APP_ENV=development
APP_DEBUG=true
APP_HOST=127.0.0.1
APP_PORT=8000

# Optional: if set, non-system API endpoints require x-api-key header
API_KEY=

DATABASE_URL=sqlite+aiosqlite:///./data/business_intelligence.db
```

### 3. Start the API

```powershell
.\.venv\Scripts\python.exe run.py
```

Docs are available at:

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Usage

System endpoints (no API key required):

- GET `/system/health`
- GET `/system/ready`

Protected endpoints (require `x-api-key` only when `API_KEY` is configured):

- POST `/discovery/google-maps`
- POST `/analysis/website`
- POST `/analysis/seo`
- GET `/statistics/summary`

### Example: Google Maps discovery

```bash
curl -X POST "http://127.0.0.1:8000/discovery/google-maps" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_KEY_IF_CONFIGURED" \
  -d '{
    "query": "coffee shop",
    "location": "New York",
    "max_results": 20,
    "save_json": true
  }'
```

### Example: Website analysis

```bash
curl -X POST "http://127.0.0.1:8000/analysis/website" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_KEY_IF_CONFIGURED" \
  -d '{
    "url": "https://example.com",
    "save_json": true
  }'
```

### Example: SEO analysis

```bash
curl -X POST "http://127.0.0.1:8000/analysis/seo" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_KEY_IF_CONFIGURED" \
  -d '{
    "url": "https://example.com",
    "save_json": true
  }'
```

## CLI Usage

Run with:

```powershell
.\.venv\Scripts\python.exe -m app.cli.main <command>
```

Available commands:

- `version`
- `show-config`
- `init-dirs`
- `google-maps-discover --query ... --location ... --max-results ...`
- `website-analyze --url ...`
- `seo-analyze --url ...`

Examples:

```powershell
.\.venv\Scripts\python.exe -m app.cli.main google-maps-discover --query "coffee shop" --location "new york" --max-results 10
.\.venv\Scripts\python.exe -m app.cli.main website-analyze --url "https://example.com"
.\.venv\Scripts\python.exe -m app.cli.main seo-analyze --url "https://example.com"
```

## Apify Actor Usage

Actor metadata and schemas live in the `.actor` folder:

- Actor definition: [.actor/actor.json](.actor/actor.json)
- Input schema: [.actor/INPUT_SCHEMA.json](.actor/INPUT_SCHEMA.json)
- Output schema: [.actor/OUTPUT_SCHEMA.json](.actor/OUTPUT_SCHEMA.json)
- Dataset schema: [.actor/DATASET_SCHEMA.json](.actor/DATASET_SCHEMA.json)

Actor runtime entrypoint:

- [scripts/apify_actor.py](scripts/apify_actor.py)

Input modes:

- `google_maps` requires `query` (optional `location`, `max_results`)
- `website` requires `url`
- `seo` requires `url`

Example actor input (google maps mode):

```json
{
  "mode": "google_maps",
  "query": "coffee shops",
  "location": "New York",
  "max_results": 20,
  "save_json": true
}
```

Output envelope format (dataset item and OUTPUT record):

```json
{
  "mode": "google_maps",
  "status": "ok",
  "timestamp": "2026-07-09T06:00:03.000000+00:00",
  "summary": {
    "requested_count": 20,
    "discovered_count": 14,
    "duration_seconds": 4.231
  },
  "data": {}
}
```

## Docker

Start full local stack:

```powershell
docker compose up --build
```

Services from [docker-compose.yml](docker-compose.yml):

- app (FastAPI)
- redis
- rabbitmq
- postgres

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

## Frontend

A simple local dashboard starter is available at:

- [frontend/index.html](frontend/index.html)

## Notes

- Exports are written under the configured `EXPORT_DIR` (default: `exports`).
- If `API_KEY` is empty, protected API routes are effectively open in local development.
- For production, set strong secrets, enforce API key usage, and run behind TLS.
