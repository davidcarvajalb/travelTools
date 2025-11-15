<template>
  <section class="card hero">
    <div>
      <h1>Travel Tools Viewer</h1>
      <p v-if="metadata">
        {{ destinationLabel }} · Source: {{ metadata.source }} · Budget:
        {{ budgetLabel }} · Generated: {{ generatedLabel }}
      </p>
      <p v-else>
        Load processed hotel data from
        <code>outputs/&lt;destination&gt;/&lt;source&gt;/hotels.json</code>.
      </p>
    </div>
    <form class="filters-grid" @submit.prevent="loadHotels">
      <div class="select-wrapper">
        <label for="destination">Destination slug</label>
        <el-select
          id="destination"
          v-model="destination"
          filterable
          placeholder="Choose destination"
          data-test="destination-input"
          :disabled="loading"
        >
          <el-option
            v-for="option in destinationOptions"
            :key="option"
            :label="option"
            :value="option"
          />
        </el-select>
      </div>
      <div class="select-wrapper">
        <label for="source">Source slug</label>
        <el-select
          id="source"
          v-model="source"
          filterable
          placeholder="Choose source"
          data-test="source-input"
          :disabled="loading"
        >
          <el-option
            v-for="option in sourceOptions"
            :key="option"
            :label="option"
            :value="option"
          />
        </el-select>
      </div>
      <div>
        <label>&nbsp;</label>
        <button
          class="primary"
          type="submit"
          data-test="load-button"
          :disabled="loading || !destination || !source"
        >
          {{ loading ? "Loading…" : "Load Hotels" }}
        </button>
      </div>
    </form>
    <p class="status-banner" v-if="!metadata">
      Example path: <code>outputs/cancun/transat/hotels.json</code>
    </p>
    <p class="error" v-if="errorMessage" data-test="error-message">
      {{ errorMessage }}
    </p>
  </section>

  <section
    v-if="metadata"
    class="card filters-card"
    :class="{ loading: loading }"
    data-test="filters-card"
  >
    <h2>Filters</h2>
    <div class="filters-grid">
      <div>
        <label for="search">Search hotel name</label>
        <input
          id="search"
          v-model="filters.search"
          data-test="search-input"
          placeholder="Dreams, Iberostar..."
          :disabled="loading || !hasFiltersEnabled"
        />
      </div>
      <div>
        <label for="rating">Minimum rating</label>
        <select
          id="rating"
          v-model.number="filters.minRating"
          data-test="rating-select"
          :disabled="loading || !hasFiltersEnabled"
        >
          <option value="0">All ratings</option>
          <option v-for="rating in ratingSteps" :key="rating" :value="rating">
            {{ rating }}+
          </option>
        </select>
      </div>
      <div>
        <label>Price range (USD)</label>
        <div class="filters-grid">
          <input
            type="number"
            v-model.number="filters.price.min"
            data-test="price-min"
            :disabled="loading || !hasFiltersEnabled"
            @blur="normalizePriceRange"
          />
          <input
            type="number"
            v-model.number="filters.price.max"
            data-test="price-max"
            :disabled="loading || !hasFiltersEnabled"
            @blur="normalizePriceRange"
          />
        </div>
        <small>
          Min: {{ formatCurrency(priceBounds.min) }} · Max: {{ formatCurrency(priceBounds.max) }}
        </small>
      </div>
      <div>
        <label>Stars</label>
        <div class="chips">
          <button
            v-for="star in availableStars"
            :key="star"
            type="button"
            class="chip"
            :class="{ active: filters.stars.includes(star) }"
            @click="toggleStar(star)"
            :disabled="loading || !hasFiltersEnabled"
          >
            {{ star }}★
          </button>
        </div>
      </div>
    </div>
    <div class="filters-actions">
      <button
        class="secondary"
        type="button"
        data-test="reset-filters"
        @click="resetFilters"
        :disabled="loading || !hasFiltersEnabled"
      >
        Reset Filters
      </button>
      <span>Showing {{ hotelCount }} of {{ metadata.total_hotels }} hotels</span>
    </div>
  </section>

  <section v-if="metadata" class="card table-card">
    <div class="table-wrapper" v-if="filteredHotels.length">
      <table>
        <thead>
          <tr>
            <th @click="changeSort('name')" data-test="sort-name">Hotel</th>
            <th @click="changeSort('stars')" data-test="sort-stars">Stars</th>
            <th @click="changeSort('rating')" data-test="sort-rating">Rating</th>
            <th @click="changeSort('reviews')" data-test="sort-reviews">Reviews</th>
            <th @click="changeSort('price')" data-test="sort-price">Price Range</th>
            <th>Air Transat</th>
            <th>Google Maps</th>
            <th>24h Drinks</th>
            <th>24h Snacks</th>
            <th>Departure</th>
            <th>Return</th>
            <th>Packages</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="hotel in filteredHotels" :key="hotel.id">
            <tr data-test="hotel-row">
              <td>
                <strong>{{ hotel.name }}</strong>
                <div class="muted">{{ hotel.city }}</div>
              </td>
              <td>{{ hotel.stars ?? "—" }}</td>
              <td>{{ formatRating(hotel.google_rating) }}</td>
              <td>{{ formatNumber(hotel.review_count) }}</td>
              <td>
                {{ formatCurrency(hotel.price_range.min) }} –
                {{ formatCurrency(hotel.price_range.max) }}
              </td>
              <td>
                <a
                  v-if="hotel.air_transat_url"
                  :href="hotel.air_transat_url"
                  target="_blank"
                  rel="noopener"
                  class="link"
                >
                  Open
                </a>
                <span v-else>—</span>
              </td>
              <td>
                <a
                  v-if="hotel.google_maps_url"
                  :href="hotel.google_maps_url"
                  target="_blank"
                  rel="noopener"
                  class="link"
                >
                  Maps
                </a>
                <span v-else>—</span>
              </td>
              <td>{{ formatBinary(hotel.drinks24h) }}</td>
              <td>{{ formatBinary(hotel.snacks24h) }}</td>
              <td>{{ formatDate(hotel.departure_date ?? "") }}</td>
              <td>{{ formatDate(hotel.return_date ?? "") }}</td>
              <td>
                <button
                  type="button"
                  class="secondary"
                  @click="togglePackages(hotel.id)"
                  data-test="package-toggle"
                >
                  {{ isExpanded(hotel.id) ? "Hide" : "Show" }} ({{ hotel.package_count }})
                </button>
              </td>
            </tr>
            <tr v-if="isExpanded(hotel.id)">
              <td colspan="6">
                <div class="packages" data-test="package-list">
                  <article
                    v-for="pkg in hotel.packages"
                    :key="pkg.departure + pkg.return"
                    class="package-card"
                  >
                    <div>
                      <strong>{{ pkg.departure }}</strong> →
                      <strong>{{ pkg.return }}</strong>
                      <span>({{ pkg.duration_days }} nights)</span>
                    </div>
                    <div>{{ pkg.room_type }}</div>
                    <div>{{ formatCurrency(pkg.price) }}</div>
                    <div class="package-meta">
                      <span>Drinks 24h: {{ formatBinary(pkg.drinks24h) }}</span>
                      <span>Snacks 24h: {{ formatBinary(pkg.snacks24h) }}</span>
                      <a
                        v-if="pkg.url"
                        :href="pkg.url"
                        target="_blank"
                        rel="noopener"
                        class="link"
                      >
                        Air Transat
                      </a>
                    </div>
                  </article>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    <p v-else class="status-banner">
      No hotels match your filters. Try broadening the search.
    </p>
  </section>

  <section v-else-if="hasFetched && !loading" class="status-banner">
    Could not find data for that destination/source combination. Make sure
    <code>hotels.json</code> exists under the <code>outputs</code> directory.
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import type {
  FilterState,
  SortKey,
  WebHotel,
  WebMetadata,
  WebOutput
} from "./types";
import {
  formatBinary,
  formatCurrency,
  formatDate,
  formatNumber,
  formatRating
} from "./utils/format";

