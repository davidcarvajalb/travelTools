import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useHotels } from '../composables/useHotels';
import { flushPromises } from '@vue/test-utils';

// Mock fetch
const mockHotels = [
    {
        id: '1',
        name: 'Hotel A',
        price_range: { min: 100, max: 200, avg: 150 },
        stars: 5,
        google_rating: 4.5,
        review_count: 100,
        drinks24h: true,
        snacks24h: true,
        spa_available: 'Yes',
        adult_only: 0,
    },
    {
        id: '2',
        name: 'Hotel B',
        price_range: { min: 50, max: 100, avg: 75 },
        stars: 3,
        google_rating: 4.0,
        review_count: 50,
        drinks24h: false,
        snacks24h: false,
        spa_available: 'No',
        adult_only: 1,
    },
];

const mockMetadata = {
    destination: 'cancun',
    source: 'transat',
    generated_at: '2023-01-01',
    budget: 2000,
    total_hotels: 2,
};

global.fetch = vi.fn();

describe('useHotels', () => {
    beforeEach(() => {
        vi.resetAllMocks();
        (global.fetch as any).mockResolvedValue({
            ok: true,
            json: async () => ({ hotels: mockHotels, metadata: mockMetadata }),
        });
    });

    it('loads data correctly', async () => {
        const { loadData, hotels, metadata, loading } = useHotels();

        expect(loading.value).toBe(false);
        const loadPromise = loadData();
        expect(loading.value).toBe(true);
        await loadPromise;
        expect(loading.value).toBe(false);

        expect(hotels.value).toHaveLength(2);
        expect(metadata.value).toEqual(mockMetadata);
    });

    it('filters by price', async () => {
        const { loadData, filters, filteredHotels } = useHotels();
        await loadData();

        filters.value.price.max = 80;
        expect(filteredHotels.value).toHaveLength(1);
        expect(filteredHotels.value[0].name).toBe('Hotel B');
    });

    it('sorts by price ascending', async () => {
        const { loadData, filters, filteredHotels } = useHotels();
        await loadData();

        filters.value.sortKey = 'price';
        filters.value.sortDirection = 'asc';

        expect(filteredHotels.value[0].name).toBe('Hotel B'); // 50
        expect(filteredHotels.value[1].name).toBe('Hotel A'); // 100
    });

    it('sorts by price descending', async () => {
        const { loadData, filters, filteredHotels } = useHotels();
        await loadData();

        filters.value.sortKey = 'price';
        filters.value.sortDirection = 'desc';

        expect(filteredHotels.value[0].name).toBe('Hotel A'); // 100
        expect(filteredHotels.value[1].name).toBe('Hotel B'); // 50
    });

    it('resets filters', async () => {
        const { loadData, filters, resetFilters, priceBounds } = useHotels();
        await loadData();

        // Change some filters
        filters.value.search = 'Hotel A';
        filters.value.minRating = 4;

        expect(filters.value.search).toBe('Hotel A');

        resetFilters();

        expect(filters.value.search).toBe('');
        expect(filters.value.minRating).toBe(0);
        expect(filters.value.price.min).toBe(priceBounds.value.min);
        expect(filters.value.price.max).toBe(priceBounds.value.max);
    });

    it('reloads data when destination changes', async () => {
        const { destination, loadData } = useHotels();
        // Initial load is called in onMounted in component, but here we call it manually or rely on watcher if we were mounting a component.
        // Since useHotels sets up a watcher, we need to verify if changing destination triggers fetch.
        // However, watchers in composables run when the reactive state changes.

        // We need to mock loadData or check fetch calls.
        await loadData();
        expect(global.fetch).toHaveBeenCalledTimes(1);

        destination.value = 'punta-cana';
        await flushPromises();

        expect(global.fetch).toHaveBeenCalledTimes(2);
        expect(global.fetch).toHaveBeenLastCalledWith(expect.stringContaining('punta-cana'));
    });
});
