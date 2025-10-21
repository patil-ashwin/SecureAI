import { getFullUrl } from '@config/api';
// components/layout/Layout/Layout.jsx
import React, { useState, useEffect } from 'react';
import { useChat } from '@contexts';
import { useAuth } from '@contexts';
import { chatHistoryService } from "@services/chatHistoryService";
import modelsService from "@services/models/modelsService";
import { APP_CONFIG } from '@config/app.config';
import styles from './Layout.module.css';

const Layout = ({ children, configs = [], onNewChat }) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [showUserProfile, setShowUserProfile] = useState(false);
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [searchValue, setSearchValue] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [models, setModels] = useState({ llm_models: [], current_llm_model: null });
  
  // Context menu state
  const [contextMenuChatId, setContextMenuChatId] = useState(null);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });

  const { currentSession, messages, clearMessages, setSession, addMessage } = useChat();
  const { userInfo, logout, isMockMode } = useAuth();

  // Fetch models from backend or use APP_CONFIG
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await modelsService.getModels();
        setModels({
          llm_models: response.llm_models || [],
          current_llm_model: response.current_llm_model || null
        });
        if (response.current_llm_model) {
          setSelectedModel(response.current_llm_model);
        }
      } catch (error) {
        console.error("Failed to fetch models, using APP_CONFIG:", error);
        // Use models from APP_CONFIG as fallback
        const configModels = [
          {
            id: 'chat',
            name: `${APP_CONFIG.models.chat.name}`,
            description: `${APP_CONFIG.models.chat.provider} - For NLP & Chat`
          },
          {
            id: 'embeddings',
            name: `${APP_CONFIG.models.embeddings.name}`,
            description: `${APP_CONFIG.models.embeddings.provider} - ${APP_CONFIG.models.embeddings.dimensions}D Embeddings`
          }
        ];
        setModels({
          llm_models: configModels,
          current_llm_model: 'chat'
        });
        setSelectedModel('chat');
      }
    };
    fetchModels();
  }, []);

  // Load chat history from service on mount
  // Handle model selection
  const handleModelSelect = (modelId) => {
    setSelectedModel(modelId);
    setShowModelDropdown(false);
  };

  // Get current model info with better description
  const currentModel = models.llm_models.find(m => m.id === selectedModel) || 
    { id: selectedModel, name: selectedModel, description: "Most capable model" };

  // Helper function to get model description
  const getModelDescription = (model) => {
    if (model.description) return model.description;
    
    // Generate descriptions based on model name/type
    const name = model.name || model.id || '';
    if (name.toLowerCase().includes('gpt-4')) {
      return 'Most capable model for complex reasoning';
    } else if (name.toLowerCase().includes('gpt-3.5')) {
      return 'Fast and cost-effective model';
    } else if (name.toLowerCase().includes('claude')) {
      return 'Advanced AI assistant with strong reasoning';
    } else if (name.toLowerCase().includes('azure')) {
      return 'Azure OpenAI powered model';
    } else if (name.toLowerCase().includes('bedrock')) {
      return 'AWS Bedrock powered model';
    } else {
      return 'AI language model';
    }
  };

  useEffect(() => {
    const savedHistory = chatHistoryService.getChatHistory();
    setChatHistory(savedHistory);
  }, []);

  // Update current session in chat history when messages change
  useEffect(() => {
    if (currentSession && messages.length > 0) {
      const userMessage = messages.find(msg => msg.type === 'user');
      if (userMessage) {
        const updatedChat = chatHistoryService.addOrUpdateChat(currentSession, userMessage.text, messages);
        setChatHistory(prev => {
          const newHistory = [...prev];
          const existingIndex = newHistory.findIndex(chat => chat.id === currentSession);
          
          if (existingIndex >= 0) {
            newHistory[existingIndex] = updatedChat;
          } else {
            newHistory.unshift(updatedChat);
          }
          
          // Mark other chats as inactive
          newHistory.forEach(chat => {
            if (chat.id !== currentSession) {
              chat.isActive = false;
            }
          });
          
          return newHistory;
        });
      }
    }
  }, [currentSession, messages]);

  // Handle clicking outside to close dropdowns
  useEffect(() => {
    const handleClickOutside = () => {
      setContextMenuChatId(null);
      setShowModelDropdown(false);
    };

    if (contextMenuChatId || showModelDropdown) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [contextMenuChatId, showModelDropdown]);

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  const handleNewChat = () => {
    if (onNewChat) {
      onNewChat();
    }
    setSelectedChatId(null);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Check file type
    const allowedTypes = [".pdf", ".doc", ".docx", ".txt", ".json"];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedTypes.includes(fileExtension)) {
      alert("Please select a valid file type: PDF, DOC, DOCX, TXT, or JSON");
      return;
    }

    // Check file size (max 10MB)
    if (file.size > 5 * 1024 * 1024) {
      alert("File size must be less than 5MB");
      return;
    }

    try {
      // Create FormData for file upload with required fields
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', file.name); // Use filename as title
      formData.append('source', 'web_upload'); // Set source as web upload
      formData.append('metadata', JSON.stringify({
        uploaded_at: new Date().toISOString(),
        file_size: file.size,
        file_type: fileExtension
      }));

      // Show loading state
      console.log('Uploading file:', file.name);
      addMessage({ type: 'system', content: `📤 Uploading "${file.name}"...` });

      // Upload file to backend
      const response = await fetch(getFullUrl('UPLOAD'), {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      console.log('Upload successful:', result);

      // Add concise success message
      const successMessage = `✅ Document "${file.name}" uploaded successfully (${(file.size / 1024).toFixed(1)} KB) - Ready for analysis`;
      
      // Add success message with debugging
      console.log('Adding success message to chat:', successMessage);
      addMessage({ type: 'system', content: successMessage });
      
      // Force a small delay to ensure message is added
      setTimeout(() => {
        console.log('Success message should now be visible');
      }, 100);

    } catch (error) {
      console.error('Upload error:', error);
      addMessage({ type: 'system', content: `❌ Failed to upload "${file.name}": ${error.message}` });
    }

    // Reset file input
    event.target.value = '';
  };

  const toggleUserProfile = () => {
    setShowUserProfile(!showUserProfile);
  };

  const toggleModelDropdown = (e) => {
    e.stopPropagation();
    setShowModelDropdown(!showModelDropdown);
    setShowUserProfile(false); // Close user profile if open
  };


  const handleLogout = () => {
    logout();
    setShowUserProfile(false);
    // Force page reload to show login page
    window.location.reload();
  };

  const updateChatHistory = (sessionId, firstMessage, sessionMessages) => {
    const updatedChat = chatHistoryService.addOrUpdateChat(sessionId, firstMessage, sessionMessages);
    setChatHistory(prev => {
      const newHistory = [...prev];
      const existingIndex = newHistory.findIndex(chat => chat.id === sessionId);
      
      if (existingIndex >= 0) {
        newHistory[existingIndex] = updatedChat;
      } else {
        newHistory.unshift(updatedChat);
      }
      
      return newHistory;
    });
  };

  const selectChat = (chatId) => {
    // Load the chat session with its messages using the service
    const chatSession = chatHistoryService.loadChatSession(chatId);
    
    if (chatSession) {
      setSession(chatId);
      clearMessages();
      
      // Load chat messages - check if messages exist and is an array
      if (chatSession.messages && Array.isArray(chatSession.messages)) {
        chatSession.messages.forEach(msg => {
          // Ensure we have required properties before adding message
          if (msg && msg.text && msg.type) {
            addMessage(msg.text, msg.type);
          }
        });
      }
      
      setSelectedChatId(chatId);
      
      // Mark selected chat as active
      setChatHistory(prev => prev.map(c => ({
        ...c,
        isActive: c.id === chatId
      })));
    } else {
      console.error('Chat session not found:', chatId);
    }
  };

  // Context menu handlers
  const handleContextMenu = (chatId, event) => {
    event.preventDefault();
    event.stopPropagation();
    
    const rect = event.currentTarget.getBoundingClientRect();
    setContextMenuPosition({
      x: rect.right - 120, // Adjust based on menu width
      y: rect.bottom
    });
    setContextMenuChatId(chatId);
  };

  const handleShareChat = (chatId) => {
    console.log('Share chat:', chatId);
    setContextMenuChatId(null);
    // TODO: Implement share functionality
  };

  const handleRenameChat = (chatId) => {
    
    setContextMenuChatId(null);
    // TODO: Implement rename functionality
  };

  const handleArchiveChat = (chatId) => {
    console.log('Archive chat:', chatId);
    setContextMenuChatId(null);
    // TODO: Implement archive functionality
  };

  const handleDeleteChat = (chatId, event) => {
    if (event) {
      event.stopPropagation();
    }
    const updatedHistory = chatHistoryService.deleteChat(chatId);
    setChatHistory(updatedHistory);
    if (selectedChatId === chatId) {
      setSelectedChatId(null);
    }
    setContextMenuChatId(null);
  };

  const filteredChats = chatHistoryService.searchChats(searchValue);

  // Get user profile from auth context or fallback to dummy data
  const getUserProfile = () => {
    if (userInfo) {
      // Parse full name from username (e.g., "Dr. Sarah Smith" -> "Dr. Sarah", "Smith")
      const parseFullName = (fullName) => {
        if (!fullName) return { firstName: 'User', lastName: '' };
        const parts = fullName.split(' ');
        if (parts.length >= 3) {
          // Handle titles like "Dr. Sarah Smith"
          return {
            firstName: parts.slice(0, -1).join(' '), // "Dr. Sarah"
            lastName: parts[parts.length - 1] // "Smith"
          };
        } else if (parts.length === 2) {
          return {
            firstName: parts[0],
            lastName: parts[1]
          };
        } else {
          return {
            firstName: parts[0],
            lastName: ''
          };
        }
      };

      const nameParts = parseFullName(userInfo.username || userInfo.name);
      
      return {
        firstName: userInfo.given_name || nameParts.firstName || 'User',
        lastName: userInfo.family_name || nameParts.lastName || '',
        email: userInfo.email || 'user@company.com',
        initials: getInitials(userInfo.given_name, userInfo.family_name, userInfo.name || userInfo.username),
        department: userInfo.department || 'Healthcare',
        role: userInfo.role || 'User'
      };
    }
    
    // No fallback - return null if no user info
    return null;
  };

  // Helper function to generate initials
  const getInitials = (firstName, lastName, fullName) => {
    if (firstName && lastName) {
      return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
    } else if (fullName) {
      const names = fullName.split(' ');
      if (names.length >= 2) {
        return `${names[0].charAt(0)}${names[names.length - 1].charAt(0)}`.toUpperCase();
      }
      return fullName.charAt(0).toUpperCase();
    }
    return 'U';
  };

  const userProfile = getUserProfile();
  
  // If no user profile, don't render user section
  if (!userProfile) {
    return (
      <div className={styles.layout}>
        {/* Sidebar */}
        <div className={`${styles.sidebar} ${isSidebarCollapsed ? styles.collapsed : ''}`}>
          <div className={styles.sidebarHeader}>
            <div className={styles.logo}>
              <span className={styles.logoText}>SecureAI</span>
              <button 
                className={styles.collapseBtn}
                onClick={toggleSidebar}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className={styles.main}>
          <div className={styles.content}>
            {children}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.layout}>
      {/* Sidebar */}
      <div className={`${styles.sidebar} ${isSidebarCollapsed ? styles.collapsed : ''}`}>
        <div className={styles.sidebarHeader}>
          <div className={styles.logo}>
            <span className={styles.logoText}>SecureAI</span>
            <button 
              className={styles.collapseBtn}
              onClick={toggleSidebar}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>

        <div className={styles.sidebarContent}>
          {/* Action Buttons */}
          <div className={styles.actionButtons}>
            <button className={styles.newChatBtn} onClick={handleNewChat}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              New chat
            </button>
          </div>

          {/* Recent Chats */}
          {!isSidebarCollapsed && (
            <>
              <div className={styles.sectionHeader}>
                <span>RECENT</span>
              </div>
              
              <div className={styles.searchContainer}>
                <input
                  type="text"
                  placeholder="Search conversations..."
                  value={searchValue}
                  onChange={(e) => setSearchValue(e.target.value)}
                  className={styles.searchInput}
                />
              </div>

              <div className={styles.chatList}>
                {filteredChats.map((chat) => (
                  <button
                    key={chat.id}
                    className={`${styles.chatItem} ${chat.isActive ? styles.active : ''}`}
                    onClick={() => selectChat(chat.id)}
                    onContextMenu={(e) => handleContextMenu(chat.id, e)}
                  >
                    <div className={styles.chatContent}>
                      <div className={styles.chatTitle}>
                        {chat.title}
                      </div>
                    </div>
                    <div className={styles.chatActions}>
                      <button
                        className={styles.chatActionBtn}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteChat(chat.id, e);
                        }}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M3 6H5H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </button>
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Context Menu */}
      {contextMenuChatId && (
        <div 
          className={styles.contextMenu}
          style={{
            position: 'fixed',
            left: contextMenuPosition.x,
            top: contextMenuPosition.y,
            zIndex: 1000
          }}
        >
          <button 
            className={styles.contextMenuItem}
            onClick={() => handleShareChat(contextMenuChatId)}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M4 12V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <polyline points="16,6 12,2 8,6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <line x1="12" y1="2" x2="12" y2="15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Share
          </button>
          <button 
            className={styles.contextMenuItem}
            onClick={() => handleRenameChat(contextMenuChatId)}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M12 20H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M16.5 3.5C16.8978 3.10218 17.4374 2.87868 18 2.87868C18.5626 2.87868 19.1022 3.10218 19.5 3.5C19.8978 3.89782 20.1213 4.43739 20.1213 5C20.1213 5.56261 19.8978 6.10218 19.5 6.5L7 19L3 20L4 16L16.5 3.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Rename
          </button>
          <button 
            className={styles.contextMenuItem}
            onClick={() => handleArchiveChat(contextMenuChatId)}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M21 8V21L12 17L3 21V8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M1 3H23V8H1V3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Archive
          </button>
          <button 
            className={`${styles.contextMenuItem} ${styles.danger}`}
            onClick={() => handleDeleteChat(contextMenuChatId)}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M3 6H5H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Delete
          </button>
        </div>
      )}

      {/* Main Content Area */}
      <div className={styles.main}>
        {/* Top Header with Model Selection and User Profile */}
        <div className={styles.headerBar}>
          <div className={styles.headerContent}>
            <div className={styles.headerTitle}>
              {/* Optional: Could add breadcrumbs or current page title here */}
            </div>
            
            {/* OpenAI Model Dropdown */}
            <div className={styles.modelSection}>
              <button 
                className={styles.modelDropdownBtn}
                onClick={toggleModelDropdown}
              >
                <div className={styles.modelIcon}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <polyline points="2,7 12,12 22,7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <polyline points="12,22 12,12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div className={styles.modelInfo}>
                  <div className={styles.modelName}>
                    {currentModel?.name?.toUpperCase() || 'NO MODEL'}
                  </div>
                  <div className={styles.modelDesc}>
                    {getModelDescription(currentModel)}
                  </div>
                </div>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M6 9L12 15L18 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>

              {/* Model Dropdown */}
              {showModelDropdown && (
                <div className={styles.modelDropdown}>
                  <div className={styles.modelDropdownHeader}>
                    <span>Select Model</span>
                  </div>
                  <div className={styles.modelDropdownContent}>
                    {models.llm_models.length > 0 ? (
                      models.llm_models.map((model) => (
                        <button
                          key={model.id}
                          className={`${styles.modelOption} ${selectedModel === model.id ? styles.selected : ''}`}
                          onClick={() => handleModelSelect(model.id)}
                        >
                          <div className={styles.modelOptionContent}>
                            <div className={styles.modelOptionName}>
                              {model.name?.toUpperCase()}
                            </div>
                            <div className={styles.modelOptionDesc}>
                              {getModelDescription(model)}
                            </div>
                          </div>
                          {selectedModel === model.id && (
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                              <polyline points="20,6 9,17 4,12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          )}
                        </button>
                      ))
                    ) : (
                      <div className={styles.noModelsMessage}>
                        No models available. Please check your configuration.
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            {/* User Profile Section */}
            <div className={styles.userSection}>
              <button 
                className={styles.userProfile}
                onClick={toggleUserProfile}
              >
                <div className={styles.userAvatar}>
                  {userProfile.initials}
                </div>
                <div className={styles.userInfo}>
                  <div className={styles.userName}>
                    {userProfile.firstName} {userProfile.lastName}
                  </div>
                  <div className={styles.userRole}>
                    {userProfile.role.charAt(0).toUpperCase() + userProfile.role.slice(1).toLowerCase()}
                  </div>
                </div>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M6 9L12 15L18 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>

              {/* User Profile Dropdown */}
              {showUserProfile && (
                <div className={styles.userDropdown}>
                  <div className={styles.userDropdownHeader}>
                    <div className={styles.userAvatarLarge}>
                      {userProfile.initials}
                    </div>
                    <div className={styles.userDetails}>
                      <div className={styles.userFullName}>
                        {userProfile.firstName} {userProfile.lastName}
                      </div>
                      <div className={styles.userEmail}>
                        {userProfile.email}
                      </div>
                      <div className={styles.userDepartment}>
                        {userProfile.department} • {userProfile.role.charAt(0).toUpperCase() + userProfile.role.slice(1).toLowerCase()}
                      </div>
                    </div>
                  </div>
                  
                  <div className={styles.userDropdownActions}>
                    <button className={styles.dropdownItem}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Profile
                    </button>
                    <button className={styles.dropdownItem}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M12 1V3M12 21V23M4.22 4.22L5.64 5.64M18.36 18.36L19.78 19.78M1 12H3M21 12H23M4.22 19.78L5.64 18.36M18.36 5.64L19.78 4.22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Settings
                    </button>
                    <button className={styles.dropdownItem} onClick={handleLogout}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <polyline points="16,17 21,12 16,7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className={styles.content}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;
