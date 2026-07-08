"""Apify Actor adapter entrypoint.

This module is a migration bridge that reuses existing services and swaps only
I/O when executed in Apify runtime.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from app.config import get_settings
from app.services import GoogleMapsDiscoveryService, SeoAnalyzerService, WebsiteAnalyzerService


def run_local_simulation(input_path: str = "data/apify_input.json") -> dict:
    """Run a local simulation of planned Apify actor behavior."""
    settings = get_settings()
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))

    mode = payload.get("mode", "google_maps")
    if mode == "google_maps":
        service = GoogleMapsDiscoveryService(settings)
        result = asyncio.run(
            service.discover(
                query=payload["query"],
                location=payload.get("location"),
                max_results=int(payload.get("max_results", 20)),
            )
        )
        return result.model_dump(mode="json")

    if mode == "website":
        service = WebsiteAnalyzerService(settings)
        result = service.analyze(payload["url"])
        return result.model_dump(mode="json")

    if mode == "seo":
        service = SeoAnalyzerService(settings)
        result = service.analyze(payload["url"])
        return result.model_dump(mode="json")

    raise ValueError(f"Unsupported mode: {mode}")


if __name__ == "__main__":
    output = run_local_simulation()
    Path("exports/apify_simulation_output.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print("Apify simulation output saved to exports/apify_simulation_output.json")
