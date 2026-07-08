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

import requests

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


def _apify_api_base() -> str:
    return os.getenv("APIFY_API_BASE_URL", "https://api.apify.com").rstrip("/")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _fetch_apify_input() -> dict:
    token = _require_env("APIFY_TOKEN")
    store_id = _require_env("APIFY_DEFAULT_KEY_VALUE_STORE_ID")
    record_key = os.getenv("APIFY_INPUT_KEY", "INPUT")

    endpoint = f"{_apify_api_base()}/v2/key-value-stores/{store_id}/records/{record_key}"
    response = requests.get(
        endpoint,
        params={"token": token, "disableRedirect": "true"},
        timeout=30,
    )

    if response.status_code == 404:
        return {}

    response.raise_for_status()
    body = response.text.strip()
    if not body:
        return {}
    return response.json()


def _push_dataset_item(item: dict) -> None:
    token = _require_env("APIFY_TOKEN")
    dataset_id = _require_env("APIFY_DEFAULT_DATASET_ID")
    endpoint = f"{_apify_api_base()}/v2/datasets/{dataset_id}/items"

    response = requests.post(
        endpoint,
        params={"token": token},
        json=item,
        timeout=60,
    )
    response.raise_for_status()


def _set_kv_record(key: str, value: dict) -> None:
    token = _require_env("APIFY_TOKEN")
    store_id = _require_env("APIFY_DEFAULT_KEY_VALUE_STORE_ID")
    endpoint = f"{_apify_api_base()}/v2/key-value-stores/{store_id}/records/{key}"

    response = requests.put(
        endpoint,
        params={"token": token, "contentType": "application/json; charset=utf-8"},
        data=json.dumps(value, ensure_ascii=True),
        timeout=30,
    )
    response.raise_for_status()


def run_apify_actor() -> None:
    """Execute Apify actor run, push dataset item, and save output record."""
    actor_input = _fetch_apify_input()
    output = asyncio.run(execute_payload(actor_input))
    _push_dataset_item(output)
    _set_kv_record("OUTPUT", output)


if __name__ == "__main__":
    if os.getenv("APIFY_IS_AT_HOME") == "1":
        run_apify_actor()
    else:
        output = run_local_simulation()
        Path("exports/apify_simulation_output.json").write_text(
            json.dumps(output, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        print("Apify simulation output saved to exports/apify_simulation_output.json")
