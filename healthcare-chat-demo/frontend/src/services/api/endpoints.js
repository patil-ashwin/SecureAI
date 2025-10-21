// API Endpoints - Now using centralized configuration
import { getFullUrl } from '@config/api';

// All endpoints now use centralized configuration
export const ENDPOINTS = {
  // Chat endpoints
  ASK: getFullUrl('ASK'),
  SEARCH: getFullUrl('SEARCH'),
  
  // Document endpoints
  UPLOAD: getFullUrl('UPLOAD'),
  
  // Model endpoints
  MODELS: getFullUrl('MODELS'),
  
  // Health check
  HEALTH: getFullUrl('HEALTH'),
  
  // Debug endpoints
  DEBUG_DOCUMENTS: getFullUrl('DEBUG_DOCUMENTS')
};

// Legacy support - keeping for backward compatibility
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8002';
