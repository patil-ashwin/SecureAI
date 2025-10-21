// src/components/common/Loader/Loader.jsx
import React from 'react';
import styles from './Loader.module.css';

const Loader = ({ 
  size = 'medium', 
  type = 'spinner', 
  text,
  className 
}) => {
  if (type === 'dots') {
    return (
      <div className={`${styles.loadingDots} ${className || ''}`}>
        <span></span>
        <span></span>
        <span></span>
        {text && <span className={styles.text}>{text}</span>}
      </div>
    );
  }

  return (
    <div className={`${styles.loaderContainer} ${className || ''}`}>
      <div className={`${styles.spinner} ${styles[size]}`} />
      {text && <span className={styles.text}>{text}</span>}
    </div>
  );
};

export default Loader;