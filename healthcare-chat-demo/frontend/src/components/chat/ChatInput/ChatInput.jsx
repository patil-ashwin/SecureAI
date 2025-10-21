import React, { useRef, useEffect } from 'react';
import styles from './ChatInput.module.css';

const ChatInput = ({ 
  value = '', 
  onChange, 
  onSend, 
  disabled = false, 
  loading = false,
  showFollowUpNotice = false 
}) => {
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [value]);

  const handleChange = (e) => {
    if (onChange) {
      onChange(e.target.value);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!disabled && !loading && value && typeof value === 'string' && value.trim()) {
      onSend();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={styles.inputContainer}>
      <div className={styles.inputWrapper}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.textareaWrapper}>
            <textarea
              ref={textareaRef}
              value={value}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              placeholder={loading ? "Processing your request..." : "Ask anything"}
              className={`${styles.textarea} ${loading ? styles.processing : ''}`}
              disabled={disabled}
              data-testid="chat-input"
              rows={1}
            />
            <button
              type="submit"
              disabled={disabled || loading || !value || typeof value !== 'string' || !value.trim()}
              className={styles.sendBtn}
              data-testid="send-button"
            >
              {loading ? (
                <div className={styles.spinner} />
              ) : (
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z"
                    fill="currentColor"
                  />
                </svg>
              )}
            </button>
          </div>
        </form>
        
      </div>
      
      {showFollowUpNotice && (
        <div className={styles.followUpNotice}>
          <p>💡 Try asking a follow-up question or request more details!</p>
        </div>
      )}
    </div>
  );
};

export default ChatInput;
