<script setup lang="ts">
import { ref } from 'vue';
import type { WebHotel, WebOutput, SortKey, SortDirection, ColumnKey } from '../types';
import { hasReviewSummary } from '../types';

const props = defineProps<{
  hotels: WebHotel[];
  metadata: WebOutput['metadata'] | null;
  loading: boolean;
}>();

const sortKey = defineModel<SortKey>('sortKey', { required: true });
const sortDirection = defineModel<SortDirection>('sortDirection', { required: true });

const columns = ref<{ key: ColumnKey; label: string; sortable?: boolean; sortKey?: SortKey }[]>([
  { key: 'name', label: 'Hotel', sortable: true, sortKey: 'name' },
  { key: 'stars', label: 'Stars', sortable: true, sortKey: 'stars' },
  { key: 'rating', label: 'Rating', sortable: true, sortKey: 'rating' },
  { key: 'reviews', label: 'Reviews', sortable: true, sortKey: 'reviews' },
  { key: 'price_min', label: 'Price', sortable: true, sortKey: 'price' },
  { key: 'air_transat', label: 'Link' },
  { key: 'google_maps', label: 'Map' },
  { key: 'summary', label: 'AI Summary' },
  { key: 'adult_only', label: 'Adults' },
  { key: 'packages', label: 'Pkgs' },
  { key: 'drinks24h', label: 'Drinks' },
  { key: 'snacks24h', label: 'Snacks' },
  { key: 'restaurants', label: 'Rest.' },
  { key: 'spa', label: 'Spa' },
  { key: 'meal_plan', label: 'Meal' },
  { key: 'thumbnail', label: 'Img' },
]);

const selectedColumns = ref<ColumnKey[]>([
  'name',
  'stars',
  'rating',
  'reviews',
  'price_min',
  'summary',
  'adult_only',
  'drinks24h',
  'snacks24h',
  'thumbnail',
]);

const toggleSort = (key: SortKey) => {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDirection.value = 'asc';
  }
};

const getSortIcon = (key: SortKey) => {
  if (sortKey.value !== key) return 'mdi-sort';
  return sortDirection.value === 'asc' ? 'mdi-sort-ascending' : 'mdi-sort-descending';
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
    maximumFractionDigits: 0,
  }).format(value);
};

const getGoogleMapsUrl = (hotel: WebHotel) => {
  if (hotel.google_maps_url) return hotel.google_maps_url;
  const query = encodeURIComponent(`${hotel.name} ${hotel.city}`);
  return `https://www.google.com/maps/search/?api=1&query=${query}`;
};

const summaryDialogVisible = ref(false);
const selectedSummaryHotel = ref<WebHotel | null>(null);

const openSummary = (hotel: WebHotel) => {
  selectedSummaryHotel.value = hotel;
  summaryDialogVisible.value = true;
};
</script>

