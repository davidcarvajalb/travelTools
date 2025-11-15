"""Tests for step4_generate_web.py"""

import pytest

from travel_tools.step4_generate_web import transform_to_web_format


def test_generates_valid_structure(sample_packages, sample_ratings):
    """Test that web output has correct structure."""
    from travel_tools.step3_merge import merge_data

    merged = merge_data(sample_packages, sample_ratings, source="transat")
    result = transform_to_web_format(merged, "cancun", "transat", 5000)

    assert "metadata" in result
    assert "hotels" in result
    assert result["metadata"]["destination"] == "cancun"
    assert result["metadata"]["source"] == "transat"
    assert result["metadata"]["budget"] == 5000


def test_adds_unique_hotel_ids(sample_packages, sample_ratings):
    """Test that unique IDs are assigned to hotels."""
    from travel_tools.step3_merge import merge_data

    merged = merge_data(sample_packages, sample_ratings, source="transat")
    result = transform_to_web_format(merged, "cancun", "transat", 5000)

    hotel_ids = [h["id"] for h in result["hotels"]]
    assert hotel_ids[0] == "hotel_000"
    assert hotel_ids[1] == "hotel_001"
    assert len(hotel_ids) == len(set(hotel_ids))  # All unique


def test_calculates_duration_days(sample_packages, sample_ratings):
    """Test that package duration is calculated correctly."""
    from travel_tools.step3_merge import merge_data

    merged = merge_data(sample_packages, sample_ratings, source="transat")
    result = transform_to_web_format(merged, "cancun", "transat", 5000)

    # Dreams hotel has packages with 7-day durations
    dreams = next(h for h in result["hotels"] if "Dreams" in h["name"])
    assert all(pkg["duration_days"] == 7 for pkg in dreams["packages"])


def test_formats_dates_as_strings(sample_packages, sample_ratings):
    """Test that dates are formatted as ISO strings."""
    from travel_tools.step3_merge import merge_data

    merged = merge_data(sample_packages, sample_ratings, source="transat")
    result = transform_to_web_format(merged, "cancun", "transat", 5000)

    for hotel in result["hotels"]:
        for pkg in hotel["packages"]:
            assert isinstance(pkg["departure"], str)
            assert isinstance(pkg["return"], str)
            # Check format: YYYY-MM-DD
            assert len(pkg["departure"]) == 10
            assert pkg["departure"].count("-") == 2


def test_includes_links_and_flags(sample_packages, sample_ratings):
    """New metadata should be exposed in web format."""
    from travel_tools.step3_merge import merge_data

    merged = merge_data(sample_packages, sample_ratings, source="transat")
    result = transform_to_web_format(merged, "cancun", "transat", 5000)

    dreams = next(h for h in result["hotels"] if "Dreams" in h["name"])
    assert dreams["air_transat_url"] == "https://example.com/dreams"
    assert dreams["google_maps_url"].startswith("https://www.google.com/maps/search/")
    assert dreams["drinks24h"] is True
    assert dreams["snacks24h"] is True
    assert dreams["departure_date"] == "2025-02-15T00:00:00"
    assert dreams["packages"][0]["url"] == "https://example.com/dreams"
