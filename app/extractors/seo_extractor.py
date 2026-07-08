"""SEO extraction logic using Requests + BeautifulSoup."""

from __future__ import annotations

from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.config import ScraperSettings
from app.schemas.seo_analysis import SeoAnalysisResult, SeoIssue


class SeoExtractor:
    """Extract and score basic on-page SEO signals."""

    def __init__(self, scraper_settings: ScraperSettings) -> None:
        self._timeout = scraper_settings.http_timeout_seconds

    def analyze(self, url: str) -> SeoAnalysisResult:
        """Run SEO checks for provided URL."""
        response = requests.get(url, timeout=self._timeout, headers={"User-Agent": "BIA-SEO-Checker/0.1"})
        response.raise_for_status()

        final_url = response.url
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        title = self._get_title(soup)
        description = self._get_meta_content(soup, "description")
        h1 = [tag.get_text(" ", strip=True) for tag in soup.select("h1") if tag.get_text(strip=True)]
        h2 = [tag.get_text(" ", strip=True) for tag in soup.select("h2") if tag.get_text(strip=True)]

        canonical_value = None
        canonical_tag = soup.select_one("link[rel='canonical']")
        if canonical_tag and canonical_tag.get("href"):
            canonical_value = urljoin(final_url, canonical_tag.get("href", "").strip())

        robots_meta = self._get_meta_content(soup, "robots")
        sitemap_url = self._detect_sitemap(final_url)

        structured_data_types = sorted(
            {
                item_type
                for item_type in ((tag.get("itemtype") or "").strip() for tag in soup.select("[itemtype]"))
                if item_type
            }
        )

        broken_links = self._find_broken_links(final_url, soup)
        missing_alt_images = sum(1 for image in soup.select("img") if not (image.get("alt") or "").strip())

        open_graph_tags = self._collect_meta_by_prefix(soup, "property", "og:")
        twitter_card_tags = self._collect_meta_by_prefix(soup, "name", "twitter:")

        result = SeoAnalysisResult(
            source_url=url,
            final_url=final_url,
            title=title,
            description=description,
            h1=h1,
            h2=h2,
            canonical=canonical_value,
            robots_meta=robots_meta,
            sitemap_url=sitemap_url,
            structured_data_types=structured_data_types,
            broken_links=broken_links,
            missing_alt_images=missing_alt_images,
            open_graph_tags=open_graph_tags,
            twitter_card_tags=twitter_card_tags,
        )

        result.issues = self._build_issues(result)
        result.score = max(0, 100 - len(result.issues) * 8)
        return result

    def _get_title(self, soup: BeautifulSoup) -> str | None:
        if not soup.title or not soup.title.text:
            return None
        value = soup.title.text.strip()
        return value or None

    def _get_meta_content(self, soup: BeautifulSoup, name: str) -> str | None:
        tag = soup.select_one(f"meta[name='{name}']")
        if not tag:
            return None
        content = (tag.get("content") or "").strip()
        return content or None

    def _detect_sitemap(self, final_url: str) -> str | None:
        parsed = urlparse(final_url)
        sitemap = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        try:
            response = requests.head(sitemap, timeout=self._timeout)
            if response.status_code < 400:
                return sitemap
        except Exception:  # noqa: BLE001
            return None
        return None

    def _find_broken_links(self, base_url: str, soup: BeautifulSoup) -> list[str]:
        links: list[str] = []
        checked = 0
        for anchor in soup.select("a[href]"):
            href = (anchor.get("href") or "").strip()
            if not href or href.startswith("mailto:") or href.startswith("tel:"):
                continue

            absolute = urljoin(base_url, href)
            if urlparse(absolute).scheme not in {"http", "https"}:
                continue

            try:
                resp = requests.head(absolute, timeout=self._timeout, allow_redirects=True)
                if resp.status_code >= 400:
                    links.append(absolute)
            except Exception:  # noqa: BLE001
                links.append(absolute)

            checked += 1
            if checked >= 30:
                break

        return sorted(set(links))[:20]

    def _collect_meta_by_prefix(self, soup: BeautifulSoup, attr_name: str, prefix: str) -> dict[str, str]:
        output: dict[str, str] = {}
        for tag in soup.select(f"meta[{attr_name}]"):
            key = (tag.get(attr_name) or "").strip()
            if not key.startswith(prefix):
                continue
            value = (tag.get("content") or "").strip()
            if value:
                output[key] = value
        return output

    def _build_issues(self, result: SeoAnalysisResult) -> list[SeoIssue]:
        issues: list[SeoIssue] = []

        if not result.title:
            issues.append(
                SeoIssue(
                    key="title",
                    severity="high",
                    message="Missing title tag",
                    suggestion="Add a unique title under 60 characters.",
                )
            )
        if not result.description:
            issues.append(
                SeoIssue(
                    key="description",
                    severity="medium",
                    message="Missing meta description",
                    suggestion="Add a compelling 140-160 character description.",
                )
            )
        if not result.h1:
            issues.append(
                SeoIssue(
                    key="h1",
                    severity="high",
                    message="No H1 tag found",
                    suggestion="Add one clear H1 heading describing primary topic.",
                )
            )
        if not result.canonical:
            issues.append(
                SeoIssue(
                    key="canonical",
                    severity="medium",
                    message="Canonical link tag missing",
                    suggestion="Add canonical URL to reduce duplicate content risk.",
                )
            )
        if result.missing_alt_images > 0:
            issues.append(
                SeoIssue(
                    key="alt",
                    severity="medium",
                    message=f"{result.missing_alt_images} images without alt text",
                    suggestion="Add descriptive alt attributes to all informative images.",
                )
            )
        if not result.open_graph_tags:
            issues.append(
                SeoIssue(
                    key="open_graph",
                    severity="low",
                    message="Open Graph tags missing",
                    suggestion="Add og:title, og:description and og:image for social previews.",
                )
            )
        if not result.twitter_card_tags:
            issues.append(
                SeoIssue(
                    key="twitter_cards",
                    severity="low",
                    message="Twitter card tags missing",
                    suggestion="Add twitter:card and related tags for X/Twitter sharing.",
                )
            )
        if result.broken_links:
            issues.append(
                SeoIssue(
                    key="broken_links",
                    severity="high",
                    message=f"Detected {len(result.broken_links)} broken links",
                    suggestion="Fix or remove links that return 4xx/5xx responses.",
                )
            )

        return issues
