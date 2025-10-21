// components/layout/PersistentGreeting/PersistentGreeting.jsx
import React, { useState } from 'react';
import { useAuth } from '@contexts/AuthContext';
import styles from './PersistentGreeting.module.css';

const PersistentGreeting = ({ showOnChat = true }) => {
  const [isVisible, setIsVisible] = useState(true);
  const { userInfo } = useAuth();

  // Get user info from auth context or fallback to default
  const getUserInfo = () => {
    if (userInfo) {
      return {
        firstName: userInfo.given_name || userInfo.name?.split(' ')[0] || 'User'
      };
    }
    
    // Fallback for cases where userInfo is not available
    return {
      firstName: "John"
    };
  };

  const user = getUserInfo();

  const handleDismiss = () => {
    setIsVisible(false);
  };

  if (!isVisible || !showOnChat) {
    return null;
  }

  return (
    <div className={styles.greetingBanner}>
      <div className={styles.greetingContent}>
        <div className={styles.greetingText}>
          <span className={styles.greetingMain}>
            Hey {user.firstName}, let's make our data intelligent!
          </span>
          <span className={styles.greetingSecondary}>
            How can I help you today?
          </span>
        </div>
        <button 
          className={styles.dismissBtn}
          onClick={handleDismiss}
          aria-label="Dismiss greeting"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default PersistentGreeting;