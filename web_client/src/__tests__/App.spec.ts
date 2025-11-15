import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ElementPlus from "element-plus";
import App from "../App.vue";
import type { WebOutput } from "../types";

const samplePayload: WebOutput = {
  metadata: {
    destination: "cancun",
    source: "transat",
    generated_at: "2024-01-10T12:00:00Z",
    budget: 5000,
    total_hotels: 2
  },
  hotels: [
    {
      id: "hotel_000",
      name: "Dreams Riviera Cancun",
      city: "Cancun",
      stars: 5,
      google_rating: 4.6,
      review_count: 2300,
      air_transat_url: "https://example.com/dreams",
      google_maps_url: "https://maps.google.com/?q=dreams",
      drinks24h: true,
      snacks24h: false,
      departure_date: "2024-03-01",
      return_date: "2024-03-08",
      price_range: { min: 1800, max: 2200, avg: 2000 },
      package_count: 1,
      packages: [
        {
          departure: "2024-03-01",
          return: "2024-03-08",
          duration_days: 7,
          room_type: "Junior Suite",
          price: 1900,
          url: "https://example.com/dreams-package",
          drinks24h: true,
          snacks24h: false
        }
      ]
    },
    {
      id: "hotel_001",
      name: "Iberostar Selection Paraiso",
      city: "Riviera Maya",
      stars: 4,
      google_rating: 4.3,
      review_count: 1800,
      air_transat_url: "https://example.com/ibero",
      google_maps_url: "https://maps.google.com/?q=ibero",
      drinks24h: false,
      snacks24h: true,
      departure_date: "2024-03-02",
      return_date: "2024-03-09",
      price_range: { min: 1500, max: 2000, avg: 1700 },
      package_count: 1,
      packages: [
        {
          departure: "2024-03-02",
          return: "2024-03-09",
          duration_days: 7,
          room_type: "Ocean View",
          price: 1600,
          url: "https://example.com/ibero-package",
          drinks24h: false,
          snacks24h: true
        }
      ]
    }
  ]
};

function stubFetch(payload: WebOutput, ok = true): void {
  const mockResponse = {
    ok,
    status: ok ? 200 : 404,
    json: async () => payload
  };
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(mockResponse));
}

function mountApp() {
  return mount(App, {
    global: {
      plugins: [ElementPlus]
    }
  });
}

describe("App.vue", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("loads hotels after submitting destination and source", async () => {
    stubFetch(samplePayload);
    const wrapper = mountApp();

    await wrapper.find('[data-test="load-button"]').trigger("click");
    await flushPromises();

    const rows = wrapper.findAll('[data-test="hotel-row"]');
    expect(rows).toHaveLength(2);
    expect(rows[0].text()).toContain("Dreams Riviera Cancun");
  });

  it("filters hotels by search term", async () => {
    stubFetch(samplePayload);
    const wrapper = mountApp();

    await wrapper.find('[data-test="load-button"]').trigger("click");
    await flushPromises();

    await wrapper.find('[data-test="search-input"]').setValue("Iberostar");
    await flushPromises();

    const rows = wrapper.findAll('[data-test="hotel-row"]');
    expect(rows).toHaveLength(1);
    expect(rows[0].text()).toContain("Iberostar");
  });

  it("shows an error message when the request fails", async () => {
    stubFetch(samplePayload, false);
    const wrapper = mountApp();

    await wrapper.find('[data-test="load-button"]').trigger("click");
    await flushPromises();

    const error = wrapper.find('[data-test="error-message"]');
    expect(error.text()).toContain("Unable to load hotels");
  });
});
