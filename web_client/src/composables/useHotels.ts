import { ref, computed, watch } from 'vue';
import type { WebOutput, WebHotel, FilterState, SortKey, SortDirection, PriceRange } from '../types';
import { hasReviewSummary } from '../types';

export function useHotels() {
  const hotels = ref<WebHotel[]>([]);
  const metadata = ref<WebOutput['metadata'] | null>(null);
  const loading = ref(false);
  const errorMessage = ref('');
  const destination = ref('cancun');
  const destinationSource = ref('transat');

  // Filters
  const filters = ref<FilterState>({
    search: '',
    minRating: 0,
    price: { min: 0, max: 10000 },
    requireDrinks24h: false,
    requireSnacks24h: false,
    requireSpa: false,
    requireAdultsOnly: false,
    sortKey: 'price',
    sortDirection: 'asc',
  });

  const priceBounds = ref<PriceRange>({ min: 0, max: 10000, avg: 0 });

  const loadData = async () => {
    loading.value = true;
    errorMessage.value = '';
    try {
      // In a real app, this might be an API call. 
      // For this viewer, we're loading static JSON files.
      const basePath = import.meta.env.DEV ? '/outputs' : '';
      const response = await fetch(
        `${basePath}/${destination.value}/${destinationSource.value}/hotels.json`
      );
      if (!response.ok) {
        throw new Error(`Unable to load hotels (${response.status})`);
      }
      const data: WebOutput = await response.json();
      hotels.value = data.hotels;
      metadata.value = data.metadata;

      // Calculate price bounds
      if (hotels.value.length > 0) {
        const prices = hotels.value.map((h) => h.price_range.min);
        priceBounds.value = {
          min: Math.min(...prices),
          max: Math.max(...prices),
          avg: prices.reduce((a, b) => a + b, 0) / prices.length,
        };
        // Set initial max price filter to max found
        filters.value.price.max = priceBounds.value.max;
        filters.value.price.min = priceBounds.value.min;
      }
    } catch (e) {
      console.error(e);
      errorMessage.value = e instanceof Error ? e.message : 'Unknown error';
      hotels.value = [];
      metadata.value = null;
    } finally {
      loading.value = false;
    }
  };

  const filteredHotels = computed(() => {
    let result = [...hotels.value];

    // Text Search
    if (filters.value.search) {
      const q = filters.value.search.toLowerCase();
      result = result.filter((h) => h.name.toLowerCase().includes(q));
    }

    // Price
    result = result.filter(
      (h) =>
        h.price_range.min >= filters.value.price.min &&
        h.price_range.min <= filters.value.price.max
    );

    // Rating
    if (filters.value.minRating > 0) {
      result = result.filter((h) => (h.stars ?? 0) >= filters.value.minRating);
    }

    // Amenities
    if (filters.value.requireDrinks24h) {
      result = result.filter((h) => h.drinks24h);
    }
    if (filters.value.requireSnacks24h) {
      result = result.filter((h) => h.snacks24h);
    }
    if (filters.value.requireSpa) {
      result = result.filter((h) => {
        if (typeof h.spa_available === 'number') return h.spa_available > 0;
        if (typeof h.spa_available === 'string')
          return h.spa_available.toLowerCase() === 'yes';
        return false;
      });
    }
    if (filters.value.requireAdultsOnly) {
      result = result.filter((h) => h.adult_only === 1);
    }

    // Sorting
    result.sort((a, b) => {
      let valA: number | string = 0;
      let valB: number | string = 0;

      switch (filters.value.sortKey) {
        case 'price':
          valA = a.price_range.min;
          valB = b.price_range.min;
          break;
        case 'stars':
          valA = a.stars ?? 0;
          valB = b.stars ?? 0;
          break;
        case 'rating':
          valA = a.google_rating ?? 0;
          valB = b.google_rating ?? 0;
          break;
        case 'reviews':
          valA = a.review_count ?? 0;
          valB = b.review_count ?? 0;
          break;
        case 'name':
          valA = a.name;
          valB = b.name;
          break;
      }

      if (valA < valB) return filters.value.sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return filters.value.sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  });

  const hotelCount = computed(() => filteredHotels.value.length);

  const hasFiltersEnabled = computed(() => {
    return (
      filters.value.search !== '' ||
      filters.value.minRating > 0 ||
      filters.value.requireDrinks24h ||
      filters.value.requireSnacks24h ||
      filters.value.requireSpa ||
      filters.value.requireAdultsOnly ||
      filters.value.price.min > priceBounds.value.min ||
      filters.value.price.max < priceBounds.value.max
    );
  });

  const resetFilters = () => {
    filters.value.search = '';
    filters.value.minRating = 0;
    filters.value.requireDrinks24h = false;
    filters.value.requireSnacks24h = false;
    filters.value.requireSpa = false;
    filters.value.requireAdultsOnly = false;
    filters.value.price.min = priceBounds.value.min;
    filters.value.price.max = priceBounds.value.max;
  };

  watch([destination, destinationSource], () => {
    loadData();
  });

  return {
    hotels,
    metadata,
    loading,
    errorMessage,
    destination,
    destinationSource,
    filters,
    priceBounds,
    filteredHotels,
    hotelCount,
    hasFiltersEnabled,
    loadData,
    resetFilters,
  };
}
