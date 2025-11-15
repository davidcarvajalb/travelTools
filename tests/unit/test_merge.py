"""Tests for step3_merge.py"""

import pytest

from travel_tools.step3_merge import merge_data


def test_merges_packages_with_ratings(sample_packages, sample_ratings):
    """Test merging packages with ratings."""
    result = merge_data(sample_packages, sample_ratings, source="transat")

    assert len(result) == 2
    assert result[0]["name"] == "Dreams Riviera Cancun"
    assert result[0]["google_rating"] == 4.5
    assert result[0]["review_count"] == 12450


def test_calculates_price_ranges(sample_packages, sample_ratings):
    """Test price range calculation."""
    result = merge_data(sample_packages, sample_ratings, source="transat")

    dreams_hotel = next(h for h in result if h["name"] == "Dreams Riviera Cancun")
    assert dreams_hotel["price_range"]["min"] == 4200
    assert dreams_hotel["price_range"]["max"] == 8500


def test_handles_missing_ratings(sample_packages):
    """Test merging when ratings are missing."""
    result = merge_data(sample_packages, [], source="transat")

    assert len(result) == 2
    assert all(h["google_rating"] is None for h in result)
    assert all(h["review_count"] is None for h in result)


def test_includes_source(sample_packages, sample_ratings):
    """Test that source is included in output."""
    result = merge_data(sample_packages, sample_ratings, source="expedia")

    assert all(h["source"] == "expedia" for h in result)


def test_adds_urls_and_flags(sample_packages, sample_ratings):
    """Ensure URLs and 24h flags are surfaced."""
    result = merge_data(sample_packages, sample_ratings, source="transat")
    dreams = next(h for h in result if h["name"] == "Dreams Riviera Cancun")
    assert dreams["air_transat_url"] == "https://example.com/dreams"
    assert dreams["google_maps_url"].startswith("https://www.google.com/maps/search/")
    assert dreams["drinks24h"] is True
    assert dreams["snacks24h"] is True
    assert dreams["adult_only"] == 1
