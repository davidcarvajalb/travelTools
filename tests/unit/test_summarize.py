"""Tests for AI summarization logic."""

import pytest
from unittest.mock import MagicMock, patch

from travel_tools.step2_5_summarize import (
    configure_gemini_api,
    summarize_reviews_with_gemini,
)
from travel_tools.types import ReviewSummary


def test_configure_gemini_api_with_key():
    """Test API configuration with provided key."""
    with patch("travel_tools.step2_5_summarize.genai") as mock_genai:
        configure_gemini_api("test-api-key")
        mock_genai.configure.assert_called_once_with(api_key="test-api-key")


def test_configure_gemini_api_from_env():
    """Test API configuration from environment variable."""
    with patch("travel_tools.step2_5_summarize.genai") as mock_genai:
        with patch("travel_tools.step2_5_summarize.os.getenv") as mock_getenv:
            mock_getenv.return_value = "env-api-key"
            configure_gemini_api()
            mock_genai.configure.assert_called_once_with(api_key="env-api-key")


def test_configure_gemini_api_missing_key():
    """Test error when API key is missing."""
    with patch("travel_tools.step2_5_summarize.os.getenv") as mock_getenv:
        mock_getenv.return_value = None
        with pytest.raises(ValueError, match="API key not found"):
            configure_gemini_api()


def test_summarize_reviews_empty_list():
    """Test summarization with no reviews."""
    summary = summarize_reviews_with_gemini(
        hotel_name="Test Hotel",
        reviews=[],
    )

    assert isinstance(summary, ReviewSummary)
    assert summary.review_count_analyzed == 0
    assert len(summary.good_points) == 0
    assert len(summary.bad_points) == 0
    assert len(summary.ugly_points) == 0
    assert "No reviews" in summary.overall_summary


@patch("travel_tools.step2_5_summarize.genai")
def test_summarize_reviews_success(mock_genai):
    """Test successful review summarization."""
    # Mock API response
    mock_response = MagicMock()
    mock_response.text = """
{
    "good_points": ["Great pool", "Friendly staff"],
    "bad_points": ["Food quality", "WiFi spotty"],
    "ugly_points": ["Cleanliness issues"],
    "overall_summary": "Mixed experience with some concerns.",
    "review_count_analyzed": 3
}
    """

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    reviews = [
        {
            "text": "Great pool but food was bad",
            "rating": 3,
            "date": "2024-01-01",
            "reviewer_name": "John",
        },
        {
            "text": "Cleanliness was an issue",
            "rating": 2,
            "date": "2024-01-02",
            "reviewer_name": "Jane",
        },
        {
            "text": "Friendly staff, WiFi problems",
            "rating": 4,
            "date": "2024-01-03",
            "reviewer_name": "Bob",
        },
    ]

    summary = summarize_reviews_with_gemini(
        hotel_name="Test Hotel",
        reviews=reviews,
    )

    assert isinstance(summary, ReviewSummary)
    assert len(summary.good_points) == 2
    assert "Great pool" in summary.good_points
    assert "Friendly staff" in summary.good_points
    assert len(summary.bad_points) == 2
    assert len(summary.ugly_points) == 1
    assert summary.review_count_analyzed == 3
    assert "Mixed experience" in summary.overall_summary


@patch("travel_tools.step2_5_summarize.genai")
def test_summarize_reviews_handles_markdown_json(mock_genai):
    """Test handling of JSON wrapped in markdown code blocks."""
    # Mock API response with markdown
    mock_response = MagicMock()
    mock_response.text = """```json
{
    "good_points": ["Nice view"],
    "bad_points": ["Expensive"],
    "ugly_points": [],
    "overall_summary": "Decent hotel.",
    "review_count_analyzed": 1
}
```"""

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    reviews = [
        {
            "text": "Nice view but expensive",
            "rating": 3,
            "date": "2024-01-01",
            "reviewer_name": "Test",
        }
    ]

    summary = summarize_reviews_with_gemini(
        hotel_name="Test Hotel",
        reviews=reviews,
    )

    assert isinstance(summary, ReviewSummary)
    assert len(summary.good_points) == 1
    assert summary.good_points[0] == "Nice view"


@patch("travel_tools.step2_5_summarize.genai")
def test_summarize_reviews_invalid_json_raises(mock_genai):
    """Test error handling for invalid JSON response."""
    # Mock API response with invalid JSON
    mock_response = MagicMock()
    mock_response.text = "This is not valid JSON"

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    reviews = [
        {
            "text": "Test review",
            "rating": 3,
            "date": "2024-01-01",
            "reviewer_name": "Test",
        }
    ]

    with pytest.raises(Exception):  # Will raise JSONDecodeError or similar
        summarize_reviews_with_gemini(
            hotel_name="Test Hotel",
            reviews=reviews,
        )


@patch("travel_tools.step2_5_summarize.genai")
def test_summarize_reviews_uses_correct_model(mock_genai):
    """Test that the correct model is used."""
    mock_response = MagicMock()
    mock_response.text = """
{
    "good_points": [],
    "bad_points": [],
    "ugly_points": [],
    "overall_summary": "Test",
    "review_count_analyzed": 0
}
    """

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    reviews = [{"text": "Test", "rating": 3, "date": "2024-01-01", "reviewer_name": "Test"}]

    summarize_reviews_with_gemini(
        hotel_name="Test Hotel",
        reviews=reviews,
        model_name="gemini-1.5-pro",
    )

    # Verify correct model was instantiated
    mock_genai.GenerativeModel.assert_called_once_with("gemini-1.5-pro")
