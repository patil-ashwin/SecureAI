import React, { useState, useEffect } from 'react';
import styles from './ProgressIndicator.module.css';

const loadingMessages = [
  "Analyzing fraud patterns...",
  "Processing ring data...",
  "Examining transaction networks...",
  "Identifying suspicious connections...",
  "Generating insights...",
  "Preparing comprehensive analysis...",
  "Connecting data points...",
  "Validating findings...",
  "Finalizing report..."
];

const ProgressIndicator = ({ isVisible, duration = 5000 }) => {
  const [currentMessage, setCurrentMessage] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isVisible) {
      setCurrentMessage(0);
      setProgress(0);
      return;
    }

    // Progress bar animation
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + (100 / (duration / 100));
      });
    }, 100);

    // Message rotation
    const messageInterval = setInterval(() => {
      setCurrentMessage(prev => (prev + 1) % loadingMessages.length);
    }, duration / loadingMessages.length);

    return () => {
      clearInterval(progressInterval);
      clearInterval(messageInterval);
    };
  }, [isVisible, duration]);

  if (!isVisible) return null;

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <div className={styles.messageContainer}>
          <div className={styles.spinnerContainer}>
            <div className={styles.spinner}>
              <div className={styles.spinnerInner}></div>
            </div>
          </div>
          <div className={styles.message}>
            {loadingMessages[currentMessage]}
          </div>
        </div>
        
        <div className={styles.progressContainer}>
          <div className={styles.progressBar}>
            <div 
              className={styles.progressFill} 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className={styles.progressText}>
            {Math.round(progress)}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator;
