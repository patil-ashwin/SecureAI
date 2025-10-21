// src/contexts/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { ssoService } from '@services/auth';
import { SSO_CONFIG } from '@config';

const AuthContext = createContext();

export { AuthContext };

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      console.log('🔐 Initializing authentication...');
      console.log('🔐 SSO_CONFIG.ENABLE_SSO:', SSO_CONFIG.ENABLE_SSO);
      console.log('🔐 Environment REACT_APP_ENABLE_SSO:', process.env.REACT_APP_ENABLE_SSO);
      
      if (SSO_CONFIG.ENABLE_SSO) {
        // Real SSO mode - check if user is already authenticated
        console.log('🔐 Real SSO mode - checking existing authentication...');
        checkAuthentication();
      } else {
        // Mock mode - ensure mock service is initialized
        console.log('🔧 Mock SSO mode - initializing mock authentication...');
        
        if (ssoService.initialize) {
          await ssoService.initialize();
        } else if (!ssoService.isAuthenticated()) {
          await ssoService.login();
        }
        
        checkAuthentication();
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      setLoading(false);
    }
  };

  const checkAuthentication = () => {
    // Check our custom login system first
    const authToken = localStorage.getItem('auth_token');
    const storedUserInfo = localStorage.getItem('user_info');
    
    if (authToken && storedUserInfo) {
      try {
        const user = JSON.parse(storedUserInfo);
        console.log('🔐 Custom login user found:', user);
        setIsAuthenticated(true);
        setUserInfo(user);
        setLoading(false);
        return;
      } catch (error) {
        console.error('Error parsing stored user info:', error);
        // Clear invalid data
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_info');
        localStorage.removeItem('user_role');
        localStorage.removeItem('username');
      }
    }
    
    // Fallback to SSO service
    const authenticated = ssoService.isAuthenticated();
    const user = ssoService.getUserInfo();
    
    console.log('🔐 Authentication check:', { authenticated, user: user?.email || 'No user info' });
    
    setIsAuthenticated(authenticated);
    setUserInfo(user);
    setLoading(false);
    
    if (!SSO_CONFIG.ENABLE_SSO && authenticated) {
      console.log('🔧 Mock SSO User:', user);
    } else if (SSO_CONFIG.ENABLE_SSO && authenticated) {
      console.log('✅ Real SSO User authenticated:', user?.email || user?.name || 'Unknown');
    } else if (SSO_CONFIG.ENABLE_SSO && !authenticated) {
      console.log('🔐 Real SSO: User not authenticated');
    }
  };

  const login = async () => {
    try {
      console.log('🔐 Login initiated...');
      setLoading(true);
      
      await ssoService.login();
      
      if (!SSO_CONFIG.ENABLE_SSO) {
        // In mock mode, login is instant
        console.log('🔧 Mock login completed');
        checkAuthentication();
      }
      // In real SSO mode, user will be redirected and callback will handle auth
    } catch (error) {
      console.error('Login error:', error);
      setLoading(false);
    }
  };

  const logout = () => {
    console.log('🔓 Logout initiated...');
    
    // Clear our custom login data
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    
    ssoService.logout();
    setIsAuthenticated(false);
    setUserInfo(null);
    
    // Always reload page to show login page
    window.location.reload();
  };

  const handleAuthCallback = async (code, state) => {
    try {
      console.log('🔐 Handling auth callback...');
      setLoading(true);
      
      await ssoService.exchangeCodeForToken(code, state);
      checkAuthentication();
      
      console.log('✅ Auth callback completed successfully');
    } catch (error) {
      console.error('Auth callback error:', error);
      setLoading(false);
      throw error;
    }
  };

  const refreshAuth = async () => {
    try {
      if (SSO_CONFIG.ENABLE_SSO && ssoService.refreshToken) {
        await ssoService.refreshToken();
        checkAuthentication();
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
    }
  };

  const value = {
    isAuthenticated,
    userInfo,
    loading,
    login,
    logout,
    handleAuthCallback,
    refreshAuth,
    getAccessToken: () => ssoService.getAccessToken(),
    isMockMode: !SSO_CONFIG.ENABLE_SSO,  // Expose mock mode status
    isRealSSO: SSO_CONFIG.ENABLE_SSO     // Expose real SSO status
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
