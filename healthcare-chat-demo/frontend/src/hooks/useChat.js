import { useCallback, useContext } from 'react';
import { useApi } from './useApi';
import { ChatContext } from '@contexts/ChatContext';
import { MESSAGE_TYPES, QUERY_STATUS } from '@utils/constants';

export const useChat = () => {
  const context = useContext(ChatContext);
  const api = useApi();

  const sendMessage = useCallback(async (text, options = {}) => {
    if (!text.trim()) return;

    try {
      // Add user message immediately
      context.addUserMessage(text);
      
      // Set loading state
      context.setLoading(true);
      context.setStatus(QUERY_STATUS.PROCESSING);

      console.log('📤 useChat: Sending message...', { text });
      
      // Send message - simplified, no session handling
      const result = await api.sendMessage(text);
      
      console.log('📥 useChat: Received result:', result);
      
      // Check if result has error
      if (!result || !result.success || result.error) {
        const errorMsg = result?.error || 'Failed to get response from server';
        console.error('❌ useChat: Error in result:', errorMsg);
        context.addErrorMessage(errorMsg);
        return;
      }
      
      // Extract response from result.data.response
      const responseText = result.data?.response;
      
      if (responseText) {
        console.log('✅ useChat: Adding AI response to chat');
        context.addMessage({
          type: MESSAGE_TYPES.ASSISTANT,
          content: responseText,
          timestamp: new Date().toISOString(),
          sources: [],
          model_used: result.data?.llm_provider || 'AWS Bedrock'
        });
      } else {
        console.error('❌ useChat: No response text in result.data:', result);
        context.addErrorMessage('No response received from AI');
      }
      
    } catch (error) {
      console.error('❌ useChat: Exception:', error);
      context.addErrorMessage(`Failed to send message: ${error.message}`);
    } finally {
      context.setLoading(false);
      context.setStatus(QUERY_STATUS.IDLE);
    }
  }, [context, api]);

  const newChat = useCallback(() => {
    context.resetChat();
  }, [context]);

  return {
    messages: context.messages,
    isLoading: context.isLoading,
    error: context.error,
    status: context.status,
    currentSession: context.currentSession,
    models: context.models,
    sendMessage,
    newChat,
    addMessage: context.addMessage,
    setModels: context.setModels,
    setCurrentLLMModel: context.setCurrentLLMModel,
    setCurrentEmbeddingModel: context.setCurrentEmbeddingModel,
  };
};
