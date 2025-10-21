// src/services/auth/index.js
import { SSO_CONFIG } from '@config';
import realSSOService from './ssoService';
import mockAuthService from './mockAuthService';

// Export the appropriate service based on config
export const ssoService = SSO_CONFIG.ENABLE_SSO ? realSSOService : mockAuthService;
export { default as mockAuthService } from './mockAuthService';
export { default as realSSOService } from './ssoService';
