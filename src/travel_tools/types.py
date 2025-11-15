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
    url: str | None = None
    drinks24h: bool = False
    snacks24h: bool = False
    adult_only: int | None = None
    amenities: list[str] = Field(default_factory=list)
    price: float
    dates: PackageDates


# Step 2: Scraped data
class GoogleRating(BaseModel):
    """Google Maps rating data."""

    hotel_name: str
    rating: float | None = None
    review_count: int | None = None


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
    departure_date: str | None = None
    return_date: str | None = None
    source: str  # 'transat', 'expedia', etc.
    price_range: PriceRange
    packages: list[HotelPackage]


# Step 4: Web output format
class WebPackage(BaseModel):
    """Package data formatted for web viewer."""
    model_config = ConfigDict(populate_by_name=True)

    departure: str
    return_date: str = Field(alias="return")
    duration_days: int
    room_type: str
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
    departure_date: str | None = None
    return_date: str | None = None
    price_range: PriceRange
    package_count: int
    packages: list[WebPackage]


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
