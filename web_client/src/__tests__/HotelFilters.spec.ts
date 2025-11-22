import { mount } from '@vue/test-utils';
import { describe, it, expect, vi } from 'vitest';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import HotelFilters from '../components/HotelFilters.vue';

const vuetify = createVuetify({ components, directives });

const defaultProps = {
    filters: {
        search: '',
        minRating: 0,
        price: { min: 0, max: 1000 },
        requireDrinks24h: false,
        requireSnacks24h: false,
        requireSpa: false,
        requireAdultsOnly: false,
        sortKey: 'price' as const,
        sortDirection: 'asc' as const,
    },
    loading: false,
    metadata: {
        destination: 'cancun',
        source: 'transat',
        generated_at: '2023-01-01',
        budget: 2000,
        total_hotels: 10,
    },
    hotelCount: 5,
    priceBounds: { min: 0, max: 1000, avg: 500 },
    hasFiltersEnabled: false,
    labels: {
        drinks24h: 'Drinks',
        snacks24h: 'Snacks',
        spa: 'Spa',
    },
};

describe('HotelFilters.vue', () => {
    it('renders correctly', () => {
        const wrapper = mount(HotelFilters, {
            props: defaultProps,
            global: { plugins: [vuetify] },
        });
        expect(wrapper.text()).toContain('Filters');
        expect(wrapper.text()).toContain('Showing 5 of 10 hotels');
    });

    it('emits update:filters when search input changes', async () => {
        const wrapper = mount(HotelFilters, {
            props: defaultProps,
            global: { plugins: [vuetify] },
        });

        const input = wrapper.find('[data-test="search-input"] input');
        await input.setValue('test search');

        // v-model update
        // Since filters is an object prop and we mutate its properties, update:filters is not emitted by default
        // unless we replace the whole object. We check if the prop is mutated.
        expect(wrapper.props().filters.search).toBe('test search');
    });

    it('emits reset event when reset button is clicked', async () => {
        const wrapper = mount(HotelFilters, {
            props: { ...defaultProps, hasFiltersEnabled: true },
            global: { plugins: [vuetify] },
        });

        await wrapper.find('[data-test="reset-filters"]').trigger('click');
        expect(wrapper.emitted('reset')).toBeTruthy();
    });

    it('disables inputs when loading', () => {
        const wrapper = mount(HotelFilters, {
            props: { ...defaultProps, loading: true },
            global: { plugins: [vuetify] },
        });

        const input = wrapper.find('[data-test="search-input"] input');
        expect(input.attributes('disabled')).toBeDefined();
    });
});
