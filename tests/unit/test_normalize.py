"""Tests for normalization step (step3_5_normalize)."""

from collections import Counter

from travel_tools.step3_5_normalize import normalize_hotel


def test_normalize_hotel_fields():
    stats: Counter[str] = Counter()
    hotel = {
        "name": "Test Hotel",
        "drinks24h": 2,
        "snacks24h": 0,
        "number_of_restaurants": "0",
        "spa_available": "",
        "meal_plan_code": "AI",
        "meal_plan_label": None,
        "thumbnail_url": "//example.com/photo.jpg",
        "packages": [
            {
                "meal_plan_code": "EP",
                "meal_plan_label": None,
                "drinks24h": 1,
                "snacks24h": None,
                "number_of_restaurants": "3",
                "spa_available": "No",
                "thumbnail_url": None,
            }
        ],
    }

    normalized = normalize_hotel(hotel, stats)

    assert normalized["drinks24h"] is True
    assert normalized["snacks24h"] is False
    assert normalized["number_of_restaurants"] is None
    assert normalized["spa_available"] is None
    assert normalized["meal_plan_code"] == "AI"
    assert normalized["meal_plan_label"] == "All Inclusive"
    assert normalized["thumbnail_url"].startswith("https://")

    pkg = normalized["packages"][0]
    assert pkg["meal_plan_code"] == "EP"
    assert pkg["meal_plan_label"] == "European Plan (no meals)"
    assert pkg["drinks24h"] is True
    assert pkg["snacks24h"] is None
    assert pkg["number_of_restaurants"] == 3
    assert pkg["spa_available"] == "No"

    assert stats["drinks24h_null"] == 0
    assert stats["snacks24h_null"] == 0
    assert stats["number_of_restaurants_null"] == 1
    assert stats["meal_plan_unknown"] >= 0
