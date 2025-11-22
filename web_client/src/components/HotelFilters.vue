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
  <div class="pa-4" v-if="metadata">
    <div class="d-flex justify-space-between align-center mb-4">
      <h2 class="text-h6 font-weight-bold">Filters</h2>
      <v-btn
        variant="text"
        color="primary"
        size="small"
        data-test="reset-filters"
        @click="emit('reset')"
        :disabled="loading || !hasFiltersEnabled"
      >
        Reset
      </v-btn>
    </div>

    <div class="text-caption text-medium-emphasis mb-4">
      Showing {{ hotelCount }} of {{ metadata.total_hotels }} hotels
    </div>

    <div class="d-flex flex-column ga-4">
      <v-text-field
        v-model="filters.search"
        data-test="search-input"
        label="Search hotel name"
        placeholder="Dreams, Iberostar..."
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        density="compact"
        hide-details
        :disabled="loading"
        bg-color="surface"
      />

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
        density="compact"
        hide-details
        :disabled="loading"
        bg-color="surface"
      />

      <div class="price-inputs">
        <v-text-field
          v-model.number="filters.price.min"
          data-test="price-min"
          label="Min Price"
          type="number"
          prefix="$"
          :disabled="loading"
          @blur="normalizePriceRange"
          variant="outlined"
          density="compact"
          hide-details
          bg-color="surface"
        />
        <span class="text-medium-emphasis">-</span>
        <v-text-field
          v-model.number="filters.price.max"
          data-test="price-max"
          label="Max Price"
          type="number"
          prefix="$"
          :disabled="loading"
          @blur="normalizePriceRange"
          variant="outlined"
          density="compact"
          hide-details
          bg-color="surface"
        />
      </div>

      <div class="text-caption text-medium-emphasis">
        Range: {{ formatCurrency(priceBounds.min) }} — {{ formatCurrency(priceBounds.max) }}
      </div>

      <v-divider></v-divider>

      <div class="d-flex flex-column">
        <v-checkbox
          v-model="filters.requireDrinks24h"
          :label="labels.drinks24h"
          :disabled="loading"
          density="compact"
          hide-details
          data-test="drinks-checkbox"
          color="primary"
        />
        <v-checkbox
          v-model="filters.requireSnacks24h"
          :label="labels.snacks24h"
          :disabled="loading"
          density="compact"
          hide-details
          data-test="snacks-checkbox"
          color="primary"
        />
        <v-checkbox
          v-model="filters.requireSpa"
          :label="labels.spa"
          :disabled="loading"
          density="compact"
          hide-details
          data-test="spa-checkbox"
          color="primary"
        />
        <v-checkbox
          v-model="filters.requireAdultsOnly"
          label="Adults Only"
          :disabled="loading"
          density="compact"
          hide-details
          data-test="adult-checkbox"
          color="primary"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.price-inputs {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 8px;
  align-items: center;
}
</style>
