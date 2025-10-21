// src/components/SmartChatInterface.jsx
/**
 * Smart Chat Interface with automatic export routing
 * Replace your existing chat component with this enhanced version
 */

import React, { useState, useRef, useEffect } from 'react';
import { useSmartQuery } from '../hooks/useSmartQuery';

const SmartChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [currentQuery, setCurrentQuery] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  
  const {
    loading,
    error,
    executeQuery,
    analyzeQuery,
    handleExportDownload,
    clearError,
    getSuggestions,
    isExportQuery
  } = useSmartQuery();

  // Generate session ID on mount
  useEffect(() => {
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  }, []);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Clear error when user starts typing
  useEffect(() => {
    if (error && currentQuery.trim()) {
      clearError();
    }
  }, [currentQuery, error, clearError]);

  /**
   * Handle query submission with smart routing
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!currentQuery.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: currentQuery.trim(),
      timestamp: new Date()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    
    // Analyze query before executing
    const analysis = analyzeQuery(currentQuery);
    
    // Add analysis info if it's an export query
    if (analysis.isExport) {
      const analysisMessage = {
        id: Date.now() + 1,
        type: 'system',
        content: `🔄 Detected export request for Ring ${analysis.payload.ring_id} (${analysis.payload.format})`,
        timestamp: new Date(),
        isExportInfo: true
      };
      setMessages(prev => [...prev, analysisMessage]);
    }

    const query = currentQuery;
    setCurrentQuery('');

    try {
      const result = await executeQuery(query, { sessionId });
      
      // Handle export results
      if (result._exportMetadata?.isDirectExport) {
        await handleExportResult(result);
      } else {
        // Handle regular query results
        await handleQueryResult(result);
      }

    } catch (err) {
      console.error('Query execution failed:', err);
      
      const errorMessage = {
        id: Date.now(),
        type: 'error',
        content: `❌ Error: ${err.message}`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  /**
   * Handle export-specific results
   */
  const handleExportResult = async (result) => {
    const ringId = result._exportMetadata.ringId;
    const format = result._exportMetadata.format;

    if (result.success) {
      // Success message
      const successMessage = {
        id: Date.now(),
        type: 'assistant',
        content: `✅ Export generated successfully for Ring ${ringId}!`,
        timestamp: new Date(),
        isExport: true,
        exportData: result
      };
      
      setMessages(prev => [...prev, successMessage]);

      // Auto-download files
      const downloadSuccess = handleExportDownload(result);
      
      if (downloadSuccess) {
        const downloadMessage = {
          id: Date.now() + 1,
          type: 'system',
          content: `📥 Download started for Ring ${ringId} (${format})`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, downloadMessage]);
      }

    } else {
      // Error message with note if available
      const errorContent = result.error || 'Export generation failed';
      const noteContent = result.note ? `\n\n💡 ${result.note}` : '';
      
      const errorMessage = {
        id: Date.now(),
        type: 'error',
        content: `❌ ${errorContent}${noteContent}`,
        timestamp: new Date(),
        isExport: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  /**
   * Handle regular query results
   */
  const handleQueryResult = async (result) => {
    const responseMessage = {
      id: Date.now(),
      type: 'assistant',
      content: result.explanation || 'Query processed successfully',
      timestamp: new Date(),
      queryData: result
    };
    
    setMessages(prev => [...prev, responseMessage]);

    // Add suggested questions if available
    if (result.suggested_questions?.length > 0) {
      const suggestionsMessage = {
        id: Date.now() + 1,
        type: 'suggestions',
        content: result.suggested_questions,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, suggestionsMessage]);
    }
  };

  /**
   * Handle suggestion click
   */
  const handleSuggestionClick = (suggestion) => {
    setCurrentQuery(suggestion);
  };

  /**
   * Get input placeholder based on current analysis
   */
  const getPlaceholder = () => {
    if (currentQuery.trim()) {
      const analysis = analyzeQuery(currentQuery);
      if (analysis.isExport) {
        return `Export detected: Ring ${analysis.payload.ring_id} (${analysis.payload.format})`;
      }
    }
    return 'Ask about fraud rings, export reports, or analyze data...';
  };

  /**
   * Render individual message
   */
  const renderMessage = (message) => {
    const baseClasses = "p-4 rounded-lg max-w-[80%] break-words";
    
    switch (message.type) {
      case 'user':
        return (
          <div key={message.id} className="flex justify-end mb-4">
            <div className={`${baseClasses} bg-blue-500 text-white ml-auto`}>
              {message.content}
            </div>
          </div>
        );
        
      case 'assistant':
        return (
          <div key={message.id} className="flex justify-start mb-4">
            <div className={`${baseClasses} bg-gray-100 text-gray-800`}>
              {message.isExport && <span className="text-green-600 font-medium">📊 Export Result: </span>}
              {message.content}
              
              {/* Export download buttons */}
              {message.exportData && message.exportData.success && (
                <div className="mt-3 flex gap-2">
                  {message.exportData.pdf_data && (
                    <button
                      onClick={() => handleExportDownload(message.exportData)}
                      className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                    >
                      📄 Download PDF
                    </button>
                  )}
                  {message.exportData.excel_data && (
                    <button
                      onClick={() => handleExportDownload(message.exportData)}
                      className="px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600"
                    >
                      📊 Download Excel
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        );
        
      case 'system':
        return (
          <div key={message.id} className="flex justify-center mb-2">
            <div className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm">
              {message.content}
            </div>
          </div>
        );
        
      case 'error':
        return (
          <div key={message.id} className="flex justify-start mb-4">
            <div className={`${baseClasses} bg-red-50 text-red-700 border border-red-200`}>
              {message.content}
            </div>
          </div>
        );
        
      case 'suggestions':
        return (
          <div key={message.id} className="flex justify-start mb-4">
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">💡 Suggested queries:</p>
              <div className="flex flex-wrap gap-2">
                {message.content.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="px-3 py-1 bg-white border border-gray-200 rounded text-sm hover:bg-gray-100 text-left"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-[600px] border border-gray-300 rounded-lg">
      {/* Header */}
      <div className="bg-gray-100 p-4 border-b border-gray-300 rounded-t-lg">
        <h3 className="font-semibold text-gray-800">Smart Fraud Analysis Chat</h3>
        <p className="text-sm text-gray-600">
          🚀 Now with smart export detection! Try: "export ring 123456"
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="mb-4">👋 Welcome! Ask me about fraud rings or export reports.</p>
            <div className="space-y-2">
              <p className="text-sm font-medium">Try these examples:</p>
              <div className="flex flex-col items-center gap-2">
                {[
                  'export ring 4534534',
                  'download ring 123456 as PDF',
                  'explain ring 4534534',
                  'generate Excel report for ring 789'
                ].map((example, idx) => (
                  <button
                    key={idx}
                    onClick={() => setCurrentQuery(example)}
                    className="px-4 py-2 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 text-sm"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {messages.map(renderMessage)}
        
        {loading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 p-4 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                <span className="text-gray-600">
                  {isExportQuery(currentQuery) ? 'Generating export...' : 'Processing query...'}
                </span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-300 p-4">
        {error && (
          <div className="mb-3 p-2 bg-red-50 text-red-700 rounded text-sm">
            ❌ {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={currentQuery}
            onChange={(e) => setCurrentQuery(e.target.value)}
            placeholder={getPlaceholder()}
            disabled={loading}
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!currentQuery.trim() || loading}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '⏳' : '🚀'}
          </button>
        </form>
        
        {/* Query analysis preview */}
        {currentQuery.trim() && (
          <div className="mt-2 text-xs text-gray-500">
            {isExportQuery(currentQuery) ? (
              <span className="text-green-600">🔄 Export query detected</span>
            ) : (
              <span>💬 Regular query</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SmartChatInterface;