"""Pytest configuration and fixtures."""

import json
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture
def sample_packages():
    """Sample package data for testing."""
    return [
        {
            "hotel_name": "Dreams Riviera Cancun",
            "city": "Puerto Morelos",
            "stars": 5,
            "room_type": "Deluxe Ocean View",
            "url": "https://example.com/dreams",
            "drinks24h": True,
            "snacks24h": False,
            "adult_only": 1,
            "amenities": ["All-Inclusive", "Beach Access"],
            "price": 4200.0,
            "dates": {"departure": "2025-02-15T00:00:00", "return": "2025-02-22T00:00:00"},
        },
        {
            "hotel_name": "Secrets Maroma",
            "city": "Playa del Carmen",
            "stars": 5,
            "room_type": "Preferred Club",
            "url": "https://example.com/secrets",
            "drinks24h": False,
            "snacks24h": True,
            "adult_only": 2,
            "amenities": ["All-Inclusive", "Adults Only"],
            "price": 5800.0,
            "dates": {"departure": "2025-03-10T00:00:00", "return": "2025-03-17T00:00:00"},
        },
        {
            "hotel_name": "Dreams Riviera Cancun",
            "city": "Puerto Morelos",
            "stars": 5,
            "room_type": "Standard",
            "url": "https://example.com/dreams",
            "drinks24h": True,
            "snacks24h": True,
            "adult_only": 1,
            "amenities": ["All-Inclusive"],
            "price": 8500.0,
            "dates": {"departure": "2025-04-05T00:00:00", "return": "2025-04-12T00:00:00"},
        },
    ]


@pytest.fixture
def sample_ratings():
    """Sample Google ratings data for testing."""
    return [
        {
            "hotel_name": "Dreams Riviera Cancun",
            "rating": 4.5,
            "review_count": 12450,
            "review_summary": {
                "good_points": ["Great pool", "Friendly staff"],
                "bad_points": ["Noise at night"],
                "ugly_points": [],
                "overall_summary": "Strong experience with minor noise issues.",
                "review_count_analyzed": 5,
            },
        },
        {
            "hotel_name": "Secrets Maroma",
            "rating": 4.7,
            "review_count": 8230,
            "review_summary": {
                "good_points": ["Amazing beach"],
                "bad_points": [],
                "ugly_points": [],
                "overall_summary": "Beautiful property with stellar beach access.",
                "review_count_analyzed": 4,
            },
        },
    ]


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory structure."""
    data_dir = tmp_path / "data" / "cancun" / "transat"
    (data_dir / "raw").mkdir(parents=True)
    (data_dir / "filtered").mkdir(parents=True)
    (data_dir / "scraped").mkdir(parents=True)
    (data_dir / "merged").mkdir(parents=True)
    return tmp_path
