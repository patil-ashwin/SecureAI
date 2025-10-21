// src/services/auth/ssoService.js
import { SSO_CONFIG } from '@config';

class SSOService {
    constructor() {
        this.config = SSO_CONFIG;
    }

    // Generate random string for code verifier
    generateCodeVerifier() {
        const array = new Uint8Array(32);
        crypto.getRandomValues(array);
        return this.base64URLEncode(array);
    }

    // Create code challenge from verifier
    async generateCodeChallenge(verifier) {
        const encoder = new TextEncoder();
        const data = encoder.encode(verifier);
        const digest = await crypto.subtle.digest('SHA-256', data);
        return this.base64URLEncode(new Uint8Array(digest));
    }

    // Base64 URL encode (without padding)
    base64URLEncode(array) {
        return btoa(String.fromCharCode.apply(null, array))
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=/g, '');
    }

    // Generate OAuth authorization URL with PKCE
    async generateAuthUrl() {
        // Generate PKCE parameters
        const codeVerifier = this.generateCodeVerifier();
        const codeChallenge = await this.generateCodeChallenge(codeVerifier);
        const state = this.generateState();

        // Store code verifier for later use
        localStorage.setItem('oauth_code_verifier', codeVerifier);

        const params = new URLSearchParams({
            client_id: this.config.OAUTH_CLIENT_ID,
            redirect_uri: this.config.OAUTH_REDIRECT_URL,
            response_type: 'code',
            scope: this.config.OAUTH_SCOPES,
            state: state,
            code_challenge: codeChallenge,
            code_challenge_method: 'S256'
        });

        return `${this.config.OAUTH_AUTHORIZATION_ENDPOINT}?${params.toString()}`;
    }

    // Generate and store state for CSRF protection
    generateState() {
        const state = Math.random().toString(36).substring(2, 15) +
            Math.random().toString(36).substring(2, 15);
        localStorage.setItem('oauth_state', state);
        return state;
    }

    // Validate OAuth state
    validateState(receivedState) {
        const storedState = localStorage.getItem('oauth_state');

        if (!storedState) {
            console.warn('No stored OAuth state found');
            return false;
        }

        if (!receivedState) {
            console.warn('No received OAuth state');
            return false;
        }

        // Clean up stored state
        localStorage.removeItem('oauth_state');

        const isValid = storedState === receivedState;
        if (!isValid) {
            console.warn('OAuth state mismatch:', { stored: storedState, received: receivedState });
        }

        return isValid;
    }

    // Exchange authorization code for access token with PKCE
    async exchangeCodeForToken(code, state) {
        if (!this.validateState(state)) {
            throw new Error('Invalid OAuth state');
        }

        // Get stored code verifier
        const codeVerifier = localStorage.getItem('oauth_code_verifier');
        localStorage.removeItem('oauth_code_verifier');

        if (!codeVerifier) {
            throw new Error('Missing code verifier');
        }

        const params = new URLSearchParams({
            grant_type: 'authorization_code',
            client_id: this.config.OAUTH_CLIENT_ID,
            code: code,
            redirect_uri: this.config.OAUTH_REDIRECT_URL,
            code_verifier: codeVerifier
        });

        try {
            const response = await fetch(this.config.OAUTH_TOKEN_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: params.toString()
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Token exchange failed:', errorData);
                throw new Error(`Token exchange failed: ${response.status}`);
            }

            const tokenData = await response.json();
            
            // Store tokens
            this.storeTokens(tokenData);
            
            // Fetch and store user info
            await this.fetchAndStoreUserInfo(tokenData.access_token);
            
            return tokenData;
        } catch (error) {
            console.error('Token exchange error:', error);
            throw error;
        }
    }

    // Store tokens securely
    storeTokens(tokenData) {
        if (tokenData.access_token) {
            localStorage.setItem(this.config.TOKEN_STORAGE_KEY, tokenData.access_token);
        }
        if (tokenData.id_token) {
            localStorage.setItem('bart_id_token', tokenData.id_token);
        }
        if (tokenData.refresh_token) {
            localStorage.setItem('bart_refresh_token', tokenData.refresh_token);
        }
    }

    // Fetch user info from OAuth provider
    async fetchAndStoreUserInfo(accessToken) {
        try {
            const response = await fetch('https://it-sso.us.bank-dns.com/idp/userinfo.openid', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch user info: ${response.status}`);
            }

            const userInfo = await response.json();
            localStorage.setItem(this.config.USER_INFO_STORAGE_KEY, JSON.stringify(userInfo));
            
            console.log('✅ SSO User Info stored:', userInfo);
            return userInfo;
        } catch (error) {
            console.error('Failed to fetch user info:', error);
            // Don't throw - user can still use the app without detailed user info
            return null;
        }
    }

    // Check if user is authenticated
    isAuthenticated() {
        const token = this.getAccessToken();
        return !!token;
    }

    // Get stored access token
    getAccessToken() {
        return localStorage.getItem(this.config.TOKEN_STORAGE_KEY);
    }

    // Get stored user info
    getUserInfo() {
        const userInfoStr = localStorage.getItem(this.config.USER_INFO_STORAGE_KEY);
        if (userInfoStr) {
            try {
                return JSON.parse(userInfoStr);
            } catch (error) {
                console.error('Failed to parse user info:', error);
                return null;
            }
        }
        return null;
    }

    // Check if token is expired (basic check)
    isTokenExpired() {
        const token = this.getAccessToken();
        if (!token) return true;

        try {
            // Basic JWT expiration check (if token is JWT)
            const payload = JSON.parse(atob(token.split('.')[1]));
            const now = Math.floor(Date.now() / 1000);
            return payload.exp < now;
        } catch (error) {
            // If we can't parse the token, assume it's valid (might not be JWT)
            return false;
        }
    }

    // Logout user
    logout() {
        localStorage.removeItem(this.config.TOKEN_STORAGE_KEY);
        localStorage.removeItem(this.config.USER_INFO_STORAGE_KEY);
        localStorage.removeItem('bart_id_token');
        localStorage.removeItem('bart_refresh_token');
        localStorage.removeItem('oauth_state');
        localStorage.removeItem('oauth_code_verifier');
        
        console.log('🔓 SSO: User logged out');
    }

    // Initiate OAuth login
    async login() {
        try {
            console.log('🔐 SSO: Initiating login...');
            const authUrl = await this.generateAuthUrl();
            console.log('🔐 SSO: Redirecting to:', authUrl);
            window.location.href = authUrl;
        } catch (error) {
            console.error('SSO Login error:', error);
            throw error;
        }
    }

    // Refresh access token if refresh token is available
    async refreshToken() {
        const refreshToken = localStorage.getItem('bart_refresh_token');
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const params = new URLSearchParams({
            grant_type: 'refresh_token',
            client_id: this.config.OAUTH_CLIENT_ID,
            refresh_token: refreshToken
        });

        try {
            const response = await fetch(this.config.OAUTH_TOKEN_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: params.toString()
            });

            if (!response.ok) {
                throw new Error(`Token refresh failed: ${response.status}`);
            }

            const tokenData = await response.json();
            this.storeTokens(tokenData);
            
            return tokenData;
        } catch (error) {
            console.error('Token refresh error:', error);
            // If refresh fails, logout user
            this.logout();
            throw error;
        }
    }

    // Handle auth callback (for use in callback component)
    async handleAuthCallback(code, state) {
        return await this.exchangeCodeForToken(code, state);
    }
}

const ssoService = new SSOService();
export { ssoService };
export default ssoService;