const destinationOptions = ["cancun", "punta-cana", "riviera-maya"];
const sourceOptions = ["transat", "expedia", "sunwing"];

const destination = ref(destinationOptions[0]);
const source = ref(sourceOptions[0]);
const hotels = ref<WebHotel[]>([]);
const metadata = ref<WebMetadata | null>(null);
const loading = ref(false);
const errorMessage = ref("");
const hasFetched = ref(false);
const expandedHotels = ref<Set<string>>(new Set());

const filters = reactive<FilterState>({
  search: "",
  minRating: 0,
  stars: [],
  price: {
    min: 0,
    max: 0
  },
  sortKey: "name",
  sortDirection: "asc"
});

const ratingSteps = [3.0, 3.5, 4.0, 4.5];
const priceBounds = ref({ min: 0, max: 0 });

const availableStars = computed(() => {
  const values = Array.from(
    new Set(
      hotels.value
        .map((hotel) => hotel.stars)
        .filter((value): value is number => typeof value === "number")
    )
  ).sort((a, b) => a - b);
  return values.length ? values : [3, 4, 5];
});

const hasFiltersEnabled = computed(() => hotels.value.length > 0);

const filteredHotels = computed(() => {
  let result = [...hotels.value];
  if (filters.search.trim()) {
    const search = filters.search.trim().toLowerCase();
    result = result.filter((hotel) =>
      hotel.name.toLowerCase().includes(search)
    );
  }

  if (filters.minRating > 0) {
    result = result.filter(
      (hotel) => (hotel.google_rating ?? 0) >= filters.minRating
    );
  }

  if (filters.stars.length) {
    result = result.filter((hotel) =>
      typeof hotel.stars === "number"
        ? filters.stars.includes(hotel.stars)
        : false
    );
  }

  result = result.filter(
    (hotel) =>
      hotel.price_range.min >= filters.price.min &&
      hotel.price_range.max <= filters.price.max
  );

  const direction = filters.sortDirection === "asc" ? 1 : -1;
  return result.sort((a, b) => {
    let comparison = 0;
    switch (filters.sortKey) {
      case "stars":
        comparison = (a.stars ?? 0) - (b.stars ?? 0);
        break;
      case "rating":
        comparison = (a.google_rating ?? 0) - (b.google_rating ?? 0);
        break;
      case "reviews":
        comparison = (a.review_count ?? 0) - (b.review_count ?? 0);
        break;
      case "price":
        comparison = a.price_range.min - b.price_range.min;
        break;
      default:
        comparison = a.name.localeCompare(b.name);
    }
    return comparison * direction;
  });
});

