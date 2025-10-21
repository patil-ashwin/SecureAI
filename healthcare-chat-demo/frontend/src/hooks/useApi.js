// Simplified API hook for SecureAI
import { useState, useCallback } from 'react';
import { chatService, modelsService } from '@services';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiCall, ...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall(...args);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Simplified sendMessage - no retries, no extra options
  const sendMessage = useCallback(async (message) => {
    return execute(chatService.sendMessage, message);
  }, [execute]);

  const fetchModels = useCallback(async () => {
    return execute(modelsService.getModels);
  }, [execute]);

  return {
    loading,
    error,
    sendMessage,
    fetchModels
  };
};
