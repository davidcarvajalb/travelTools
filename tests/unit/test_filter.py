"""Tests for step1_filter.py"""

import pytest

from travel_tools.step1_filter import filter_packages, transform_transat_package


def test_transform_transat_package():
    """Test transformation of Transat format to standard format."""
    transat_pkg = {
        "hotel": {
            "name": "Test Hotel",
            "city": "Cancun",
            "transatStars": 5,
            "numberOfRestaurants": 9,
            "adultOnly": 1,
            "drinks24h": 1,
            "snacks24h": 0
        },
        "mealPlanCode": "AI",
        "totalPriceForGroup": 5000,
        "departureDate": "2025-02-15T00:00:00",
        "returnDate": "2025-02-22T00:00:00"
    }

    result = transform_transat_package(transat_pkg)

    assert result["hotel_name"] == "Test Hotel"
    assert result["city"] == "Cancun"
    assert result["stars"] == 5
    assert result["price"] == 5000
    assert "All-Inclusive" in result["amenities"]
    assert "Adults Only" in result["amenities"]
    assert "24h Drinks" in result["amenities"]


def test_filters_packages_above_budget():
    """Test that packages above budget are filtered out."""
    transat_packages = [
        {
            "hotel": {"name": "Hotel A", "city": "Cancun", "transatStars": 4},
            "totalPriceForGroup": 4000,
            "mealPlanCode": "AI",
            "departureDate": "2025-02-15T00:00:00",
            "returnDate": "2025-02-22T00:00:00"
        },
        {
            "hotel": {"name": "Hotel B", "city": "Cancun", "transatStars": 5},
            "totalPriceForGroup": 6000,
            "mealPlanCode": "AI",
            "departureDate": "2025-02-15T00:00:00",
            "returnDate": "2025-02-22T00:00:00"
        },
    ]

    result = filter_packages(transat_packages, budget=5000)
    assert len(result) == 1
    assert all(pkg["price"] <= 5000 for pkg in result)


def test_filters_packages_at_budget():
    """Test that packages exactly at budget are included."""
    transat_packages = [
        {
            "hotel": {"name": "Hotel A", "city": "Cancun", "transatStars": 4},
            "totalPriceForGroup": 4200,
            "mealPlanCode": "AI",
            "departureDate": "2025-02-15T00:00:00",
            "returnDate": "2025-02-22T00:00:00"
        },
    ]

    result = filter_packages(transat_packages, budget=4200)
    assert len(result) == 1
    assert result[0]["price"] == 4200


def test_handles_empty_input():
    """Test filtering empty package list."""
    result = filter_packages([], budget=5000)
    assert result == []


def test_all_packages_within_budget():
    """Test when all packages are within budget."""
    transat_packages = [
        {
            "hotel": {"name": "Hotel A", "city": "Cancun", "transatStars": 4},
            "totalPriceForGroup": 4000,
            "mealPlanCode": "AI",
            "departureDate": "2025-02-15T00:00:00",
            "returnDate": "2025-02-22T00:00:00"
        },
        {
            "hotel": {"name": "Hotel B", "city": "Cancun", "transatStars": 5},
            "totalPriceForGroup": 5000,
            "mealPlanCode": "AI",
            "departureDate": "2025-02-15T00:00:00",
            "returnDate": "2025-02-22T00:00:00"
        },
    ]

    result = filter_packages(transat_packages, budget=10000)
    assert len(result) == 2
