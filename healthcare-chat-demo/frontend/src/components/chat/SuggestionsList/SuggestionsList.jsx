// src/components/chat/SuggestionsList/SuggestionsList.jsx
import React from 'react';
import { ChevronRight, MessageSquare } from 'lucide-react';
import { Button } from '@components/common';
import styles from './SuggestionsList.module.css';

const SuggestionsList = ({ 
  suggestions = [], 
  onSuggestionClick,
  title = "AI suggested follow-up questions:",
  disabled = false,
  className 
}) => {
  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div className={`${styles.suggestions} ${className || ''}`}>
      <div className={styles.header}>
        <MessageSquare size={14} />
        <span className={styles.title}>{title}</span>
      </div>
      
      <div className={styles.list}>
        {suggestions.map((suggestion, index) => (
          <Button
            key={index}
            variant="ghost"
            onClick={() => onSuggestionClick && onSuggestionClick(suggestion)}
            disabled={disabled}
            className={styles.suggestionItem}
          >
            <ChevronRight size={12} className={styles.arrow} />
            <span className={styles.text}>{suggestion}</span>
          </Button>
        ))}
      </div>
    </div>
  );
};

export default SuggestionsList;