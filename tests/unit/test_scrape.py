"""Tests for step2_scrape.py"""

import pytest

from unittest.mock import MagicMock, patch

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from travel_tools.step2_scrape import (
    extract_unique_hotels,
    scrape_hotel,
    scrape_with_retry,
    scrape_reviews,
    deduplicate_reviews,
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
    from travel_tools.types import GoogleRating

    calls = {"count": 0}

    def fake_scrape(hotel_name, page, max_reviews=0, debug=False, debug_dir=None):
        calls["count"] += 1
        if calls["count"] < 2:
            raise Exception("temporary issue")
        return GoogleRating(hotel_name=hotel_name, rating=4.0, review_count=123)

    monkeypatch.setattr("travel_tools.step2_scrape.scrape_hotel", fake_scrape)
    page = MagicMock()

    result = scrape_with_retry("Dreams", page, max_reviews=0)

    assert result.rating == 4.0
    assert calls["count"] == 2


# ============================================================================
# Review Scraping Tests
# ============================================================================


def test_scrape_reviews_clicks_reviews_tab():
    """Test that scrape_reviews clicks the Reviews tab."""
    page = MagicMock()
    # Mock successful click
    page.click.return_value = None
    # Mock locators
    page.locator.return_value.first = MagicMock()
    page.locator.return_value.all.return_value = []

    scrape_reviews("Test Hotel", page, max_reviews=10)

    # Should have attempted to click Reviews tab
    assert page.click.called


def test_scrape_reviews_extracts_review_data():
    """Test that scrape_reviews extracts text, rating, date, and name."""
    from travel_tools.types import Review

    page = MagicMock()

    # Mock successful click and scroll
    page.click.return_value = None
    page.wait_for_timeout.return_value = None

    # Mock review elements with proper structure
    review1 = MagicMock()
    text_elem1 = MagicMock()
    text_elem1.text_content.return_value = "Great hotel with amazing pool!"
    rating_elem1 = MagicMock()
    rating_elem1.get_attribute.return_value = "5 stars"
    rating_elem1.text_content.return_value = "5 stars"
    date_elem1 = MagicMock()
    date_elem1.text_content.return_value = "2 weeks ago"
    name_elem1 = MagicMock()
    name_elem1.text_content.return_value = "John Doe"

    def review1_locator(selector):
        mock = MagicMock()
        mock.first = MagicMock()
        if "wiI7pd" in selector:  # text
            mock.first.text_content.return_value = "Great hotel with amazing pool!"
            mock.first.is_visible.return_value = False
        elif "star" in selector:  # rating via aria-label/text
            mock.first.get_attribute.return_value = "5 stars"
            mock.first.text_content.return_value = "5 stars"
        elif 'span:has-text("/")' in selector:
            mock.first.text_content.return_value = "5/5"
        elif "DZSIDd" in selector or "xRkPPb" in selector:  # date (updated selectors)
            mock.first.text_content.return_value = "2 weeks ago"
        elif "d4r55" in selector:  # name (updated selector)
            mock.first.text_content.return_value = "John Doe"
        return mock

    review1.locator.side_effect = review1_locator

    # Mock page.locator for feed and reviews
    # Mock feed container with scroll + locator
    feed = MagicMock()
    feed.first = MagicMock()
    feed.first.scroll_into_view_if_needed.return_value = None
    feed.first.locator.return_value.all.return_value = [review1]

    def page_locator(selector):
        if "feed" in selector:
            return feed
        if "data-review-id" in selector:
            mock = MagicMock()
            mock.all.return_value = [review1]
            return mock
        if 'span:has-text("/")' in selector:
            mock = MagicMock()
            mock.first = MagicMock()
            mock.first.text_content.return_value = "5/5"
            return mock
        return MagicMock()

    page.locator.side_effect = page_locator
    page.mouse.wheel.return_value = None

    reviews = scrape_reviews("Test Hotel", page, max_reviews=10)

    assert len(reviews) == 1
    assert reviews[0].text == "Great hotel with amazing pool!"
    assert reviews[0].rating == 5
    assert reviews[0].date == "2 weeks ago"
    assert reviews[0].reviewer_name == "John Doe"


def test_scrape_reviews_handles_timeout():
    """Test that scrape_reviews handles timeout gracefully."""
    page = MagicMock()
    page.click.side_effect = PlaywrightTimeoutError("timeout")

    reviews = scrape_reviews("Test Hotel", page, max_reviews=10)

    # Should return empty list on timeout
    assert reviews == []


def test_scrape_reviews_returns_empty_on_error():
    """Test that scrape_reviews returns empty list on error."""
    page = MagicMock()
    page.click.side_effect = Exception("Unknown error")

    reviews = scrape_reviews("Test Hotel", page, max_reviews=10)

    assert reviews == []


def test_deduplicate_reviews():
    from travel_tools.types import Review

    review = Review(text="Great stay", rating=5, date="today", reviewer_name="Alex")
    duplicates = [
        review,
        review,
        Review(text="Great stay", rating=5, date="today", reviewer_name="Alex"),
    ]
    unique = deduplicate_reviews(duplicates)
    assert len(unique) == 1
