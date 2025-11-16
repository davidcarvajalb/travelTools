<template>
  <v-app>
    <v-main>
      <div class="page-container">
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
              <v-select
                id="destination"
                v-model="destination"
                :items="destinationOptions"
                data-test="destination-input"
                :disabled="loading"
                variant="outlined"
                density="comfortable"
                placeholder="Choose destination"
                hide-details
              />
            </div>
            <div class="select-wrapper">
              <label for="source">Source slug</label>
              <v-select
                id="source"
                v-model="source"
                :items="sourceOptions"
                data-test="source-input"
                :disabled="loading"
                variant="outlined"
                density="comfortable"
                placeholder="Choose source"
                hide-details
              />
            </div>
            <div class="load-button">
              <label>&nbsp;</label>
              <v-btn
                color="primary"
                class="w-100"
                type="submit"
                data-test="load-button"
                :disabled="loading || !destination || !source"
              >
                {{ loading ? "Loading…" : "Load Hotels" }}
              </v-btn>
            </div>
          </form>
          <p class="status-banner" v-if="!metadata">
            Example path: <code>outputs/cancun/transat/hotels.json</code>
          </p>
          <p class="error" v-if="errorMessage" data-test="error-message">
            {{ errorMessage }}
          </p>
        </section>

        <v-card
          v-if="metadata"
          class="filters-card card"
          :loading="loading"
          data-test="filters-card"
          elevation="4"
        >
          <v-card-title class="filters-header">
            <div>
              <p class="muted overline">Filters</p>
              <h2>Fine-tune your stay</h2>
            </div>
            <div class="muted filters-count">
              Showing {{ hotelCount }} of {{ metadata.total_hotels }} hotels
            </div>
          </v-card-title>
          <v-card-text>
            <div class="filters-grid filters-grid--form">
              <div>
                <v-text-field
                  v-model="filters.search"
                  data-test="search-input"
                  label="Search hotel name"
                  placeholder="Dreams, Iberostar..."
                  prepend-inner-icon="mdi-magnify"
                  :disabled="loading || !hasFiltersEnabled"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                />
              </div>
              <div>
                <v-select
                  v-model.number="filters.minRating"
                  data-test="rating-select"
                  label="Minimum rating"
                  :items="ratingSelectItems"
                  item-title="title"
                  item-value="value"
                  :disabled="loading || !hasFiltersEnabled"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                />
              </div>
              <div>
                <v-text-field
                  v-model.number="filters.price.min"
                  data-test="price-min"
                  label="Price min (CAD)"
                  type="number"
                  :disabled="loading || !hasFiltersEnabled"
                  @blur="normalizePriceRange"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                />
              </div>
              <div>
                <v-text-field
                  v-model.number="filters.price.max"
                  data-test="price-max"
                  label="Price max (CAD)"
                  type="number"
                  :disabled="loading || !hasFiltersEnabled"
                  @blur="normalizePriceRange"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                />
              </div>
              <div>
                <div class="checkbox-label">Adults only</div>
                <v-checkbox-group
                  v-model="filters.adultOnly"
                  class="checkbox-group"
                  :disabled="loading || !hasFiltersEnabled"
                >
                  <v-checkbox
                    v-for="option in adultOnlyOptions"
                    :key="option"
                    :label="adultOnlyLabel(option)"
                    :value="option"
                    hide-details
                    density="comfortable"
                    :data-test="`adult-checkbox-${option}`"
                  />
                </v-checkbox-group>
              </div>
            </div>
            <p class="filters-note">
              Prices shown in CAD · Available range:
              {{ formatCurrency(priceBounds.min) }} — {{ formatCurrency(priceBounds.max) }}
            </p>
            <div class="filters-actions">
              <v-btn
                variant="text"
                color="primary"
                data-test="reset-filters"
                @click="resetFilters"
                :disabled="loading || !hasFiltersEnabled"
              >
                Reset Filters
              </v-btn>
            </div>
          </v-card-text>
        </v-card>

        <section v-if="metadata" class="card table-card">
          <div class="table-wrapper" v-if="filteredHotels.length">
            <table>
              <thead>
                <tr>
                  <th @click="changeSort('name')" data-test="sort-name">Hotel</th>
                  <th @click="changeSort('stars')" data-test="sort-stars">Stars</th>
                  <th @click="changeSort('rating')" data-test="sort-rating">Rating</th>
                  <th @click="changeSort('reviews')" data-test="sort-reviews">Reviews</th>
                  <th @click="changeSort('price')" data-test="sort-price">Min Price (CAD)</th>
                  <th>Max Price (CAD)</th>
                  <th>Air Transat</th>
                  <th>Google Maps</th>
                  <th>AI Summary</th>
                  <th>Adults Only</th>
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
                      {{ formatCurrency(hotel.price_range.min) }}
                    </td>
                    <td>{{ formatCurrency(hotel.price_range.max) }}</td>
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
                    <td>
                      <v-btn
                        v-if="hasReviewSummary(hotel)"
                        variant="tonal"
                        color="primary"
                        size="small"
                        @click="openSummary(hotel)"
                        data-test="ai-summary-btn"
                      >
                        ✨ AI Summary
                      </v-btn>
                      <span
                        v-else
                        class="wip-pill"
                        aria-label="AI summary in progress"
                        data-test="summary-wip"
                      >
                        ⏳ WIP
                      </span>
                    </td>
                    <td>{{ formatAdultOnly(hotel.adult_only) }}</td>
                    <td>
                      <v-btn
                        variant="outlined"
                        color="primary"
                        size="small"
                        @click="togglePackages(hotel.id)"
                        data-test="package-toggle"
                      >
                        {{ isExpanded(hotel.id) ? "Hide" : "Show" }} ({{ hotel.package_count }})
                      </v-btn>
                    </td>
                  </tr>
                  <tr v-if="isExpanded(hotel.id)">
                    <td colspan="11">
                      <div class="packages" data-test="package-list">
                        <article
                          v-for="pkg in hotel.packages"
                          :key="pkg.departure + pkg.return"
                          class="package-card"
                        >
                          <div class="package-dates">
                            <div><strong>Departure:</strong> {{ formatDate(pkg.departure) }}</div>
                            <div><strong>Return:</strong> {{ formatDate(pkg.return) }}</div>
                            <div><strong>Duration:</strong> {{ pkg.duration_days }} nights</div>
                          </div>
                          <div class="package-meta">
                            <span><strong>Room:</strong> {{ pkg.room_type }}</span>
                            <span><strong>Price:</strong> {{ formatCurrency(pkg.price) }}</span>
                            <span><strong>24h Drinks:</strong> {{ formatBinary(pkg.drinks24h) }}</span>
                            <span><strong>24h Snacks:</strong> {{ formatBinary(pkg.snacks24h) }}</span>
                          </div>
                          <div class="package-actions">
                            <a
                              v-if="pkg.url"
                              :href="pkg.url"
                              target="_blank"
                              rel="noopener"
                              class="link"
                            >
                              View Package
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

        <v-dialog
          v-model="summaryDialogVisible"
          max-width="720"
          data-test="summary-dialog"
          scrollable
        >
          <v-card class="summary-modal">
            <v-card-title>
              <div class="summary-header">
                <div>
                  <p class="muted overline">AI Summary</p>
                  <h3 class="summary-title">{{ summaryHotel?.name ?? "No hotel selected" }}</h3>
                  <p class="muted">{{ summaryHotel?.city }}</p>
                </div>
                <div class="muted powered-by">🤖 Powered by Google Gemini</div>
              </div>
            </v-card-title>
            <v-card-text>
              <div v-if="activeSummary" class="summary-body">
                <div class="summary-section">
                  <h4>✅ The Good</h4>
                  <div class="badge-grid" v-if="activeSummary.good_points.length">
                    <span v-for="point in activeSummary.good_points" :key="point" class="badge badge-good">
                      {{ point }}
                    </span>
                  </div>
                  <p v-else class="muted">No positive highlights available.</p>
                </div>

                <div class="summary-section">
                  <h4>⚠️ The Bad</h4>
                  <div class="badge-grid" v-if="activeSummary.bad_points.length">
                    <span v-for="point in activeSummary.bad_points" :key="point" class="badge badge-bad">
                      {{ point }}
                    </span>
                  </div>
                  <p v-else class="muted">No notable complaints reported.</p>
                </div>

                <div class="summary-section">
                  <h4>💀 The Ugly</h4>
                  <div class="badge-grid" v-if="activeSummary.ugly_points.length">
                    <span v-for="point in activeSummary.ugly_points" :key="point" class="badge badge-ugly">
                      {{ point }}
                    </span>
                  </div>
                  <p v-else class="muted">No deal-breakers identified.</p>
                </div>

                <div class="summary-section overall">
                  <h4>📝 Overall</h4>
                  <p>{{ activeSummary.overall_summary }}</p>
                  <p class="muted small">
                    Reviews analyzed: {{ activeSummary.review_count_analyzed }}
                  </p>
                </div>
              </div>
              <div v-else class="muted">
                No AI summary available for this hotel yet.
              </div>
            </v-card-text>
          </v-card>
        </v-dialog>
      </div>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import type {
  AdultOnlyFilter,
  FilterState,
  SortKey,
  WebHotel,
  WebMetadata,
  WebOutput
} from "./types";
import {
  formatAdultOnly,
  formatBinary,
  formatCurrency,
  formatDate,
  formatNumber,
  formatRating
} from "./utils/format";
import { hasReviewSummary } from "./types";

