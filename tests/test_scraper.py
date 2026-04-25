"""
tests/test_scraper.py – Unit tests for the scraper module.
"""

from unittest.mock import patch

from scraper import _extract_bike_name, get_latest_motorcycle_launches


class TestExtractBikeName:
    def test_extract_from_launch_headline(self):
        title = "Honda CB500F launched in Malaysia at RM29,888"
        assert "Honda CB500F" in _extract_bike_name(title)

    def test_extract_all_new_prefix(self):
        title = "All-new Yamaha MT-07 price and specs revealed"
        result = _extract_bike_name(title)
        assert "Yamaha" in result

    def test_fallback_returns_title(self):
        title = "some random article with no pattern"
        assert _extract_bike_name(title) == title

    def test_extract_kawasaki(self):
        title = "Kawasaki Ninja ZX-10R 2025 now available in Malaysia"
        result = _extract_bike_name(title)
        assert "Kawasaki" in result


class TestGetLatestMotorcycleLaunches:
    @patch("scraper._scrape_bikesrepublic", return_value=[])
    @patch("scraper._scrape_wapcar", return_value=[])
    @patch("scraper._scrape_paultan", return_value=[])
    def test_returns_empty_when_no_sources(self, mock_p, mock_w, mock_b):
        result = get_latest_motorcycle_launches()
        assert result == []

    @patch(
        "scraper._scrape_bikesrepublic",
        return_value=[
            {
                "title": "Honda Wave Alpha launched in Malaysia",
                "url": "https://www.bikesrepublic.com/test",
                "source": "BikesRepublic",
                "fetched_at": "2024-01-01T00:00:00",
            }
        ],
    )
    @patch("scraper._scrape_wapcar", return_value=[])
    @patch("scraper._scrape_paultan", return_value=[])
    def test_adds_bike_name_field(self, mock_p, mock_w, mock_b):
        result = get_latest_motorcycle_launches()
        assert len(result) == 1
        assert "bike_name" in result[0]

    @patch(
        "scraper._scrape_bikesrepublic",
        return_value=[
            {
                "title": "Duplicate Article",
                "url": "https://example.com/duplicate",
                "source": "BikesRepublic",
                "fetched_at": "2024-01-01T00:00:00",
            }
        ],
    )
    @patch(
        "scraper._scrape_wapcar",
        return_value=[
            {
                "title": "Duplicate Article",
                "url": "https://example.com/duplicate",
                "source": "Wapcar",
                "fetched_at": "2024-01-01T00:00:00",
            }
        ],
    )
    @patch("scraper._scrape_paultan", return_value=[])
    def test_deduplication_by_url(self, mock_p, mock_w, mock_b):
        result = get_latest_motorcycle_launches()
        assert len(result) == 1
