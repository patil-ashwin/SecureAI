// src/services/auth/mockAuthService.js
// Enhanced mock authentication service for local testing

class MockAuthService {
  constructor() {
    this.mockUser = null; // No default mock user
    
    this.mockTokenData = {
      access_token: 'mock-access-token-12345',
      id_token: 'mock-id-token-67890',
      token_type: 'Bearer',
      expires_in: 3600,
      scope: 'openid profile'
    };
  }

  // Mock login - simulate instant authentication
  async login() {
    console.log('🔧 Mock SSO: Simulating login process...');
    
    // Simulate slight delay for realism
    await new Promise(resolve => setTimeout(resolve, 500));
    
    this.storeTokens(this.mockTokenData);
    console.log('✅ Mock SSO: Login completed successfully');
    console.log('🔧 Mock User Info:', this.mockUser);
    
    return Promise.resolve(this.mockTokenData);
  }

  // Mock logout
  logout() {
    console.log('🔧 Mock SSO: Simulating logout...');
    localStorage.removeItem('mock_token');
    localStorage.removeItem('mock_user_info');
    localStorage.removeItem('mock_id_token');
    console.log('✅ Mock SSO: Logout completed');
  }

  // Mock token storage
  storeTokens(tokenData) {
    console.log('🔧 Mock SSO: Storing tokens...');
    localStorage.setItem('mock_token', tokenData.access_token);
    localStorage.setItem('mock_user_info', JSON.stringify(this.mockUser));
    if (tokenData.id_token) {
      localStorage.setItem('mock_id_token', tokenData.id_token);
    }
  }

  // Mock authentication check
  isAuthenticated() {
    const token = localStorage.getItem('mock_token');
    const hasToken = !!token;
    console.log('🔧 Mock SSO: Authentication check -', hasToken ? '✅ Authenticated' : '❌ Not authenticated');
    return hasToken;
  }

  // Mock user info retrieval
  getUserInfo() {
    const userInfoStr = localStorage.getItem('mock_user_info');
    if (userInfoStr) {
      try {
        const userInfo = JSON.parse(userInfoStr);
        console.log('🔧 Mock SSO: Retrieved user info for', userInfo.email);
        return userInfo;
      } catch (error) {
        console.warn('🔧 Mock SSO: Failed to parse stored user info');
        return null;
      }
    }
    
    // If no stored user info, return null
    console.log('🔧 Mock SSO: No stored user info');
    return null;
  }

  // Mock access token retrieval
  getAccessToken() {
    const token = localStorage.getItem('mock_token');
    if (!token) {
      console.log('🔧 Mock SSO: No stored token, returning default');
      return 'mock-access-token-default';
    }
    return token;
  }

  // Mock ID token retrieval
  getIdToken() {
    return localStorage.getItem('mock_id_token') || 'mock-id-token-default';
  }

  // Mock token expiration check (always valid in mock mode)
  isTokenExpired() {
    console.log('🔧 Mock SSO: Token expiration check - always valid in mock mode');
    return false;
  }

  // Mock callback handling (for compatibility)
  async handleAuthCallback(code, state) {
    console.log('🔧 Mock SSO: Simulating callback handling with code:', code, 'state:', state);
    await new Promise(resolve => setTimeout(resolve, 300));
    
    this.storeTokens(this.mockTokenData);
    console.log('✅ Mock SSO: Callback processed successfully');
    return Promise.resolve(this.mockTokenData);
  }

  // Mock token exchange (for compatibility)
  async exchangeCodeForToken(code, state) {
    console.log('🔧 Mock SSO: Simulating token exchange...');
    return this.handleAuthCallback(code, state);
  }

  // Mock token refresh (always succeeds in mock mode)
  async refreshToken() {
    console.log('🔧 Mock SSO: Simulating token refresh...');
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const newTokenData = {
      ...this.mockTokenData,
      access_token: 'mock-refreshed-token-' + Date.now()
    };
    
    this.storeTokens(newTokenData);
    console.log('✅ Mock SSO: Token refreshed successfully');
    return newTokenData;
  }

  // For compatibility - these methods exist but do nothing meaningful in mock mode
  async generateAuthUrl() {
    console.log('🔧 Mock SSO: Generating mock auth URL...');
    return 'javascript:void(0); // Mock auth URL';
  }

  generateState() {
    return 'mock-state-' + Math.random().toString(36).substr(2, 9);
  }

  validateState(state) {
    console.log('🔧 Mock SSO: Validating state:', state, '- always valid in mock mode');
    return true;
  }

  // Mock user profile update (for testing user management features)
  updateUserProfile(updates) {
    console.log('🔧 Mock SSO: Updating user profile with:', updates);
    const currentUser = this.getUserInfo();
    const updatedUser = { ...currentUser, ...updates };
    localStorage.setItem('mock_user_info', JSON.stringify(updatedUser));
    console.log('✅ Mock SSO: User profile updated');
    return updatedUser;
  }

  // Clear all mock data (for testing)
  clearMockData() {
    console.log('🔧 Mock SSO: Clearing all mock data...');
    localStorage.removeItem('mock_token');
    localStorage.removeItem('mock_user_info');
    localStorage.removeItem('mock_id_token');
    console.log('✅ Mock SSO: All mock data cleared');
  }

  // Get mock service status
  getStatus() {
    return {
      mode: 'mock',
      authenticated: this.isAuthenticated(),
      user: this.getUserInfo()?.email || 'No user',
      token: this.getAccessToken() ? 'Present' : 'Missing',
      timestamp: new Date().toISOString()
    };
  }

  // Auto-initialize if needed (called by auth context)
  async initialize() {
    console.log('🔧 Mock SSO: Initializing mock authentication service...');
    
    // If no token exists, auto-login
    if (!this.isAuthenticated()) {
      console.log('🔧 Mock SSO: No existing authentication, performing auto-login...');
      await this.login();
    } else {
      console.log('🔧 Mock SSO: Existing authentication found');
    }
    
    console.log('✅ Mock SSO: Initialization complete');
    return true;
  }
}

const mockAuthService = new MockAuthService();
export { mockAuthService };
export default mockAuthService;
