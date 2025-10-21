// src/components/auth/OAuthCallback/OAuthCallback.jsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '@contexts';
import styles from './OAuthCallback.module.css';

const OAuthCallback = () => {
  const { handleAuthCallback, login } = useAuth();
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

        await handleAuthCallback(code, state);
        
        // Redirect to main application
        window.location.href = '/';
      } catch (err) {
        console.error('OAuth callback processing error:', err);
        
        // Handle specific OAuth state errors
        if (err.message.includes('Invalid OAuth state') || err.message.includes('state')) {
          setError({
            title: 'Authentication Session Expired',
            message: 'Your login session has expired. Please try signing in again.',
            showRetry: true
          });
        } else {
          setError({
            title: 'Authentication Error',
            message: err.message,
            showRetry: true
          });
        }
        setProcessing(false);
      }
    };

    processCallback();
  }, [handleAuthCallback]);

  const handleRetry = async () => {
    try {
      setProcessing(true);
      setError(null);
      
      // Clear any stale auth data
      localStorage.removeItem('oauth_state');
      localStorage.removeItem('oauth_code_verifier');
      
      // Restart login process
      await login();
    } catch (err) {
      setError({
        title: 'Retry Failed',
        message: 'Unable to restart authentication. Please refresh the page.',
        showRetry: false
      });
      setProcessing(false);
    }
  };

  if (processing) {
    return (
      <div className={styles.callbackContainer}>
        <div className={styles.processingMessage}>
          <div className={styles.spinner}></div>
          <h2>Completing sign-in...</h2>
          <p>Please wait while we authenticate you.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.callbackContainer}>
        <div className={styles.errorMessage}>
          <h2>{error.title}</h2>
          <p>{error.message}</p>
          <div className={styles.errorActions}>
            {error.showRetry && (
              <button onClick={handleRetry} className={styles.retryButton}>
                Try Again
              </button>
            )}
            <button onClick={() => window.location.href = '/'} className={styles.homeButton}>
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default OAuthCallback;