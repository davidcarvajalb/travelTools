<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useHotels } from './composables/useHotels';
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

const drawer = ref(true);

const destinations = [
  { title: 'Cancun', value: 'cancun' },
  { title: 'Punta Cana', value: 'punta-cana' },
  { title: 'Martinique', value: 'martinique' },
  { title: 'Puerto Plata & Samana', value: 'puerto-plata-samana' },
];

const sources = [
  { title: 'Air Transat', value: 'transat' },
];

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
    maximumFractionDigits: 0,
  }).format(value);
};

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
    <v-app-bar color="primary" density="compact" elevation="2">
      <v-app-bar-nav-icon variant="text" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      
      <v-app-bar-title>Travel Tools</v-app-bar-title>

      <v-spacer></v-spacer>

      <div class="d-flex align-center ga-4 mr-4">
        <v-select
          v-model="destination"
          :items="destinations"
          density="compact"
          variant="outlined"
          hide-details
          bg-color="primary-darken-1"
          class="app-bar-select"
          style="width: 200px"
        ></v-select>

        <v-select
          v-model="destinationSource"
          :items="sources"
          density="compact"
          variant="outlined"
          hide-details
          bg-color="primary-darken-1"
          class="app-bar-select"
          style="width: 150px"
        ></v-select>
      </div>

      <div class="text-caption mr-4 text-white d-none d-md-block" v-if="metadata">
        <div>Budget: {{ budgetLabel }}</div>
        <div class="text-medium-emphasis text-white">Updated: {{ generatedLabel }}</div>
      </div>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" width="300">
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
    </v-navigation-drawer>

    <v-main class="bg-grey-lighten-4">
      <v-container fluid class="pa-4 fill-height align-start">
        <v-alert
          v-if="errorMessage"
          type="error"
          title="Error loading data"
          :text="errorMessage"
          class="mb-4 w-100"
          data-test="error-message"
        ></v-alert>

        <HotelTable
          v-if="!errorMessage"
          :hotels="filteredHotels"
          :metadata="metadata"
          :loading="loading"
          v-model:sort-key="filters.sortKey"
          v-model:sort-direction="filters.sortDirection"
        />
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped>
.app-bar-select :deep(.v-field__outline) {
  --v-field-border-opacity: 0.2;
}
</style>
