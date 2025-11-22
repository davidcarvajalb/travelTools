<script setup lang="ts">
import type { WebOutput } from '../types';

defineProps<{
  metadata: WebOutput['metadata'] | null;
  destinationLabel: string;
  budgetLabel: string;
  generatedLabel: string;
  errorMessage: string;
}>();

const destination = defineModel<string>('destination', { required: true });
const destinationSource = defineModel<string>('source', { required: true });

const destinations = [
  { title: 'Cancun', value: 'cancun' },
  { title: 'Punta Cana', value: 'punta-cana' },
  { title: 'Martinique', value: 'martinique' },
  { title: 'Puerto Plata & Samana', value: 'puerto-plata-samana' },
];

const sources = [
  { title: 'Air Transat', value: 'transat' },
];
</script>

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

    <div class="filters-grid">
      <div class="select-wrapper">
        <label for="destination">Destination slug</label>
        <v-select
          id="destination"
          v-model="destination"
          :items="destinations"
          density="compact"
          variant="outlined"
          hide-details
          bg-color="surface"
        ></v-select>
      </div>
      <div class="select-wrapper">
        <label for="source">Source</label>
        <v-select
          id="source"
          v-model="destinationSource"
          :items="sources"
          density="compact"
          variant="outlined"
          hide-details
          bg-color="surface"
        ></v-select>
      </div>
    </div>

    <p class="muted small">
      Select a destination and source to load the report.
      <br />
      Example path: <code>outputs/cancun/transat/hotels.json</code>
    </p>
    <p class="error" v-if="errorMessage" data-test="error-message">
      {{ errorMessage }}
    </p>
  </section>
</template>

<style scoped>
.hero {
  background: linear-gradient(135deg, #5d5fef 0%, #8e90ff 100%);
  color: white;
  border: none;
}

.hero h1 {
  color: white;
  margin-bottom: 0.5rem;
}

.hero p {
  color: rgba(255, 255, 255, 0.9);
}

.hero code {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.select-wrapper label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.error {
  color: #ffcccc;
  background: rgba(255, 0, 0, 0.1);
  padding: 0.5rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.muted {
  opacity: 0.8;
}

.small {
  font-size: 0.875rem;
  margin-top: 1rem;
}
</style>
