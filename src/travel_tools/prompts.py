"""AI prompts for review summarization.

This module contains configurable prompts for different AI providers.
Prompts are stored as templates that can be easily modified without
changing the core summarization logic.
"""

from typing import Protocol


class PromptTemplate(Protocol):
    """Protocol for prompt templates."""

    def format_review_summarization(self, hotel_name: str, reviews_text: str) -> str:
        """Format a prompt for review summarization."""
        ...


class GeminiPrompts:
    """Prompts optimized for Google Gemini API."""

    @staticmethod
    def format_review_summarization(hotel_name: str, reviews_text: str) -> str:
        """Format a prompt for Gemini to summarize hotel reviews.

        Args:
            hotel_name: Name of the hotel
            reviews_text: Combined text of all reviews

        Returns:
            Formatted prompt string
        """
        return f"""Analyze the following hotel reviews and produce the JSON output below. Ignore duplicates, emojis, and filler phrases. Focus only on meaningful content.

Return ONLY this JSON:
{{
  "good_points": [],
  "bad_points": [],
  "ugly_points": [],
  "overall_summary": "",
  "review_count_analyzed": 0
}}

Rules:
- Summarize only recurring themes across reviews
- Max 5 items per list
- Each item 8–20 words, concise and factual
- good_points = commonly praised aspects
- bad_points = moderate or occasional issues
- ugly_points = serious or repeated deal-breakers
- overall_summary = 2–3 sentences (40–70 words)
- No markdown, no explanations, no extra text
- Compress long reviews internally before extracting themes
- If a theme appears only once, ignore it

Reviews for "{hotel_name}":
{reviews_text}"""


class ClaudePrompts:
    """Prompts optimized for Anthropic Claude API (for future use)."""

    @staticmethod
    def format_review_summarization(hotel_name: str, reviews_text: str) -> str:
        """Format a prompt for Claude to summarize hotel reviews."""
        return f"""You are analyzing hotel reviews for "{hotel_name}".

Here are the reviews to analyze:

<reviews>
{reviews_text}
</reviews>

Please analyze these reviews and provide a structured summary in JSON format with:

1. good_points: Array of positive aspects (recurring themes that guests enjoyed)
2. bad_points: Array of negative aspects (issues that were problematic but not critical)
3. ugly_points: Array of serious issues (deal-breakers like health/safety concerns)
4. overall_summary: A balanced 2-3 sentence summary of the guest experience
5. review_count_analyzed: Number of reviews you analyzed

Focus on:
- Recurring themes mentioned by multiple guests
- Being balanced and honest about both strengths and weaknesses
- Identifying truly serious issues vs. minor complaints
- Keeping each point concise and actionable

Return your response as valid JSON only, no other text."""


# Default prompt template to use
DEFAULT_PROMPT_TEMPLATE = GeminiPrompts


def get_prompt_template(provider: str = "gemini") -> type[PromptTemplate]:
    """Get the appropriate prompt template for a given AI provider.

    Args:
        provider: Name of the AI provider ("gemini", "claude", etc.)

    Returns:
        Prompt template class for the specified provider

    Raises:
        ValueError: If provider is not supported
    """
    providers = {
        "gemini": GeminiPrompts,
        "claude": ClaudePrompts,
    }

    if provider not in providers:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Available providers: {', '.join(providers.keys())}"
        )

    return providers[provider]