const hotelCount = computed(() => filteredHotels.value.length);
const budgetLabel = computed(() =>
  metadata.value ? formatCurrency(metadata.value.budget) : ""
);
const generatedLabel = computed(() =>
  metadata.value ? metadata.value.generated_at.slice(0, 10) : ""
);
const destinationLabel = computed(() =>
  metadata.value ? formatDestination(metadata.value.destination) : ""
);

function formatDestination(slug: string): string {
  return slug
    .split("-")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

function updateFilterBounds(data: WebHotel[]): void {
  if (!data.length) {
    filters.price.min = 0;
    filters.price.max = 0;
    filters.stars = [];
    priceBounds.value = { min: 0, max: 0 };
    return;
  }

  const pricePoints = data.flatMap((hotel) => [
    hotel.price_range.min,
    hotel.price_range.max
  ]);
  const minPrice = Math.floor(Math.min(...pricePoints));
  const maxPrice = Math.ceil(Math.max(...pricePoints));
  priceBounds.value = { min: minPrice, max: maxPrice };
  filters.price.min = minPrice;
  filters.price.max = maxPrice;

  const stars = Array.from(
    new Set(
      data
        .map((hotel) => hotel.stars)
        .filter((value): value is number => typeof value === "number")
    )
  ).sort((a, b) => a - b);
  filters.stars = stars.length ? stars : [];
}

function resetFilters(): void {
  filters.search = "";
  filters.minRating = 0;
  filters.sortKey = "name";
  filters.sortDirection = "asc";
  updateFilterBounds(hotels.value);
}

function toggleStar(star: number): void {
  if (filters.stars.includes(star)) {
    filters.stars = filters.stars.filter((value) => value !== star);
  } else {
    filters.stars = [...filters.stars, star];
  }
}

function changeSort(key: SortKey): void {
  if (filters.sortKey === key) {
    filters.sortDirection = filters.sortDirection === "asc" ? "desc" : "asc";
    return;
  }
  filters.sortKey = key;
  filters.sortDirection = key === "name" ? "asc" : "desc";
}

function normalizePriceRange(): void {
  if (filters.price.min < priceBounds.value.min) {
    filters.price.min = priceBounds.value.min;
  }
  if (filters.price.max > priceBounds.value.max) {
    filters.price.max = priceBounds.value.max;
  }
  if (filters.price.min > filters.price.max) {
    filters.price.max = filters.price.min;
  }
}

function isExpanded(id: string): boolean {
  return expandedHotels.value.has(id);
}

function togglePackages(id: string): void {
  const next = new Set(expandedHotels.value);
  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }
  expandedHotels.value = next;
}

async function loadHotels(): Promise<void> {
  if (!destination.value || !source.value) {
    errorMessage.value = "Please provide both destination and source slugs.";
    return;
  }

  loading.value = true;
  errorMessage.value = "";
  hasFetched.value = true;
  expandedHotels.value = new Set();

  try {
    const url = new URL(
      `${destination.value}/${source.value}/hotels.json`,
      `${window.location.origin}/`
    );
    const response = await fetch(url.toString(), { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Unable to load hotels (${response.status})`);
    }

    const payload = (await response.json()) as WebOutput;
    hotels.value = payload.hotels;
    metadata.value = payload.metadata;
    resetFilters();
  } catch (error) {
    hotels.value = [];
    metadata.value = null;
    filters.stars = [];
    const message =
      error instanceof Error ? error.message : "Unknown error occurred";
    errorMessage.value = message;
  } finally {
    loading.value = false;
  }
}
</script>
