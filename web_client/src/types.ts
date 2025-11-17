export interface Review {
  text: string;
  rating: number; // 1-5
  date: string;
  reviewer_name: string | null;
}

export interface ReviewSummary {
  good_points: string[];
  bad_points: string[];
  ugly_points: string[];
  overall_summary: string;
  review_count_analyzed: number;
}

export interface PriceRange {
  min: number;
  max: number;
  avg: number;
}

export interface WebPackage {
  departure: string;
  return: string;
  duration_days: number;
  room_type: string;
  meal_plan_code?: string | null;
  meal_plan_label?: string | null;
  number_of_restaurants?: number | null;
  spa_available?: string | null | number;
  thumbnail_url?: string | null;
  price: number;
  url?: string | null;
  drinks24h: boolean | null;
  snacks24h: boolean | null;
}

export interface WebHotel {
  id: string;
  name: string;
  city: string;
  stars: number | null;
  google_rating: number | null;
  review_count: number | null;
  air_transat_url?: string | null;
  google_maps_url?: string | null;
  drinks24h: boolean | null;
  snacks24h: boolean | null;
  adult_only?: number | null;
  number_of_restaurants?: number | null;
  spa_available?: string | null | number;
  meal_plan_code?: string | null;
  meal_plan_label?: string | null;
  thumbnail_url?: string | null;
  departure_date?: string | null;
  return_date?: string | null;
  price_range: PriceRange;
  package_count: number;
  packages: WebPackage[];
  review_summary?: ReviewSummary | null;
}

export interface WebMetadata {
  destination: string;
  source: string;
  generated_at: string;
  budget: number;
  total_hotels: number;
}

export interface WebOutput {
  metadata: WebMetadata;
  hotels: WebHotel[];
}

export type SortKey = "name" | "stars" | "rating" | "reviews" | "price";
export type SortDirection = "asc" | "desc";
export type AdultOnlyFilter = "any" | "yes" | "no" | "maybe";
export type TriState = "yes" | "no" | "unknown";
export type SpaFilter = TriState;
export type ColumnKey =
  | "name"
  | "stars"
  | "rating"
  | "reviews"
  | "price_min"
  | "price_max"
  | "air_transat"
  | "google_maps"
  | "summary"
  | "adult_only"
  | "packages"
  | "drinks24h"
  | "snacks24h"
  | "restaurants"
  | "spa"
  | "meal_plan"
  | "thumbnail";

export interface FilterState {
  search: string;
  minRating: number;
  price: {
    min: number;
    max: number;
  };
  requireDrinks24h: boolean;
  requireSnacks24h: boolean;
  requireSpa: boolean;
  requireAdultsOnly: boolean;
  sortKey: SortKey;
  sortDirection: SortDirection;
}

// Type guard functions
export function hasReviewSummary(hotel: WebHotel): hotel is WebHotel & { review_summary: ReviewSummary } {
  return hotel.review_summary !== null && hotel.review_summary !== undefined;
}

export function isValidReview(review: unknown): review is Review {
  if (typeof review !== 'object' || review === null) {
    return false;
  }

  const r = review as Review;
  return (
    typeof r.text === 'string' &&
    typeof r.rating === 'number' &&
    r.rating >= 1 &&
    r.rating <= 5 &&
    typeof r.date === 'string'
  );
}
