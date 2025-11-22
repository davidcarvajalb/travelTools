<script setup lang="ts">
import type { FilterState, WebOutput, PriceRange } from '../types';

defineProps<{
  loading: boolean;
  metadata: WebOutput['metadata'] | null;
  hotelCount: number;
  priceBounds: PriceRange;
  hasFiltersEnabled: boolean;
  labels: Record<string, string>;
}>();

const filters = defineModel<FilterState>('filters', { required: true });

const emit = defineEmits<{
  (e: 'reset'): void;
}>();

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
    maximumFractionDigits: 0,
  }).format(value);
};

// Helper to normalize price range on blur
const normalizePriceRange = () => {
  if (filters.value.price.min > filters.value.price.max) {
    const temp = filters.value.price.min;
    filters.value.price.min = filters.value.price.max;
    filters.value.price.max = temp;
  }
};
</script>

<template>
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
            variant="outlined"
            density="comfortable"
            hide-details
            :disabled="loading"
            bg-color="surface"
          />
        </div>

        <div>
          <v-select
            v-model="filters.minRating"
            label="Min Rating"
            :items="[
              { title: 'Any', value: 0 },
              { title: '3+ Stars', value: 3 },
              { title: '4+ Stars', value: 4 },
              { title: '5 Stars', value: 5 },
            ]"
            variant="outlined"
            density="comfortable"
            hide-details
            :disabled="loading"
            bg-color="surface"
          />
        </div>

        <div>
          <v-text-field
            v-model.number="filters.price.min"
            data-test="price-min"
            label="Price min (CAD)"
            type="number"
            prefix="$"
            :disabled="loading"
            @blur="normalizePriceRange"
            variant="outlined"
            density="comfortable"
            hide-details
            bg-color="surface"
          />
        </div>
        <div>
          <v-text-field
            v-model.number="filters.price.max"
            data-test="price-max"
            label="Price max (CAD)"
            type="number"
            prefix="$"
            :disabled="loading"
            @blur="normalizePriceRange"
            variant="outlined"
            density="comfortable"
            hide-details
            bg-color="surface"
          />
        </div>

        <div>
          <v-checkbox
            v-model="filters.requireDrinks24h"
            :label="labels.drinks24h"
            :disabled="loading"
            density="comfortable"
            hide-details
            data-test="drinks-checkbox"
            color="primary"
          />
        </div>
        <div>
          <v-checkbox
            v-model="filters.requireSnacks24h"
            :label="labels.snacks24h"
            :disabled="loading"
            density="comfortable"
            hide-details
            data-test="snacks-checkbox"
            color="primary"
          />
        </div>
        <div>
          <v-checkbox
            v-model="filters.requireSpa"
            :label="labels.spa"
            :disabled="loading"
            density="comfortable"
            hide-details
            data-test="spa-checkbox"
            color="primary"
          />
        </div>
        <div>
          <v-checkbox
            v-model="filters.requireAdultsOnly"
            label="Adults Only"
            :disabled="loading"
            density="comfortable"
            hide-details
            data-test="adult-checkbox"
            color="primary"
          />
        </div>
      </div>

      <p class="filters-note">
        Prices shown in CAD · Available range:
        {{ formatCurrency(priceBounds.min) }} —
        {{ formatCurrency(priceBounds.max) }}
      </p>

      <div class="filters-actions">
        <v-btn
          variant="text"
          color="error"
          data-test="reset-filters"
          @click="emit('reset')"
          :disabled="loading || !hasFiltersEnabled"
        >
          Reset Filters
        </v-btn>
      </div>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.filters-card {
  border: 1px solid #e0e0e0;
  background: white;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 0;
}

.filters-header h2 {
  font-size: 1.5rem;
  margin: 0;
  color: #1a1a1a;
}

.filters-grid--form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.filters-note {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #666;
}

.filters-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
}

.overline {
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.75rem;
  font-weight: 600;
}

.muted {
  color: #6c6f80;
}
</style>
