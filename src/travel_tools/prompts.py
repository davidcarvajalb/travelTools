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
        return f"""Analyze the following hotel reviews for "{hotel_name}" and provide a structured summary.

Reviews:
{reviews_text}

Please provide a JSON response with the following structure:
{{
    "good_points": ["list of positive highlights from reviews"],
    "bad_points": ["list of negative aspects mentioned"],
    "ugly_points": ["list of serious issues or deal-breakers"],
    "overall_summary": "A brief 2-3 sentence summary of the overall sentiment",
    "review_count_analyzed": <number of reviews analyzed>
}}

Guidelines:
- good_points: Extract recurring positive themes (e.g., "Great pool area", "Friendly staff")
- bad_points: Extract common complaints that are concerning but not critical (e.g., "Food variety limited", "WiFi spotty")
- ugly_points: Extract serious issues that might be deal-breakers (e.g., "Health/safety concerns", "Severe cleanliness issues", "Major maintenance problems")
- Keep each point concise (1-2 sentences max)
- Focus on recurring themes mentioned by multiple reviewers
- Be honest and balanced - include both positives and negatives
- overall_summary: Synthesize the overall experience in 2-3 sentences

Return ONLY the JSON object, no additional text."""


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
