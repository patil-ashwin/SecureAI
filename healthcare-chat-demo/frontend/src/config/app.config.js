// src/config/app.config.js
export const APP_CONFIG = {
  name: 'SecureAI Healthcare Assistant',
  version: '1.0.0',
  description: 'AI-powered healthcare assistant with PHI protection',
  author: 'SecureAI Team',
  homepage: '/',
  
  // Model Configuration
  models: {
    chat: {
      name: 'Claude 3.5 Sonnet',
      provider: 'AWS Bedrock',
      id: 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    },
    embeddings: {
      name: 'Titan Text Embeddings V2',
      provider: 'AWS Bedrock',
      id: 'amazon.titan-embed-text-v2:0',
      dimensions: 1024
    }
  },
  
  // Feature flags
  features: {
    darkMode: true,
    exportData: true,
    followUpQueries: true,
    suggestions: true,
    parameterForms: true
  },
  
  // UI Configuration
  ui: {
    maxMessages: 100,
    typingSpeed: 50,
    animationDuration: 300,
    autoScroll: true
  },
  
  // Development settings
  enableLogging: process.env.NODE_ENV === 'development',
  enableDebug: process.env.REACT_APP_DEBUG === 'true'
};
