// src/config/api.config.js
export const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8002',
  timeout: parseInt(process.env.REACT_APP_API_TIMEOUT) || 30000,
  retryAttempts: 3,
  endpoints: {
    // Chat endpoints
    chat: '/api/chat',
    generateSummary: '/api/generate-discharge-summary',
    
    // Patient endpoints
    patient: '/api/patient',
    
    // Health check
    health: '/api/health'
  }
};