const destinationOptions = ["cancun", "punta-cana"];
const sourceOptions = ["transat"];

const destination = ref(destinationOptions[1]);
const source = ref(sourceOptions[0]);
const hotels = ref<WebHotel[]>([]);
const metadata = ref<WebMetadata | null>(null);
const loading = ref(false);
const errorMessage = ref("");
const hasFetched = ref(false);
const expandedHotels = ref<Set<string>>(new Set());
const summaryDialogVisible = ref(false);
const summaryHotel = ref<WebHotel | null>(null);

const filters = reactive<FilterState>({
  search: "",
  minRating: 0,
  price: {
    min: 0,
    max: 0
  },
  adultOnly: [],
  sortKey: "name",
  sortDirection: "asc"
});

const priceBounds = ref({ min: 0, max: 0 });

const ratingOptions = computed(() => {
  const values = Array.from(
    new Set(
      hotels.value
        .map((hotel) => hotel.google_rating)
        .filter((value): value is number => typeof value === "number")
        .map((rating) => Number(rating.toFixed(1)))
    )
  ).sort((a, b) => a - b);
  return values;
});

const ratingSelectItems = computed(() => [
  { title: "All ratings", value: 0 },
  ...ratingOptions.value.map((rating) => ({
    title: `${rating.toFixed(1)}+`,
    value: rating
  }))
]);

