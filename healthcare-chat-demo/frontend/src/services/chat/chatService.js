// Simple chat service for SecureAI Healthcare Assistant
import { API_CONFIG } from '../../config/api.config';

export const chatService = {
  /**
   * Send chat message with PHI protection
   */
  async sendMessage(message, options = {}) {
    try {
      // Get user role from localStorage (set during login)
      const userRole = localStorage.getItem('user_role') || 'general';
      const username = localStorage.getItem('username') || 'Anonymous';
      
      console.log('📤 Chat Service: Sending message to backend...', { message, userRole, username });
      
      const authToken = localStorage.getItem('auth_token');
      
      const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.chat}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          user_role: userRole,
          user_id: username,
          auth_token: authToken
        })
      });

      console.log('📥 Chat Service: Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Chat Service: HTTP error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Chat Service: Parsed response:', data);
      
      // Return in format expected by useChat hook
      return {
        success: true,
        data: {
          response: data.decrypted_response,
          original_message: data.original_message,
          protected_message: data.protected_message,
          phi_detected: data.phi_detected,
          audit_trail: data.audit_trail,
          llm_provider: data.llm_provider,
          timestamp: data.timestamp
        }
      };
    } catch (error) {
      console.error('❌ Chat service error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
};

export default chatService;
