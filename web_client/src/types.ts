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
  price: number;
  url?: string | null;
  drinks24h: boolean;
  snacks24h: boolean;
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
  drinks24h: boolean;
  snacks24h: boolean;
  adult_only?: number | null;
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

export interface FilterState {
  search: string;
  minRating: number;
  stars: number[];
  price: {
    min: number;
    max: number;
  };
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
