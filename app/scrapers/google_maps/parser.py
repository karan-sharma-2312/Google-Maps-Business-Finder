"""Google Maps parsing helpers.

This module converts raw page content and text fragments into normalized values.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup


_COORDINATE_PATTERN = re.compile(r"@(-?\d+\.\d+),(-?\d+\.\d+)")
_FLOAT_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")
_INT_PATTERN = re.compile(r"\d[\d,\.]*")


def extract_coordinates_from_maps_url(url: str | None) -> tuple[float | None, float | None]:
    """Extract latitude and longitude from a Google Maps place URL."""
    if not url:
        return None, None

    match = _COORDINATE_PATTERN.search(url)
    if not match:
        return None, None

    try:
        return float(match.group(1)), float(match.group(2))
    except ValueError:
        return None, None


def parse_rating(raw_text: str | None) -> float | None:
    """Parse decimal rating value from text such as '4.6 stars'."""
    if not raw_text:
        return None

    match = _FLOAT_PATTERN.search(raw_text.replace(",", "."))
    if not match:
        return None

    try:
        return float(match.group(0))
    except ValueError:
        return None


def parse_reviews_count(raw_text: str | None) -> int | None:
    """Parse reviews count from text such as '(1,234)' or '1.234 reviews'."""
    if not raw_text:
        return None

    match = _INT_PATTERN.search(raw_text)
    if not match:
        return None

    normalized = re.sub(r"[^\d]", "", match.group(0))
    if not normalized:
        return None

    try:
        return int(normalized)
    except ValueError:
        return None


def extract_image_urls_from_html(html: str, limit: int = 12) -> list[str]:
    """Extract candidate business image URLs from page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    image_urls: list[str] = []

    for img in soup.select("img[src]"):
        src = img.get("src", "").strip()
        if not src:
            continue

        parsed = urlparse(src)
        if parsed.scheme not in {"http", "https"}:
            continue

        if "googleusercontent" in parsed.netloc or "gstatic" in parsed.netloc:
            image_urls.append(src)

        if len(image_urls) >= limit:
            break

    deduped: list[str] = []
    seen: set[str] = set()
    for url in image_urls:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped
