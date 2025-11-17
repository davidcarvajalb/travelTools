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
          <div class="filters-grid">
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
                @update:model-value="loadHotels"
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
                @update:model-value="loadHotels"
              />
            </div>
          </div>
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
                <v-checkbox
                  v-model="filters.requireAdultsOnly"
                  :label="`Adults only`"
                  :disabled="loading || !hasFiltersEnabled"
                  density="comfortable"
                  hide-details
                  data-test="adult-checkbox"
                />
              </div>
              <div>
                <v-checkbox
                  v-model="filters.requireDrinks24h"
                  :label="labels.drinks24h"
                  :disabled="loading || !hasFiltersEnabled"
                  density="comfortable"
                  hide-details
                  data-test="drinks-checkbox"
                />
              </div>
              <div>
                <v-checkbox
                  v-model="filters.requireSnacks24h"
                  :label="labels.snacks24h"
                  :disabled="loading || !hasFiltersEnabled"
                  density="comfortable"
                  hide-details
                  data-test="snacks-checkbox"
                />
              </div>
              <div>
                <v-checkbox
                  v-model="filters.requireSpa"
                  :label="labels.spaAvailable"
                  :disabled="loading || !hasFiltersEnabled"
                  density="comfortable"
                  hide-details
                  data-test="spa-checkbox"
                />
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
          <div class="column-chooser">
            <div class="checkbox-label">Table columns</div>
            <div class="column-chooser__options">
              <v-checkbox
                v-for="col in columnOptions"
                :key="col.key"
                :model-value="isColumnVisible(col.key)"
                @update:model-value="toggleColumn(col.key)"
                :label="col.label"
                density="compact"
                hide-details
                color="primary"
                :data-test="`col-${col.key}`"
              />
            </div>
          </div>
          <div class="table-wrapper" v-if="filteredHotels.length">
            <table>
              <thead>
                <tr>
                  <th @click="changeSort('name')" data-test="sort-name">Hotel</th>
                  <th
                    v-if="isColumnVisible('stars')"
                    @click="changeSort('stars')"
                    data-test="sort-stars"
                  >
                    Stars
                  </th>
                  <th
                    v-if="isColumnVisible('rating')"
                    @click="changeSort('rating')"
                    data-test="sort-rating"
                  >
                    Rating
                  </th>
                  <th
                    v-if="isColumnVisible('reviews')"
                    @click="changeSort('reviews')"
                    data-test="sort-reviews"
                  >
                    Reviews
                  </th>
                  <th
                    v-if="isColumnVisible('price_min')"
                    @click="changeSort('price')"
                    data-test="sort-price"
                  >
                    Min Price (CAD)
                  </th>
                  <th v-if="isColumnVisible('price_max')">Max Price (CAD)</th>
                  <th v-if="isColumnVisible('air_transat')">Air Transat</th>
                  <th v-if="isColumnVisible('google_maps')">Google Maps</th>
                  <th v-if="isColumnVisible('summary')">AI Summary</th>
                  <th v-if="isColumnVisible('drinks24h')">{{ labels.drinks24h }}</th>
                  <th v-if="isColumnVisible('snacks24h')">{{ labels.snacks24h }}</th>
                  <th v-if="isColumnVisible('restaurants')">{{ labels.restaurants }}</th>
                  <th v-if="isColumnVisible('spa')">{{ labels.spaAvailable }}</th>
                  <th v-if="isColumnVisible('meal_plan')">{{ labels.mealPlan }}</th>
                  <th v-if="isColumnVisible('adult_only')">Adults Only</th>
                  <th v-if="isColumnVisible('packages')">Packages</th>
                  <th v-if="isColumnVisible('thumbnail')">{{ labels.thumbnail }}</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="hotel in filteredHotels" :key="hotel.id">
                  <tr data-test="hotel-row">
                    <td>
                      <strong>{{ hotel.name }}</strong>
                      <div class="muted">{{ hotel.city }}</div>
                    </td>
                    <td v-if="isColumnVisible('stars')">{{ hotel.stars ?? "—" }}</td>
                    <td v-if="isColumnVisible('rating')">{{ formatRating(hotel.google_rating) }}</td>
                    <td v-if="isColumnVisible('reviews')">{{ formatNumber(hotel.review_count) }}</td>
                    <td v-if="isColumnVisible('price_min')">
                      {{ formatCurrency(hotel.price_range.min) }}
                    </td>
                    <td v-if="isColumnVisible('price_max')">{{ formatCurrency(hotel.price_range.max) }}</td>
                    <td v-if="isColumnVisible('air_transat')">
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
                    <td v-if="isColumnVisible('google_maps')">
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
                    <td v-if="isColumnVisible('summary')">
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
                    <td v-if="isColumnVisible('drinks24h')">{{ formatBinary(hotel.drinks24h) }}</td>
                    <td v-if="isColumnVisible('snacks24h')">{{ formatBinary(hotel.snacks24h) }}</td>
                    <td v-if="isColumnVisible('restaurants')">
                      {{ hotel.number_of_restaurants ?? labels.unknown }}
                    </td>
                    <td v-if="isColumnVisible('spa')">
                      {{ hotel.spa_available ?? labels.unknown }}
                    </td>
                    <td v-if="isColumnVisible('meal_plan')">
                      {{ formatMealPlan(hotel.meal_plan_code, hotel.meal_plan_label) }}
                    </td>
                    <td v-if="isColumnVisible('adult_only')">{{ formatAdultOnly(hotel.adult_only) }}</td>
                    <td v-if="isColumnVisible('packages')">
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
                    <td v-if="isColumnVisible('thumbnail')">
                      <v-img
                        v-if="hotel.thumbnail_url"
                        :src="hotel.thumbnail_url"
                        height="80"
                        width="120"
                        cover
                        class="thumbnail"
                      />
                      <span v-else>{{ labels.unknown }}</span>
                    </td>
                  </tr>
                  <tr v-if="isExpanded(hotel.id)">
                    <td :colspan="visibleColumns.length + 1">
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
                            <ul class="stacked">
                              <li><strong>Room:</strong> {{ pkg.room_type }}</li>
                              <li><strong>Meal plan:</strong> {{ formatMealPlan(pkg.meal_plan_code, pkg.meal_plan_label) }}</li>
                              <li><strong>Price:</strong> {{ formatCurrency(pkg.price) }}</li>
                              <li><strong>{{ labels.drinks24h }}:</strong> {{ formatBinary(pkg.drinks24h) }}</li>
                              <li><strong>{{ labels.snacks24h }}:</strong> {{ formatBinary(pkg.snacks24h) }}</li>
                              <li><strong>{{ labels.restaurants }}:</strong> {{ pkg.number_of_restaurants ?? labels.unknown }}</li>
                              <li><strong>{{ labels.spaAvailable }}:</strong> {{ pkg.spa_available ?? labels.unknown }}</li>
                            </ul>
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
                            <v-img
                              v-if="pkg.thumbnail_url"
                              :src="pkg.thumbnail_url"
                              height="120"
                              width="180"
                              cover
                              class="thumbnail"
                            />
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
  WebOutput,
  ColumnKey,
  TriState,
  SpaFilter
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

const labels: Record<string, string> = {
  filtersTitle: "Filters",
  fineTune: "Fine-tune your stay",
  drinks24h: "24h Drinks",
  snacks24h: "24h Snacks",
  spaAvailable: "Spa",
  mealPlan: "Meal plan",
  restaurants: "Restaurants",
  thumbnail: "Thumbnail",
  unknown: "Unknown",
  yes: "Yes",
  no: "No"
};

const destinationOptions = ["cancun", "punta-cana", "riviera-maya"];
const sourceOptions = ["transat"];

const destination = ref(destinationOptions[0]);
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
  requireDrinks24h: false,
  requireSnacks24h: false,
  requireSpa: false,
  requireAdultsOnly: false,
  sortKey: "name",
  sortDirection: "asc"
});

const visibleColumns = ref<ColumnKey[]>([
  "stars",
  "rating",
  "reviews",
  "price_min",
  "price_max",
  "air_transat",
  "google_maps",
  "summary",
  "adult_only",
  "packages",
  // leave the rest optional by default
]);

const priceBounds = ref({ min: 0, max: 0 });

const columnOptions = computed(() => [
  { key: "stars", label: "Stars" },
  { key: "rating", label: "Rating" },
  { key: "reviews", label: "Reviews" },
  { key: "price_min", label: "Min Price" },
  { key: "price_max", label: "Max Price" },
  { key: "air_transat", label: "Air Transat" },
  { key: "google_maps", label: "Google Maps" },
  { key: "summary", label: "AI Summary" },
  { key: "adult_only", label: "Adults Only" },
  { key: "packages", label: "Packages" },
  { key: "drinks24h", label: labels.drinks24h },
  { key: "snacks24h", label: labels.snacks24h },
  { key: "restaurants", label: labels.restaurants },
  { key: "spa", label: labels.spaAvailable },
  { key: "meal_plan", label: labels.mealPlan },
  { key: "thumbnail", label: labels.thumbnail }
]);

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

  if (filters.requireDrinks24h) {
    result = result.filter((hotel) => mapTriBool(hotel.drinks24h) === "yes");
  }

  if (filters.requireSnacks24h) {
    result = result.filter((hotel) => mapTriBool(hotel.snacks24h) === "yes");
  }

  if (filters.requireSpa) {
    result = result.filter((hotel) => mapSpa(hotel.spa_available) === "yes");
  }

  if (filters.requireAdultsOnly) {
    result = result.filter((hotel) => mapAdultOnly(hotel.adult_only) === "yes");
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
  filters.requireDrinks24h = false;
  filters.requireSnacks24h = false;
  filters.requireSpa = false;
  filters.requireAdultsOnly = false;
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

function isColumnVisible(key: ColumnKey): boolean {
  return visibleColumns.value.includes(key);
}

function toggleColumn(key: ColumnKey): void {
  if (visibleColumns.value.includes(key)) {
    visibleColumns.value = visibleColumns.value.filter((k) => k !== key);
    return;
  }
  visibleColumns.value = [...visibleColumns.value, key];
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

function mapTriBool(value: boolean | null | undefined): TriState {
  if (value === true) return "yes";
  if (value === false) return "no";
  return "unknown";
}

function mapSpa(value: string | number | null | undefined): SpaFilter {
  if (value === null || value === undefined || value === "") return "unknown";
  if (typeof value === "number") {
    if (value === 0) return "no";
    if (value > 0) return "yes";
    return "unknown";
  }
  const normalized = value.toString().trim().toLowerCase();
  if (["no", "not available", "none", "n"].includes(normalized)) return "no";
  return "yes";
}

function formatMealPlan(code?: string | null, label?: string | null): string {
  if (label) return label;
  if (code) return code;
  return labels.unknown;
}
</script>
