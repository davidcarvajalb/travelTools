"""Tests for Review and ReviewSummary models."""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from travel_tools.types import (
    GoogleRating,
    HotelData,
    Review,
    ReviewSummary,
    WebHotel,
    PriceRange,
)


# ============================================================================
# Review Model Tests
# ============================================================================


def test_review_model_valid_data():
    """Test Review model with valid data."""
    review = Review(
        text="Great hotel, loved the pool!",
        rating=5,
        date="2025-01-15",
        reviewer_name="John Doe"
    )
    assert review.text == "Great hotel, loved the pool!"
    assert review.rating == 5
    assert review.date == "2025-01-15"
    assert review.reviewer_name == "John Doe"


def test_review_model_strips_whitespace():
    """Test Review model strips whitespace from strings."""
    review = Review(
        text="  Great hotel  ",
        rating=4,
        date="  2025-01-15  ",
        reviewer_name="  Jane Doe  "
    )
    assert review.text == "Great hotel"
    assert review.date == "2025-01-15"
    assert review.reviewer_name == "Jane Doe"


def test_review_model_missing_required_fields():
    """Test Review model raises error when required fields are missing."""
    with pytest.raises(ValidationError) as exc_info:
        Review(rating=5, date="2025-01-15")  # Missing text

    assert "text" in str(exc_info.value)


def test_review_model_invalid_rating_too_high():
    """Test Review model rejects rating > 5."""
    with pytest.raises(ValidationError) as exc_info:
        Review(text="Good", rating=6, date="2025-01-15")

    assert "rating" in str(exc_info.value).lower()


def test_review_model_invalid_rating_too_low():
    """Test Review model rejects rating < 1."""
    with pytest.raises(ValidationError) as exc_info:
        Review(text="Bad", rating=0, date="2025-01-15")

    assert "rating" in str(exc_info.value).lower()


def test_review_model_empty_text():
    """Test Review model rejects empty text."""
    with pytest.raises(ValidationError) as exc_info:
        Review(text="", rating=3, date="2025-01-15")

    assert "text" in str(exc_info.value).lower()


def test_review_model_optional_reviewer_name():
    """Test Review model allows None for optional reviewer_name."""
    review = Review(
        text="Anonymous review",
        rating=4,
        date="2025-01-15",
        reviewer_name=None
    )
    assert review.reviewer_name is None


def test_review_model_relative_date():
    """Test Review model accepts relative dates like '2 weeks ago'."""
    review = Review(
        text="Recent visit",
        rating=5,
        date="2 weeks ago"
    )
    assert review.date == "2 weeks ago"


def test_review_model_json_serialization():
    """Test Review model serializes to JSON correctly."""
    review = Review(
        text="Excellent service",
        rating=5,
        date="2025-01-15",
        reviewer_name="Alice"
    )

    json_data = review.model_dump_json()
    parsed = json.loads(json_data)

    assert parsed["text"] == "Excellent service"
    assert parsed["rating"] == 5
    assert parsed["date"] == "2025-01-15"
    assert parsed["reviewer_name"] == "Alice"


# ============================================================================
# ReviewSummary Model Tests
# ============================================================================


def test_review_summary_valid_data():
    """Test ReviewSummary model with valid data."""
    summary = ReviewSummary(
        good_points=["Clean rooms", "Great pool", "Friendly staff"],
        bad_points=["Noisy", "Small breakfast"],
        ugly_points=["Construction noise"],
        overall_summary="Good hotel with minor issues",
        review_count_analyzed=15
    )

    assert len(summary.good_points) == 3
    assert len(summary.bad_points) == 2
    assert len(summary.ugly_points) == 1
    assert summary.overall_summary == "Good hotel with minor issues"
    assert summary.review_count_analyzed == 15


def test_review_summary_empty_lists():
    """Test ReviewSummary model accepts empty lists."""
    summary = ReviewSummary(
        good_points=[],
        bad_points=[],
        ugly_points=[],
        overall_summary="No clear themes",
        review_count_analyzed=5
    )

    assert summary.good_points == []
    assert summary.bad_points == []
    assert summary.ugly_points == []


def test_review_summary_default_empty_lists():
    """Test ReviewSummary model uses default empty lists."""
    summary = ReviewSummary(
        overall_summary="Summary text",
        review_count_analyzed=10
    )

    assert summary.good_points == []
    assert summary.bad_points == []
    assert summary.ugly_points == []


def test_review_summary_missing_required_fields():
    """Test ReviewSummary model raises error when required fields are missing."""
    with pytest.raises(ValidationError) as exc_info:
        ReviewSummary(
            good_points=["Clean"],
            review_count_analyzed=5
        )  # Missing overall_summary

    assert "overall_summary" in str(exc_info.value)


def test_review_summary_empty_summary_text():
    """Test ReviewSummary model rejects empty summary text."""
    with pytest.raises(ValidationError) as exc_info:
        ReviewSummary(
            overall_summary="",
            review_count_analyzed=5
        )

    assert "overall_summary" in str(exc_info.value).lower()


def test_review_summary_negative_review_count():
    """Test ReviewSummary model rejects negative review count."""
    with pytest.raises(ValidationError) as exc_info:
        ReviewSummary(
            overall_summary="Test",
            review_count_analyzed=-1
        )

    assert "review_count_analyzed" in str(exc_info.value).lower()


def test_review_summary_strips_whitespace():
    """Test ReviewSummary model strips whitespace from strings."""
    summary = ReviewSummary(
        good_points=["  Clean  ", "  Great  "],
        overall_summary="  Nice hotel  ",
        review_count_analyzed=10
    )

    assert summary.good_points == ["Clean", "Great"]
    assert summary.overall_summary == "Nice hotel"


