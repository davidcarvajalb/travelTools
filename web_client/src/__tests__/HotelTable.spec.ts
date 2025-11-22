import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import HotelTable from '../components/HotelTable.vue';

const vuetify = createVuetify({ components, directives });

const mockHotels = [
    {
        id: '1',
        name: 'Hotel A',
        city: 'City A',
        stars: 5,
        google_rating: 4.5,
        review_count: 100,
        price_range: { min: 100, max: 200, avg: 150 },
        drinks24h: true,
        snacks24h: true,
        adult_only: 0,
        package_count: 2,
        packages: [], // Add missing required property
    },
];

const defaultProps = {
    hotels: mockHotels,
    metadata: {
        destination: 'cancun',
        source: 'transat',
        generated_at: '2023-01-01',
        budget: 2000,
        total_hotels: 1,
    },
    loading: false,
    sortKey: 'price' as const,
    sortDirection: 'asc' as const,
};

describe('HotelTable.vue', () => {
    it('renders hotel data', () => {
        const wrapper = mount(HotelTable, {
            props: defaultProps,
            global: { plugins: [vuetify] },
        });

        expect(wrapper.text()).toContain('Hotel A');
        expect(wrapper.text()).toContain('City A');
    });

    it('toggles sort direction when header is clicked', async () => {
        const wrapper = mount(HotelTable, {
            props: { ...defaultProps, sortKey: 'name' as const, sortDirection: 'asc' as const }, // Start sorted by name asc
            global: { plugins: [vuetify] },
        });

        const headers = wrapper.findAll('th');
        const nameHeader = headers.find(h => h.text().includes('Hotel'));

        if (nameHeader) {
            await nameHeader.trigger('click');
            // Should toggle to desc
            expect(wrapper.emitted('update:sortDirection')?.[0]).toEqual(['desc']);
        }
    });
});
