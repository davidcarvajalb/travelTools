"""Tests for AI prompt templates."""

import pytest

from travel_tools.prompts import (
    ClaudePrompts,
    GeminiPrompts,
    get_prompt_template,
)


def test_gemini_prompt_includes_hotel_name():
    """Test that Gemini prompt includes the hotel name."""
    hotel_name = "Test Resort"
    reviews_text = "Great hotel!"

    prompt = GeminiPrompts.format_review_summarization(hotel_name, reviews_text)

    assert hotel_name in prompt
    assert reviews_text in prompt


def test_gemini_prompt_requests_json_structure():
    """Test that Gemini prompt requests specific JSON structure."""
    prompt = GeminiPrompts.format_review_summarization("Hotel", "Review text")

    # Check for required JSON fields
    assert "good_points" in prompt
    assert "bad_points" in prompt
    assert "ugly_points" in prompt
    assert "overall_summary" in prompt
    assert "review_count_analyzed" in prompt


def test_gemini_prompt_includes_guidelines():
    """Test that Gemini prompt includes helpful guidelines."""
    prompt = GeminiPrompts.format_review_summarization("Hotel", "Review")

    # Check for guidance keywords
    assert "recurring" in prompt.lower() or "theme" in prompt.lower()
    assert "json" in prompt.lower()


def test_claude_prompt_includes_hotel_name():
    """Test that Claude prompt includes the hotel name."""
    hotel_name = "Test Resort"
    reviews_text = "Great hotel!"

    prompt = ClaudePrompts.format_review_summarization(hotel_name, reviews_text)

    assert hotel_name in prompt
    assert reviews_text in prompt


def test_claude_prompt_uses_xml_tags():
    """Test that Claude prompt uses XML-style tags."""
    prompt = ClaudePrompts.format_review_summarization("Hotel", "Review")

    assert "<reviews>" in prompt
    assert "</reviews>" in prompt


def test_get_prompt_template_gemini():
    """Test getting Gemini prompt template."""
    template = get_prompt_template("gemini")
    assert template == GeminiPrompts


def test_get_prompt_template_claude():
    """Test getting Claude prompt template."""
    template = get_prompt_template("claude")
    assert template == ClaudePrompts


def test_get_prompt_template_invalid():
    """Test error for invalid provider."""
    with pytest.raises(ValueError, match="Unsupported provider"):
        get_prompt_template("invalid")


def test_prompt_templates_have_same_signature():
    """Test that both templates have compatible signatures."""
    hotel = "Test Hotel"
    reviews = "Test review"

    gemini_prompt = GeminiPrompts.format_review_summarization(hotel, reviews)
    claude_prompt = ClaudePrompts.format_review_summarization(hotel, reviews)

    # Both should return strings
    assert isinstance(gemini_prompt, str)
    assert isinstance(claude_prompt, str)

    # Both should be non-empty
    assert len(gemini_prompt) > 0
    assert len(claude_prompt) > 0
