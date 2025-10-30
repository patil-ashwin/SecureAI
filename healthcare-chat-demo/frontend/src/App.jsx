// src/App.jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChatProvider, ThemeProvider, AuthProvider } from '@contexts';
import { Layout } from '@components/layout';
import { MessageList, ChatInput } from '@components/chat';
import { WelcomeScreen } from '@components/layout';
import LoginForm from '@components/LoginForm';
import UserProfile from '@components/UserProfile';
import TimeBasedGreeting from '@components/TimeBasedGreeting';
import OAuthCallback from '@components/auth/OAuthCallback';
import { useChat } from '@hooks';
import styles from './App.module.css';

// Main Chat Interface Component
const ChatInterface = ({ userInfo, onLogout }) => {
  const {
    messages,
    isLoading,
    sendMessage,
    newChat
  } = useChat();

  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSubmit = async (e) => {
    if (e && e.preventDefault) {
      e.preventDefault();
    }
    if (!inputValue || typeof inputValue !== 'string' || !inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setIsTyping(true);
    // Clear input immediately to avoid showing the same text twice (in bubble and in box)
    setInputValue('');

    try {
      await sendMessage(userMessage, {});
    } catch (error) {
      console.error('Error sending message:', error);
      // Keep input empty; the user can retype or use arrow-up to retry
    } finally {
      setIsTyping(false);
    }
  };

  const handleNewChat = () => {
    newChat();
    setInputValue('');
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <h1>SecureAI Healthcare Assistant</h1>
        <button 
          onClick={handleNewChat}
          className={styles.newChatButton}
          disabled={isLoading}
        >
          New Chat
        </button>
      </div>
      
      
      <div className={styles.chatContent}>
        <TimeBasedGreeting userInfo={userInfo} />

        {/* Show messages first so input stays below the latest response */}
        <MessageList 
          messages={messages}
          loading={false}
          isTyping={false}
        />

        {/* Prompt comes after responses */}
        <ChatInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSubmit}
          disabled={isLoading}
          loading={isLoading || isTyping}
          placeholder="Ask anything"
        />

        {/* Show a concise working indicator just below the prompt (left aligned) */}
        {(isLoading || isTyping) && (
          <div className={styles.workingIndicator}>We’re working on it…</div>
        )}
      </div>
    </div>
  );
};

// Main App Component with Authentication
const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = () => {
    const authToken = localStorage.getItem('auth_token');
    const storedUserInfo = localStorage.getItem('user_info');
    
    if (authToken && storedUserInfo) {
      try {
        const user = JSON.parse(storedUserInfo);
        setUserInfo(user);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error parsing stored user info:', error);
        handleLogout();
      }
    }
    setLoading(false);
  };

  const handleLogin = (user) => {
    setUserInfo(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    setUserInfo(null);
    setIsAuthenticated(false);
    // Force page reload to show login page
    window.location.reload();
  };

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className={styles.app} style={{ background: '#1a1a1a', minHeight: '100vh' }}>
        <LoginForm onLogin={handleLogin} onCancel={() => {}} />
      </div>
    );
  }

  return (
    <div className={styles.app}>
      <ChatProvider>
        <ThemeProvider>
          <AuthProvider>
            <Router>
              <Layout>
                <Routes>
                  <Route 
                    path="/" 
                    element={<ChatInterface userInfo={userInfo} onLogout={handleLogout} />} 
                  />
                  <Route path="/welcome" element={<WelcomeScreen />} />
                  <Route path="/oauth/callback" element={<OAuthCallback />} />
                </Routes>
              </Layout>
            </Router>
          </AuthProvider>
        </ThemeProvider>
      </ChatProvider>
    </div>
  );
};

export default App;