import React from 'react';
import styles from './MessageBubble.module.css';
import ExportDownload from '../../ExportDownload';
import { formatAnalysisText, extractRingId, isRingAnalysis } from '../../../utils/textFormatter';

const MessageBubble = ({ 
  message, 
  onSuggestionClick,
  onParameterSubmit,
  showAvatar = true,
  className 
}) => {
  const isUser = message.type === 'user';
  const isAssistant = message.type === 'assistant';
  const isSystem = message.type === 'system';
  const isError = message.type === 'error';

  const messageClass = `${styles.message} ${styles[message.type]} ${className || ''}`;

  // Check if this message contains ring analysis
  const hasRingAnalysis = isRingAnalysis(message.content);
  const ringId = hasRingAnalysis ? extractRingId(message.content) : null;

  // Create export data structure for ExportDownload component
  const createExportData = (ringId, messageText) => {
    if (!ringId || !messageText) return null;
    
    return {
      success: true,
      ring_id: ringId,
      generated_at: new Date().toISOString(),
      pdf_data: null, // Will trigger demo download
      excel_data: null, // Will trigger demo download
      pdf_filename: `Ring_${ringId}_Analysis.pdf`,
      excel_filename: `Ring_${ringId}_Data.xlsx`,
      note: 'Demo version - contains sample data for testing purposes'
    };
  };

  const renderContent = () => {
    if (isUser) {
      return message.content;
    } else if (isError) {
      return <span className={styles.errorText}>{message.content}</span>;
    } else {
      // Format assistant/system messages with proper HTML and professional styling
      const formattedText = formatAnalysisText(message.content);
      
      return (
        <div>
          {/* Professional content container with border */}
          <div style={professionalStyles.contentContainer}>
            <div 
              style={professionalStyles.contentInner}
              dangerouslySetInnerHTML={{ __html: formattedText }} 
            />
            
            {/* Add export functionality for ring analysis */}
            {hasRingAnalysis && ringId && (
              <ExportDownload 
                exportData={createExportData(ringId, message.content)}
                loading={false}
              />
            )}
          </div>
        </div>
      );
    }
  };

  const formatTimestamp = (timestamp) => {
    try {
      return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch {
      return '';
    }
  };

  return (
    <div className={messageClass}>
      <div className={styles.messageRow}>
        <div className={styles.messageContainer}>
          <div className={styles.messageContent}>
            {renderContent()}
          </div>
          
          {/* Show suggestions if available */}
          {message.suggestions && message.suggestions.length > 0 && onSuggestionClick && (
            <div style={professionalStyles.suggestionsContainer}>
              <div style={professionalStyles.suggestionsHeader}>
                <div style={professionalStyles.suggestionsIcon}>💡</div>
                <span style={professionalStyles.suggestionsTitle}>AI Suggested Follow-up Questions</span>
              </div>
              <div style={professionalStyles.suggestionsList}>
                {message.suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => onSuggestionClick(suggestion)}
                    style={professionalStyles.suggestionButton}
                    onMouseOver={(e) => {
                      e.target.style.background = '#333333';
                      e.target.style.borderColor = '#555555';
                      e.target.style.transform = 'translateY(-1px)';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.background = '#262626';
                      e.target.style.borderColor = '#404040';
                      e.target.style.transform = 'translateY(0)';
                    }}
                  >
                    <div style={professionalStyles.suggestionNumber}>{index + 1}</div>
                    <span style={professionalStyles.suggestionText}>{suggestion}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
          
          <div className={styles.messageTime}>
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
      </div>
    </div>
  );
};

// Professional styling for content and suggestions
const professionalStyles = {
  contentContainer: {
    border: '1px solid #404040',
    borderRadius: '12px',
    background: 'linear-gradient(145deg, #1a1a1a 0%, #1e1e1e 100%)',
    padding: '0',
    overflow: 'hidden',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)'
  },
  contentInner: {
    padding: '24px',
    color: '#ececec',
    lineHeight: '1.7',
    fontSize: '15px',
    fontFamily: '"Söhne", ui-sans-serif, system-ui, -apple-system, sans-serif',
    // Enhanced text styling
    '& h3': {
      color: '#10a37f',
      fontSize: '18px',
      fontWeight: '600',
      marginBottom: '16px',
      marginTop: '24px',
      paddingBottom: '8px',
      borderBottom: '1px solid #333333'
    },
    '& p': {
      marginBottom: '16px',
      color: '#ececec'
    },
    '& strong': {
      color: '#ffffff',
      fontWeight: '600'
    },
    '& ul, & ol': {
      paddingLeft: '20px',
      marginBottom: '16px'
    },
    '& li': {
      marginBottom: '8px',
      color: '#d1d5db'
    }
  },
  suggestionsContainer: {
    borderTop: '1px solid #333333',
    padding: '20px 24px',
    background: '#1a1a1a'
  },
  suggestionsHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '16px'
  },
  suggestionsIcon: {
    fontSize: '20px'
  },
  suggestionsTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#10a37f'
  },
  suggestionsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  suggestionButton: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    background: '#262626',
    border: '1px solid #404040',
    borderRadius: '10px',
    padding: '16px',
    color: '#ececec',
    cursor: 'pointer',
    textAlign: 'left',
    fontSize: '14px',
    transition: 'all 0.2s ease',
    lineHeight: '1.5'
  },
  suggestionNumber: {
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    background: '#10a37f',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    fontWeight: '600',
    flexShrink: 0,
    marginTop: '2px'
  },
  suggestionText: {
    flex: 1,
    color: '#d1d5db'
  }
};

export default MessageBubble;