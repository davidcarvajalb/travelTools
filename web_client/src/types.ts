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
  departure_date?: string | null;
  return_date?: string | null;
  price_range: PriceRange;
  package_count: number;
  packages: WebPackage[];
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
