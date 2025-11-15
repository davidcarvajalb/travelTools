"""Tests for step2_scrape.py"""

import pytest

from unittest.mock import MagicMock, patch

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from travel_tools.step2_scrape import (
    extract_unique_hotels,
    scrape_hotel,
    scrape_with_retry,
)


def test_extracts_unique_hotel_names(sample_packages):
    """Test extraction of unique hotel names from packages."""
    hotels = extract_unique_hotels(sample_packages)
    assert len(hotels) == 2
    assert set(hotels) == {"Dreams Riviera Cancun", "Secrets Maroma"}


def test_handles_empty_packages():
    """Test extraction from empty package list."""
    hotels = extract_unique_hotels([])
    assert hotels == []


def test_sorts_hotel_names(sample_packages):
    """Test that hotel names are sorted."""
    hotels = extract_unique_hotels(sample_packages)
    assert hotels == sorted(hotels)


def _make_locator(text: str):
    locator = MagicMock()
    locator.first = locator
    locator.get_attribute.return_value = text
    locator.text_content.return_value = text
    return locator


def test_scrape_hotel_parses_rating_and_reviews():
    """Ensure scrape_hotel extracts numeric fields."""
    page = MagicMock()
    rating_loc = _make_locator("4.5 stars")
    reviews_loc = _make_locator("21,450 reviews")
    page.locator.side_effect = [rating_loc, reviews_loc]

    result = scrape_hotel("Dreams", page, debug=True)

    assert result.rating == 4.5
    assert result.review_count == 21450
    page.goto.assert_called_once()


def test_scrape_hotel_handles_timeout():
    """Timeout should return default data."""
    page = MagicMock()
    page.goto.side_effect = PlaywrightTimeoutError("timeout")

    result = scrape_hotel("Dreams", page)

    assert result.rating is None
    assert result.review_count is None


def test_scrape_with_retry_retries(monkeypatch):
    """Retry wrapper should call scrape_hotel until success."""
    calls = {"count": 0}

    def fake_scrape(hotel_name, page, debug=False):
        calls["count"] += 1
        if calls["count"] < 2:
            raise Exception("temporary issue")
        return MagicMock(rating=4.0, review_count=123)

    monkeypatch.setattr("travel_tools.step2_scrape.scrape_hotel", fake_scrape)
    page = MagicMock()

    result = scrape_with_retry("Dreams", page)

    assert result.rating == 4.0
    assert calls["count"] == 2
