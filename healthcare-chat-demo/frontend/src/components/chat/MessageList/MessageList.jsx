import React, { useEffect, useRef, useState } from 'react';
import styles from './MessageList.module.css';
import MessageBubble from '../MessageBubble';

const MessageList = ({ 
  messages = [], 
  loading = false,
  onSuggestionClick,
  onParameterSubmit,
  className 
}) => {
  const bottomRef = useRef(null);
  const containerRef = useRef(null);
  const [userScrolled, setUserScrolled] = useState(false);
  const prevMessagesLength = useRef(messages.length);

  // Track if user manually scrolled up
  const handleScroll = () => {
    if (!containerRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    
    // If user scrolls up, mark as manually scrolled
    if (!isAtBottom && !loading) {
      setUserScrolled(true);
    } else if (isAtBottom) {
      setUserScrolled(false);
    }
  };

  // Auto-scroll to bottom only for new messages and if user hasn't scrolled up
  useEffect(() => {
    // Only auto-scroll if:
    // 1. Not manually scrolled by user, OR
    // 2. A new message was added (not just loading state change)
    const newMessageAdded = messages.length > prevMessagesLength.current;
    
    if (bottomRef.current && (!userScrolled || newMessageAdded)) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
      if (newMessageAdded) {
        setUserScrolled(false);
      }
    }
    
    prevMessagesLength.current = messages.length;
  }, [messages, loading, userScrolled]);

  return (
    <div 
      ref={containerRef}
      className={styles.messageList}
      onScroll={handleScroll}
    >
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          onSuggestionClick={onSuggestionClick}
          onParameterSubmit={onParameterSubmit}
        />
      ))}
      
      {loading && (
        <div className={styles.loadingMessage}>
          <div className={styles.messageRow}>
            <div className={styles.messageContainer}>
              <div className={styles.loadingContent}>
                <div className={styles.loadingDots}>
                  <div className={styles.dot}></div>
                  <div className={styles.dot}></div>
                  <div className={styles.dot}></div>
                </div>
                <div className={styles.loadingText}>
                  {loading ? 'Processing your request...' : 'Analyzing...'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Invisible element to scroll to */}
      <div ref={bottomRef} />
    </div>
  );
};

export default MessageList;
