import { describe, it, expect } from 'vitest'
import type { Review, ReviewSummary, WebHotel } from '../types'
import { hasReviewSummary, isValidReview } from '../types'

describe('Review type', () => {
  it('should validate Review structure', () => {
    const review: Review = {
      text: 'Great hotel!',
      rating: 5,
      date: '2025-01-15',
      reviewer_name: 'John Doe'
    }

    expect(review.text).toBe('Great hotel!')
    expect(review.rating).toBeGreaterThanOrEqual(1)
    expect(review.rating).toBeLessThanOrEqual(5)
    expect(review.date).toBe('2025-01-15')
    expect(review.reviewer_name).toBe('John Doe')
  })

  it('should allow optional reviewer_name', () => {
    const review: Review = {
      text: 'Anonymous review',
      rating: 4,
      date: '2025-01-15',
      reviewer_name: null
    }

    expect(review.reviewer_name).toBeNull()
  })

  it('should accept relative dates', () => {
    const review: Review = {
      text: 'Recent visit',
      rating: 5,
      date: '2 weeks ago',
      reviewer_name: 'Alice'
    }

    expect(review.date).toBe('2 weeks ago')
  })
})

describe('ReviewSummary type', () => {
  it('should validate ReviewSummary structure', () => {
    const summary: ReviewSummary = {
      good_points: ['Clean rooms', 'Great pool'],
      bad_points: ['Noisy', 'Small breakfast'],
      ugly_points: ['Construction'],
      overall_summary: 'Good hotel with minor issues',
      review_count_analyzed: 15
    }

    expect(summary.good_points).toHaveLength(2)
    expect(summary.bad_points).toHaveLength(2)
    expect(summary.ugly_points).toHaveLength(1)
    expect(summary.overall_summary).toBe('Good hotel with minor issues')
    expect(summary.review_count_analyzed).toBe(15)
  })

  it('should allow empty arrays', () => {
    const summary: ReviewSummary = {
      good_points: [],
      bad_points: [],
      ugly_points: [],
      overall_summary: 'No clear themes',
      review_count_analyzed: 5
    }

    expect(summary.good_points).toEqual([])
    expect(summary.bad_points).toEqual([])
    expect(summary.ugly_points).toEqual([])
  })
})

describe('WebHotel with review_summary', () => {
  it('should include optional review_summary field', () => {
    const hotel: WebHotel = {
      id: 'hotel_001',
      name: 'Test Hotel',
      city: 'Cancun',
      stars: 5,
      google_rating: 4.5,
      review_count: 200,
      drinks24h: true,
      snacks24h: false,
      price_range: { min: 3000, max: 4000, avg: 3500 },
      package_count: 3,
      packages: [],
      review_summary: {
        good_points: ['Pool', 'Staff'],
        bad_points: ['Food'],
        ugly_points: [],
        overall_summary: 'Nice resort',
        review_count_analyzed: 15
      }
    }

    expect(hotel.review_summary).toBeDefined()
    expect(hotel.review_summary?.good_points).toHaveLength(2)
    expect(hotel.review_summary?.overall_summary).toBe('Nice resort')
  })

  it('should allow null review_summary', () => {
    const hotel: WebHotel = {
      id: 'hotel_002',
      name: 'Another Hotel',
      city: 'Cancun',
      stars: 4,
      google_rating: 4.0,
      review_count: 100,
      drinks24h: false,
      snacks24h: false,
      price_range: { min: 2000, max: 3000, avg: 2500 },
      package_count: 1,
      packages: [],
      review_summary: null
    }

    expect(hotel.review_summary).toBeNull()
  })

  it('should allow undefined review_summary', () => {
    const hotel: WebHotel = {
      id: 'hotel_003',
      name: 'Old Hotel',
      city: 'Cancun',
      stars: 3,
      google_rating: 3.8,
      review_count: 50,
      drinks24h: false,
      snacks24h: false,
      price_range: { min: 1500, max: 2000, avg: 1750 },
      package_count: 1,
      packages: []
    }

    expect(hotel.review_summary).toBeUndefined()
  })
})

describe('Type guard: hasReviewSummary', () => {
  it('should return true when hotel has review_summary', () => {
    const hotel: WebHotel = {
      id: 'hotel_001',
      name: 'Test Hotel',
      city: 'Cancun',
      stars: 5,
      google_rating: 4.5,
      review_count: 200,
      drinks24h: true,
      snacks24h: false,
      price_range: { min: 3000, max: 4000, avg: 3500 },
      package_count: 3,
      packages: [],
      review_summary: {
        good_points: ['Pool'],
        bad_points: [],
        ugly_points: [],
        overall_summary: 'Great',
        review_count_analyzed: 10
      }
    }

    expect(hasReviewSummary(hotel)).toBe(true)

    if (hasReviewSummary(hotel)) {
      // TypeScript should narrow the type here
      expect(hotel.review_summary.overall_summary).toBe('Great')
    }
  })

  it('should return false when review_summary is null', () => {
    const hotel: WebHotel = {
      id: 'hotel_002',
      name: 'Test Hotel',
      city: 'Cancun',
      stars: 4,
      google_rating: 4.0,
      review_count: 100,
      drinks24h: false,
      snacks24h: false,
      price_range: { min: 2000, max: 3000, avg: 2500 },
      package_count: 1,
      packages: [],
      review_summary: null
    }

    expect(hasReviewSummary(hotel)).toBe(false)
  })

  it('should return false when review_summary is undefined', () => {
    const hotel: WebHotel = {
      id: 'hotel_003',
      name: 'Test Hotel',
      city: 'Cancun',
      stars: 3,
      google_rating: 3.8,
      review_count: 50,
      drinks24h: false,
      snacks24h: false,
      price_range: { min: 1500, max: 2000, avg: 1750 },
      package_count: 1,
      packages: []
    }

    expect(hasReviewSummary(hotel)).toBe(false)
  })
})

describe('Type guard: isValidReview', () => {
  it('should return true for valid review object', () => {
    const review = {
      text: 'Great hotel!',
      rating: 5,
      date: '2025-01-15',
      reviewer_name: 'John'
    }

    expect(isValidReview(review)).toBe(true)
  })

  it('should return false for missing text', () => {
    const review = {
      rating: 5,
      date: '2025-01-15',
      reviewer_name: 'John'
    }

    expect(isValidReview(review)).toBe(false)
  })

  it('should return false for invalid rating (too high)', () => {
    const review = {
      text: 'Great!',
      rating: 6,
      date: '2025-01-15',
      reviewer_name: 'John'
    }

    expect(isValidReview(review)).toBe(false)
  })

  it('should return false for invalid rating (too low)', () => {
    const review = {
      text: 'Bad',
      rating: 0,
      date: '2025-01-15',
      reviewer_name: 'John'
    }

    expect(isValidReview(review)).toBe(false)
  })

  it('should return false for missing date', () => {
    const review = {
      text: 'Great!',
      rating: 5,
      reviewer_name: 'John'
    }

    expect(isValidReview(review)).toBe(false)
  })

  it('should accept review with null reviewer_name', () => {
    const review = {
      text: 'Anonymous',
      rating: 4,
      date: '2025-01-15',
      reviewer_name: null
    }

    expect(isValidReview(review)).toBe(true)
  })

  it('should return false for non-object input', () => {
    expect(isValidReview(null)).toBe(false)
    expect(isValidReview(undefined)).toBe(false)
    expect(isValidReview('string')).toBe(false)
    expect(isValidReview(123)).toBe(false)
  })
})
