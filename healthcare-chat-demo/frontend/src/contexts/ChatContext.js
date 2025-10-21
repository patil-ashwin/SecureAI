// src/contexts/ChatContext.js
import React, { createContext, useReducer, useCallback } from 'react';
import { MESSAGE_TYPES, QUERY_STATUS } from '@utils/constants';
import { generateId } from '@utils/helpers';

// Initial state
const initialState = {
  messages: [],
  currentSession: null,
  isLoading: false,
  error: null,
  status: QUERY_STATUS.IDLE,
  models: {
    embedding_models: [],
    llm_models: [],
    current_embedding_model: null,
    current_llm_model: null
  }
};

// Action types
const ACTION_TYPES = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_STATUS: 'SET_STATUS',
  ADD_MESSAGE: 'ADD_MESSAGE',
  UPDATE_MESSAGE: 'UPDATE_MESSAGE',
  CLEAR_MESSAGES: 'CLEAR_MESSAGES',
  SET_SESSION: 'SET_SESSION',
  SET_MODELS: 'SET_MODELS',
  RESET_CHAT: 'RESET_CHAT'
};

// Reducer
const chatReducer = (state, action) => {
  switch (action.type) {
    case ACTION_TYPES.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };

    case ACTION_TYPES.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isLoading: false,
        status: action.payload ? QUERY_STATUS.ERROR : state.status
      };

    case ACTION_TYPES.SET_STATUS:
      return {
        ...state,
        status: action.payload
      };

    case ACTION_TYPES.ADD_MESSAGE:
      return {
        ...state,
        messages: [...state.messages, action.payload]
      };

    case ACTION_TYPES.UPDATE_MESSAGE:
      return {
        ...state,
        messages: state.messages.map(msg =>
          msg.id === action.payload.id ? { ...msg, ...action.payload.updates } : msg
        )
      };

    case ACTION_TYPES.CLEAR_MESSAGES:
      return {
        ...state,
        messages: []
      };

    case ACTION_TYPES.SET_SESSION:
      return {
        ...state,
        currentSession: action.payload
      };

    case ACTION_TYPES.SET_MODELS:
      return {
        ...state,
        models: action.payload
      };

    case ACTION_TYPES.RESET_CHAT:
      return {
        ...initialState,
        models: state.models // Preserve models when resetting chat
      };

    default:
      return state;
  }
};

// Context
const ChatContext = createContext();

// Provider component
export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Actions
  const setLoading = useCallback((loading) => {
    dispatch({ type: ACTION_TYPES.SET_LOADING, payload: loading });
  }, []);

  const setError = useCallback((error) => {
    dispatch({ type: ACTION_TYPES.SET_ERROR, payload: error });
  }, []);

  const setStatus = useCallback((status) => {
    dispatch({ type: ACTION_TYPES.SET_STATUS, payload: status });
  }, []);

  const addMessage = useCallback((message) => {
    const messageWithId = {
      id: generateId(),
      timestamp: Date.now(),
      ...message
    };
    dispatch({ type: ACTION_TYPES.ADD_MESSAGE, payload: messageWithId });
    return messageWithId.id;
  }, []);

  const addUserMessage = useCallback((content) => {
    return addMessage({
      type: MESSAGE_TYPES.USER,
      content,
      status: QUERY_STATUS.SENT
    });
  }, [addMessage]);

  const addAssistantMessage = useCallback((content, metadata = {}) => {
    return addMessage({
      type: MESSAGE_TYPES.ASSISTANT,
      content,
      metadata,
      status: QUERY_STATUS.COMPLETED
    });
  }, [addMessage]);

  const addSystemMessage = useCallback((content) => {
    return addMessage({
      type: MESSAGE_TYPES.SYSTEM,
      content,
      status: QUERY_STATUS.COMPLETED
    });
  }, [addMessage]);

  const addErrorMessage = useCallback((content) => {
    return addMessage({
      type: MESSAGE_TYPES.ERROR,
      content,
      status: QUERY_STATUS.ERROR
    });
  }, [addMessage]);

  const updateMessage = useCallback((id, updates) => {
    dispatch({
      type: ACTION_TYPES.UPDATE_MESSAGE,
      payload: { id, updates }
    });
  }, []);

  const clearMessages = useCallback(() => {
    dispatch({ type: ACTION_TYPES.CLEAR_MESSAGES });
  }, []);

  const setSession = useCallback((sessionId) => {
    dispatch({ type: ACTION_TYPES.SET_SESSION, payload: sessionId });
  }, []);

  const setModels = useCallback((models) => {
    dispatch({ type: ACTION_TYPES.SET_MODELS, payload: models });
  }, []);

  const resetChat = useCallback(() => {
    dispatch({ type: ACTION_TYPES.RESET_CHAT });
  }, []);

  const value = {
    // State
    ...state,
    
    // Actions
    setLoading,
    setError,
    setStatus,
    addMessage,
    addUserMessage,
    addAssistantMessage,
    addSystemMessage,
    addErrorMessage,
    updateMessage,
    clearMessages,
    setSession,
    setModels,
    resetChat
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export { ChatContext };
