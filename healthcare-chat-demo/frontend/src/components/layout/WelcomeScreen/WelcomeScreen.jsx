import React from 'react';
import MessageList from '../../chat/MessageList';
import styles from './WelcomeScreen.module.css';

const WelcomeScreen = ({ 
  onSend, 
  inputValue, 
  onInputChange, 
  isLoading = false,
  showGreeting = true,
  messages = []
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSend && inputValue && inputValue.trim()) {
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
    <div className={styles.welcomeContainer}>
      {showGreeting && (
        <div className={styles.greetingSection}>
          <h1 className={styles.greetingTitle}>
            Hey John, let's make our data more intelligent!
          </h1>
          <p className={styles.greetingSubtitle}>
            How can I help you today?
          </p>
        </div>
      )}

      {/* Messages Section */}
      {messages && messages.length > 0 && (
        <div className={styles.messagesSection}>
          <MessageList 
            messages={messages}
            isLoading={isLoading}
          />
        </div>
      )}

      {/* Input Section */}
      <div className={styles.inputSection}>
        <form onSubmit={handleSubmit} className={styles.inputForm}>
          <div className={styles.inputWrapper}>
            <input
              type="text"
              value={inputValue || ''}
              onChange={(e) => onInputChange && onInputChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything"
              className={styles.inputField}
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue || !inputValue.trim()}
              className={styles.sendButton}
            >
              {isLoading ? (
                <div className={styles.loadingSpinner} />
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
        
        {/* Progress indicator */}
        {isLoading && (
          <div className={styles.progressIndicator}>
            <div className={styles.progressText}>
              <span className={styles.progressDots}>
                <span></span>
                <span></span>
                <span></span>
              </span>
              We are working on it...
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WelcomeScreen;
