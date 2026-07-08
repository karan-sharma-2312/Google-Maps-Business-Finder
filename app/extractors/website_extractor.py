"""Website extraction logic for business enrichment.

This module uses Requests and BeautifulSoup to analyze public website signals.
"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.config import ScraperSettings
from app.schemas.website_analysis import SocialLinks, WebsiteAnalysisResult

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
_GA_RE = re.compile(r"G-[A-Z0-9]{6,}")
_PIXEL_RE = re.compile(r"(?:fbq\(['\"]init['\"],\s*['\"])(\d{8,20})")


class WebsiteExtractor:
    """Extract structured website insights from publicly accessible pages."""

    def __init__(self, scraper_settings: ScraperSettings) -> None:
        self._timeout = scraper_settings.http_timeout_seconds
        self._max_retries = scraper_settings.http_max_retries
        self._backoff_seconds = scraper_settings.http_retry_backoff_seconds

    def analyze(self, url: str) -> WebsiteAnalysisResult:
        """Download and parse website content from the provided URL."""
        response = self._request_with_retry(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        final_url = response.url
        base_url = f"{urlparse(final_url).scheme}://{urlparse(final_url).netloc}"

        links = self._extract_links(soup, base_url)

        result = WebsiteAnalysisResult(
            source_url=url,
            final_url=final_url,
            title=self._extract_title(soup),
            description=self._extract_description(soup),
            emails=sorted(set(_EMAIL_RE.findall(html))),
            phone_numbers=self._normalize_phones(_PHONE_RE.findall(soup.get_text(" ", strip=True))),
            whatsapp_links=self._filter_links(links, ("wa.me", "api.whatsapp.com", "whatsapp.com")),
            contact_page=self._first_page_match(links, ("contact",)),
            social_links=SocialLinks(
                facebook=self._filter_links(links, ("facebook.com",)),
                instagram=self._filter_links(links, ("instagram.com",)),
                linkedin=self._filter_links(links, ("linkedin.com",)),
                twitter_x=self._filter_links(links, ("twitter.com", "x.com")),
                youtube=self._filter_links(links, ("youtube.com", "youtu.be")),
                telegram=self._filter_links(links, ("t.me", "telegram.me")),
                pinterest=self._filter_links(links, ("pinterest.com",)),
            ),
            logo_url=self._extract_logo(soup, base_url),
            favicon_url=self._extract_favicon(soup, base_url),
            about_page=self._first_page_match(links, ("about", "our-story")),
            services_page=self._first_page_match(links, ("services", "service")),
            products_page=self._first_page_match(links, ("products", "product", "shop")),
            careers_page=self._first_page_match(links, ("careers", "jobs", "join-us")),
            blog_page=self._first_page_match(links, ("blog", "news", "articles")),
            technologies=self._detect_technologies(html),
            cms=self._detect_cms(html),
            hosting=None,
            analytics_ids=sorted(set(_GA_RE.findall(html))),
            meta_pixel_ids=self._extract_meta_pixel_ids(html),
            schema_types=self._extract_schema_types(soup),
        )
        return result

    def _request_with_retry(self, url: str) -> requests.Response:
        session = requests.Session()
        last_exc: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                response = session.get(
                    url,
                    timeout=self._timeout,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; BIA-Bot/0.1; +https://example.com/bot)"},
                )
                response.raise_for_status()
                return response
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if attempt >= self._max_retries:
                    break
                import time

                time.sleep(self._backoff_seconds * attempt)

        raise RuntimeError(f"Failed to fetch website after retries: {url}") from last_exc

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        links: list[str] = []
        for anchor in soup.select("a[href]"):
            href = anchor.get("href", "").strip()
            if not href:
                continue
            absolute = urljoin(base_url, href)
            parsed = urlparse(absolute)
            if parsed.scheme in {"http", "https"}:
                links.append(absolute)
        return sorted(set(links))

    def _extract_title(self, soup: BeautifulSoup) -> str | None:
        if not soup.title or not soup.title.text:
            return None
        title = soup.title.text.strip()
        return title or None

    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        meta = soup.select_one("meta[name='description']")
        if not meta:
            return None
        content = (meta.get("content") or "").strip()
        return content or None

    def _extract_logo(self, soup: BeautifulSoup, base_url: str) -> str | None:
        candidates = [
            "img[alt*='logo' i]",
            "img[class*='logo' i]",
            "img[id*='logo' i]",
        ]
        for selector in candidates:
            tag = soup.select_one(selector)
            if not tag:
                continue
            src = (tag.get("src") or "").strip()
            if src:
                return urljoin(base_url, src)
        return None

    def _extract_favicon(self, soup: BeautifulSoup, base_url: str) -> str | None:
        rel_candidates = ["icon", "shortcut icon", "apple-touch-icon"]
        for rel_value in rel_candidates:
            tag = soup.select_one(f"link[rel='{rel_value}']")
            if not tag:
                continue
            href = (tag.get("href") or "").strip()
            if href:
                return urljoin(base_url, href)
        return None

    def _filter_links(self, links: list[str], keywords: tuple[str, ...]) -> list[str]:
        matches = [link for link in links if any(keyword in link.lower() for keyword in keywords)]
        return matches[:25]

    def _first_page_match(self, links: list[str], keywords: tuple[str, ...]) -> str | None:
        for link in links:
            path = urlparse(link).path.lower()
            if any(keyword in path for keyword in keywords):
                return link
        return None

    def _normalize_phones(self, phones: list[str]) -> list[str]:
        normalized: list[str] = []
        for phone in phones:
            compact = re.sub(r"\s+", " ", phone).strip()
            if len(re.sub(r"\D", "", compact)) < 8:
                continue
            normalized.append(compact)
        return sorted(set(normalized))[:25]

    def _detect_technologies(self, html: str) -> list[str]:
        lower_html = html.lower()
        signatures = {
            "React": "react",
            "Next.js": "_next",
            "Vue": "vue",
            "Angular": "angular",
            "jQuery": "jquery",
            "Bootstrap": "bootstrap",
            "Tailwind": "tailwind",
            "Google Tag Manager": "googletagmanager",
            "Cloudflare": "cloudflare",
        }

        detected: list[str] = []
        for tech, marker in signatures.items():
            if marker in lower_html:
                detected.append(tech)
        return detected

    def _detect_cms(self, html: str) -> str | None:
        lower_html = html.lower()
        if "wp-content" in lower_html:
            return "WordPress"
        if "shopify" in lower_html:
            return "Shopify"
        if "wix" in lower_html:
            return "Wix"
        if "squarespace" in lower_html:
            return "Squarespace"
        return None

    def _extract_meta_pixel_ids(self, html: str) -> list[str]:
        return sorted(set(_PIXEL_RE.findall(html)))

    def _extract_schema_types(self, soup: BeautifulSoup) -> list[str]:
        schema_types: set[str] = set()
        for tag in soup.select("[itemtype]"):
            item_type = (tag.get("itemtype") or "").strip()
            if item_type:
                schema_types.add(item_type)
        return sorted(schema_types)
