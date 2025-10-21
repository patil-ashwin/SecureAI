// src/components/common/Avatar/Avatar.jsx
import React from 'react';
import { User, Bot } from 'lucide-react';
import styles from './Avatar.module.css';

const Avatar = ({ 
  type = 'user', 
  size = 'medium',
  src,
  alt,
  className 
}) => {
  const avatarClass = `${styles.avatar} ${styles[size]} ${styles[type]} ${className || ''}`;

  if (src) {
    return (
      <div className={avatarClass}>
        <img src={src} alt={alt || 'Avatar'} className={styles.image} />
      </div>
    );
  }

  return (
    <div className={avatarClass}>
      {type === 'assistant' ? (
        <Bot size={size === 'small' ? 14 : size === 'large' ? 20 : 16} />
      ) : (
        <User size={size === 'small' ? 14 : size === 'large' ? 20 : 16} />
      )}
    </div>
  );
};

export default Avatar;