def test_review_summary_json_serialization():
    """Test ReviewSummary model serializes to JSON correctly."""
    summary = ReviewSummary(
        good_points=["Pool", "Beach"],
        bad_points=["Noise"],
        ugly_points=[],
        overall_summary="Decent resort",
        review_count_analyzed=20
    )

    json_data = summary.model_dump_json()
    parsed = json.loads(json_data)

    assert parsed["good_points"] == ["Pool", "Beach"]
    assert parsed["bad_points"] == ["Noise"]
    assert parsed["ugly_points"] == []
    assert parsed["overall_summary"] == "Decent resort"
    assert parsed["review_count_analyzed"] == 20


# ============================================================================
# Integration with Existing Models
# ============================================================================


def test_google_rating_with_reviews():
    """Test GoogleRating model with reviews field."""
    reviews = [
        Review(text="Great!", rating=5, date="2025-01-15"),
        Review(text="Good", rating=4, date="2025-01-14")
    ]

    rating = GoogleRating(
        hotel_name="Test Hotel",
        rating=4.5,
        review_count=100,
        reviews=reviews
    )

    assert len(rating.reviews) == 2
    assert rating.reviews[0].rating == 5
    assert rating.reviews[1].rating == 4


def test_google_rating_empty_reviews():
    """Test GoogleRating model with empty reviews list."""
    rating = GoogleRating(
        hotel_name="Test Hotel",
        rating=4.0,
        review_count=50,
        reviews=[]
    )

    assert rating.reviews == []


def test_google_rating_default_empty_reviews():
    """Test GoogleRating model defaults to empty reviews list."""
    rating = GoogleRating(
        hotel_name="Test Hotel",
        rating=4.0,
        review_count=50
    )

    assert rating.reviews == []


def test_hotel_data_with_review_summary():
    """Test HotelData model with review_summary field."""
    summary = ReviewSummary(
        good_points=["Clean"],
        bad_points=["Noisy"],
        ugly_points=[],
        overall_summary="Good hotel",
        review_count_analyzed=10
    )

    hotel = HotelData(
        name="Test Hotel",
        city="Cancun",
        stars=4,
        google_rating=4.2,
        review_count=100,
        air_transat_url=None,
        google_maps_url=None,
        drinks24h=True,
        snacks24h=False,
        departure_date="2025-12-23",
        return_date="2025-12-29",
        source="transat",
        price_range=PriceRange(min=4000.0, max=5000.0, avg=4500.0),
        packages=[],
        review_summary=summary
    )

    assert hotel.review_summary is not None
    assert hotel.review_summary.overall_summary == "Good hotel"


def test_hotel_data_without_review_summary():
    """Test HotelData model allows None for review_summary."""
    hotel = HotelData(
        name="Test Hotel",
        city="Cancun",
        stars=4,
        google_rating=4.2,
        review_count=100,
        air_transat_url=None,
        google_maps_url=None,
        drinks24h=True,
        snacks24h=False,
        departure_date="2025-12-23",
        return_date="2025-12-29",
        source="transat",
        price_range=PriceRange(min=4000.0, max=5000.0, avg=4500.0),
        packages=[],
        review_summary=None
    )

    assert hotel.review_summary is None


def test_web_hotel_with_review_summary():
    """Test WebHotel model with review_summary field."""
    summary = ReviewSummary(
        good_points=["Pool", "Staff"],
        bad_points=["Food"],
        ugly_points=[],
        overall_summary="Nice resort",
        review_count_analyzed=15
    )

    hotel = WebHotel(
        id="hotel_001",
        name="Test Hotel",
        city="Cancun",
        stars=5,
        google_rating=4.5,
        review_count=200,
        price_range=PriceRange(min=3000.0, max=4000.0, avg=3500.0),
        package_count=3,
        packages=[],
        review_summary=summary
    )

    assert hotel.review_summary is not None
    assert len(hotel.review_summary.good_points) == 2


def test_web_hotel_serializes_with_review_summary():
    """Test WebHotel serializes review_summary to JSON correctly."""
    summary = ReviewSummary(
        good_points=["Beach"],
        overall_summary="Great location",
        review_count_analyzed=5
    )

    hotel = WebHotel(
        id="hotel_002",
        name="Beach Resort",
        city="Cancun",
        stars=4,
        google_rating=4.0,
        review_count=100,
        price_range=PriceRange(min=2000.0, max=3000.0, avg=2500.0),
        package_count=1,
        packages=[],
        review_summary=summary
    )

    json_data = hotel.model_dump_json()
    parsed = json.loads(json_data)

    assert "review_summary" in parsed
    assert parsed["review_summary"]["good_points"] == ["Beach"]
    assert parsed["review_summary"]["overall_summary"] == "Great location"
    assert parsed["review_summary"]["review_count_analyzed"] == 5


def test_models_backward_compatible():
    """Test that existing code without reviews still works."""
    # Old-style GoogleRating without reviews
    rating = GoogleRating(
        hotel_name="Old Hotel",
        rating=3.8,
        review_count=50
    )
    assert rating.reviews == []

    # Old-style HotelData without review_summary
    hotel = HotelData(
        name="Old Hotel",
        city="Cancun",
        stars=3,
        google_rating=3.8,
        review_count=50,
        air_transat_url=None,
        google_maps_url=None,
        drinks24h=False,
        snacks24h=False,
        departure_date="2025-12-23",
        return_date="2025-12-29",
        source="transat",
        price_range=PriceRange(min=2000.0, max=2500.0, avg=2250.0),
        packages=[]
    )
    assert hotel.review_summary is None