const adultOnlyOptions = computed<AdultOnlyFilter[]>(() => {
  const values = Array.from(
    new Set(
      hotels.value
        .map((hotel) => mapAdultOnly(hotel.adult_only))
        .filter((value): value is AdultOnlyFilter => value !== null && value !== "any")
    )
  );
  if (!values.length) {
    return ["yes", "no", "maybe"];
  }
  const order: AdultOnlyFilter[] = ["yes", "no", "maybe"];
  return values.sort((a, b) => order.indexOf(a) - order.indexOf(b));
});

const hasFiltersEnabled = computed(() => hotels.value.length > 0);
const activeSummary = computed(() =>
  summaryHotel.value && hasReviewSummary(summaryHotel.value)
    ? summaryHotel.value.review_summary
    : null
);

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

  if (filters.adultOnly.length) {
    result = result.filter((hotel) => {
      const mapped = mapAdultOnly(hotel.adult_only);
      return mapped ? filters.adultOnly.includes(mapped) : false;
    });
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
    filters.adultOnly = [];
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
}

function resetFilters(): void {
  filters.search = "";
  filters.minRating = 0;
  filters.adultOnly = [];
  filters.sortKey = "name";
  filters.sortDirection = "asc";
  updateFilterBounds(hotels.value);
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

function openSummary(hotel: WebHotel): void {
  summaryHotel.value = hotel;
  summaryDialogVisible.value = true;
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
    const message =
      error instanceof Error ? error.message : "Unknown error occurred";
    errorMessage.value = message;
  } finally {
    loading.value = false;
  }
}

loadHotels();

function mapAdultOnly(value: number | null | undefined): AdultOnlyFilter | null {
  if (value === null || value === undefined) return null;
  if (Number.isNaN(value)) return null;
  if (value === 1) return "yes";
  if (value === 0) return "no";
  return "maybe";
}

function adultOnlyLabel(option: AdultOnlyFilter): string {
  if (option === "yes") return "Yes";
  if (option === "no") return "No";
  if (option === "maybe") return "Maybe";
  return "Any";
}
</script>
