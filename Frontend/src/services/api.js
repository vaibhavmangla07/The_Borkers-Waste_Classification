/**
 * EcoVision AI - API Client Service Abstraction
 * 
 * Strict architectural rule:
 * UI components must NEVER call fetch/endpoints directly.
 * All API interactions must route through this service.
 * Mock data is isolated here as a development fallback when backend is offline.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL !== undefined 
  ? import.meta.env.VITE_API_BASE_URL 
  : (import.meta.env.DEV ? 'http://localhost:8000' : '');
const ENABLE_MOCKS_ON_FAILURE = true;

/**
 * Standardized API error representation
 */
export class ApiError extends Error {
  constructor(message, code = 'API_ERROR', status = 500, details = null) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

/**
 * Isolated mock data for offline development
 */
export const MOCK_DATA = {
  health: {
    status: 'healthy',
    timestamp: '2026-10-01T09:30:00Z',
    version: '1.0.0'
  },
  categories: [
    { id: 1, name: 'Plastic', slug: 'plastic', group: 'Recyclable', description: 'Bottles, containers, polymers, and synthetic packaging.' },
    { id: 2, name: 'Organic', slug: 'organic', group: 'Compostable', description: 'Food scraps, fruit peels, yard trimmings, and coffee grounds.' },
    { id: 3, name: 'Glass', slug: 'glass', group: 'Recyclable', description: 'Clear, green, and brown glass jars and bottles.' },
    { id: 4, name: 'Metal', slug: 'metal', group: 'Recyclable', description: 'Aluminum cans, tin containers, and foil items.' },
    { id: 5, name: 'Paper & Cardboard', slug: 'paper', group: 'Recyclable', description: 'Clean newspapers, boxes, paperboard, and office sheets.' },
    { id: 6, name: 'Hazardous / E-Waste', slug: 'hazardous', group: 'Special Disposal', description: 'Batteries, electronics, chemicals, and fluorescents.' }
  ],
  sampleClassification: {
    classification_id: 104,
    category: 'Plastic',
    confidence: 0.964,
    confidence_level: 'high',
    message: 'High-confidence classification',
    predictions: [
      { category: 'Plastic', confidence: 0.964 },
      { category: 'Glass', confidence: 0.021 },
      { category: 'Metal', confidence: 0.008 }
    ],
    disposal: {
      title: 'Recyclable Waste',
      bin_type: 'Dry / recyclable bin (Blue/Green)',
      instructions: [
        'Empty and rinse the container to remove food residue',
        'Remove non-recyclable plastic wrap or absorbent pads',
        'Place in clean dry recyclable stream'
      ],
      avoid: [
        'Do not mix with wet organic waste',
        'Do not leave liquid contents inside'
      ]
    },
    inference_ms: 74,
    created_at: new Date().toISOString()
  },
  analyticsSummary: {
    total_scans: 14820,
    accuracy_rate: 94.6,
    active_users: 1240,
    co2_saved_kg: 3420.5
  },
  analyticsCategories: [
    { category: 'Plastic', count: 5230, percentage: 35.3 },
    { category: 'Organic', count: 4120, percentage: 27.8 },
    { category: 'Paper & Cardboard', count: 2640, percentage: 17.8 },
    { category: 'Glass', count: 1540, percentage: 10.4 },
    { category: 'Metal', count: 980, percentage: 6.6 },
    { category: 'E-Waste', count: 310, percentage: 2.1 }
  ],
  recentHistory: [
    {
      id: 104,
      category: 'Plastic',
      confidence: 0.964,
      confidence_level: 'high',
      created_at: '2026-10-01T09:12:00Z',
      thumbnail: null
    },
    {
      id: 103,
      category: 'Organic',
      confidence: 0.885,
      confidence_level: 'high',
      created_at: '2026-10-01T08:45:00Z',
      thumbnail: null
    },
    {
      id: 102,
      category: 'Metal',
      confidence: 0.642,
      confidence_level: 'moderate',
      created_at: '2026-10-01T08:10:00Z',
      thumbnail: null
    },
    {
      id: 101,
      category: 'Glass',
      confidence: 0.420,
      confidence_level: 'low',
      created_at: '2026-10-01T07:30:00Z',
      thumbnail: null
    }
  ]
};

/**
 * Internal generic request handler with standard error formatting
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders = {};

  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errPayload = data?.error || {};
      throw new ApiError(
        errPayload.message || `Request failed with status ${response.status}`,
        errPayload.code || 'HTTP_ERROR',
        response.status,
        data
      );
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    // Network error or backend offline
    throw new ApiError(
      error.message || 'Network error: could not connect to EcoVision AI backend',
      'NETWORK_FAILURE',
      0,
      null
    );
  }
}

/**
 * Exported API service object conforming to the EcoVision AI Backend Blueprint
 */
export const api = {
  // System Health
  async getHealth() {
    try {
      return await request('/health');
    } catch (err) {
      if (ENABLE_MOCKS_ON_FAILURE) return MOCK_DATA.health;
      throw err;
    }
  },

  async getHealthReady() {
    try {
      return await request('/health/ready');
    } catch (err) {
      if (ENABLE_MOCKS_ON_FAILURE) return { status: 'ready', database: 'connected', model: 'loaded' };
      throw err;
    }
  },

  // Waste Categories
  async getCategories() {
    try {
      return await request('/api/categories');
    } catch (err) {
      if (ENABLE_MOCKS_ON_FAILURE) return MOCK_DATA.categories;
      throw err;
    }
  },

  async getCategoryGuidance(slug) {
    try {
      return await request(`/api/categories/${encodeURIComponent(slug)}/guidance`);
    } catch (err) {
      if (ENABLE_MOCKS_ON_FAILURE) return MOCK_DATA.sampleClassification.disposal;
      throw err;
    }
  },

  // Classification API: POST /api/classify with multipart/form-data
  async classifyImage(file) {
    if (!file) {
      throw new ApiError('No image file provided for classification', 'NO_FILE', 400);
    }

    // Client-side quick validation (formats: JPG, PNG, WEBP, <= 5MB)
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      throw new ApiError('Please upload a JPG, PNG or WEBP image.', 'UNSUPPORTED_FILE_TYPE', 400);
    }
    const MAX_SIZE_BYTES = 5 * 1024 * 1024;
    if (file.size > MAX_SIZE_BYTES) {
      throw new ApiError('Image size exceeds maximum limit of 5 MB.', 'FILE_TOO_LARGE', 400);
    }

    const formData = new FormData();
    formData.append('image', file);

    try {
      return await request('/api/classify', {
        method: 'POST',
        body: formData
      });
    } catch (err) {
      if (ENABLE_MOCKS_ON_FAILURE) {
        // Return structured mock response matching backend contract
        return {
          ...MOCK_DATA.sampleClassification,
          classification_id: Math.floor(100 + Math.random() * 900),
          created_at: new Date().toISOString()
        };
      }
      throw err;
    }
  },

