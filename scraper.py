"""
scraper.py – Fetches the latest motorcycle launch news from Malaysian websites.

Sources:
  - BikesRepublic (https://www.bikesrepublic.com)
  - Wapcar.my     (https://wapcar.my)
  - Paultan.org   (https://paultan.org)
"""

import logging
import re
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 15  # seconds


def _get_soup(url: str) -> Optional[BeautifulSoup]:
    """Download a page and return a BeautifulSoup object, or None on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None


def _scrape_bikesrepublic(limit: int = 5) -> list[dict]:
    """Scrape latest articles from BikesRepublic.com."""
    results = []
    soup = _get_soup("https://www.bikesrepublic.com/news/")
    if not soup:
        return results

    articles = soup.select("article.post, div.post-item, div.jeg_post")[:limit * 2]
    for article in articles:
        title_tag = article.find(["h2", "h3", "h4"])
        link_tag = article.find("a", href=True)
        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        url = link_tag["href"]
        if not url.startswith("http"):
            url = "https://www.bikesrepublic.com" + url

        # Filter for launch/new model keywords
        if any(kw in title.lower() for kw in ["launch", "new", "2024", "2025", "price", "malaysia"]):
            results.append(
                {
                    "title": title,
                    "url": url,
                    "source": "BikesRepublic",
                    "fetched_at": datetime.utcnow().isoformat(),
                }
            )
        if len(results) >= limit:
            break

    logger.info("BikesRepublic: found %d articles", len(results))
    return results


def _scrape_wapcar(limit: int = 5) -> list[dict]:
    """Scrape latest motorcycle articles from Wapcar.my."""
    results = []
    soup = _get_soup("https://www.wapcar.my/news?category=motorcycle")
    if not soup:
        return results

    articles = soup.select("div.news-item, article, div.article-card")[:limit * 2]
    for article in articles:
        title_tag = article.find(["h2", "h3", "h4", "a"])
        link_tag = article.find("a", href=True)
        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        url = link_tag["href"]
        if not url.startswith("http"):
            url = "https://www.wapcar.my" + url

        if any(kw in title.lower() for kw in ["launch", "new", "2024", "2025", "price", "malaysia", "motor"]):
            results.append(
                {
                    "title": title,
                    "url": url,
                    "source": "Wapcar",
                    "fetched_at": datetime.utcnow().isoformat(),
                }
            )
        if len(results) >= limit:
            break

    logger.info("Wapcar: found %d articles", len(results))
    return results


def _scrape_paultan(limit: int = 5) -> list[dict]:
    """Scrape latest motorcycle articles from Paultan.org."""
    results = []
    soup = _get_soup("https://paultan.org/?s=motorcycle+malaysia+launch")
    if not soup:
        return results

    articles = soup.select("article.post, div.post")[:limit * 2]
    for article in articles:
        title_tag = article.find(["h1", "h2", "h3"])
        link_tag = article.find("a", href=True)
        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        url = link_tag["href"]

        if any(kw in title.lower() for kw in ["motorcycle", "bike", "launch", "motor"]):
            results.append(
                {
                    "title": title,
                    "url": url,
                    "source": "Paultan.org",
                    "fetched_at": datetime.utcnow().isoformat(),
                }
            )
        if len(results) >= limit:
            break

    logger.info("Paultan.org: found %d articles", len(results))
    return results


def _extract_bike_name(title: str) -> str:
    """
    Try to extract a clean motorcycle name/model from an article title.
    Falls back to the raw title if no pattern matches.
    """
    # Common patterns: "Honda CB500F launched in Malaysia", "All-new Yamaha MT-07 …"
    patterns = [
        r"(?:all-new\s+)?([A-Z][a-z]+(?:\s+[A-Z0-9][A-Za-z0-9-]*){1,4})\s+(?:launched|unveiled|introduced|now|price|2024|2025)",
        r"(?:new|all-new)\s+([A-Z][a-z]+(?:\s+[A-Z0-9][A-Za-z0-9-]*){1,4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return title


def get_latest_motorcycle_launches(limit_per_source: int = 5) -> list[dict]:
    """
    Aggregate motorcycle launch news from all sources.

    Returns a list of dicts, each with keys:
        title, url, source, bike_name, fetched_at
    """
    all_articles: list[dict] = []
    all_articles.extend(_scrape_bikesrepublic(limit_per_source))
    all_articles.extend(_scrape_wapcar(limit_per_source))
    all_articles.extend(_scrape_paultan(limit_per_source))

    # Deduplicate by URL
    seen_urls: set[str] = set()
    unique_articles = []
    for article in all_articles:
        if article["url"] not in seen_urls:
            seen_urls.add(article["url"])
            article["bike_name"] = _extract_bike_name(article["title"])
            unique_articles.append(article)

    logger.info("Total unique articles fetched: %d", len(unique_articles))
    return unique_articles
