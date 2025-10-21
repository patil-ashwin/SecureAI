// src/services/models/modelsService.js
import apiClient from '../api/apiClient';
import { ENDPOINTS } from '../api/endpoints';

class ModelsService {
  /**
   * Get available models information
   * @returns {Promise<Object>} Models data
   */
  async getModels() {
    try {
      const response = await apiClient.get(ENDPOINTS.MODELS);
      return response;
    } catch (error) {
      console.error('Error fetching models:', error);
      throw error;
    }
  }

  /**
   * Get embedding models only
   * @returns {Promise<Array>} Embedding models
   */
  async getEmbeddingModels() {
    try {
      const response = await this.getModels();
      return response.embedding_models || [];
    } catch (error) {
      console.error('Error fetching embedding models:', error);
      return [];
    }
  }

  /**
   * Get LLM models only
   * @returns {Promise<Array>} LLM models
   */
  async getLLMModels() {
    try {
      const response = await this.getModels();
      return response.llm_models || [];
    } catch (error) {
      console.error('Error fetching LLM models:', error);
      return [];
    }
  }

  /**
   * Get current active models
   * @returns {Promise<Object>} Current models
   */
  async getCurrentModels() {
    try {
      const response = await this.getModels();
      return {
        embedding: response.current_embedding_model,
        llm: response.current_llm_model
      };
    } catch (error) {
      console.error('Error fetching current models:', error);
      return {
        embedding: null,
        llm: null
      };
    }
  }
}

export default new ModelsService();
