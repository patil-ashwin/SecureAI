// src/components/auth/OAuthCallback.jsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '@contexts/AuthContext';

const OAuthCallback = () => {
  const { handleAuthCallback } = useAuth();
  const [error, setError] = useState(null);
  const [processing, setProcessing] = useState(true);

  useEffect(() => {
    const processCallback = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');

        if (error) {
          throw new Error(`OAuth error: ${error}`);
        }

        if (!code || !state) {
          throw new Error('Missing authorization code or state');
        }

        console.log('🔐 Processing OAuth callback...');
        await handleAuthCallback(code, state);
        
        // Clear URL parameters and redirect to main app
        window.history.replaceState({}, document.title, window.location.pathname);
        window.location.reload();
      } catch (err) {
        console.error('OAuth callback processing error:', err);
        setError(err.message);
        setProcessing(false);
      }
    };

    processCallback();
  }, [handleAuthCallback]);

  if (processing) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        gap: '20px'
      }}>
        <div style={{ 
          width: '40px', 
          height: '40px', 
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #3498db',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <p>Processing authentication...</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        gap: '20px'
      }}>
        <div style={{ color: 'red', fontSize: '18px' }}>❌ Authentication Error</div>
        <div style={{ color: '#666' }}>{error}</div>
        <button 
          onClick={() => window.location.href = '/'}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3498db',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Return to Home
        </button>
      </div>
    );
  }

  return null;
};

export default OAuthCallback;
