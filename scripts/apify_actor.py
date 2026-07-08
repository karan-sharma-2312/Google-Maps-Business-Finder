"""Apify Actor one-shot runtime entrypoint.

This module executes exactly one input payload, pushes structured results to
Apify Dataset/Key-Value Store, and exits. It also supports local simulation.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import json
import os
from pathlib import Path
from time import perf_counter

from apify import Actor

from app.config import get_settings
from app.services import GoogleMapsDiscoveryService, SeoAnalyzerService, WebsiteAnalyzerService


async def execute_payload(payload: dict) -> dict:
    """Execute one normalized payload and return output envelope."""
    settings = get_settings()
    started = perf_counter()
    now = datetime.now(tz=UTC).isoformat()

    mode = payload.get("mode", "google_maps")
    if mode == "google_maps":
        if not payload.get("query"):
            raise ValueError("'query' is required for mode='google_maps'")

        service = GoogleMapsDiscoveryService(settings)
        requested = int(payload.get("max_results", settings.scraper.google_maps_default_max_results))
        result = await service.discover(
            query=payload["query"],
            location=payload.get("location"),
            max_results=requested,
        )

        duration = round(perf_counter() - started, 3)
        return {
            "mode": "google_maps",
            "status": "ok",
            "timestamp": now,
            "summary": {
                "requested_count": requested,
                "discovered_count": result.discovered_count,
                "duration_seconds": duration,
            },
            "data": result.model_dump(mode="json"),
        }

    if mode == "website":
        if not payload.get("url"):
            raise ValueError("'url' is required for mode='website'")

        service = WebsiteAnalyzerService(settings)
        result = service.analyze(payload["url"])

        duration = round(perf_counter() - started, 3)
        return {
            "mode": "website",
            "status": "ok",
            "timestamp": now,
            "summary": {
                "requested_count": 1,
                "discovered_count": 1,
                "duration_seconds": duration,
            },
            "data": result.model_dump(mode="json"),
        }

    if mode == "seo":
        if not payload.get("url"):
            raise ValueError("'url' is required for mode='seo'")

        service = SeoAnalyzerService(settings)
        result = service.analyze(payload["url"])

        duration = round(perf_counter() - started, 3)
        return {
            "mode": "seo",
            "status": "ok",
            "timestamp": now,
            "summary": {
                "requested_count": 1,
                "discovered_count": 1,
                "duration_seconds": duration,
            },
            "data": result.model_dump(mode="json"),
        }

    raise ValueError(f"Unsupported mode: {mode}")


def run_local_simulation(input_path: str = "data/apify_input.json") -> dict:
    """Run local simulation with JSON input file."""
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    return asyncio.run(execute_payload(payload))


async def run_apify_actor() -> None:
    """Execute Apify actor run, push dataset item, and save output record."""
    async with Actor:
        actor_input = await Actor.get_input() or {}
        output = await execute_payload(actor_input)
        await Actor.push_data(output)
        await Actor.set_value("OUTPUT", output)


if __name__ == "__main__":
    if os.getenv("APIFY_IS_AT_HOME") == "1":
        asyncio.run(run_apify_actor())
    else:
        output = run_local_simulation()
    Path("exports/apify_simulation_output.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print("Apify simulation output saved to exports/apify_simulation_output.json")
