// src/services/chatHistoryService.js
class ChatHistoryService {
  constructor() {
    this.storageKey = 'tigerGraphRAG_history';
  }

  /**
   * Get chat history from localStorage
   * @returns {Array} Chat history
   */
  getChatHistory() {
    try {
      const history = localStorage.getItem(this.storageKey);
      return history ? JSON.parse(history) : [];
    } catch (error) {
      console.error('Error loading chat history:', error);
      return [];
    }
  }

  /**
   * Save chat history to localStorage
   * @param {Array} history - Chat history
   */
  saveChatHistory(history) {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(history));
    } catch (error) {
      console.error('Error saving chat history:', error);
    }
  }

  /**
   * Add a new chat to history
   * @param {Object} chat - Chat object
   */
  addChat(chat) {
    const history = this.getChatHistory();
    const newChat = {
      id: Date.now().toString(),
      title: chat.title || 'New Chat',
      timestamp: Date.now(),
      ...chat
    };
    
    history.unshift(newChat);
    this.saveChatHistory(history);
    return newChat;
  }

  /**
   * Add or update a chat in history
   * @param {string} sessionId - Session ID
   * @param {string} firstMessage - First message content
   * @param {Array} sessionMessages - All messages in session
   */
  addOrUpdateChat(sessionId, firstMessage, sessionMessages) {
    const history = this.getChatHistory();
    const existingIndex = history.findIndex(chat => chat.id === sessionId);
    
    const chatData = {
      id: sessionId,
      title: firstMessage || 'New Chat',
      timestamp: Date.now(),
      lastMessage: firstMessage,
      messageCount: sessionMessages ? sessionMessages.length : 1
    };

    if (existingIndex !== -1) {
      // Update existing chat
      history[existingIndex] = { ...history[existingIndex], ...chatData };
    } else {
      // Add new chat
      history.unshift(chatData);
    }
    
    this.saveChatHistory(history);
    return chatData;
  }

  /**
   * Update a chat in history
   * @param {string} chatId - Chat ID
   * @param {Object} updates - Updates to apply
   */
  updateChat(chatId, updates) {
    const history = this.getChatHistory();
    const index = history.findIndex(chat => chat.id === chatId);
    
    if (index !== -1) {
      history[index] = { ...history[index], ...updates };
      this.saveChatHistory(history);
    }
  }

  /**
   * Delete a chat from history
   * @param {string} chatId - Chat ID
   */
  deleteChat(chatId) {
    const history = this.getChatHistory();
    const filteredHistory = history.filter(chat => chat.id !== chatId);
    this.saveChatHistory(filteredHistory);
  }

  /**
   * Clear all chat history
   */
  clearHistory() {
    localStorage.removeItem(this.storageKey);
  }

  /**
   * Search chat history
   * @param {string} query - Search query
   * @returns {Array} Filtered chat history
   */
  searchChats(query) {
    const history = this.getChatHistory();
    if (!query || !query.trim()) return history;
    
    const lowercaseQuery = query.toLowerCase();
    return history.filter(chat => 
      chat.title.toLowerCase().includes(lowercaseQuery) ||
      (chat.lastMessage && chat.lastMessage.toLowerCase().includes(lowercaseQuery))
    );
  }

  /**
   * Get chat by ID
   * @param {string} chatId - Chat ID
   * @returns {Object|null} Chat object or null
   */
  getChatById(chatId) {
    const history = this.getChatHistory();
    return history.find(chat => chat.id === chatId) || null;
  }

  /**
   * Get recent chats
   * @param {number} limit - Number of recent chats to return
   * @returns {Array} Recent chats
   */
  getRecentChats(limit = 10) {
    const history = this.getChatHistory();
    return history.slice(0, limit);
  }
}

export const chatHistoryService = new ChatHistoryService();
export default chatHistoryService;