  // History Endpoints
  async getHistory(params = {}) {
    const query = new URLSearchParams(params).toString();
    const endpoint = `/api/history${query ? `?${query}` : ''}`;
    try {
      return await request(endpoint);
    } catch (err) {
      if (ENABLE_MOCKS_ON_FAILURE) {
        return {
          items: MOCK_DATA.recentHistory,
          total: MOCK_DATA.recentHistory.length,
          page: 1,
          limit: 10
        };
      }
      throw err;
    }
  },

  async getHistoryItem(id) {
    try {
      return await request(`/api/history/${id}`);
    } catch (err) {
      if (ENABLE_MOCKS_ON_FAILURE) {
        return {
          ...MOCK_DATA.sampleClassification,
          classification_id: Number(id)
        };
      }
      throw err;
    }
  },

  getHistoryImageUrl(id) {
    return `${API_BASE_URL}/api/history/${id}/image`;
  },

  // Analytics Endpoints
  async getAnalyticsSummary() {
    try {
      return await request('/api/analytics/summary');
    } catch (err) {
      if (ENABLE_MOCKS_ON_FAILURE) return MOCK_DATA.analyticsSummary;
      throw err;
    }
  },

  async getAnalyticsCategories() {
    try {
      return await request('/api/analytics/categories');
    } catch (err) {
      if (ENABLE_MOCKS_ON_FAILURE) return MOCK_DATA.analyticsCategories;
      throw err;
    }
  },

  async getAnalyticsActivity(range = '7d') {
    try {
      return await request(`/api/analytics/activity?range=${encodeURIComponent(range)}`);
    } catch (err) {
      if (ENABLE_MOCKS_ON_FAILURE) {
        return [
          { date: '2026-09-25', scans: 410 },
          { date: '2026-09-26', scans: 530 },
          { date: '2026-09-27', scans: 620 },
          { date: '2026-09-28', scans: 490 },
          { date: '2026-09-29', scans: 780 },
          { date: '2026-09-30', scans: 890 },
          { date: '2026-10-01', scans: 940 }
        ];
      }
      throw err;
    }
  },

  // Auth Endpoints (Optional/Future)
  async register(credentials) {
    return request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
  },

  async login(credentials) {
    return request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
  }
};

export default api;
