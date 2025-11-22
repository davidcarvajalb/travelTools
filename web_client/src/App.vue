<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useHotels } from './composables/useHotels';
import HeroSection from './components/HeroSection.vue';
import HotelFilters from './components/HotelFilters.vue';
import HotelTable from './components/HotelTable.vue';

const {
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
} = useHotels();

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
    maximumFractionDigits: 0,
  }).format(value);
};

const destinationLabel = computed(() => {
  return destination.value
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
});

const budgetLabel = computed(() => {
  return metadata.value ? formatCurrency(metadata.value.budget) : '-';
});

const generatedLabel = computed(() => {
  return metadata.value
    ? new Date(metadata.value.generated_at).toLocaleString()
    : '-';
});

const labels = {
  drinks24h: '24h Drinks',
  snacks24h: '24h Snacks',
  spa: 'Spa Available',
};

onMounted(() => {
  loadData();
});
</script>

<template>
  <v-app>
    <v-main>
      <div class="page-container">
        <HeroSection
          v-model:destination="destination"
          v-model:source="destinationSource"
          :metadata="metadata"
          :destination-label="destinationLabel"
          :budget-label="budgetLabel"
          :generated-label="generatedLabel"
          :error-message="errorMessage"
        />

        <HotelFilters
          v-model:filters="filters"
          :loading="loading"
          :metadata="metadata"
          :hotel-count="hotelCount"
          :price-bounds="priceBounds"
          :has-filters-enabled="hasFiltersEnabled"
          :labels="labels"
          @reset="resetFilters"
        />

        <HotelTable
          :hotels="filteredHotels"
          :metadata="metadata"
          :loading="loading"
          v-model:sort-key="filters.sortKey"
          v-model:sort-direction="filters.sortDirection"
        />
      </div>
    </v-main>
  </v-app>
</template>

<style scoped>
.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.05);
}
</style>
