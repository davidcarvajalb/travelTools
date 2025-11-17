"""Type definitions for travel tools pipeline."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


# Step 1: Input package format
class PackageDates(BaseModel):
    """Date range for a package."""
    model_config = ConfigDict(populate_by_name=True)

    departure: datetime
    return_date: datetime = Field(alias="return")



class HotelPackage(BaseModel):
    """Hotel package from Transat/Expedia API."""

    hotel_name: str
    city: str
    stars: int | None = None
    room_type: str
    meal_plan_code: str | None = None
    meal_plan_label: str | None = None
    number_of_restaurants: int | None = None
    spa_available: str | int | None = None
    thumbnail_url: str | None = None
    url: str | None = None
    drinks24h: bool = False
    snacks24h: bool = False
    adult_only: int | None = None
    amenities: list[str] = Field(default_factory=list)
    price: float
    dates: PackageDates


# Step 2: Scraped data
class Review(BaseModel):
    """Individual Google Maps review."""
    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(..., min_length=1, description="Review text content")
    rating: int = Field(..., ge=1, le=5, description="Star rating 1-5")
    date: str = Field(..., description="Review date (YYYY-MM-DD or relative like '2 weeks ago')")
    reviewer_name: str | None = Field(None, description="Name of reviewer")


class ReviewSummary(BaseModel):
    """AI-generated review summary."""
    model_config = ConfigDict(str_strip_whitespace=True)

    good_points: list[str] = Field(default_factory=list, description="Positive highlights")
    bad_points: list[str] = Field(default_factory=list, description="Negative aspects")
    ugly_points: list[str] = Field(default_factory=list, description="Deal-breakers")
    overall_summary: str = Field(..., min_length=1, description="Overall summary text")
    review_count_analyzed: int = Field(..., ge=0, description="Number of reviews analyzed")


class GoogleRating(BaseModel):
    """Google Maps rating data."""

    hotel_name: str
    rating: float | None = None
    review_count: int | None = None
    reviews: list[Review] = Field(default_factory=list, description="Scraped reviews")


# Step 3: Merged output
class PriceRange(BaseModel):
    """Price statistics for a hotel."""

    min: float
    max: float
    avg: float


class HotelData(BaseModel):
    """Complete hotel data with packages and ratings."""

    name: str
    city: str
    stars: int | None
    google_rating: float | None
    review_count: int | None
    air_transat_url: str | None = None
    google_maps_url: str | None = None
    drinks24h: bool = False
    snacks24h: bool = False
    adult_only: int | None = None
    number_of_restaurants: int | None = None
    spa_available: str | int | None = None
    meal_plan_code: str | None = None
    meal_plan_label: str | None = None
    thumbnail_url: str | None = None
    departure_date: str | None = None
    return_date: str | None = None
    source: str  # 'transat', 'expedia', etc.
    price_range: PriceRange
    packages: list[HotelPackage]
    review_summary: ReviewSummary | None = Field(None, description="AI-generated review summary")


# Step 4: Web output format
class WebPackage(BaseModel):
    """Package data formatted for web viewer."""
    model_config = ConfigDict(populate_by_name=True)

    departure: str
    return_date: str = Field(alias="return")
    duration_days: int
    room_type: str
    meal_plan_code: str | None = None
    meal_plan_label: str | None = None
    number_of_restaurants: int | None = None
    spa_available: str | int | None = None
    thumbnail_url: str | None = None
    price: float
    url: str | None = None
    drinks24h: bool = False
    snacks24h: bool = False

class WebHotel(BaseModel):
    """Hotel data formatted for web viewer."""

    id: str  # hotel_001, hotel_002, etc.
    name: str
    city: str
    stars: int | None
    google_rating: float | None
    review_count: int | None
    air_transat_url: str | None = None
    google_maps_url: str | None = None
    drinks24h: bool = False
    snacks24h: bool = False
    adult_only: int | None = None
    number_of_restaurants: int | None = None
    spa_available: str | int | None = None
    meal_plan_code: str | None = None
    meal_plan_label: str | None = None
    thumbnail_url: str | None = None
    departure_date: str | None = None
    return_date: str | None = None
    price_range: PriceRange
    package_count: int
    packages: list[WebPackage]
    review_summary: ReviewSummary | None = Field(None, description="AI-generated review summary")


class WebMetadata(BaseModel):
    """Metadata for web output."""

    destination: str
    source: str
    generated_at: str
    budget: int
    total_hotels: int


class WebOutput(BaseModel):
    """Complete web output structure."""

    metadata: WebMetadata
    hotels: list[WebHotel]


# CLI types
Destination = Literal["cancun", "punta-cana", "riviera-maya"]
Source = Literal["transat", "expedia", "sunwing"]
SortBy = Literal["price", "rating", "reviews", "stars"]
