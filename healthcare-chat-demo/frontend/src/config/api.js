// Centralized API Configuration
// This is the SINGLE place where backend URL is defined

const API_CONFIG = {
  // Backend URL - ONLY place this is defined
  BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8002',
  
  // API endpoints
  ENDPOINTS: {
    // Chat endpoints
    ASK: '/api/chat',
    SEARCH: '/api/search',
    
    // Document endpoints
    UPLOAD: '/api/upload',
    
    // Model endpoints
    MODELS: '/api/models',
    
    // Health check
    HEALTH: '/api/health',
    
    // Debug endpoints
    DEBUG_DOCUMENTS: '/api/debug/documents'
  },
  
  // Request configuration
  TIMEOUT: parseInt(process.env.REACT_APP_API_TIMEOUT) || 30000,
  RETRY_ATTEMPTS: 3
};

// Helper functions
export const getApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

export const getFullUrl = (endpoint) => {
  return getApiUrl(API_CONFIG.ENDPOINTS[endpoint] || endpoint);
};

// Export the config
export default API_CONFIG;