<template>
  <div v-if="metadata" class="h-100 d-flex flex-column">
    <div class="d-flex justify-end mb-2">
      <v-menu :close-on-content-click="false">
        <template v-slot:activator="{ props }">
          <v-btn
            color="secondary"
            variant="text"
            prepend-icon="mdi-table-cog"
            v-bind="props"
            size="small"
          >
            Columns
          </v-btn>
        </template>
        <v-card min-width="200" max-height="400" class="overflow-y-auto pa-2">
          <v-checkbox
            v-for="col in columns"
            :key="col.key"
            v-model="selectedColumns"
            :value="col.key"
            :label="col.label"
            density="compact"
            hide-details
            color="primary"
          />
        </v-card>
      </v-menu>
    </div>

    <v-card class="flex-grow-1 table-card" elevation="1">
      <div class="table-wrapper" v-if="hotels.length">
        <table>
          <thead>
            <tr>
              <th
                v-for="col in columns"
                :key="col.key"
                v-show="selectedColumns.includes(col.key)"
                :class="{ sortable: col.sortable }"
                @click="col.sortable && col.sortKey ? toggleSort(col.sortKey) : null"
              >
                <div class="th-content">
                  {{ col.label }}
                  <v-icon
                    v-if="col.sortable && col.sortKey"
                    :icon="getSortIcon(col.sortKey)"
                    size="small"
                    class="sort-icon"
                  />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="hotel in hotels" :key="hotel.id" data-test="hotel-row">
              <td v-if="selectedColumns.includes('name')" class="col-name">
                <div class="hotel-name">{{ hotel.name }}</div>
                <div class="hotel-city">{{ hotel.city }}</div>
              </td>
              <td v-if="selectedColumns.includes('stars')" class="col-stars">
                <v-rating
                  :model-value="hotel.stars ?? 0"
                  color="amber"
                  density="compact"
                  size="small"
                  readonly
                  half-increments
                />
              </td>
              <td v-if="selectedColumns.includes('rating')" class="col-rating">
                <div class="rating-badge" v-if="hotel.google_rating">
                  {{ hotel.google_rating }}
                </div>
                <span v-else class="muted">-</span>
              </td>
              <td v-if="selectedColumns.includes('reviews')" class="col-reviews">
                {{ hotel.review_count }}
              </td>
              <td v-if="selectedColumns.includes('price_min')" class="col-price">
                <div class="price-main">
                  {{ formatCurrency(hotel.price_range.min) }}
                </div>
                <div class="price-sub" v-if="hotel.price_range.min !== hotel.price_range.max">
                  - {{ formatCurrency(hotel.price_range.max) }}
                </div>
              </td>
              <td v-if="selectedColumns.includes('air_transat')">
                <a
                  v-if="hotel.air_transat_url"
                  :href="hotel.air_transat_url"
                  target="_blank"
                  class="icon-link"
                >
                  <v-icon icon="mdi-airplane" color="primary" />
                </a>
              </td>
              <td v-if="selectedColumns.includes('google_maps')">
                <a :href="getGoogleMapsUrl(hotel)" target="_blank" class="icon-link">
                  <v-icon icon="mdi-map-marker" color="secondary" />
                </a>
              </td>
              <td v-if="selectedColumns.includes('summary')" class="col-summary">
                <div v-if="hasReviewSummary(hotel)">
                  <v-btn
                    size="small"
                    variant="tonal"
                    color="primary"
                    prepend-icon="mdi-robot"
                    @click="openSummary(hotel)"
                    data-test="ai-summary-btn"
                  >
                    View Summary
                  </v-btn>
                </div>
                <span
                  v-else
                  class="wip-pill"
                  aria-label="AI summary in progress"
                  data-test="summary-wip"
                >
                  ⏳ WIP
                </span>
              </td>
              <td v-if="selectedColumns.includes('adult_only')">
                <v-icon
                  v-if="hotel.adult_only"
                  icon="mdi-account-off"
                  color="grey-darken-1"
                  title="Adults Only"
                />
              </td>
              <td v-if="selectedColumns.includes('packages')">
                {{ hotel.package_count }}
              </td>
              <td v-if="selectedColumns.includes('drinks24h')">
                <v-icon v-if="hotel.drinks24h" icon="mdi-glass-cocktail" color="success" />
              </td>
              <td v-if="selectedColumns.includes('snacks24h')">
                <v-icon v-if="hotel.snacks24h" icon="mdi-food" color="success" />
              </td>
              <td v-if="selectedColumns.includes('restaurants')">
                {{ hotel.number_of_restaurants }}
              </td>
              <td v-if="selectedColumns.includes('spa')">
                <v-icon
                  v-if="hotel.spa_available"
                  icon="mdi-spa"
                  color="purple-lighten-2"
                />
              </td>
              <td v-if="selectedColumns.includes('meal_plan')">
                <span class="badge" v-if="hotel.meal_plan_code">{{ hotel.meal_plan_code }}</span>
              </td>
              <td v-if="selectedColumns.includes('thumbnail')">
                <img
                  v-if="hotel.thumbnail_url"
                  :src="hotel.thumbnail_url"
                  class="hotel-thumb"
                  loading="lazy"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty-state">
        <v-icon icon="mdi-magnify-remove-outline" size="64" color="grey-lighten-1" />
        <h3>No hotels found</h3>
        <p>Try adjusting your filters</p>
      </div>
    </v-card>

    <v-dialog v-model="summaryDialogVisible" max-width="700">
      <v-card v-if="selectedSummaryHotel && hasReviewSummary(selectedSummaryHotel)">
        <v-card-title class="d-flex justify-space-between align-center bg-primary">
          <span class="text-h5 text-white">{{ selectedSummaryHotel.name }}</span>
          <v-btn icon="mdi-close" variant="text" @click="summaryDialogVisible = false" color="white"></v-btn>
        </v-card-title>
        
        <v-card-text class="pa-6">
          <div class="summary-section">
            <div class="d-flex align-center mb-3">
              <v-icon icon="mdi-information-outline" color="primary" class="mr-2" size="small"></v-icon>
              <h3 class="text-subtitle-1 font-weight-bold">Overall Summary</h3>
            </div>
            <p class="text-body-1 mb-6 summary-text-content">
              {{ selectedSummaryHotel.review_summary.overall_summary }}
            </p>
          </div>

          <v-divider class="my-4"></v-divider>

          <div class="summary-section">
            <div class="d-flex align-center mb-3">
              <v-icon icon="mdi-thumb-up" color="success" class="mr-2" size="small"></v-icon>
              <h3 class="text-subtitle-1 font-weight-bold text-success">What Guests Love</h3>
            </div>
            <ul class="points-list good-points">
              <li v-for="point in selectedSummaryHotel.review_summary.good_points" :key="point">
                {{ point }}
              </li>
            </ul>
          </div>

          <v-divider class="my-4"></v-divider>

          <div class="summary-section" v-if="selectedSummaryHotel.review_summary.bad_points.length > 0">
            <div class="d-flex align-center mb-3">
              <v-icon icon="mdi-thumb-down" color="error" class="mr-2" size="small"></v-icon>
              <h3 class="text-subtitle-1 font-weight-bold text-error">Common Concerns</h3>
            </div>
            <ul class="points-list bad-points">
              <li v-for="point in selectedSummaryHotel.review_summary.bad_points" :key="point">
                {{ point }}
              </li>
            </ul>
          </div>

          <div class="text-caption text-medium-emphasis mt-4">
            <v-icon icon="mdi-robot" size="x-small" class="mr-1"></v-icon>
            Based on {{ selectedSummaryHotel.review_summary.review_count_analyzed }} guest reviews
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.table-card {
  background: white;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.table-wrapper {
  overflow-x: auto;
  flex-grow: 1;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

th {
  text-align: left;
  padding: 1rem;
  background: #f8f9fa;
  color: #666;
  font-weight: 600;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 1;
}

th.sortable {
  cursor: pointer;
  user-select: none;
}

th.sortable:hover {
  background: #eee;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: top;
}

tr:hover td {
  background: #f9f9ff;
}

.hotel-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1rem;
}

.hotel-city {
  font-size: 0.75rem;
  color: #666;
}

.rating-badge {
  background: #4caf50;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: bold;
  display: inline-block;
}

.price-main {
  font-weight: 700;
  color: #2c3e50;
  font-size: 1rem;
}

.price-sub {
  font-size: 0.75rem;
  color: #666;
}

.icon-link {
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.icon-link:hover {
  opacity: 1;
}

.col-summary {
  min-width: 250px;
  max-width: 400px;
}

.hotel-thumb {
  width: 60px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
}

.badge {
  background: #e0e0e0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.empty-state {
  padding: 4rem;
  text-align: center;
  color: #666;
}

.summary-section {
  margin-bottom: 0.5rem;
}

.summary-text-content {
  line-height: 1.6;
  color: #424242;
}

.points-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.points-list li {
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
  line-height: 1.5;
}

.good-points li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #2e7d32;
  font-weight: bold;
  font-size: 1.1rem;
}

.bad-points li::before {
  content: "×";
  position: absolute;
  left: 0;
  color: #c62828;
  font-weight: bold;
  font-size: 1.2rem;
}

.wip-pill {
  background: #fff3e0;
  color: #e65100;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}
</style>
