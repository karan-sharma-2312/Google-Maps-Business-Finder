"""Google Maps business scraper.

This module contains an async Playwright implementation that discovers businesses
for a query, iterates result cards, and extracts business details.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from playwright.async_api import BrowserContext, Locator, Page, TimeoutError, async_playwright

from app.config import ScraperSettings
from app.core import get_logger
from app.schemas.business import BusinessRecord, Coordinates
from app.scrapers.google_maps.parser import (
    extract_coordinates_from_maps_url,
    extract_image_urls_from_html,
    parse_rating,
    parse_reviews_count,
)


@dataclass(slots=True)
class GoogleMapsQuery:
    """Search criteria for Google Maps discovery."""

    query: str
    location: str | None = None
    max_results: int = 20

    def full_query(self) -> str:
        """Build the full search string sent to Google Maps."""
        if self.location:
            return f"{self.query} in {self.location}"
        return self.query


class GoogleMapsScraper:
    """Async Google Maps scraper with retry-safe extraction behavior."""

    def __init__(self, settings: ScraperSettings) -> None:
        self._settings = settings
        self._logger = get_logger({"component": "google-maps-scraper"})

    async def search_businesses(self, request: GoogleMapsQuery) -> list[BusinessRecord]:
        """Discover businesses from Google Maps based on query criteria."""
        self._logger.info(
            "Starting Google Maps search query='{}' location='{}' max_results={}",
            request.query,
            request.location,
            request.max_results,
        )

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self._settings.playwright_headless)
            context = await browser.new_context()

            try:
                results_page = await context.new_page()
                await self._prepare_page(results_page)
                await results_page.goto(self._settings.google_maps_base_url, wait_until="domcontentloaded")
                await self._perform_search(results_page, request.full_query())

                links = await self._collect_business_links(results_page, request.max_results)
                businesses = await self._extract_businesses(context, links)
                return businesses
            finally:
                await context.close()
                await browser.close()

    async def _prepare_page(self, page: Page) -> None:
        page.set_default_navigation_timeout(self._settings.playwright_navigation_timeout_ms)
        page.set_default_timeout(self._settings.playwright_navigation_timeout_ms)

    async def _perform_search(self, page: Page, search_text: str) -> None:
        await self._accept_consent_if_present(page)

        search_input = await self._resolve_search_input(page)
        if search_input is None:
            raise RuntimeError("Unable to locate Google Maps search input after retries")

        await search_input.fill("")
        await search_input.type(search_text, delay=25)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2500)

    async def _resolve_search_input(self, page: Page) -> Locator | None:
        selectors = (
            "input#searchboxinput",
            "input[aria-label='Search Google Maps']",
            "input[aria-label*='Search']",
            "input[name='q']",
        )

        for selector in selectors:
            locator = page.locator(selector)
            try:
                await locator.first.wait_for(state="visible", timeout=7000)
                return locator.first
            except TimeoutError:
                continue

        return None

    async def _accept_consent_if_present(self, page: Page) -> None:
        consent_selectors = (
            "button:has-text('Accept all')",
            "button:has-text('I agree')",
            "form button:has-text('Accept')",
            "button[aria-label='Accept all']",
        )

        for selector in consent_selectors:
            button = page.locator(selector)
            if await button.count() == 0:
                continue
            try:
                await button.first.click(timeout=2000)
                await page.wait_for_timeout(1200)
                self._logger.info("Accepted consent dialog using selector '{}'", selector)
                return
            except Exception:  # noqa: BLE001
                continue

    async def _collect_business_links(self, page: Page, max_results: int) -> list[str]:
        panel = page.locator("div[role='feed']")
        await panel.first.wait_for(state="visible", timeout=self._settings.playwright_navigation_timeout_ms)

        links: list[str] = []
        seen: set[str] = set()
        retries_without_growth = 0
        max_retries_without_growth = 6

        while len(links) < max_results and retries_without_growth < max_retries_without_growth:
            anchors = page.locator("a[href*='/maps/place']")
            count = await anchors.count()

            for index in range(count):
                href = await anchors.nth(index).get_attribute("href")
                if not href or "/maps/place" not in href:
                    continue
                if href in seen:
                    continue
                seen.add(href)
                links.append(href)
                if len(links) >= max_results:
                    break

            before_scroll_count = len(links)
            await panel.first.hover()
            await page.mouse.wheel(0, 3200)
            await page.wait_for_timeout(1300)

            if len(links) == before_scroll_count:
                retries_without_growth += 1
            else:
                retries_without_growth = 0

        self._logger.info("Collected {} business detail links", len(links))
        return links[:max_results]

    async def _extract_businesses(self, context: BrowserContext, links: list[str]) -> list[BusinessRecord]:
        semaphore = asyncio.Semaphore(self._settings.playwright_max_concurrency)

        async def worker(url: str) -> BusinessRecord | None:
            async with semaphore:
                return await self._extract_one_business(context, url)

        records = await asyncio.gather(*(worker(url) for url in links), return_exceptions=False)
        return [record for record in records if record is not None]

    async def _extract_one_business(self, context: BrowserContext, url: str) -> BusinessRecord | None:
        page = await context.new_page()
        await self._prepare_page(page)

        try:
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(1200)

            name = await self._safe_text(page, "h1.DUwDvf")
            if not name:
                self._logger.warning("Skipping detail page with missing business name: {}", url)
                return None

            category = await self._safe_text(page, "button.DkEaL")
            rating_text = await self._safe_text(page, "div.F7nice span")
            reviews_text = await self._safe_attr(page, "button[jsaction*='pane.rating.moreReviews']", "aria-label")
            address = await self._safe_text(page, "button[data-item-id='address'] .Io6YTe")
            phone = await self._safe_text(page, "button[data-item-id^='phone:tel:'] .Io6YTe")
            website = await self._safe_attr(page, "a[data-item-id='authority']", "href")
            status = await self._safe_text(page, "span.ZDu9vd")
            description = await self._safe_text(page, "div.PYvSYb")
            opening_hours = await self._extract_opening_hours(page)

            html = await page.content()
            image_urls = extract_image_urls_from_html(html)

            latitude, longitude = extract_coordinates_from_maps_url(url)

            return BusinessRecord(
                business_name=name,
                category=category,
                rating=parse_rating(rating_text),
                reviews_count=parse_reviews_count(reviews_text),
                address=address,
                phone=phone,
                website=website,
                google_maps_url=url,
                coordinates=Coordinates(latitude=latitude, longitude=longitude),
                opening_hours=opening_hours,
                business_status=status,
                business_description=description,
                business_images=image_urls,
            )
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Failed to extract business from '{}': {}", url, exc)
            return None
        finally:
            await page.close()

    async def _extract_opening_hours(self, page: Page) -> list[str]:
        rows = page.locator("table.eK4R0e tr")
        count = await rows.count()
        hours: list[str] = []

        for index in range(count):
            row = rows.nth(index)
            day = await row.locator("td:nth-child(1)").inner_text()
            schedule = await row.locator("td:nth-child(2)").inner_text()
            day_clean = day.strip()
            schedule_clean = schedule.strip()
            if day_clean and schedule_clean:
                hours.append(f"{day_clean}: {schedule_clean}")

        return hours

    async def _safe_text(self, page: Page, selector: str) -> str | None:
        locator = page.locator(selector)
        if await locator.count() == 0:
            return None

        text = await locator.first.inner_text()
        text_clean = text.strip()
        return text_clean or None

    async def _safe_attr(self, page: Page, selector: str, attr: str) -> str | None:
        locator = page.locator(selector)
        if await locator.count() == 0:
            return None

        value = await locator.first.get_attribute(attr)
        if not value:
            return None

        value_clean = value.strip()
        return value_clean or None
