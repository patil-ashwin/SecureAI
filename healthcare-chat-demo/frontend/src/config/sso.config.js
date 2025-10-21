// src/config/sso.config.js
export const SSO_CONFIG = {
  // Enable/Disable SSO - Correctly handle the environment variable
  ENABLE_SSO: process.env.REACT_APP_ENABLE_SSO === 'true', // Explicitly check for 'true' string
  
  // Bank SSO Configuration
  OAUTH_CLIENT_ID: 'BART_Graph_Analytics',
  OAUTH_REDIRECT_URL: process.env.REACT_APP_SSO_REDIRECT_URL || 'http://localhost:5000/wb',
  OAUTH_AUTHORIZATION_ENDPOINT: 'https://it-sso.us.bank-dns.com/as/authorization.oauth2',
  OAUTH_TOKEN_ENDPOINT: 'https://it-sso.us.bank-dns.com/as/token.oauth2',
  OAUTH_SCOPES: 'openid profile',
  TOKEN_STORAGE_KEY: 'bart_access_token',
  USER_INFO_STORAGE_KEY: 'bart_user_info',
  
  // Debug logging
  _debug: () => {
    console.log('🔧 SSO Config Debug:');
    console.log('- process.env.REACT_APP_ENABLE_SSO:', process.env.REACT_APP_ENABLE_SSO);
    console.log('- typeof:', typeof process.env.REACT_APP_ENABLE_SSO);
    console.log('- ENABLE_SSO result:', process.env.REACT_APP_ENABLE_SSO === 'true');
    console.log('- Mode:', process.env.REACT_APP_ENABLE_SSO === 'true' ? 'REAL SSO' : 'MOCK MODE');
    console.log('- All SSO env vars:', {
      REACT_APP_ENABLE_SSO: process.env.REACT_APP_ENABLE_SSO,
      REACT_APP_SSO_REDIRECT_URL: process.env.REACT_APP_SSO_REDIRECT_URL
    });
  }
};

// Auto-debug on import (only in development)
if (process.env.NODE_ENV === 'development') {
  SSO_CONFIG._debug();
}
