import React, { useState, useEffect } from 'react';
import styles from './LoadingIndicator.module.css';

const loadingMessages = [
  "Analyzing fraud patterns...",
  "Processing ring data...",
  "Examining transaction networks...",
  "Identifying connections...",
  "Generating insights...",
  "Preparing response..."
];

const LoadingIndicator = ({ showMessages = false }) => {
  const [currentMessage, setCurrentMessage] = useState(0);

  useEffect(() => {
    if (!showMessages) return;

    const interval = setInterval(() => {
      setCurrentMessage(prev => (prev + 1) % loadingMessages.length);
    }, 1500);

    return () => clearInterval(interval);
  }, [showMessages]);

  return (
    <div className={styles.loadingContainer}>
      <div className={styles.loadingContent}>
        <div className={styles.loadingDots}>
          <div className={styles.dot}></div>
          <div className={styles.dot}></div>
          <div className={styles.dot}></div>
        </div>
        <div className={styles.loadingText}>
          {showMessages ? loadingMessages[currentMessage] : "Analyzing..."}
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;
